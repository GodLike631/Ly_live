# -*- coding: utf-8 -*-
"""
OnlyTarts (onlytarts.com) Python Spider
兼容 FongMi/TV (T3) 与 WebHomeTV / PeekPro (T4)
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
            'Accept-Language': 'en-US,en;q=0.9',
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
            'vod_play_url': '正片$' + slug,
        }

        return {'list': [vod]}

    def _extract_play_url(self, html, slug):
        if slug in self._play_cache:
            return self._play_cache[slug]

        mp4_url = ''

        # 1. 从 window.initials 提取完整列表
        m = re.search(r'window\.initials\s*=\s*(\{.*?\});', html, re.DOTALL)
        if m:
            try:
                data = json.loads(m.group(1))
                video_info = data.get('video', {})
                sources = video_info.get('sources', [])
                
                # 过滤掉 preview / trailer 切片
                valid_sources = []
                for src in sources:
                    u = src.get('url', '')
                    t = str(src.get('title', '')).lower()
                    if u and 'preview' not in u.lower() and 'trailer' not in t and 'preview' not in t:
                        valid_sources.append(src)
                
                if not valid_sources and sources:
                    valid_sources = sources

                # 按清晰度从高到低排序，优先找 720p / 1080p，排除超短片段
                for target in ['1080', '720', '480', '360']:
                    for src in valid_sources:
                        if target in str(src.get('title', '')):
                            mp4_url = src.get('url', '')
                            break
                    if mp4_url:
                        break

                if not mp4_url and valid_sources:
                    mp4_url = valid_sources[0].get('url', '')

            except Exception:
                pass

        # 2. 从 HTML 直接匹配完整的 video source
        if not mp4_url:
            sources_html = re.findall(r'<source[^>]+src="([^"]+\.mp4[^"]*)"[^>]*>', html)
            for src_url in sources_html:
                if 'preview' not in src_url.lower():
                    mp4_url = src_url
                    break

        # 3. 兜底匹配 xhcdn 直链
        if not mp4_url:
            all_mp4s = re.findall(r'(https://[a-zA-Z0-9\.]+\.xhcdn\.com/[^"\']+\.mp4[^"\']*)', html)
            for u in all_mp4s:
                if 'preview' not in u.lower():
                    mp4_url = u
                    break

        if mp4_url:
            self._play_cache[slug] = mp4_url

        return mp4_url

    def playerContent(self, flag, id, vipFlags):
        if not id:
            return {'parse': 1, 'playUrl': '', 'url': ''}

        if '$' in id:
            id = id.split('$')[-1]

        slug = str(id)
        mp4_url = self._play_cache.get(slug)

        if not mp4_url:
            url = f'{self.host}/video/{slug}'
            html = self._fetch_html(url)
            mp4_url = self._extract_play_url(html, slug)

        if not mp4_url:
            return {'parse': 1, 'playUrl': '', 'url': ''}

        # 传递标准播放 Header，防防盗链中途掐断
        return {
            'parse': 0,
            'playUrl': '',
            'url': mp4_url,
            'header': {
                'User-Agent': self.header['User-Agent'],
                'Referer': f'{self.host}/video/{slug}',
                'Origin': self.host,
            },
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
