#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
══════════════════════════════════════════════════════════════════
《遮天法 2.0》定制爬虫源 — MissAV (完整自包含版)
- 动态路由: 自动嗅探获取最新 DMCA 镜像前缀，解决分类“找不到数据”
- 四极秘境: 内置 JS-Packer 纯算法解密，直取 Surrit M3U8 直链
- 播放优化: 采用原生 Header 注入穿透 Cloudflare 防盗链
══════════════════════════════════════════════════════════════════
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
        self.siteUrl = "https://missav.ws"
        self.session = requests.Session()
        self._dm_prefix = ""
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Referer": "https://missav.ws/",
            "Connection": "keep-alive"
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

    # ──── 核心：自动嗅探最新的 DMCA 镜像前缀 ────
    def _get_dm_prefix(self):
        if self._dm_prefix:
            return self._dm_prefix
        try:
            resp = self.session.get(f"{self.siteUrl}/cn", headers=self.headers, allow_redirects=True, timeout=8)
            m = re.search(r'missav\.ws/(dm[0-9]+)', resp.url)
            if m:
                self._dm_prefix = m.group(1)
                return self._dm_prefix
            m_html = re.search(r'dmcaDummy\s*:\s*[\'"](dm[0-9]+)[\'"]', resp.text)
            if m_html:
                self._dm_prefix = m_html.group(1)
                return self._dm_prefix
        except Exception:
            pass
        return ""

    # ──── 四极秘境：JS Packer 算法解密 ────
    def _unpack_js(self, p, a, c, k):
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
                p = packer_match.group(1)
                a = int(packer_match.group(2))
                c = int(packer_match.group(3))
                k = packer_match.group(4).split('|')
                unpacked = self._unpack_js(p, a, c, k)
                
                m = re.search(r"['\"](https?://[^'\"]+\.m3u8)['\"]", unpacked)
                if m:
                    return m.group(1)
            except Exception:
                pass
        
        m = re.search(r'(https?://[^"\']+\.m3u8)', html)
        if m:
            return m.group(1)
        return ""

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

    # 2. 分类列表 (自动补齐前缀与容错解析)
    def categoryContent(self, tid, pg="1", filter=False, extend=None):
        dm = self._get_dm_prefix()
        tid = tid.strip("/")
        
        if dm and not tid.startswith("dm"):
            base_path = f"{dm}/{tid}"
        else:
            base_path = tid
            
        url = f"{self.siteUrl}/{base_path}?page={pg}" if str(pg) != "1" else f"{self.siteUrl}/{base_path}"
        
        html = self._fetch(url)
        soup = BeautifulSoup(html, "html.parser")
        videos = []
        seen = set()

        for item in soup.select("div.thumbnail"):
            a_tag = item.select_one("div.my-2 a") or item.find("a", href=True)
            if not a_tag:
                continue
                
            href = a_tag.get("href", "")
            if not href or href == "#" or "javascript" in href:
                continue

            name = a_tag.get_text(strip=True)
            img = item.find("img")
            if not name and img:
                name = img.get("alt", "")

            pic = ""
            if img:
                pic = img.get("data-src") or img.get("src", "")
                if "data:image" in pic:
                    pic = img.get("data-src", "")

            remarks = ""
            time_node = item.select_one("span.bg-gray-800, span.absolute.bottom-1")
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

    # 3. 详情页解析
    def detailContent(self, ids):
        vod_id = ids[0]
        url = self._fix_url(vod_id)
        html = self._fetch(url)
        soup = BeautifulSoup(html, "html.parser")

        title_node = soup.select_one("h1, meta[property='og:title']")
        title = ""
        if title_node:
            if title_node.name == "meta":
                title = title_node.get("content", "")
            else:
                title = title_node.get_text(strip=True)

        img_node = soup.select_one("video.player, meta[property='og:image']")
        pic = ""
        if img_node:
            pic = img_node.get("data-poster") or img_node.get("content", "")

        remarks = ""
        act_node = soup.select_one("div.text-secondary a[href*='/actresses/']")
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

    # 4. 播放地址解析
    def playerContent(self, flag, id, vipFlags):
        url = self._fix_url(id)
        html = self._fetch(url)

        raw_m3u8 = self._extract_m3u8(html)
        if raw_m3u8:
            play_headers = {
                "User-Agent": self.headers["User-Agent"],
                "Referer": "https://missav.ws/",
                "Origin": "https://missav.ws"
            }
            header_str = "&".join([f"{k}={v}" for k, v in play_headers.items()])
            
            return {
                "parse": 0,
                "url": raw_m3u8,
                "header": header_str
            }

        return {
            "parse": 1,
            "url": url,
            "header": f"Referer={self.siteUrl}/"
        }

    # 5. 关键词搜索
    def searchContent(self, key, quick, pg="1"):
        search_url = f"{self.siteUrl}/cn/search/{parse.quote(key)}?page={pg}"
        html = self._fetch(search_url)
        soup = BeautifulSoup(html, "html.parser")
        videos = []
        seen = set()

        for item in soup.select("div.thumbnail"):
            a_tag = item.select_one("div.my-2 a") or item.find("a", href=True)
            if not a_tag:
                continue
                
            href = a_tag.get("href", "")
            if not href or href == "#" or "javascript" in href:
                continue

            name = a_tag.get_text(strip=True)
            img = item.find("img")
            if not name and img:
                name = img.get("alt", "")

            pic = ""
            if img:
                pic = img.get("data-src") or img.get("src", "")
                if "data:image" in pic:
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
    
    print("=== 1. 测试动态前缀嗅探 ===")
    prefix = spider._get_dm_prefix()
    print(f"当前嗅探到的动态前缀: {prefix}")
    
    print("\n=== 2. 测试分类（新作上市） ===")
    cat_res = spider.categoryContent("cn/release", "1", False, {})
    print(f"获取影片数量: {len(cat_res['list'])}")
    if cat_res["list"]:
        print("第一条影片:", json.dumps(cat_res["list"][0], ensure_ascii=False, indent=2))
        
        test_vod_id = cat_res["list"][0]["vod_id"]
        print(f"\n=== 3. 测试播放解析 ({test_vod_id}) ===")
        play_res = spider.playerContent("", test_vod_id, "")
        print("播放参数:", json.dumps(play_res, ensure_ascii=False, indent=2))
