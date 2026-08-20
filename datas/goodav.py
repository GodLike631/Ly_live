#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
《遮天法 2.0》定制爬虫源 - goodav17 (正妹AV)
- 适配真實分類: 無碼/人妻/巨乳/中出/OL/VR/本土等
- 破除 17 秒試看: 自動提取 iframe 中 Base64 加密的完整 MP4 直鏈
"""

import sys
import os
import re
import json
import base64
import html as html_lib
from urllib import parse
import requests
from bs4 import BeautifulSoup

try:
    from base.spider import Spider as SpiderBase
except ImportError:
    class SpiderBase:
        pass


class Spider(SpiderBase):
    def __init__(self):
        super().__init__()
        self.siteUrl = "https://goodav17.com"
        self.session = requests.Session()
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh-TW;q=0.9,zh;q=0.8,en;q=0.7",
            "Referer": "https://goodav17.com/"
        }

    def init(self, extend=""):
        return True

    def isVideoFormat(self, url):
        formats = [".m3u8", ".mp4", ".flv", ".mkv", ".ts", ".mov"]
        return any(f in url.lower() for f in formats)

    def manualVideoCheck(self):
        return False

    def _fetch(self, url, headers=None, timeout=12):
        h = self.headers.copy()
        if headers:
            h.update(headers)
        try:
            resp = self.session.get(url, headers=h, timeout=timeout, allow_redirects=True)
            resp.encoding = "utf-8"
            return resp.text
        except Exception:
            return ""

    def _fix_url(self, url):
        if not url:
            return ""
        if url.startswith("http://") or url.startswith("https://"):
            return url
        if url.startswith("//"):
            return f"https:{url}"
        if url.startswith("/"):
            return f"{self.siteUrl}{url}"
        return f"{self.siteUrl}/{url}"

    def _clean_title(self, title):
        t = html_lib.unescape(title or "")
        t = re.sub(r"<[^>]+>", "", t)
        return t.strip()

    # 1. 首页分类 (homeContent)
    def homeContent(self, filter=False):
        classes = [
            {"type_name": "無碼專區", "type_id": "type_無碼"},
            {"type_name": "本土自拍", "type_id": "local"},
            {"type_name": "VR專區", "type_id": "vr"},
            {"type_name": "人妻熟女", "type_id": "type_人妻"},
            {"type_name": "巨乳美胸", "type_id": "type_巨乳"},
            {"type_name": "OL制服", "type_id": "type_OL"},
            {"type_name": "潮吹中出", "type_id": "type_中出"},
            {"type_name": "可愛女友", "type_id": "type_可愛"},
            {"type_name": "美腿美尻", "type_id": "type_美腿"},
            {"type_name": "多P群交", "type_id": "type_多P"},
            {"type_name": "絲襪誘惑", "type_id": "type_絲襪"},
            {"type_name": "女僕教師", "type_id": "type_教師或家教"},
            {"type_name": "女學生", "type_id": "type_學生"}
        ]
        return {"class": classes}

    # 2. 分类列表 (categoryContent)
    def categoryContent(self, tid, pg="1", filter=False, extend=None):
        pg = str(pg)
        if tid.startswith("type_"):
            type_name = tid.replace("type_", "")
            encoded_name = parse.quote(type_name)
            url = f"{self.siteUrl}/type/{encoded_name}/{pg}/"
        elif tid == "local":
            url = f"{self.siteUrl}/local/{pg}/"
        elif tid == "vr":
            url = f"{self.siteUrl}/vr/{pg}/"
        else:
            encoded_name = parse.quote(tid)
            url = f"{self.siteUrl}/type/{encoded_name}/{pg}/"

        html = self._fetch(url)
        soup = BeautifulSoup(html, "html.parser")
        videos = []
        seen = set()

        for item in soup.select(".movie, .movie_image"):
            a_tag = item.find("a") if item.name != "a" else item
            if not a_tag:
                continue

            href = a_tag.get("href", "")
            if not href or href in seen or "/html/" not in href:
                continue

            img = item.find("img")
            name = a_tag.get_text(strip=True) or (img.get("alt", "") if img else "")
            pic = (img.get("large_image") or img.get("small_image") or img.get("src", "")) if img else ""

            if href and (name or img):
                seen.add(href)
                videos.append({
                    "vod_id": href,
                    "vod_name": self._clean_title(name),
                    "vod_pic": self._fix_url(pic),
                    "vod_remarks": ""
                })

        return {
            "list": videos,
            "page": int(pg),
            "pagecount": int(pg) + 1 if len(videos) >= 12 else int(pg),
            "limit": len(videos),
            "total": 9999
        }

    # 3. 详情页解析 (detailContent)
    def detailContent(self, ids):
        vod_id = ids[0]
        url = self._fix_url(vod_id)
        html = self._fetch(url)
        soup = BeautifulSoup(html, "html.parser")

        title_node = soup.select_one("#m_title_text, #m_title, h1, .title")
        title = self._clean_title(title_node.get_text(strip=True) if title_node else "正妹AV")

        img_node = soup.select_one("#m_image img, .m_image img")
        pic = self._fix_url(img_node.get("src", "")) if img_node else ""

        # 番号与类型信息提取
        remarks = ""
        desig_node = soup.select_one("#m_designation")
        if desig_node:
            remarks = self._clean_title(desig_node.get_text(strip=True))

        return {
            "list": [{
                "vod_id": vod_id,
                "vod_name": title,
                "vod_pic": pic,
                "vod_remarks": remarks,
                "vod_play_from": "正妹專線",
                "vod_play_url": f"完整高清${url}"
            }]
        }

    # 4. 播放地址解析 (四极解密：破除 17 秒试看)
    def playerContent(self, flag, id, vipFlags):
        url = self._fix_url(id)
        html = self._fetch(url)

        # 核心解密：匹配 iframe 中的嵌入参数 u=Base64
        # 形式：src="https://ggjav.com/main/embed?u=aHR0cHM6Ly92aWRlby0...=&site=goodav"
        embed_match = re.search(r'embed\?u=([a-zA-Z0-9+/=]+)', html)
        if embed_match:
            try:
                b64_str = embed_match.group(1)
                real_video_url = base64.b64decode(b64_str).decode("utf-8")
                if real_video_url.startswith("http"):
                    # 成功提取完整直链，直接直连播放（免第三方页面 17 秒广告拦截）
                    return {
                        "parse": 0,
                        "url": real_video_url,
                        "header": {
                            "User-Agent": self.headers["User-Agent"],
                            "Referer": "https://ggjav.com/"
                        }
                    }
            except Exception:
                pass

        # 备选提取：直接探测源码中可能存在的其他 mp4 / m3u8
        video_match = re.search(r'(https?://[^"\s\',]+\.(?:m3u8|mp4)[^"\s\',]*)', html)
        if video_match:
            return {
                "parse": 0,
                "url": video_match.group(1).replace(r"\/", "/"),
                "header": {"Referer": "https://goodav17.com/"}
            }

        # 兜底：嗅探 iframe
        iframe_match = re.search(r'<iframe[^>]+id=[\'"]video_frame[\'"][^>]+src=[\'"]([^\'"]+)[\'"]', html)
        if iframe_match:
            return {
                "parse": 1,
                "url": self._fix_url(iframe_match.group(1)),
                "header": {"Referer": "https://goodav17.com/"}
            }

        return {"parse": 1, "url": url, "header": {"Referer": "https://goodav17.com/"}}

    # 5. 搜索 (searchContent)
    def searchContent(self, key, quick, pg="1"):
        search_url = f"{self.siteUrl}/search/{parse.quote(key)}/{pg}/"
        html = self._fetch(search_url)
        soup = BeautifulSoup(html, "html.parser")
        videos = []
        seen = set()

        for item in soup.select(".movie"):
            a_tag = item.find("a")
            if not a_tag:
                continue

            href = a_tag.get("href", "")
            if not href or href in seen or "/html/" not in href:
                continue

            img = item.find("img")
            name = a_tag.get_text(strip=True) or (img.get("alt", "") if img else "")
            pic = (img.get("large_image") or img.get("small_image") or img.get("src", "")) if img else ""

            if href and (name or img):
                seen.add(href)
                videos.append({
                    "vod_id": href,
                    "vod_name": self._clean_title(name),
                    "vod_pic": self._fix_url(pic),
                    "vod_remarks": ""
                })

        return {"list": videos}

    # 6. 本地代理 (localProxy)
    def localProxy(self, param):
        return [404, "text/plain", "Not Supported"]


if __name__ == "__main__":
    spider = Spider()
    spider.init()
    print("--- 1. 測試 homeContent ---")
    print(json.dumps(spider.homeContent(), ensure_ascii=False, indent=2))
    
    print("\n--- 2. 測試 categoryContent (無碼專區) ---")
    cat = spider.categoryContent("type_無碼", "1", False, {})
    print(json.dumps(cat, ensure_ascii=False, indent=2))
    
    if cat["list"]:
        test_id = cat["list"][0]["vod_id"]
        print(f"\n--- 3. 測試 detailContent ({test_id}) ---")
        detail = spider.detailContent([test_id])
        print(json.dumps(detail, ensure_ascii=False, indent=2))
        
        print(f"\n--- 4. 測試 playerContent ({test_id}) [解密完整MP4直鏈] ---")
        play = spider.playerContent("", test_id, "")
        print(json.dumps(play, ensure_ascii=False, indent=2))
