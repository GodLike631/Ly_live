#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
《遮天法 2.0》定制爬虫源 - goodav17 (道宫秘境·本地代理穿透版)
- 激活本地 HTTP 代理服务器 (DaoGong)
- 拦截并重写 HLS m3u8 切片，强制附加 Referer 穿透防盗链超时
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
        self.siteUrl = "https://goodav17.com"
        self.session = requests.Session()
        self.proxyPort = 9979
        self._proxy_server = None
        self._proxy_thread = None
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh-TW;q=0.9,zh;q=0.8,en;q=0.7",
            "Referer": "https://goodav17.com/"
        }

    def init(self, extend=""):
        self.start_proxy()
        return True

    def isVideoFormat(self, url):
        formats = [".m3u8", ".mp4", ".flv", ".mkv", ".ts", ".mov"]
        return any(f in url.lower() for f in formats)

    def manualVideoCheck(self):
        return False

    # ──── 道宫秘境 · 本地代理服务器 ────
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
                            "Referer": "https://ggjav.com/",
                            "Origin": "https://ggjav.com"
                        }
                        resp = requests.get(raw_url, headers=h, timeout=12)
                        
                        # 文本重写：将 m3u8 内的所有分片路径转化为本地代理
                        base_url = raw_url.rsplit("/", 1)[0]
                        lines = resp.text.split("\n")
                        new_lines = []
                        for line in lines:
                            line_str = line.strip()
                            if line_str and not line_str.startswith("#"):
                                if not line_str.startswith("http"):
                                    ts_url = f"{base_url}/{line_str}"
                                else:
                                    ts_url = line_str
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
                            "Referer": "https://ggjav.com/",
                            "Origin": "https://ggjav.com"
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

        for port in [9979, 9980, 9981, 9982, 9983, 9984]:
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
                "vod_play_from": "道宮專線",
                "vod_play_url": f"完整高清${url}"
            }]
        }

    # 4. 播放地址解析 (道宫本地代理中转)
    def playerContent(self, flag, id, vipFlags):
        self.start_proxy()
        url = self._fix_url(id)
        html = self._fetch(url)

        # 提取 Base64 原始地址
        raw_stream_url = ""
        b64_match = re.search(r'embed\?u=([a-zA-Z0-9+/=]+)', html)
        if b64_match:
            try:
                decoded = base64.b64decode(b64_match.group(1)).decode("utf-8")
                if decoded.startswith("http"):
                    raw_stream_url = decoded
            except Exception:
                pass

        if raw_stream_url:
            # 构建目标 m3u8 地址
            if raw_stream_url.endswith(".mp4") and "ggjav.com" in raw_stream_url:
                target_m3u8 = f"{raw_stream_url}/index.m3u8"
            else:
                target_m3u8 = raw_stream_url

            # 封装为本地代理播放地址
            enc_target = base64.b64encode(target_m3u8.encode()).decode()
            proxy_play_url = f"http://127.0.0.1:{self.proxyPort}/proxy_m3u8?url={enc_target}"

            return {
                "parse": 0,
                "url": proxy_play_url,
                "header": ""
            }

        # 兜底：嗅探
        return {
            "parse": 1,
            "url": url,
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

    # 6. 本地代理接口兼容
    def localProxy(self, param):
        return [404, "text/plain", "Not Supported"]


if __name__ == "__main__":
    spider = Spider()
    spider.init()
    test_id = "/html/20975/"
    print(f"=== 道宫代理测试 ({test_id}) ===")
    play = spider.playerContent("", test_id, "")
    print(json.dumps(play, ensure_ascii=False, indent=2))
