# -*- coding: utf-8 -*-
# by @嗷呜 (优化修复版)
import json
import random
import string
import sys
import time
from base64 import b64decode
from urllib.parse import quote
from Crypto.Cipher import AES
from Crypto.Hash import MD5
from Crypto.Util.Padding import unpad

sys.path.append('..')
try:
    from base.spider import Spider
except ImportError:
    class Spider:
        pass


class Spider(Spider):

    def init(self, extend=""):
        self.did = self.getdid()
        res = self.gettoken()
        if res and len(res) == 3:
            self.token, self.phost, self.host = res
        else:
            self.token, self.phost, self.host = "", "", ""

    def isVideoFormat(self, url):
        return any(x in url.lower() for x in ['.m3u8', '.mp4', '.flv'])

    def manualVideoCheck(self):
        return False

    def action(self, action):
        pass

    def destroy(self):
        pass

    # 扩展备选域名池与后缀
    hs = ['wcyfhknomg', 'pdcqllfomw', 'alxhzjvean', 'bqeaaxzplt', 'hfbtpixjso', 'app', 'api']
    tlds = ['work', 'com', 'xyz', 'top']

    ua = 'Mozilla/5.0 (Linux; Android 11; M2012K10C Build/RP1A.200720.011; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/87.0.4280.141 Mobile Safari/537.36;SuiRui/twitter/ver=1.4.4'

    def homeContent(self, filter):
        if not self.host:
            return {'class': []}
        try:
            resp = self.fetch(f'{self.host}/api/video/classifyList', headers=self.headers()).json()
            data = resp.get('encData', '')
            data1 = self.aes(data)
            result = {
                'filters': {
                    "1": [{"key": "fl", "name": "分类", "value": [{"n": "最近更新", "v": "1"}, {"n": "最多播放", "v": "2"}, {"n": "好评榜", "v": "3"}]}],
                    "2": [{"key": "fl", "name": "分类", "value": [{"n": "最近更新", "v": "1"}, {"n": "最多播放", "v": "2"}, {"n": "好评榜", "v": "3"}]}],
                    "3": [{"key": "fl", "name": "分类", "value": [{"n": "最近更新", "v": "1"}, {"n": "最多播放", "v": "2"}, {"n": "好评榜", "v": "3"}]}],
                    "4": [{"key": "fl", "name": "分类", "value": [{"n": "最近更新", "v": "1"}, {"n": "最多播放", "v": "2"}, {"n": "好评榜", "v": "3"}]}],
                    "5": [{"key": "fl", "name": "分类", "value": [{"n": "最近更新", "v": "1"}, {"n": "最多播放", "v": "2"}, {"n": "好评榜", "v": "3"}]}],
                    "6": [{"key": "fl", "name": "分类", "value": [{"n": "最近更新", "v": "1"}, {"n": "最多播放", "v": "2"}, {"n": "好评榜", "v": "3"}]}],
                    "7": [{"key": "fl", "name": "分类", "value": [{"n": "最近更新", "v": "1"}, {"n": "最多播放", "v": "2"}, {"n": "好评榜", "v": "3"}]}],
                    "jx": [{"key": "type", "name": "精选", "value": [{"n": "日榜", "v": "1"}, {"n": "周榜", "v": "2"}, {"n": "月榜", "v": "3"}, {"n": "总榜", "v": "4"}]}]
                }
            }
            classes = [{'type_name': "精选", 'type_id': "jx"}]
            for k in data1.get('data', []):
                classes.append({'type_name': k['classifyTitle'], 'type_id': str(k['classifyId'])})
            result['class'] = classes
            return result
        except Exception:
            return {'class': []}

    def homeVideoContent(self):
        return {'list': []}

    def categoryContent(self, tid, pg, filter, extend):
        if not self.host:
            return {'list': []}
        pg = str(pg)
        path = f'/api/video/queryVideoByClassifyId?pageSize=20&page={pg}&classifyId={tid}&sortType={extend.get("fl", "1")}'
        if 'click' in tid:
            path = f'/api/video/queryPersonVideoByType?pageSize=20&page={pg}&userId={tid.replace("click", "")}'
        if tid == 'jx':
            path = f'/api/video/getRankVideos?pageSize=20&page={pg}&type={extend.get("type", "1")}'
        try:
            resp = self.fetch(f'{self.host}{path}', headers=self.headers()).json()
            data = resp.get('encData', '')
            data1 = self.aes(data).get('data', [])
            videos = []
            for k in data1:
                id = f'{k.get("videoId")}?{k.get("userId")}?{k.get("nickName")}'
                if 'click' in tid:
                    id = id + 'click'
                cover = k.get('coverImg', [''])[0] if k.get('coverImg') else ''
                pic_url = self.getProxyUrl() + f"&url={cover}" if hasattr(self, 'getProxyUrl') else cover
                videos.append({
                    "vod_id": id,
                    'vod_name': k.get('title'),
                    'vod_pic': pic_url,
                    'vod_remarks': self.dtim(k.get('playTime')),
                    'style': {"type": "rect", "ratio": 1.33}
                })
            return {
                "list": videos,
                "page": int(pg),
                "pagecount": 9999,
                "limit": 20,
                "total": 999999
            }
        except Exception:
            return {'list': []}

    def detailContent(self, ids):
        if not self.host:
            return {'list': []}
        try:
            vid = ids[0].replace('click', '').split('?')
            path = f'/api/video/can/watch?videoId={vid[0]}'
            resp = self.fetch(f'{self.host}{path}', headers=self.headers()).json()
            data = resp.get('encData', '')
            data1 = self.aes(data).get('playPath', '')
            nick = vid[2] if len(vid) > 2 else "播放"
            clj = '[a=cr:' + json.dumps({'id': vid[1] + 'click', 'name': nick}) + '/]' + nick + '[/a]' if len(vid) > 1 else nick
            if 'click' in ids[0]:
                clj = nick
            vod = {'vod_director': clj, 'vod_play_from': "推特", 'vod_play_url': f"{nick}${data1}"}
            return {"list": [vod]}
        except Exception:
            return {"list": []}

    def searchContent(self, key, quick, pg='1'):
        if not self.host:
            return {'list': []}
        path = f'/api/search/keyWord?pageSize=20&page={pg}&searchWord={quote(key)}&searchType=1'
        try:
            resp = self.fetch(f'{self.host}{path}', headers=self.headers()).json()
            data = resp.get('encData', '')
            data1 = self.aes(data).get('videoList', [])
            videos = []
            for k in data1:
                id = f'{k.get("videoId")}?{k.get("userId")}?{k.get("nickName")}'
                cover = k.get('coverImg', [''])[0] if k.get('coverImg') else ''
                pic_url = self.getProxyUrl() + f"&url={cover}" if hasattr(self, 'getProxyUrl') else cover
                videos.append({
                    "vod_id": id,
                    'vod_name': k.get('title'),
                    'vod_pic': pic_url,
                    'vod_remarks': self.dtim(k.get('playTime')),
                    'style': {"type": "rect", "ratio": 1.33}
                })
            return {
                "list": videos,
                "page": int(pg),
                "pagecount": 9999,
                "limit": 20,
                "total": 999999
            }
        except Exception:
            return {'list': []}

    def playerContent(self, flag, id, vipFlags):
        headers = self.headers()
        header_str = "&".join([f"{k}={v}" for k, v in headers.items()])
        return {"parse": 0, "url": id, "header": header_str}

    def localProxy(self, param):
        return self.imgs(param)

    def getsign(self):
        t = str(int(time.time() * 1000))
        sign = self.md5(t)
        return sign, t

    def headers(self):
        sign, t = self.getsign()
        return {'User-Agent': self.ua, 'deviceid': self.did, 't': t, 's': sign, 'aut': getattr(self, 'token', '')}

    def aes(self, word):
        if not word:
            return {}
        try:
            key = b64decode("SmhiR2NpT2lKSVV6STFOaQ==")
            iv = key
            cipher = AES.new(key, AES.MODE_CBC, iv)
            decrypted = unpad(cipher.decrypt(b64decode(word)), AES.block_size)
            return json.loads(decrypted.decode('utf-8'))
        except Exception:
            return {}

    def dtim(self, seconds):
        try:
            seconds = int(seconds)
            hours = seconds // 3600
            minutes = (seconds % 3600) // 60
            secs = seconds % 60
            if hours > 0:
                return f"{str(hours).zfill(2)}:{str(minutes).zfill(2)}:{str(secs).zfill(2)}"
            return f"{str(minutes).zfill(2)}:{str(secs).zfill(2)}"
        except Exception:
            return "666"

    def gettoken(self, i=0, max_attempts=15):
        if i >= len(self.hs) or i >= max_attempts:
            return None
        
        # 尝试轮询不同的主域名与后缀
        host_name = self.hs[i % len(self.hs)]
        for tld in self.tlds:
            random_sub = ''.join(random.choices(string.ascii_lowercase + string.digits, k=random.randint(5, 10)))
            current_domain = f"https://{random_sub}.{host_name}.{tld}"
            try:
                url = f'{current_domain}/api/user/traveler'
                sign, t = self.getsign()
                headers = {
                    'User-Agent': self.ua,
                    'Accept': 'application/json',
                    'deviceid': self.did,
                    't': t,
                    's': sign,
                }
                data = {
                    'deviceId': self.did,
                    'tt': 'U',
                    'code': '##X-4m6Goo4zzPi1hF##',
                    'chCode': 'tt09'
                }
                response = self.post(url, json=data, headers=headers, timeout=5)
                if response.status_code == 200:
                    res_json = response.json()
                    if res_json.get('data'):
                        data1 = res_json['data']
                        return data1['token'], data1['imgDomain'], current_domain
            except Exception:
                continue
        return self.gettoken(i + 1, max_attempts)

    def getdid(self):
        did = getattr(self, 'getCache', lambda k: '')('did')
        if not did:
            t = str(int(time.time()))
            did = self.md5(t)
            if hasattr(self, 'setCache'):
                self.setCache('did', did)
        return did

    def md5(self, text):
        h = MD5.new()
        h.update(text.encode('utf-8'))
        return h.hexdigest()

    def imgs(self, param):
        headers = {'User-Agent': self.ua}
        url = param.get('url', '')
        data = self.fetch(f"{getattr(self, 'phost', '')}{url}", headers=headers)
        bdata = self.img(data.content, 100, '2020-zq3-888')
        return [200, data.headers.get('Content-Type'), bdata]

    def img(self, data: bytes, length: int, key: str):
        GIF = b'\x47\x49\x46'
        JPG = b'\xFF\xD8\xFF'
        PNG = b'\x89\x50\x4E\x47\x0D\x0A\x1A\x0A'

        if len(data) > 7 and (data[1:8] == PNG[1:8] or data[:3] == JPG):
            return data
        if len(data) > 2 and data[:3] == GIF:
            return data

        key_bytes = key.encode('utf-8')
        result = bytearray(data)
        for i in range(min(length, len(result))):
            result[i] ^= key_bytes[i % len(key_bytes)]
        return bytes(result)