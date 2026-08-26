# -*- coding: utf-8 -*-
"""
OnlyTarts (onlytarts.com) Python Spider - 完整正片修复版
- 优先嗅探与提取 HLS m3u8 / 真实完整长视频直链
- 彻底过滤 60s sample / preview / trailer 截断流
- 兼容 FongMi(T3) / TVBox(T4) 播放器协议
"""
import sys
import re
import json

sys.path.append('..')

try:
    from base.spider import Spider
except ImportError:
    import requests as rq
    class Spider:
        _session = rq.Session()
        def fetch(self, url, headers=None, **kw):
            kw.pop('timeout', None)
            r = self._session.get(url, headers=headers, timeout=15, **kw)
            r.encoding = 'utf-8'
            return r


class Spider(Spider):
    HOST = 'https://onlytarts.com'

    def getName(self):
        return "OnlyTarts"

    def init(self, extend=''):
        self.extend = extend if not isinstance(extend, list) else ''
        self.host = self.HOST
        self.header = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                          '(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7',
            'Referer': self.host + '/',
        }
        self._play_cache = {}

    def _fetch_html(self, url, timeout=15):
        try:
            rsp = self.fetch(url, headers=self.header, timeout=timeout)
            try:
                rsp.encoding = 'utf-8'
            except Exception:
                pass
            return rsp.text or ''
        except Exception:
            return ''

    def _parse_videos(self, html):
        videos = []
        card_pattern = r'<div class="video-card__item(?:-big)?[^"]*"[^>]*>(.*?)(?=<div class="video-card__item|<div class="pagination|$)'
        cards = re.findall(card_pattern, html, re.DOTALL)

        for card in cards:
            href_m = re.search(r'href="(https://onlytarts\.com/video/[^"]+)"', card)
            if not href_m:
                continue
            href = href_m.group(1)
            if href.endswith('/video') or href.endswith('/video/best'):
                continue
            slug = href.rsplit('/', 1)[-1] if '/' in href else href

            img_m = re.search(r'src="(https://static\.onlytarts\.com/poster/[^"]+)"', card)
            pic = img_m.group(1) if img_m else ''
            if pic:
                pic = re.sub(r'/poster/(\d+)/\d+/', r'/poster/\1/600/', pic)

            alt_m = re.search(r'alt="([^"]+)"', card)
            title = alt_m.group(1) if alt_m else slug

            dur_m = re.search(r'(\d{1,2}:\d{2})', card)
            duration = dur_m.group(1) if dur_m else ''

            videos.append({
                'vod_id': slug,
                'vod_name': title,
                'vod_pic': pic,
                'vod_remarks': duration,
            })

        return videos

    def _get_pagecount(self, html):
        pages = re.findall(r'page=(\d+)', html)
        if pages:
            return max(int(p) for p in pages)
        return 1

    def homeContent(self, filter):
        classes = [
            {'type_id': 'video', 'type_name': 'Newest'},
            {'type_id': 'video/best', 'type_name': 'Best'},
        ]

        html = self._fetch_html(self.host + '/tag')
        tags = re.findall(r'href="https://onlytarts\.com/tag/([^"]+)"[^>]*>([^<]+)<', html)
        for tag_slug, tag_name in tags:
            tag_name = tag_name.strip()
            if tag_name and tag_slug:
                classes.append({
                    'type_id': 'tag/' + tag_slug,
                    'type_name': tag_name,
                })

        return {'class': classes}

    def homeVideoContent(self):
        result = {'list': []}
        try:
            html = self._fetch_html(self.host + '/video')
            result['list'] = self._parse_videos(html)
        except Exception:
            pass
        return result

    def categoryContent(self, tid, pg, filter, ext):
        page = int(pg) if pg else 1
        if page < 1:
            page = 1

        url = f'{self.host}/{tid}?page={page}'
        html = self._fetch_html(url)

        videos = self._parse_videos(html)
        page_count = self._get_pagecount(html)

        return {
            'list': videos,
            'page': page,
            'pagecount': page_count,
            'limit': len(videos),
            'total': page_count * 12,
        }

    def detailContent(self, ids):
        slug = str(ids[0]) if ids else ''
        if not slug:
            return {}

        url = f'{self.host}/video/{slug}'
        html = self._fetch_html(url)

        title_m = re.search(r'<title>([^<]+)</title>', html)
        title = title_m.group(1).split(' - ')[0] if title_m else slug
        title = re.sub(r'\s*Porn:.*', '', title, flags=re.I).strip()

        poster_m = re.search(r'"poster":"([^"]+)"', html)
        if not poster_m:
            poster_m = re.search(r'poster="(https://static\.onlytarts\.com/poster/[^"]+)"', html)
        pic = poster_m.group(1).replace('\\/', '/') if poster_m else ''
        if pic:
            pic = re.sub(r'/poster/(\d+)/\d+/', r'/poster/\1/1200/', pic)

        self._extract_play_url(html, slug)

        dur_m = re.search(r'"duration":"?(\d+)"?', html)
        duration = ''
        if dur_m:
            secs = int(dur_m.group(1))
            duration = f'{secs // 60}:{secs % 60:02d}'

        tags = re.findall(r'href="https://onlytarts\.com/tag/[^"]+"[^>]*>([^<]+)<', html)
        tag_str = ', '.join(set(t.strip() for t in tags if t.strip()))[:200]

        vod = {
            'vod_id': slug,
            'vod_name': title,
            'vod_pic': pic,
            'vod_remarks': duration,
            'vod_tags': tag_str,
            'vod_play_from': 'OnlyTarts',
            'vod_play_url': '完整正片$' + slug,
        }

        return {'list': [vod]}

    def _is_short_preview(self, url, title=""):
        """精准检测是否为试看/悬停预览切片"""
        combined = f"{url} {title}".lower()
        banned = ['preview', 'trailer', 'sample', '_60s', 'short', 'thumb', 'promo']
        return any(b in combined for b in banned)

    def _extract_play_url(self, html, slug):
        if slug in self._play_cache:
            return self._play_cache[slug]

        play_url = ''

        # 1. 优先提取 HLS / M3U8 完整视频流（正片多为 HLS 分发）
        hls_matches = re.findall(r'(https?://[^\s"\'<>]+\.m3u8[^\s"\'<>]*)', html)
        for h_url in hls_matches:
            if not self._is_short_preview(h_url):
                play_url = h_url
                break

        # 2. 从 window.initials 结构化数据深入提取
        if not play_url:
            m = re.search(r'window\.initials\s*=\s*(\{.*?\});', html, re.DOTALL)
            if m:
                try:
                    data = json.loads(m.group(1))
                    video_info = data.get('video', {})
                    
                    # 检查是否有 hls_url / stream_url
                    if video_info.get('hls_url'):
                        play_url = video_info['hls_url']
                    elif video_info.get('stream_url'):
                        play_url = video_info['stream_url']

                    # 检查 sources 列表
                    if not play_url:
                        sources = video_info.get('sources', [])
                        valid_sources = []
                        for src in sources:
                            u = src.get('url', '')
                            t = str(src.get('title', ''))
                            if u and not self._is_short_preview(u, t):
                                valid_sources.append((t, u))

                        # 优先取高分辨率的正片
                        for target in ['1080', '720', '480', '360', 'default']:
                            for t, u in valid_sources:
                                if target in t.lower():
                                    play_url = u
                                    break
                            if play_url:
                                break

                        if not play_url and valid_sources:
                            play_url = valid_sources[0][1]

                except Exception:
                    pass

        # 3. 从 video / source 标签提取完整的 MP4 直链
        if not play_url:
            sources_html = re.findall(r'<source[^>]+src="([^"]+)"[^>]*>', html)
            for src_url in sources_html:
                if not self._is_short_preview(src_url):
                    play_url = src_url
                    break

        # 4. 兜底匹配 xhcdn 直链
        if not play_url:
            all_mp4s = re.findall(r'(https://[a-zA-Z0-9\.]+\.xhcdn\.com/[^"\']+\.mp4[^"\']*)', html)
            for u in all_mp4s:
                if not self._is_short_preview(u):
                    play_url = u
                    break

        if play_url:
            self._play_cache[slug] = play_url

        return play_url

    def playerContent(self, flag, id, vipFlags):
        if not id:
            return {'parse': 1, 'playUrl': '', 'url': ''}

        if '$' in id:
            id = id.split('$')[-1]

        slug = str(id)
        play_url = self._play_cache.get(slug)

        if not play_url:
            url = f'{self.host}/video/{slug}'
            html = self._fetch_html(url)
            play_url = self._extract_play_url(html, slug)

        if not play_url:
            # 兜底走 WebView 嗅探，避免彻底无法播放
            return {
                'parse': 1,
                'url': f'{self.host}/video/{slug}',
                'header': f"User-Agent={self.header['User-Agent']}&Referer={self.host}/"
            }

        # 构造双向兼容的 Header 格式
        headers_dict = {
            'User-Agent': self.header['User-Agent'],
            'Referer': f'{self.host}/video/{slug}',
            'Origin': self.host,
        }

        # 判断是 M3U8 还是 MP4
        return {
            'parse': 0,
            'playUrl': '',
            'url': play_url,
            'header': headers_dict,
        }

    def searchContent(self, key, quick, pg):
        page = int(pg) if pg else 1
        if page < 1:
            page = 1

        try:
            url = f'{self.host}/search/{key}?page={page}'
            html = self._fetch_html(url)
            videos = self._parse_videos(html)
            page_count = self._get_pagecount(html)
            if page_count < 1:
                page_count = 1

            return {
                'list': videos,
                'page': page,
                'pagecount': page_count,
                'limit': len(videos),
                'total': page_count * 12,
            }
        except Exception:
            return {'list': [], 'page': page, 'pagecount': 1, 'limit': 0, 'total': 0}

    def isLive(self):
        return False

    def manualContent(self, lv):
        return {}
