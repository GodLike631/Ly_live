# coding=utf-8
# !/usr/bin/python
import json
import sys
import uuid
import copy

sys.path.append('..')
try:
    from base.spider import Spider
except ImportError:
    class Spider:
        pass

from pyquery import PyQuery as pq
from concurrent.futures import ThreadPoolExecutor, as_completed


class Spider(Spider):

    host = 'https://v.qq.com'
    apihost = 'https://pbaccess.video.qq.com'

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
        'origin': host,
        'referer': f'{host}/'
    }

    def init(self, extend=""):
        self.dbody = {
            "page_params": {
                "channel_id": "",
                "filter_params": "sort=75",
                "page_type": "channel_operation",
                "page_id": "channel_list_second_page"
            }
        }
        self.body = copy.deepcopy(self.dbody)

    def getName(self):
        return "腾讯视频"

    def isVideoFormat(self, url):
        formats = [".m3u8", ".mp4", ".flv", ".mkv", ".ts"]
        return any(f in (url or "").lower() for f in formats)

    def manualVideoCheck(self):
        return False

    def destroy(self):
        pass

    def _safe_post_json(self, url, body, headers=None):
        try:
            rsp = self.post(url, json=body, headers=headers or self.headers)
            if hasattr(rsp, 'json'):
                return rsp.json()
            elif isinstance(rsp, (str, bytes)):
                return json.loads(rsp)
            elif hasattr(rsp, 'text'):
                return json.loads(rsp.text)
            return {}
        except Exception:
            return {}

    def _safe_get_html(self, url):
        try:
            rsp = self.fetch(url, headers=self.headers)
            text = getattr(rsp, 'text', str(rsp))
            if hasattr(self, 'cleanText'):
                text = self.cleanText(text)
            return pq(text)
        except Exception:
            return pq("<html></html>")

    def homeContent(self, filter):
        cdata = {
            "电视剧": "100113",
            "电影": "100173",
            "综艺": "100109",
            "纪录片": "100105",
            "动漫": "100119",
            "少儿": "100150",
            "短剧": "110755"
        }
        result = {}
        classes = []
        filters = {}
        for k, v in cdata.items():
            classes.append({'type_name': k, 'type_id': v})

        with ThreadPoolExecutor(max_workers=min(len(classes), 8)) as executor:
            futures = [executor.submit(self.get_filter_data, item['type_id']) for item in classes]
            for future in futures:
                try:
                    cid, data = future.result()
                    if not data or not isinstance(data, dict):
                        continue

                    module_list = data.get('data', {}).get('module_list_datas', [])
                    if not module_list:
                        continue

                    filter_dict = {}
                    try:
                        items = module_list[-1]['module_datas'][-1]['item_data_lists']['item_datas']
                        for item in items:
                            params = item.get('item_params', {})
                            filter_key = params.get('index_item_key')
                            if not filter_key:
                                continue
                            if filter_key not in filter_dict:
                                filter_dict[filter_key] = {
                                    'key': filter_key,
                                    'name': params.get('index_name', filter_key),
                                    'value': []
                                }
                            filter_dict[filter_key]['value'].append({
                                'n': params.get('option_name', ''),
                                'v': params.get('option_value', '')
                            })
                    except (IndexError, KeyError, TypeError):
                        pass

                    if filter_dict:
                        filters[cid] = list(filter_dict.values())
                except Exception:
                    continue

        result['class'] = classes
        result['filters'] = filters
        return result

    def homeVideoContent(self):
        vlist = []
        try:
            data = self._safe_get_html(self.host)
            its = data('script')
            s = None
            for it in its.items():
                txt = it.text() or ""
                if 'window.__INITIAL_STATE__' in txt:
                    s = txt
                    break
            if s:
                index = s.find('=')
                if index != -1:
                    raw_json = s[index + 1:].strip()
                    if raw_json.endswith(';'):
                        raw_json = raw_json[:-1]
                    sd = json.loads(raw_json)
                    card_list = sd.get('storeModulesData', {}).get('channelsModulesMap', {}).get('choice', {}).get('cardListData', [])
                    for its in card_list:
                        if not isinstance(its, dict):
                            continue
                        cards = its.get('children_list', {}).get('list', {}).get('cards', [])
                        for it in cards:
                            p = it.get('params', {})
                            if not p:
                                continue
                            tag_raw = p.get('uni_imgtag') or p.get('imgtag') or '{}'
                            try:
                                tag = json.loads(tag_raw) if isinstance(tag_raw, str) else tag_raw
                            except Exception:
                                tag = {}
                            cid = it.get('id') or p.get('cid') or ''
                            name = p.get('mz_title') or p.get('title') or ''
                            if name and cid and 'http' not in str(cid):
                                vlist.append({
                                    'vod_id': str(cid),
                                    'vod_name': name,
                                    'vod_pic': p.get('image_url', ''),
                                    'vod_year': tag.get('tag_2', {}).get('text', ''),
                                    'vod_remarks': tag.get('tag_4', {}).get('text', '')
                                })
        except Exception:
            pass
        return {'list': vlist}

    def categoryContent(self, tid, pg, filter, extend):
        result = {
            'list': [],
            'page': int(pg),
            'pagecount': int(pg),
            'limit': 90,
            'total': 0
        }
        params = {
            "sort": extend.get('sort', '75'),
            "attr": extend.get('attr', '-1'),
            "itype": extend.get('itype', '-1'),
            "ipay": extend.get('ipay', '-1'),
            "iarea": extend.get('iarea', '-1'),
            "iyear": extend.get('iyear', '-1'),
            "theater": extend.get('theater', '-1'),
            "award": extend.get('award', '-1'),
            "recommend": extend.get('recommend', '-1')
        }

        if pg == '1' or not hasattr(self, 'body') or not self.body:
            req_body = copy.deepcopy(self.dbody)
        else:
            req_body = copy.deepcopy(self.body)

        req_body['page_params']['channel_id'] = tid
        req_body['page_params']['filter_params'] = self.josn_to_params(params)

        api_url = f'{self.apihost}/trpc.universal_backend_service.page_server_rpc.PageServer/GetPageData?video_appid=1000005&vplatform=2&vversion_name=8.9.10&new_mark_label_enabled=1'
        data = self._safe_post_json(api_url, req_body)

        ndata = data.get('data', {})
        if not ndata:
            return result

        if ndata.get('has_next_page'):
            result['pagecount'] = int(pg) + 1
            req_body['page_context'] = ndata.get('next_page_context', '')
            self.body = req_body
        else:
            result['pagecount'] = int(pg)

        vlist = []
        try:
            item_datas = ndata['module_list_datas'][-1]['module_datas'][-1]['item_data_lists']['item_datas']
            for its in item_datas:
                p = its.get('item_params', {})
                cid = p.get('cid')
                if not cid:
                    continue
                tag_raw = p.get('uni_imgtag') or p.get('imgtag') or '{}'
                try:
                    tag = json.loads(tag_raw) if isinstance(tag_raw, str) else tag_raw
                except Exception:
                    tag = {}
                name = p.get('mz_title') or p.get('title') or ''
                pic = p.get('new_pic_hz') or p.get('new_pic_vt') or p.get('image_url', '')
                vlist.append({
                    'vod_id': str(cid),
                    'vod_name': name,
                    'vod_pic': pic,
                    'vod_year': tag.get('tag_2', {}).get('text', ''),
                    'vod_remarks': tag.get('tag_4', {}).get('text', '')
                })
        except (KeyError, IndexError, TypeError):
            pass

        result['list'] = vlist
        result['total'] = 999999 if ndata.get('has_next_page') else len(vlist)
        return result

    def detailContent(self, ids):
        if not ids or not ids[0]:
            return {'list': []}
        cid = ids[0]

        vbody = {
            "page_params": {
                "req_from": "web",
                "cid": cid,
                "vid": "",
                "lid": "",
                "page_type": "detail_operation",
                "page_id": "detail_page_introduction"
            },
            "has_cache": 1
        }

        body = {
            "page_params": {
                "req_from": "web_vsite",
                "page_id": "vsite_episode_list",
                "page_type": "detail_operation",
                "id_type": "1",
                "page_size": "",
                "cid": cid,
                "vid": "",
                "lid": "",
                "page_num": "",
                "page_context": "",
                "detail_page_type": "1"
            },
            "has_cache": 1
        }

        with ThreadPoolExecutor(max_workers=2) as executor:
            future_detail = executor.submit(self.get_vdata, vbody)
            future_episodes = executor.submit(self.get_vdata, body)
            vdata = future_detail.result()
            data = future_episodes.result()

        pdata = self.process_tabs(data, body, ids)

        try:
            actors = []
            try:
                star_list = vdata['data']['module_list_datas'][0]['module_datas'][0]['item_data_lists']['item_datas'][0].get('sub_items', {}).get('star_list', {}).get('item_datas', [])
                actors = [star.get('item_params', {}).get('name', '') for star in star_list if star.get('item_params', {}).get('name')]
            except (KeyError, IndexError, TypeError):
                pass

            plist, ylist = self.process_pdata(pdata, ids)

            valid_names = []
            valid_urls = []
            if plist:
                valid_names.append('腾讯视频')
                valid_urls.append('#'.join(plist))
            if ylist:
                valid_names.append('预告片')
                valid_urls.append('#'.join(ylist))

            # 若未提取到正片列表，至少生成一条默认正片供播放嗅探
            if not valid_names:
                valid_names.append('腾讯视频')
                valid_urls.append(f"正片${cid}")

            vod = self.build_vod(vdata, actors, valid_urls, valid_names)
            vod['vod_id'] = cid
            return {'list': [vod]}
        except Exception as e:
            return self.handle_exception(e, "Error processing detail")

    def searchContent(self, key, quick, pg="1"):
        body = {
            "version": "24072901",
            "clientType": 1,
            "filterValue": "",
            "uuid": str(uuid.uuid4()),
            "retry": 0,
            "query": key,
            "pagenum": max(0, int(pg) - 1),
            "pagesize": 30,
            "queryFrom": 0,
            "searchDatakey": "",
            "transInfo": "",
            "isneedQc": True,
            "preQid": "",
            "adClientInfo": "",
            "extraInfo": {"isNewMarkLabel": "1", "multi_terminal_pc": "1"}
        }
        api_url = f'{self.apihost}/trpc.videosearch.mobile_search.MultiTerminalSearch/MbSearch?vplatform=2'
        data = self._safe_post_json(api_url, body)

        vlist = []
        try:
            area_boxes = data.get('data', {}).get('areaBoxList', [])
            if area_boxes:
                for box in area_boxes:
                    for k in box.get('itemList', []):
                        doc_id = k.get('doc', {}).get('id')
                        vinfo = k.get('videoInfo', {})
                        if not doc_id or not vinfo:
                            continue

                        img_tag = vinfo.get('imgTag')
                        tag = {}
                        if isinstance(img_tag, str) and img_tag.strip():
                            try:
                                tag = json.loads(img_tag)
                            except Exception:
                                tag = {}
                        elif isinstance(img_tag, dict):
                            tag = img_tag

                        vlist.append({
                            'vod_id': str(doc_id),
                            'vod_name': vinfo.get('title', ''),
                            'vod_pic': vinfo.get('imgUrl', ''),
                            'vod_year': tag.get('tag_2', {}).get('text', ''),
                            'vod_remarks': tag.get('tag_4', {}).get('text', '')
                        })
        except Exception:
            pass

        return {'list': vlist, 'page': int(pg)}

    def playerContent(self, flag, id, vipFlags):
        """
        修复只播15秒广告/试看问题：
        1. 补全标准官方播放页 URL
        2. 接入支持跳过广告与解出 VIP 正片的解析链
        3. 增加兜底 headers 伪装
        """
        if id.startswith("http"):
            play_url = id
        elif '@' in id:
            cid, vid = id.split('@', 1)
            play_url = f"https://v.qq.com/x/cover/{cid}/{vid}.html"
        else:
            play_url = f"https://v.qq.com/x/cover/{id}.html"

        # 头部伪装（防盗链/防空壳）
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
            'Referer': 'https://v.qq.com/'
        }

        # 方案 A：直接输出官方播放页交给客户端主力解析接口（适用于 TVBox 配置了完整 parses 规则源）
        # return {
        #     'parse': 1,
        #     'url': play_url,
        #     'header': json.dumps(headers)
        # }

        # 方案 B（推荐）：直连稳定支持免广告解析接口（parse 设为 1，交由播放器加载解析页面嗅探正片）
        jx_api = "https://jx.jsonplayer.com/player/?url="
        # 备用稳定接口：https://jx.aidouer.net/?url= 或 https://jx.m3u8.tv/jiexi/?url=
        
        return {
            'parse': 1,
            'url': f"{jx_api}{play_url}",
            'header': json.dumps(headers),
            'jx': 1
        }

    def localProxy(self, param):
        return [404, "text/plain", ""]

    def get_filter_data(self, cid):
        hbody = copy.deepcopy(self.dbody)
        hbody['page_params']['channel_id'] = cid
        api_url = f'{self.apihost}/trpc.universal_backend_service.page_server_rpc.PageServer/GetPageData?video_appid=1000005&vplatform=2&vversion_name=8.9.10&new_mark_label_enabled=1'
        data = self._safe_post_json(api_url, hbody)
        return cid, data

    def get_vdata(self, body):
        try:
            api_url = f'{self.apihost}/trpc.universal_backend_service.page_server_rpc.PageServer/GetPageData?video_appid=3000010&vplatform=2&vversion_name=8.2.96'
            return self._safe_post_json(api_url, body)
        except Exception:
            return {'data': {'module_list_datas': []}}

    def process_pdata(self, pdata, ids):
        plist = []
        ylist = []
        seen = set()

        for k in pdata:
            if not isinstance(k, dict):
                continue
            item_id = k.get('item_id') or k.get('id')
            params = k.get('item_params', {})
            vid = params.get('vid') or item_id

            if not vid or vid in seen:
                continue
            seen.add(vid)

            title = params.get('union_title') or params.get('title') or f"第{len(plist) + 1}集"
            play_key = f"{ids[0]}@{vid}"
            entry = f"{title}${play_key}"

            # 区分预告片/花絮与正片
            is_trailer = (
                '预告' in title or 
                '花絮' in title or 
                params.get('is_trailer') == '1' or 
                params.get('video_type') in ['2', '3']
            )

            if is_trailer:
                ylist.append(entry)
            else:
                plist.append(entry)

        return plist, ylist

    def build_vod(self, vdata, actors, valid_urls, valid_names):
        try:
            d = vdata['data']['module_list_datas'][0]['module_datas'][0]['item_data_lists']['item_datas'][0].get('item_params', {})
        except (KeyError, IndexError, TypeError):
            d = {}

        return {
            'type_name': d.get('sub_genre', ''),
            'vod_name': d.get('title', ''),
            'vod_year': d.get('year', ''),
            'vod_area': d.get('area_name', ''),
            'vod_remarks': d.get('holly_online_time', '') or d.get('hotval', ''),
            'vod_actor': ','.join(filter(None, actors)),
            'vod_content': d.get('cover_description', ''),
            'vod_play_from': '$$$'.join(valid_names) if valid_names else '腾讯视频',
            'vod_play_url': '$$$'.join(valid_urls) if valid_urls else ''
        }

    def handle_exception(self, e, message):
        return {'list': [{'vod_name': '解析异常', 'vod_play_from': '提示', 'vod_play_url': f'{message}#1'}]}

    def process_tabs(self, data, body, ids):
        try:
            module_list = data.get('data', {}).get('module_list_datas', [])
            if not module_list:
                return []

            pdata = []
            try:
                pdata = module_list[-1]['module_datas'][-1]['item_data_lists']['item_datas']
            except (KeyError, IndexError, TypeError):
                pdata = []

            tabs_raw = None
            try:
                tabs_raw = module_list[-1]['module_datas'][-1].get('module_params', {}).get('tabs')
            except (KeyError, IndexError, TypeError):
                pass

            if tabs_raw:
                tabs = json.loads(tabs_raw) if isinstance(tabs_raw, str) else tabs_raw
                if isinstance(tabs, list) and len(tabs) > 1:
                    remaining_tabs = tabs[1:]
                    task_queue = []
                    for tab in remaining_tabs:
                        nbody = copy.deepcopy(body)
                        nbody['page_params']['page_context'] = tab.get('page_context', '')
                        task_queue.append(nbody)

                    with ThreadPoolExecutor(max_workers=min(len(task_queue), 8)) as executor:
                        future_map = {executor.submit(self.get_vdata, task): idx for idx, task in enumerate(task_queue)}
                        results = [None] * len(task_queue)
                        for future in as_completed(future_map.keys()):
                            idx = future_map[future]
                            results[idx] = future.result()
                        for result in results:
                            if result and isinstance(result, dict):
                                try:
                                    page_data = result['data']['module_list_datas'][-1]['module_datas'][-1]['item_data_lists']['item_datas']
                                    pdata.extend(page_data)
                                except (KeyError, IndexError, TypeError):
                                    continue
            return pdata
        except Exception:
            return []

    def josn_to_params(self, params, skip_empty=False):
        query = []
        for k, v in params.items():
            if skip_empty and not v:
                continue
            query.append(f"{k}={v}")
        return "&".join(query)
