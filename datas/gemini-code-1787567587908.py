#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
══════════════════════════════════════════════════════════════════
《遮天法 2.0》 — Sxyprn 专享爬虫源 (TVBox / py-drpy 标准规范)
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

# 尝试导入 TVBox 基础类（兼容 drpy 运行时环境）
try:
    from base.spider import Spider as SpiderBase
except ImportError:
    class SpiderBase:
        pass


class YuanTianShu:
    """源天书：网络请求与基础处理"""
    def __init__(self):
        self.siteUrl = "https://sxyprn.com"
        self._ua_pool = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64; rv:133.0) Gecko/20100101 Firefox/133.0",
        ]

    def _random_ua(self) -> str:
        return random.choice(self._ua_pool)

    def _build_headers(self, extra: dict = None) -> dict:
        h = {
            "User-Agent": self._random_ua(),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
            "Connection": "keep-alive",
            "Referer": f"{self.siteUrl}/",
        }
        if extra:
            h.update(extra)
        return h

    def fetch(self, url: str, headers: dict = None, timeout: int = 15) -> str:
        """支持优先使用 curl_cffi 穿透 Cloudflare，失败则降级到 requests"""
        h = self._build_headers(headers)
        try:
            from curl_cffi import requests as cffi_req
            resp = cffi_req.get(url, headers=h, timeout=timeout, impersonate="chrome131", allow_redirects=True)
            return resp.text
        except Exception:
            pass

        try:
            import requests
            resp = requests.get(url, headers=h, timeout=timeout, allow_redirects=True)
            resp.encoding = getattr(resp, "apparent_encoding", None) or "utf-8"
            return resp.text
        except Exception as e:
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
    """红尘仙·万法归一 Spider 实现"""

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

    def homeContent(self, filter: bool = False) -> dict:
        """获取分类配置"""
        classes = [
            {"type_name": "最新视频", "type_id": "/latest"},
            {"type_name": "最热视频", "type_id": "/popular"},
            {"type_name": "高分视频", "type_id": "/top-rated"},
            {"type_name": "频道分类", "type_id": "/categories"},
        ]
        return {"class": classes}

    def _parse_video_list(self, html: str) -> list:
        """从页面 HTML 结构中提取视频列表"""
        soup = BeautifulSoup(html, "html.parser")
        videos = []
        seen = set()

        # 匹配视频项卡片容器
        items = soup.select(".post, .video_item, .custom_post, div[id^='post_']")
        if not items:
            items = soup.select("a[href*='/post/'], a[href*='/video/']")

        for item in items:
            if item.name == "a":
                a_tag = item
            else:
                a_tag = item.select_one("a[href*='/post/'], a[href*='/video/'], a[href*='.html']")

            if not a_tag:
                continue

            href = a_tag.get("href", "")
            if not href or href in seen:
                continue
            seen.add(href)

            img_tag = item.select_one("img")
            title = (
                a_tag.get("title")
                or (img_tag.get("alt") if img_tag else "")
                or a_tag.get_text(strip=True)
            )

            pic = ""
            if img_tag:
                pic = (
                    img_tag.get("data-src")
                    or img_tag.get("data-original")
                    or img_tag.get("src")
                    or ""
                )

            # 抓取时长或标签副标题
            duration_elem = item.select_one(".duration, .post_duration, .time")
            remarks = duration_elem.get_text(strip=True) if duration_elem else ""

            if title:
                videos.append({
                    "vod_id": href,
                    "vod_name": self.clean_title(title),
                    "vod_pic": self.fix_url(pic, self.siteUrl),
                    "vod_remarks": remarks
                })
        return videos

    def categoryContent(self, tid: str, pg: str, filter: bool, extend: dict) -> dict:
        """获取分类列表分页"""
        page = int(pg)
        if page == 1:
            url = f"{self.siteUrl}{tid}"
        else:
            url = f"{self.siteUrl}{tid}/{page}" if not tid.endswith("/") else f"{self.siteUrl}{tid}{page}"

        html = self.fetch(url)
        videos = self._parse_video_list(html)

        return {
            "list": videos,
            "page": page,
            "pagecount": page + 1 if len(videos) >= 15 else page,
            "limit": len(videos),
            "total": 9999
        }

    def detailContent(self, ids: list) -> dict:
        """详情页解析：获取标题、海报与播放链接列表"""
        path = ids[0]
        url = self.fix_url(path, self.siteUrl)
        html = self.fetch(url)
        soup = BeautifulSoup(html, "html.parser")

        title_node = soup.select_one("h1, .post_title, .video_title, .title")
        vod_name = self.clean_title(title_node.get_text(strip=True)) if title_node else "在线视频"

        pic_node = soup.select_one(".post_thumb img, .video_thumb img, #video_player img, img.poster")
        vod_pic = ""
        if pic_node:
            vod_pic = pic_node.get("data-src") or pic_node.get("src") or ""
        vod_pic = self.fix_url(vod_pic, self.siteUrl)

        # 视频剧集地址配置
        vod_play_url = f"正片${url}"

        return {
            "list": [{
                "vod_id": path,
                "vod_name": vod_name,
                "vod_pic": vod_pic,
                "vod_play_from": "Sxyprn",
                "vod_play_url": vod_play_url
            }]
        }

    def playerContent(self, flag: str, id: str, vipFlags: str) -> dict:
        """播放解析：提取页面直链或 HTML5 video 资源"""
        url = self.fix_url(id, self.siteUrl)
        html = self.fetch(url)

        # 13层提取规则策略：多层正则抽取视频直链
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
                if extracted.startswith("http") or extracted.startswith("//") or extracted.startswith("/"):
                    real_url = self.fix_url(extracted, self.siteUrl)
                    break

        headers = {
            "User-Agent": self._random_ua(),
            "Referer": f"{self.siteUrl}/",
        }

        if real_url:
            return {
                "parse": 0,
                "url": real_url,
                "header": headers
            }

        # 未直接抽取出直链时，转给嗅探/内置解析器处理
        return {
            "parse": 1,
            "url": url,
            "header": headers
        }

    def searchContent(self, key: str, quick: str, pg: str = "1") -> dict:
        """搜索处理"""
        encoded_key = urllib.parse.quote(key)
        page = int(pg)
        if page == 1:
            url = f"{self.siteUrl}/search/{encoded_key}"
        else:
            url = f"{self.siteUrl}/search/{encoded_key}/{page}"

        html = self.fetch(url)
        videos = self._parse_video_list(html)
        return {"list": videos}

    def localProxy(self, param: dict) -> list:
        return [200, "text/plain", "OK"]


if __name__ == "__main__":
    # 本地自测用例
    spider = Spider()
    spider.init()
    print("=== 测试首页分类 ===")
    home = spider.homeContent()
    print(json.dumps(home, ensure_ascii=False, indent=2))

    print("\n=== 测试分类列表 ===")
    cate = spider.categoryContent(tid="/latest", pg="1", filter=False, extend={})
    print(f"获取视频数: {len(cate.get('list', []))}")
    if cate.get("list"):
        sample = cate["list"][0]
        print(f"样例: {sample['vod_name']} -> {sample['vod_id']}")

        print("\n=== 测试详情页 ===")
        detail = spider.detailContent([sample["vod_id"]])
        print(json.dumps(detail, ensure_ascii=False, indent=2))
