#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
《遮天法》定制爬虫源 - goodav17
遵循 TVBox / py-drpy 接口契约规范
"""

import sys
import os
import re
import json
import time
import base64
import html as html_lib
from urllib import parse
import requests
from bs4 import BeautifulSoup

# 兼容 TVBox / drpy 基础类导入
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
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1"
        }

    def init(self, extend=""):
        return True

    def isVideoFormat(self, url):
        formats = [".m3u8", ".mp4", ".flv", ".mkv", ".ts", ".avi", ".mov", ".webm"]
        return any(f in url.lower() for f in formats)

    def manualVideoCheck(self):
        return False

    def _fetch(self, url, headers=None, timeout=10):
        h = self.headers.copy()
        if headers:
            h.update(headers)
        try:
            resp = self.session.get(url, headers=h, timeout=timeout, allow_redirects=True)
            resp.encoding = resp.apparent_encoding or "utf-8"
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
            {"type_name": "全部视频", "type_id": "all"},
            {"type_name": "最新更新", "type_id": "new"},
            {"type_name": "热门精选", "type_id": "hot"},
            {"type_name": "国产高清", "type_id": "1"},
            {"type_name": "日韩精选", "type_id": "2"},
            {"type_name": "欧美大片", "type_id": "3"}
        ]
        return {"class": classes}

    # 2. 分类列表 (categoryContent)
    def categoryContent(self, tid, pg="1", filter=False, extend=None):
        pg = str(pg)
        if tid == "all":
            url = f"{self.siteUrl}/page/{pg}" if pg != "1" else f"{self.siteUrl}/"
        elif tid.isdigit():
            url = f"{self.siteUrl}/category/{tid}/page/{pg}" if pg != "1" else f"{self.siteUrl}/category/{tid}/"
        else:
            url = f"{self.siteUrl}/{tid}/page/{pg}" if pg != "1" else f"{self.siteUrl}/{tid}/"

        html = self._fetch(url)
        soup = BeautifulSoup(html, "html.parser")
        videos = []

        # 通用匹配：卡片容器及 a 标签
        items = soup.select(".video-item, .item, .movie-item, article, .post") or soup.find_all("a", href=re.compile(r"/(?:video|vod|play|watch|\d+)/"))
        seen = set()

        for item in items:
            a_tag = item if item.name == "a" else item.find("a")
            if not a_tag:
                continue

            href = a_tag.get("href", "")
            if not href or href in seen or href == self.siteUrl or href == f"{self.siteUrl}/":
                continue

            img_tag = item.find("img") if item.name != "a" else a_tag.find("img")
            name = a_tag.get("title") or (img_tag.get("alt", "") if img_tag else "") or a_tag.get_text(strip=True)
            pic = (img_tag.get("data-original") or img_tag.get("data-src") or img_tag.get("src", "")) if img_tag else ""

            if name and href:
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
            "pagecount": int(pg) + 1 if len(videos) >= 10 else int(pg),
            "limit": len(videos),
            "total": 9999
        }

    # 3. 详情页解析 (detailContent)
    def detailContent(self, ids):
        vod_id = ids[0]
        url = self._fix_url(vod_id)
        html = self._fetch(url)
        soup = BeautifulSoup(html, "html.parser")

        # 获取影片标题
        title_node = soup.select_one("h1, h2, .title, .post-title, .entry-title")
        title = self._clean_title(title_node.get_text(strip=True) if title_node else "在线播放")

        # 获取封面图
        pic_node = soup.select_one(".poster img, .cover img, .entry-content img, article img")
        pic = self._fix_url(pic_node.get("src") or pic_node.get("data-src", "")) if pic_node else ""

        # 选集探测：寻找所有可能的播放/选集链接
        ep_links = []
        for a in soup.select("a[href*='play'], a[href*='video'], .playlist a, .episodes a"):
            ep_href = a.get("href", "")
            ep_name = a.get_text(strip=True) or a.get("title", "")
            if ep_href and ep_name:
                ep_links.append(f"{ep_name}${self._fix_url(ep_href)}")

        # 若无明确列表，则当前详情页即为单集播放页
        if not ep_links:
            ep_links.append(f"正片${url}")

        return {
            "list": [{
                "vod_id": vod_id,
                "vod_name": title,
                "vod_pic": pic,
                "vod_play_from": "遮天专线",
                "vod_play_url": "#".join(ep_links)
            }]
        }

    # 4. 播放地址多层提取 (playerContent)
    def playerContent(self, flag, id, vipFlags):
        url = self._fix_url(id)
        html = self._fetch(url)

        # 13层提取：优先探测直接嵌入的 m3u8 / mp4 地址
        m3u8_match = re.search(r'(https?://[^"\s\',]+\.m3u8[^"\s\',]*)', html)
        if m3u8_match:
            return {"parse": 0, "url": m3u8_match.group(1).replace(r"\/", "/"), "header": f"Referer={self.siteUrl}/"}

        mp4_match = re.search(r'(https?://[^"\s\',]+\.mp4[^"\s\',]*)', html)
        if mp4_match:
            return {"parse": 0, "url": mp4_match.group(1).replace(r"\/", "/"), "header": f"Referer={self.siteUrl}/"}

        # 探测 player_data / player_aaaa / 初始化 JS 变量
        js_data_match = re.search(r'var\s+player_(?:data|aaaa)\s*=\s*([^\n;]+)', html)
        if js_data_match:
            try:
                raw_json = json.loads(js_data_match.group(1))
                real_url = raw_json.get("url", "")
                if real_url:
                    return {"parse": 0, "url": real_url, "header": f"Referer={self.siteUrl}/"}
            except Exception:
                pass

        # 探测 iframe 嵌套播放源
        iframe_match = re.search(r'<iframe[^>]+src=["\']([^"\']+)["\']', html)
        if iframe_match:
            iframe_url = self._fix_url(iframe_match.group(1))
            return {"parse": 1, "url": iframe_url, "header": f"Referer={self.siteUrl}/"}

        # 兜底：交由 TVBox 内置 webview 解析
        return {"parse": 1, "url": url, "header": f"Referer={self.siteUrl}/"}

    # 5. 关键词搜索 (searchContent)
    def searchContent(self, key, quick, pg="1"):
        search_url = f"{self.siteUrl}/search/{parse.quote(key)}/page/{pg}"
        html = self._fetch(search_url)
        if not html or len(html) < 200:
            search_url = f"{self.siteUrl}/?s={parse.quote(key)}"
            html = self._fetch(search_url)

        soup = BeautifulSoup(html, "html.parser")
        videos = []
        seen = set()

        for a_tag in soup.select("a[href*='video'], a[href*='vod'], .video-item a, article a"):
            href = a_tag.get("href", "")
            if not href or href in seen or href == self.siteUrl:
                continue

            img_tag = a_tag.find("img")
            name = a_tag.get("title") or (img_tag.get("alt", "") if img_tag else "") or a_tag.get_text(strip=True)
            pic = (img_tag.get("data-original") or img_tag.get("data-src") or img_tag.get("src", "")) if img_tag else ""

            if name and href:
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
    print("=== 测试 homeContent ===")
    print(json.dumps(spider.homeContent(), ensure_ascii=False, indent=2))