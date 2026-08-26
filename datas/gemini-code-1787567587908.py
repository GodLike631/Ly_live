#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
══════════════════════════════════════════════════════════════════
《遮天法 2.0》 — Sxyprn 专享爬虫源（全兼容修复版）
══════════════════════════════════════════════════════════════════
"""

import sys
import os
import re
import json
import base64
import random
import urllib.parse
from bs4 import BeautifulSoup

try:
    from base.spider import Spider as SpiderBase
except ImportError:
    class SpiderBase:
        pass


class YuanTianShu:
    """源天书：网络请求、TLS伪装与数据清洗"""
    def __init__(self):
        self.siteUrl = "https://sxyprn.com"
        self._ua_pool = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64; rv:133.0) Gecko/20100101 Firefox/133.0",
        ]

    def _random_ua(self) -> str:
        return random.choice(self._ua_pool)

    def _build_headers(self, extra: dict = None) -> dict:
        h = {
            "User-Agent": self._random_ua(),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Referer": f"{self.siteUrl}/",
            "Connection": "keep-alive",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "same-origin",
        }
        if extra:
            h.update(extra)
        return h

    def fetch(self, url: str, headers: dict = None, timeout: int = 15) -> str:
        """优先使用 curl_cffi 伪装 TLS 指纹突破 Cloudflare"""
        h = self._build_headers(headers)
        
        # 1. 尝试使用 curl_cffi (首选，防 CF 拦截)
        try:
            from curl_cffi import requests as cffi_req
            resp = cffi_req.get(url, headers=h, timeout=timeout, impersonate="chrome131", allow_redirects=True)
            if resp.status_code == 200 and len(resp.text) > 500:
                return resp.text
        except Exception:
            pass

        # 2. 回退使用 requests
        try:
            import requests
            session = requests.Session()
            resp = session.get(url, headers=h, timeout=timeout, allow_redirects=True)
            resp.encoding = getattr(resp, "apparent_encoding", None) or "utf-8"
            return resp.text
        except Exception:
            return ""

    @staticmethod
    def fix_url(url: str, host: str) -> str:
        if not url:
            return ""
        if url.startswith("http://") or url.startswith("https://"):
            return url
        if url.startswith("//"):
            return f"https:{url}"
        if url.startswith("/"):
            return f"{host.rstrip('/')}{url}"
        return f"{host.rstrip('/')}/{url}"

    @staticmethod
    def clean_title(title: str) -> str:
        import html as _html
        t = _html.unescape(title or "")
        t = re.sub(r"<[^>]+>", "", t)
        return t.strip()


class Spider(SpiderBase, YuanTianShu):
    """TVBox 标准入口 Spider"""

    def __init__(self):
        super().__init__()
        self.siteUrl = "https://sxyprn.com"

    def init(self, extend=""):
        return True

    def isVideoFormat(self, url):
        formats = [".m3u8", ".mp4", ".flv", ".mkv", ".ts", ".webm"]
        return any(f in url.lower() for f in formats)

    def manualVideoCheck(self):
        return False

    def _parse_video_list(self, html: str) -> list:
        """通用页面视频卡片提取逻辑"""
        if not html:
            return []

        soup = BeautifulSoup(html, "html.parser")
        videos = []
        seen = set()

        # 匹配 post_el 容器、标准卡片或包含链接的容器
        items = soup.select("div[class*='post_el'], div.post, div.custom_post, .video_item")
        if not items:
            # 兜底查找所有含有 .html 的链接
            items = soup.find_all("a", href=re.compile(r"/[a-zA-Z0-9_-]+\.html"))

        for item in items:
            if item.name == "a":
                a_tag = item
            else:
                a_tag = item.find("a", href=re.compile(r"\.html"))

            if not a_tag:
                continue

            href = a_tag.get("href", "")
            if not href or href in seen or href == "/":
                continue
            seen.add(href)

            # 获取标题
            img_tag = item.find("img") if item.name != "a" else a_tag.find("img")
            title = (
                a_tag.get("title")
                or (img_tag.get("alt") if img_tag else "")
                or a_tag.get_text(strip=True)
            )

            # 获取图片与防盗链格式化
            pic = ""
            if img_tag:
                pic = (
                    img_tag.get("data-src")
                    or img_tag.get("data-original")
                    or img_tag.get("src")
                    or ""
                )
            pic_url = self.fix_url(pic, self.siteUrl)
            if pic_url:
                # 附带 TVBox 专用的图片 Referer 头，防止封面图 403 裂开
                pic_url = f"{pic_url}@Referer=https://sxyprn.com/"

            # 抓取时长/标签
            duration_elem = item.select_one(".duration, .post_duration, .time, .text_duration")
            remarks = duration_elem.get_text(strip=True) if duration_elem else ""

            if title:
                videos.append({
                    "vod_id": href,
                    "vod_name": self.clean_title(title),
                    "vod_pic": pic_url,
                    "vod_remarks": remarks
                })
        return videos

    def homeContent(self, filter: bool = False) -> dict:
        """首页：同时返回分类与首屏推荐列表，避免界面全白"""
        classes = [
            {"type_name": "最新推荐", "type_id": "/"},
            {"type_name": "高分热门", "type_id": "/top/"},
            {"type_name": "热门趋势", "type_id": "/trending/"},
            {"type_name": "经典分类", "type_id": "/categories/"},
        ]
        
        # 请求首页数据作为进入 TVBox 的初始列表
        html = self.fetch(self.siteUrl)
        vod_list = self._parse_video_list(html)

        return {
            "class": classes,
            "list": vod_list
        }

    def categoryContent(self, tid: str, pg: str, filter: bool, extend: dict) -> dict:
        """分类列表分页"""
        page = int(pg)
        target_path = tid.rstrip("/")

        if page == 1:
            url = f"{self.siteUrl}{target_path}" if target_path else f"{self.siteUrl}/"
        else:
            # 适配分页格式（?page=X 或 /page/X）
            url = f"{self.siteUrl}{target_path}?page={page}" if target_path else f"{self.siteUrl}/?page={page}"

        html = self.fetch(url)
        videos = self._parse_video_list(html)

        return {
            "list": videos,
            "page": page,
            "pagecount": page + 1 if len(videos) >= 12 else page,
            "limit": len(videos),
            "total": 9999
        }

    def detailContent(self, ids: list) -> dict:
        """详情页解析"""
        path = ids[0]
        url = self.fix_url(path, self.siteUrl)
        html = self.fetch(url)
        soup = BeautifulSoup(html, "html.parser")

        title_node = soup.select_one("h1, .post_title, .title, .video-name")
        vod_name = self.clean_title(title_node.get_text(strip=True)) if title_node else "在线播放"

        pic_node = soup.select_one(".post_thumb img, .video_thumb img, #player img, img.poster, img")
        vod_pic = ""
        if pic_node:
            vod_pic = pic_node.get("data-src") or pic_node.get("src") or ""
        vod_pic = self.fix_url(vod_pic, self.siteUrl)
        if vod_pic:
            vod_pic = f"{vod_pic}@Referer=https://sxyprn.com/"

        return {
            "list": [{
                "vod_id": path,
                "vod_name": vod_name,
                "vod_pic": vod_pic,
                "vod_play_from": "Sxyprn",
                "vod_play_url": f"正片${url}"
            }]
        }

    def playerContent(self, flag: str, id: str, vipFlags: str) -> dict:
        """播放直链抽取与解析分发"""
        url = self.fix_url(id, self.siteUrl)
        html = self.fetch(url)

        # 匹配多种常见 m3u8 与 mp4 规则
        patterns = [
            r'src="([^"]+\.m3u8[^"]*)"',
            r'src="([^"]+\.mp4[^"]*)"',
            r'<source[^>]+src=["\']([^"\']+)["\']',
            r'"video_url"\s*:\s*"([^"]+)"',
            r'"file"\s*:\s*"([^"]+)"',
            r'var\s+video_url\s*=\s*["\']([^"\']+)["\']',
        ]

        real_url = ""
        for pat in patterns:
            match = re.search(pat, html)
            if match:
                extracted = match.group(1).replace(r"\/", "/")
                real_url = self.fix_url(extracted, self.siteUrl)
                break

        header_str = f"User-Agent={self._random_ua()}&Referer=https://sxyprn.com/"

        if real_url:
            return {
                "parse": 0,
                "url": real_url,
                "header": header_str
            }

        # 未抓到静态直链时交付嗅探解析
        return {
            "parse": 1,
            "url": url,
            "header": header_str
        }

    def searchContent(self, key: str, quick: str, pg: str = "1") -> dict:
        """搜索处理"""
        encoded_key = urllib.parse.quote(key)
        page = int(pg)
        url = f"{self.siteUrl}/search/{encoded_key}?page={page}"

        html = self.fetch(url)
        videos = self._parse_video_list(html)
        return {"list": videos}

    def localProxy(self, param: dict) -> list:
        return [200, "text/plain", "OK"]


if __name__ == "__main__":
    spider = Spider()
    spider.init()
    
    print("=== 测试首页（包含分类与推荐列表） ===")
    home = spider.homeContent()
    print(f"分类数量: {len(home.get('class', []))}")
    print(f"首屏视频数: {len(home.get('list', []))}")
    
    if home.get("list"):
        first_item = home["list"][0]
        print(f"首条数据: {first_item['vod_name']} -> {first_item['vod_id']}")
        
        print("\n=== 测试详情解析 ===")
        detail = spider.detailContent([first_item["vod_id"]])
        print(json.dumps(detail, ensure_ascii=False, indent=2))
