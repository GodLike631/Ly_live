#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
══════════════════════════════════════════════════════════════════
《遮天法 2.0》定制爬虫源 — MissAV (全功能适配版)
- 四极秘境: 内置纯 Python JS-Packer 解密器，秒破 eval 混淆提取 m3u8
- 道宫秘境: 本地 HTTP 代理服务器转发切片，穿透 Cloudflare 403 与防盗链
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
            "Referer": "https://missav.ws/"
        }

    def init(self, extend=""):
        self.start_proxy()
        return True

    def isVideoFormat(self, url):
        formats = [".m3u8", ".mp4", ".flv", ".mkv", ".ts", ".mov"]
        return any(f in url.lower() for f in formats)

    def manualVideoCheck(self):
        return False

    # ──── 四极秘境 · JS Packer 纯算法解密 ────
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
        """解析页面内的 Packer JS 提取真实播放直链"""
        packer_match = re.search(r"eval\(function\(p,a,c,k,e,d\)\{.*?\}\('(.*?)',(\d+),(\d+),'(.*?)'\.split\('\|'\)", html, re.S)
        if packer_match:
            try:
                p, a, c, k = packer_match.group(1), int(packer_match.group(2)), int(packer_match.group(3)), packer_match.group(4).split('|')
                unpacked = self._unpack_js(p, a, c, k)
                # 寻找 1080p / 720p / playlist.m3u8
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

        # 兜底普通探测
        m = re.search(r'(https?://surrit\.com/[a-zA-Z0-9\-]+/(?:playlist|1080p/video|720p/video)\.m3u8)', html)
        if m:
            return m.group(1)
        return ""

    # ──── 道宫秘境 · 本地代理大阵 ────
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

                        # 重写分片为本地中转代理，绕开 403 白名单限制
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

    # 1. 首页分类 (homeContent)
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
            {"type_name": "本月热门", "type_id": "cn/monthly-hot"}
        ]
        return {"class": classes}

    # 2. 分类列表 (categoryContent)
    def categoryContent(self, tid, pg="1", filter=False, extend=None):
        pg = str(pg)
        url = f"{self.siteUrl}/{tid}?page={pg}" if pg != "1" else f"{self.siteUrl}/{tid}"
        html = self._fetch(url)
        soup = BeautifulSoup(html, "html.parser")
        videos = []
        seen = set()

        for item in soup.select("div.thumbnail, div.group"):
            a_tag = item.find("a", href=True)
            if not a_tag:
                continue

            href = a_tag.get("href", "")
            if not href or href in seen or "javascript:" in href:
                continue

            img = item.find("img")
            name = a_tag.get("alt", "") or (img.get("alt", "") if img else "")
            if not name:
                title_node = item.find_next("a", class_=re.compile(r"text-secondary|text-nord4"))
                if title_node:
                    name = title_node.get_text(strip=True)

            pic = (img.get("data-src") or img.get("src", "")) if img else ""

            if href and (name or pic):
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

        title_node = soup.select_one("h1, meta[property='og:title']")
        if title_node and title_node.name == "meta":
            title = title_node.get("content", "")
        else:
            title = title_node.get_text(strip=True) if title_node else "MissAV 视频"

        img_node = soup.select_one("meta[property='og:image'], video.player")
        pic = img_node.get("content") or img_node.get("data-poster", "") if img_node else ""

        # 番号与女优信息
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

        # 1. 纯算法解密 Packer JS 提取真实 m3u8
        raw_m3u8 = self._extract_m3u8(html)

        # 2. 封装为本地代理播放地址（彻底穿透 Cloudflare 403）
        if raw_m3u8:
            enc_target = base64.b64encode(raw_m3u8.encode()).decode()
            proxy_play_url = f"http://127.0.0.1:{self.proxyPort}/proxy_m3u8?url={enc_target}"
            return {
                "parse": 0,
                "url": proxy_play_url,
                "header": ""
            }

        # 兜底嗅探
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

        for item in soup.select("div.thumbnail, div.group"):
            a_tag = item.find("a", href=True)
            if not a_tag:
                continue

            href = a_tag.get("href", "")
            if not href or href in seen or "javascript:" in href:
                continue

            img = item.find("img")
            name = a_tag.get("alt", "") or (img.get("alt", "") if img else "")
            pic = (img.get("data-src") or img.get("src", "")) if img else ""

            if href and (name or pic):
                seen.add(href)
                videos.append({
                    "vod_id": href,
                    "vod_name": self._clean_title(name),
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
    test_id = "/dm27/cn/sone-166-uncensored-leak"
    print(f"=== 测试详情与播放 ({test_id}) ===")
    detail = spider.detailContent([test_id])
    print("详情返回:", json.dumps(detail, ensure_ascii=False, indent=2))
    play = spider.playerContent("", test_id, "")
    print("播放返回:", json.dumps(play, ensure_ascii=False, indent=2))