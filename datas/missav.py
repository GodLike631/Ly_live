#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
══════════════════════════════════════════════════════════════════
《遮天法 2.0》定制爬虫源 — MissAV (分类路径重构终极版)
- 适配标准语言路由与动态重定向，全分类覆盖
- 双层 DOM 嗅探：div.thumbnail / a.text-secondary
- 四极 JS-Packer 解密 + 道宫本地代理转发
══════════════════════════════════════════════════════════════════
"""

import sys
import os
import re
import json
import time
import base64
import threading
import html as html_lib
from urllib import parse
from urllib.parse import parse_qs, urlparse
import http.server
import socketserver
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
        self.siteUrl = "https://missav.ws"
        self.session = requests.Session()
        self.proxyPort = 9985
        self._proxy_server = None
        self._proxy_thread = None
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Referer": "https://missav.ws/",
            "Connection": "keep-alive"
        }

    def init(self, extend=""):
        self.start_proxy()
        return True

    def isVideoFormat(self, url):
        formats = [".m3u8", ".mp4", ".flv", ".mkv", ".ts", ".mov"]
        return any(f in url.lower() for f in formats)

    def manualVideoCheck(self):
        return False

    # ──── 四极秘境 · JS Packer 算法解密 ────
    def _unpack_js(self, p, a, c, k, e=None, d=None):
        def _base_n(num, b):
            digits = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
            if num == 0:
                return "0"
            res = ""
            while num > 0:
                res = digits[num % b] + res
                num //= b
            return res

        for i in range(c - 1, -1, -1):
            key = _base_n(i, a)
            val = k[i] if i < len(k) and k[i] else key
            p = re.sub(r'\b' + re.escape(key) + r'\b', val, p)
        return p

    def _extract_m3u8(self, html):
        packer_match = re.search(r"eval\(function\(p,a,c,k,e,d\)\{.*?\}\('(.*?)',(\d+),(\d+),'(.*?)'\.split\('\|'\)", html, re.S)
        if packer_match:
            try:
                p, a, c, k = packer_match.group(1), int(packer_match.group(2)), int(packer_match.group(3)), packer_match.group(4).split('|')
                unpacked = self._unpack_js(p, a, c, k)
                m_1080 = re.search(r"['\"](https?://[^'\"]+/1080p/video\.m3u8)['\"]", unpacked)
                m_720 = re.search(r"['\"](https?://[^'\"]+/720p/video\.m3u8)['\"]", unpacked)
                m_list = re.search(r"['\"](https?://[^'\"]+/playlist\.m3u8)['\"]", unpacked)

                if m_1080:
                    return m_1080.group(1)
                if m_720:
                    return m_720.group(1)
                if m_list:
                    return m_list.group(1)
            except Exception:
                pass

        m = re.search(r'(https?://surrit\.com/[a-zA-Z0-9\-]+/(?:playlist|1080p/video|720p/video)\.m3u8)', html)
        if m:
            return m.group(1)
        return ""

    # ──── 道宫秘境 · 本地代理 ────
    def start_proxy(self):
        if self._proxy_server:
            return True

        outer = self

        class ProxyHandler(http.server.BaseHTTPRequestHandler):
            def do_GET(self):
                parsed = urlparse(self.path)
                params = parse_qs(parsed.query)

                if parsed.path == "/proxy_m3u8":
                    try:
                        raw_url = base64.b64decode(params.get("url", [""])[0]).decode()
                        h = {
                            "User-Agent": outer.headers["User-Agent"],
                            "Referer": "https://missav.ws/",
                            "Origin": "https://missav.ws"
                        }
                        resp = requests.get(raw_url, headers=h, timeout=12)
                        base_url = raw_url.rsplit("/", 1)[0]

                        lines = resp.text.split("\n")
                        new_lines = []
                        for line in lines:
                            line_str = line.strip()
                            if line_str and not line_str.startswith("#"):
                                ts_url = line_str if line_str.startswith("http") else f"{base_url}/{line_str}"
                                ts_enc = base64.b64encode(ts_url.encode()).decode()
                                new_lines.append(f"http://127.0.0.1:{outer.proxyPort}/proxy_ts?url={ts_enc}")
                            else:
                                new_lines.append(line)

                        body = "\n".join(new_lines).encode("utf-8")
                        self.send_response(200)
                        self.send_header("Content-Type", "application/vnd.apple.mpegurl")
                        self.send_header("Content-Length", str(len(body)))
                        self.send_header("Access-Control-Allow-Origin", "*")
                        self.end_headers()
                        self.wfile.write(body)
                    except Exception as e:
                        self.send_response(500)
                        self.end_headers()
                        self.wfile.write(str(e).encode())

                elif parsed.path == "/proxy_ts":
                    try:
                        real_ts = base64.b64decode(params.get("url", [""])[0]).decode()
                        h = {
                            "User-Agent": outer.headers["User-Agent"],
                            "Referer": "https://missav.ws/",
                            "Origin": "https://missav.ws"
                        }
                        r = requests.get(real_ts, headers=h, stream=True, timeout=15)
                        self.send_response(r.status_code)
                        self.send_header("Content-Type", "video/mp2t")
                        self.send_header("Access-Control-Allow-Origin", "*")
                        self.end_headers()
                        for chunk in r.iter_content(chunk_size=65536):
                            self.wfile.write(chunk)
                    except Exception as e:
                        self.send_response(502)
                        self.end_headers()
                else:
                    self.send_response(404)
                    self.end_headers()

            def log_message(self, format, *args):
                pass

        for port in [9985, 9986, 9987, 9988, 9989]:
            try:
                self.proxyPort = port
                self._proxy_server = socketserver.ThreadingTCPServer(("127.0.0.1", port), ProxyHandler)
                self._proxy_thread = threading.Thread(target=self._proxy_server.serve_forever, daemon=True)
                self._proxy_thread.start()
                return True
            except OSError:
                continue
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

    # 1. 首页分类
    def homeContent(self, filter=False):
        classes = [
            {"type_name": "最近更新", "type_id": "cn/new"},
            {"type_name": "新作上市", "type_id": "cn/release"},
            {"type_name": "中文字幕", "type_id": "cn/chinese-subtitle"},
            {"type_name": "无码流出", "type_id": "cn/uncensored-leak"},
            {"type_name": "FC2", "type_id": "cn/fc2"},
            {"type_name": "HEYZO", "type_id": "cn/heyzo"},
            {"type_name": "一本道", "type_id": "cn/1pondo"},
            {"type_name": "天然素人", "type_id": "cn/10musume"},
            {"type_name": "东京热", "type_id": "cn/tokyohot"},
            {"type_name": "麻豆传媒", "type_id": "cn/madou"},
            {"type_name": "VR专区", "type_id": "cn/genres/VR"},
            {"type_name": "今日热门", "type_id": "cn/today-hot"},
            {"type_name": "本月热门", "type_id": "cn/monthly-hot"}
        ]
        return {"class": classes}

    # 2. 分类列表 (categoryContent)
    def categoryContent(self, tid, pg="1", filter=False, extend=None):
        pg = str(pg)
        tid = tid.strip("/")
        
        # 兼容自动跳转与直接路由
        target_path = tid if tid.startswith("http") else f"{self.siteUrl}/{tid}"
        url = f"{target_path}?page={pg}" if pg != "1" else target_path

        html = self._fetch(url)
        soup = BeautifulSoup(html, "html.parser")
        videos = []
        seen = set()

        # 针对 MissAV 真实 DOM 容器做广度匹配
        for item in soup.select("div.thumbnail, div.relative.aspect-w-16, div.my-2"):
            parent = item.find_parent("div", class_=re.compile(r"thumbnail|group")) or item

            title_node = parent.select_one("div.my-2 a, div.text-sm a, a.text-secondary, a[alt]")
            img = parent.find("img")

            href = ""
            if title_node and title_node.get("href"):
                href = title_node.get("href")
            elif parent.find("a", href=True):
                href = parent.find("a", href=True).get("href")

            if not href or href in seen or "javascript:" in href or href == "#":
                continue

            name = ""
            if title_node and title_node.get_text(strip=True):
                name = title_node.get_text(strip=True)
            elif title_node and title_node.get("alt"):
                name = title_node.get("alt")
            elif img and img.get("alt"):
                name = img.get("alt")

            pic = ""
            if img:
                pic = img.get("data-src") or img.get("src", "")
                if pic.startswith("data:image"):
                    pic = img.get("data-src", "")

            remarks = ""
            time_node = parent.select_one("span.bg-gray-800, span.text-nord5")
            if time_node:
                remarks = time_node.get_text(strip=True)

            if href and (name or pic):
                seen.add(href)
                videos.append({
                    "vod_id": href,
                    "vod_name": self._clean_title(name or "MissAV 影片"),
                    "vod_pic": self._fix_url(pic),
                    "vod_remarks": remarks
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

        title_node = soup.select_one("h1, meta[property='og:title']")
        if title_node and title_node.name == "meta":
            title = title_node.get("content", "")
        else:
            title = title_node.get_text(strip=True) if title_node else "MissAV 视频"

        img_node = soup.select_one("meta[property='og:image'], video.player")
        pic = img_node.get("content") or img_node.get("data-poster", "") if img_node else ""

        remarks = ""
        act_node = soup.select_one("div:has(> span:contains('女优')) a, a[href*='/actresses/']")
        if act_node:
            remarks = act_node.get_text(strip=True)

        return {
            "list": [{
                "vod_id": vod_id,
                "vod_name": self._clean_title(title),
                "vod_pic": self._fix_url(pic),
                "vod_remarks": remarks,
                "vod_play_from": "MissAV专线",
                "vod_play_url": f"正片播放${url}"
            }]
        }

    # 4. 播放地址解析 (四极解密 + 道宫本地代理转发)
    def playerContent(self, flag, id, vipFlags):
        self.start_proxy()
        url = self._fix_url(id)
        html = self._fetch(url)

        raw_m3u8 = self._extract_m3u8(html)
        if raw_m3u8:
            enc_target = base64.b64encode(raw_m3u8.encode()).decode()
            proxy_play_url = f"http://127.0.0.1:{self.proxyPort}/proxy_m3u8?url={enc_target}"
            return {
                "parse": 0,
                "url": proxy_play_url,
                "header": ""
            }

        return {
            "parse": 1,
            "url": url,
            "header": f"Referer={self.siteUrl}/"
        }

    # 5. 关键词搜索 (searchContent)
    def searchContent(self, key, quick, pg="1"):
        search_url = f"{self.siteUrl}/cn/search/{parse.quote(key)}?page={pg}"
        html = self._fetch(search_url)
        soup = BeautifulSoup(html, "html.parser")
        videos = []
        seen = set()

        for item in soup.select("div.thumbnail, div.grid > div"):
            title_node = item.select_one("div.my-2 a, div.text-sm a, a.text-secondary")
            main_a = item.find("a", href=True)

            href = title_node.get("href") if title_node and title_node.get("href") else (main_a.get("href", "") if main_a else "")

            if not href or href in seen or "javascript:" in href or href == "#":
                continue

            name = title_node.get_text(strip=True) if title_node else ""
            img = item.find("img")
            if not name and img:
                name = img.get("alt", "")

            pic = (img.get("data-src") or img.get("src", "")) if img else ""
            if pic.startswith("data:image") and img:
                pic = img.get("data-src", "")

            if href and (name or pic):
                seen.add(href)
                videos.append({
                    "vod_id": href,
                    "vod_name": self._clean_title(name or "MissAV 影片"),
                    "vod_pic": self._fix_url(pic),
                    "vod_remarks": ""
                })

        return {"list": videos}

    # 6. 本地代理接口兼容
    def localProxy(self, param):
        return [404, "text/plain", "Not Supported"]


if __name__ == "__main__":
    spider = Spider()
    spider.init()
    print("=== 测试新作上市 ===")
    res = spider.categoryContent("cn/release", "1", False, {})
    print(f"新作上市抓取数量: {len(res['list'])}")
    print("=== 测试无码流出 ===")
    res2 = spider.categoryContent("cn/uncensored-leak", "1", False, {})
    print(f"无码流出抓取数量: {len(res2['list'])}")
