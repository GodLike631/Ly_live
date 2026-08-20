#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
《遮天法 2.0》定制爬虫源 - goodav17 (正妹AV 完美修复版)
- 修复防盗链导致播放连接超时的问题
- 优化 TVBox Header 注入与真实播放源重定向追踪
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

    # 4. 播放地址解析 (强化 Referer 注入与重定向追踪)
    def playerContent(self, flag, id, vipFlags):
        url = self._fix_url(id)
        html = self._fetch(url)

        # 1. 查找 iframe 真实嵌入地址
        iframe_src = ""
        iframe_match = re.search(r'<iframe[^>]+id=[\'"]video_frame[\'"][^>]+src=[\'"]([^\'"]+)[\'"]', html)
        if iframe_match:
            iframe_src = iframe_match.group(1)
        else:
            embed_m = re.search(r'src=[\'"](https?://ggjav\.com/main/embed\?[^\'"]+)[\'"]', html)
            if embed_m:
                iframe_src = embed_m.group(1)

        real_video_url = ""

        # 2. 从 iframe 参数中直接提取 Base64
        if "embed?u=" in iframe_src or "embed?u=" in html:
            b64_match = re.search(r'embed\?u=([a-zA-Z0-9+/=]+)', iframe_src or html)
            if b64_match:
                try:
                    b64_str = b64_match.group(1)
                    decoded = base64.b64decode(b64_str).decode("utf-8")
                    if decoded.startswith("http"):
                        real_video_url = decoded
                except Exception:
                    pass

        # 3. 若直接 Base64 不通，请求 iframe 内部页面进一步探测 video 标签
        if not real_video_url and iframe_src:
            iframe_html = self._fetch(iframe_src, headers={"Referer": self.siteUrl})
            v_match = re.search(r'<source[^>]+src=[\'"]([^\'"]+\.mp4[^\'"]*)[\'"]', iframe_html) or \
                      re.search(r'src=[\'"](https?://[^"\']+\.mp4[^"\']*)[\'"]', iframe_html)
            if v_match:
                real_video_url = v_match.group(1)

        # 4. 成功获取直链后，注入防盗链所需的完整 Headers
        if real_video_url:
            # 兼容 TVBox/影视仓 的 Header 协议（Referer / User-Agent）
            play_headers = (
                f"User-Agent={self.headers['User-Agent']}"
                f"&Referer=https://ggjav.com/"
                f"&Origin=https://ggjav.com"
            )
            return {
                "parse": 0,
                "url": real_video_url,
                "header": play_headers
            }

        # 兜底：嗅探
        fallback_url = iframe_src if iframe_src else url
        return {
            "parse": 1,
            "url": fallback_url,
            "header": f"Referer={self.siteUrl}/"
        }

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
    # 针对截图中的 4881990 进行单项播放测试
    test_id = "/html/4881990/"
    print(f"=== 测试详情与播放 ({test_id}) ===")
    detail = spider.detailContent([test_id])
    print("详情返回:", json.dumps(detail, ensure_ascii=False, indent=2))
    play = spider.playerContent("", test_id, "")
    print("播放返回:", json.dumps(play, ensure_ascii=False, indent=2))
