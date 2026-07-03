import os
import re
import random
import string
import glob
import datetime
import json

cnb_path = 'datas/cnb.json'
haitun_path = 'datas/haitun.json'

# 控制开关和追踪器的文件路径
lock_file_path = 'datas/控制开关.txt'
tracker_path = 'datas/最新接口文件名.txt'

# ====================================================================
# ⏰ 【每月 1 号自动大洗牌与控制开关自动生成逻辑 - 引入月份判定版】 (原逻辑保留)
# ====================================================================
today = datetime.datetime.now()
current_month = str(today.month) 
is_reset_day = (today.day == 1)

saved_month = ""
saved_code = ""

if os.path.exists(lock_file_path):
    with open(lock_file_path, 'r', encoding='utf-8') as f:
        content = f.read().strip()
        if "-" in content:
            saved_month, saved_code = content.split("-", 1)
        else:
            saved_code = content

if is_reset_day and saved_month != current_month:
    current_token = ''.join(random.choices(string.ascii_lowercase + string.digits, k=3))
    with open(lock_file_path, 'w', encoding='utf-8') as f:
        f.write(f"{current_month}-{current_token}")
    print(f"⏰ 【每月1号全新硬核洗牌】检测到进入新月份 {current_month} 月！已全自动抽签生成本月新密锁: {current_token}")
elif is_reset_day and saved_month == current_month:
    current_token = saved_code
    print(f"🔒 【安全阀拦截】今日 1 号已经是当月第二次运行，保持原暗号: {current_token}")
else:
    if not saved_code or len(saved_code) != 3 or "-" not in (content if os.path.exists(lock_file_path) else ""):
        current_token = ''.join(random.choices(string.ascii_lowercase + string.digits, k=3))
        with open(lock_file_path, 'w', encoding='utf-8') as f:
            f.write(f"{current_month}-{current_token}")
    else:
        current_token = saved_code
    print(f"📡 正常沿用本月密锁: {current_token}")

if current_token in ["全量版", "纯净版"]:
    output_filename = "老杨TV纯净版.json"
else:
    output_filename = f"老杨TV纯净版{current_token}.json"

output_path = f"datas/{output_filename}"
print(f"🎯 最终结算 -> 目标输出：{output_filename}")

# ====================================================================
# 🛡️ 【金蝉脱壳：绿色版过期旧线一键调包为纯文字滚动大轰炸】 (原逻辑保留)
# ====================================================================
old_configs = glob.glob('datas/老杨TV纯净版*.json') + glob.glob('datas/老杨TV无18*.json')
for old_file in old_configs:
    if os.path.basename(old_file) != output_filename:
        try:
            trap_json = {
                "spider": "", 
                "notice": "⚠️ 警告：当前“老杨TV”绿色专线密码已过期断流！老链接已彻底作废！\n\n最新密码或纯净版链接加QQ群“532637640”获取",
                "sites": [
                    {"key": "老杨绿色纯文字提示", "name": "➡️ 请前往QQ群“532637640”获取最新密码🚨 ➡️ 请前往QQ群“532637640”获取最新密码", "type": 3, "api": "csp_JuDou", "searchable": 0, "quickSearch": 0, "filterable": 0},
                    {"key": "老杨绿色纯文字提示2", "name": "🚨 不要看这里了 ➡️ 请前往QQ群“532637640”获取最新密码", "type": 3, "api": "csp_JuDou", "searchable": 0, "quickSearch": 0, "filterable": 0}
                ],
                "lives": [
                    {"group": "🚨 接口过期断流 ｜ 提示", "channels": [{"name": "👉 当前线路已过期 ➡️  请前往QQ群“532637640”获取最新密码", "urls": ["http://127.0.0.1"]}]}
                ]
            }
            with open(old_file, 'w', encoding='utf-8') as f:
                json.dump(trap_json, f, ensure_ascii=False, indent=4)
            print(f"📡 【金蝉脱壳】已成功将过期旧线调包为纯文字大轰炸: {old_file}")
        except:
            pass

for garbage in ['datas/local_config.json', *glob.glob('datas/config_*.json')]:
    try: os.remove(garbage)
    except: pass


# ====================================================================
# 🧠 【核心逻辑：正统 JSON 对象读取与合并逻辑】
# ====================================================================
def load_json_safe(path):
    if not os.path.exists(path):
        return {}
    with open(path, 'r', encoding='utf-8') as f:
        try:
            return json.load(f)
        except Exception as e:
            print(f"❌ 错误：{path} JSON 格式不正确！无法解析。")
            return {}

json_cnb = load_json_safe(cnb_path)
json_haitun = load_json_safe(haitun_path)

haitun_sites = json_haitun.get("sites", [])
haitun_lives = json_haitun.get("lives", [])

for item in haitun_sites:
    if "name" in item:
        item["name"] = f"{item['name']}｜Tg：@huliys9"
for item in haitun_lives:
    if "name" in item:
        item["name"] = f"{item['name']}｜Tg：@huliys9"

country_live_dict = {
    "name": "乡村电视安全防屏蔽占位符",
    "type": 0,
    "playerType": 2,
    "ua": "okhttp/5.3.2",
    "url": "https://gh-proxy.com/https://raw.githubusercontent.com/GodLike631/test/refs/heads/main/datas/%E4%B9%A1%E6%9D%91%E7%94%B5%E8%A7%86.txt"
}
if len(haitun_lives) >= 5:
    haitun_lives.insert(5, country_live_dict)
else:
    haitun_lives.append(country_live_dict)

cnb_sites = json_cnb.get("sites", [])
cnb_lives = json_cnb.get("lives", [])

# 備份去重時需要的原有解析列表
combined_parses = json_haitun.get("parses", []) + json_cnb.get("parses", [])

json_cnb["sites"] = haitun_sites + cnb_sites
json_cnb["lives"] = haitun_lives + cnb_lives

final_json_text = json.dumps(json_cnb, ensure_ascii=False, indent=4)

final_json_text = final_json_text.replace('"key": "hajim-腾讯备"', '"spider": "./tvbox.jar",\n            "key": "hajim-腾讯备"')
final_json_text = final_json_text.replace('"key": "茫茫"', '"spider": "./tvbox.jar",\n            "key": "茫茫"')

final_json_text = final_json_text.replace('🐬', '').replace('海豚影视', '').replace('海豚', '')
final_json_text = final_json_text.replace('完全免费，如有收费的都是骗子', '').replace('交流群 TG：@hshsjk9', '')

path_replacements = {
    './spider.jar': 'https://cnb.cool/fish2018/xs/-/git/raw/main/spider.jar',
    './XBPQ/': 'https://cnb.cool/fish2018/xs/-/git/raw/main/XBPQ/',
    './XYQHiker/': 'https://cnb.cool/fish2018/xs/-/git/raw/main/XYQHiker/',
    './js/': 'https://cnb.cool/fish2018/xs/-/git/raw/main/js/',
    './json/': 'https://cnb.cool/fish2018/xs/-/git/raw/main/json/',
    './py/': 'https://cnb.cool/fish2018/xs/-/git/raw/main/py/',
    'http://127.0.0.1:9978/file/TVBox/logo.png': 'https://img.naixiai.cn/2026/06/18/IMG_6638.jpeg'
}
for src, dst in path_replacements.items():
    final_json_text = final_json_text.replace(src, dst)

thanks_warning = "\n\n👑 【特别致谢与版权声明】\n本接口的诞生离不开大后方几位业内顶流技术大佬的无私奉献，特此致谢：\n🐋 感谢鱼佬的付出 (源码基础: fish2018/webhtv，TG群: https://t.me/webhtv)\n 感谢佬的付出 (核心仓库: FGBLH/GHK，TG群: https://t.me/hshsjk9)"
welcome_notice = "👑 欢迎使用【老杨TV粉丝专属绿色纯净线】！本接口由老杨TV结合海豚佬＆鱼佬的优质资源缝合而成，纯净无广告！🚨 重要提示：本接口密码不定期全自动更换！如果遇到失效 or 断流，请及时回 Telegram 频道（@huliys9）或微信群获取当前最新密码！"

try:
    final_obj = json.loads(final_json_text)
    
    # 🌟【FongMi 规范性改造】公告与致谢合并到 notice，并物理擦除无用 warningText
    final_obj["notice"] = welcome_notice + thanks_warning
    if "warningText" in final_obj:
        final_obj.pop("warningText")
    
    ordered_obj = {}
    if "notice" in final_obj: 
        ordered_obj["notice"] = final_obj.pop("notice")
        
    ordered_obj.update(final_obj)
    
    # 🛡️ 绿色版原功能保留：全自动全盘对象级物理擦除 18 禁不健康元素
    clean_sites = []
    for site in ordered_obj.get("sites", []):
        site_str = json.dumps(site, ensure_ascii=False)
        if "🔞" not in site_str and "18+" not in site_str and "有三级片" not in site_str:
            clean_sites.append(site)
            
    clean_lives = []
    for live in ordered_obj.get("lives", []):
        live_str = json.dumps(live, ensure_ascii=False)
        if "🔞" not in live_str and "18+" not in live_str and "有三级片" not in live_str:
            if live and isinstance(live, dict):
                # 🛠️ 优化：直播流统一补齐或升级最稳健的 okhttp/5.3.2 UA
                if not live.get("ua") or live.get("ua") == "okhttp":
                    live["ua"] = "okhttp/5.3.2"
                clean_lives.append(live)
            
    ordered_obj["sites"] = clean_sites
    ordered_obj["lives"] = clean_lives

    # 🎯 【靶向解密还原】：净化做完后，把乡村电视的名字完美恢复
    for live in ordered_obj.get("lives", []):
        if live.get("name") == "乡村电视安全防屏蔽占位符" or "乡村电视" in live.get("name", ""):
            live["name"] = "乡村电视 ｜Tg：@huliys9"

    # ====================================================================
    # 🌟【全新黑科技注入區：大屏體驗極致優化】
    # ====================================================================
    try:
        # --- 1. 解析器去重與優化加載 ---
        unique_parses = []
        seen_names = set()
        for p in combined_parses:
            name = p.get("name", "")
            if name and name not in seen_names:
                unique_parses.append(p)
                seen_names.add(name)
        ordered_obj["parses"] = unique_parses

        # --- 2. 注入國內低延遲 AliDNS 到 doh 首位 并修复潜在拼写错误 ---
        if "doh" in ordered_obj and isinstance(ordered_obj["doh"], list):
            for doh_item in ordered_obj["doh"]:
                if doh_item.get("url", "").endswith("/dns-quer"):
                    doh_item["url"] = doh_item["url"] + "y"
            
            ali_doh = {
                "name": "AliDNS",
                "url": "https://dns.alidns.com/dns-query",
                "ips": ["223.5.5.5", "223.6.6.6"]
            }
            if not any(d.get("name") == "AliDNS" for d in ordered_obj["doh"]):
                ordered_obj["doh"].insert(0, ali_doh)

        # --- 3. 物理剔除直播流末尾的無用空對象 {} 規避閃退 ---
        if "lives" in ordered_obj and isinstance(ordered_obj["lives"], list):
            ordered_obj["lives"] = [live for live in ordered_obj["lives"] if live]

        # --- 4. 雲端高級去廣告 WebView JS 腳本強勢注入 ---
        custom_js_rules = [
            "console.log('老楊TV綠色版高級WebView攔截器啟動');",
            "window.addEventListener('DOMContentLoaded', function() {",
            "   document.querySelectorAll('video').forEach(v => { v.muted = true; v.play().catch(e=>{}); });",
            "   Function.prototype.__constructor__ = Function.prototype.constructor;",
            "   Function.prototype.constructor = function() { if (arguments && typeof arguments[0] === 'string' && arguments[0].includes('debugger')) { return function(){}; } return Function.prototype.__constructor__.apply(this, arguments); };",
            "});",
            "setInterval(() => {",
            "   let selectors = ['.adv-class', '.pop-banner', '#notice-modal', '[id*=\"partner\"]', '[class*=\"baidu\"]', 'iframe[src*=\"game\"]', 'iframe[src*=\"bet\"]', '#pop-ad', '.sidebar-ads', 'a[href*=\"999\"]'];",
            "   selectors.forEach(sel => { document.querySelectorAll(sel).forEach(el => el.remove()); });",
            "}, 400);"
        ]

        current_rules = ordered_obj.get("rules", [])
        if not isinstance(current_rules, list):
            current_rules = []
            
        ad_hosts = ["vip.wwgz.cn", "lziplayer.com", "m3u8.apibdzy.com", "cj.ffzyapi.com", "api.hbzyapi.com"]
        for rule in current_rules:
            if isinstance(rule, dict) and "hosts" in rule:
                for h in rule["hosts"]:
                    if h not in ad_hosts: ad_hosts.append(h)

        js_injection_rule = {
            "name": "老楊TV·雲端高級去广告JS注入",
            "hosts": ad_hosts,
            "script": custom_js_rules
        }
        ordered_obj["rules"] = [js_injection_rule] + [r for r in current_rules if r.get("name") != "老楊TV·雲端高級去广告JS注入"]

        # --- 5 & 6. 站點名字清洗、智慧大類劃分 与 九大方阵动态重排同步清洗算法 ---
        block_1_douban = []       # 1. 豆瓣首页专享
        block_2_yingshi = []      # 2. 影视/追剧/APP大类
        block_3_duanju = []       # 3. 短剧/剧场
        block_4_dongman = []      # 4. 动漫类
        block_5_cili = []         # 5. 网盘/磁力/4K
        block_6_tiyu = []         # 6. 体育/看球/直播
        block_7_shaoer = []       # 7. 少儿课堂/教育
        block_8_yinyue = []       # 8. 音乐/听书/功能线/DJ
        block_9_fuli = []         # 9. 福利/18禁 (绿色纯净版理论上此列表为空)

        tg_tail_count = 0

        for site in ordered_obj.get("sites", []):
            if "name" not in site:
                continue
                
            raw_name = site["name"]
            s_key = site.get("key", "")
            s_genre = site.get("genre", "")
            
            # 清洗基础名称
            for char in ['丨', '┃', ' ']:
                raw_name = raw_name.strip(char)
            raw_name = re.sub(r'\s+', ' ', raw_name)
            
            if "｜Tg：@huliys9" in raw_name:
                tg_tail_count += 1
                if tg_tail_count > 5: raw_name = raw_name.replace("｜Tg：@huliys9", "").strip()
            elif "｜Tg:@huliys9" in raw_name:
                tg_tail_count += 1
                if tg_tail_count > 5: raw_name = raw_name.replace("｜Tg:@huliys9", "").strip()

            if "ext" in site and site["ext"] == {}:
                site["ext"] = ""

            # 🛠️ 瓜子靶向保护：防误伤，强力摘出
            is_guazi = "瓜子" in raw_name or "GZ" == s_key

            # 🛠️ 阵营智能判定与分类组装
            if "豆瓣" in raw_name and "首页" in raw_name:
                site["name"] = "豆瓣 • 首页｜此接口非原创，合并自海豚佬 and 鱼佬接口，感谢两位大佬的付出，如有侵权，联系删除｜@huliys9"
                site["category"] = "综合"
                site["searchable"] = 0
                block_1_douban.append(site)
                
            elif "短剧" in raw_name or "剧场" in raw_name:
                # 🛠️ 修正：包含 DJ/dj 关键词的线一律强行分流进入音乐阵营
                if "dj" in raw_name.lower() or "dj" in s_key.lower():
                    if not raw_name.startswith("🦋"): raw_name = f"🦋 {raw_name}"
                    site["name"] = raw_name
                    site["category"] = "音乐"
                    site["searchable"] = 0
                    block_8_yinyue.append(site)
                else:
                    if not raw_name.startswith("🦋"): raw_name = f"🦋 {raw_name}"
                    site["name"] = raw_name
                    site["category"] = "短剧"
                    site["genre"] = "shortdrama"
                    block_3_duanju.append(site)
                    
            elif "动漫" in raw_name or "新番" in raw_name or "anime" in s_key.lower() or "a1" in raw_name.lower():
                if not raw_name.startswith("🦋"): raw_name = f"🦋 {raw_name}"
                site["name"] = raw_name
                site["category"] = "动漫"
                block_4_dongman.append(site)
                
            elif "磁力" in raw_name or "索" in raw_name or "盘" in raw_name or "云盘" in raw_name or "4k" in raw_name.lower():
                if not raw_name.startswith("🦋"): raw_name = f"🦋 {raw_name}"
                site["name"] = raw_name
                site["category"] = "网盘/磁力"
                if "PanWebShare" in site.get("api", ""):
                    site["changeable"] = 1
                block_5_cili.append(site)
                
            elif "体育" in raw_name or "球" in raw_name or "直播" in raw_name:
                if not raw_name.startswith("🦋"): raw_name = f"🦋 {raw_name}"
                site["name"] = raw_name
                site["category"] = "体育/直播"
                block_6_tiyu.append(site)
                
            elif "少儿" in raw_name or "课堂" in raw_name or "教学" in raw_name or "教育" in raw_name:
                if not raw_name.startswith("🦋"): raw_name = f"🦋 {raw_name}"
                site["name"] = raw_name
                site["category"] = "少儿"
                site["searchable"] = 0
                block_7_shaoer.append(site)
                
            elif "音乐" in raw_name or "网易云" in raw_name or "听书" in raw_name or "唱会" in raw_name or "fm" in raw_name.lower() or "相声" in raw_name or "小品" in raw_name or "戏曲" in raw_name or "推送" in raw_name or "配置" in raw_name or "版本" in raw_name or "本地" in raw_name or "dj" in raw_name.lower() or "dj" in s_key.lower():
                # 🛠️ 音乐和DJ专线统一合流进入第八阵营并修改对应category开关
                if not raw_name.startswith("🦋"): raw_name = f"🦋 {raw_name}"
                site["name"] = raw_name
                if "音乐" in raw_name or "网易云" in raw_name or "听书" in raw_name or "fm" in raw_name.lower() or "dj" in raw_name.lower() or "dj" in s_key.lower():
                    site["category"] = "音乐"
                else:
                    site["category"] = "综合"
                site["searchable"] = 0
                block_8_yinyue.append(site)
                
            else:
                # 影视/追剧/APP大类（包括洗净的瓜子影视等）
                if not raw_name.startswith("🦋"): raw_name = f"🦋 {raw_name}"
                site["name"] = raw_name
                site["category"] = "综合"
                block_2_yingshi.append(site)

            # 补齐非音乐少儿类的影视全局搜索开关
            if site.get("category") not in ["少儿", "音乐"] and "searchable" not in site:
                site["searchable"] = 1

        # 🛠️ 爱奇艺纯净线名称修复，去掉冗长致谢词，强制换上统一的官方TG后缀
        for site in block_2_yingshi:
            if site.get("key") == "AQY":
                site["name"] = "🦋 爱奇艺 ｜Tg：@huliys9"

        # 👑 按九大方阵顺序重组，落盘（福利 block_9 在绿色版中会被前方的擦除功能干掉，保持空列表安全坠尾）
        ordered_obj["sites"] = block_1_douban + block_2_yingshi + block_3_duanju + block_4_dongman + block_5_cili + block_6_tiyu + block_7_shaoer + block_8_yinyue + block_9_fuli
        print(f"🚀 【重排结算】绿色精简版洗牌算法圆满完成！豆瓣置顶并谢鸣、瓜子返航、DJ合流、18禁残余已全数清空。")

    except Exception as inner_e:
        print(f"⚠️ 提示：大屏高级美化优化处理时跳过，原因: {inner_e}")

    # ====================================================================
    # 🌟【写出最终文件与落盘】
    # ====================================================================
    output_json_text = json.dumps(ordered_obj, ensure_ascii=False, indent=4)

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(output_json_text)
        
    with open(tracker_path, 'w', encoding='utf-8') as f:
        f.write(output_filename)
        
    print(f"🎉 【绿色精简防屏蔽纯净版】更新成功！配置名: {output_path}")

except Exception as e:
    print(f"❌ 严重错误：最后的本地过滤渲染失败，reason: {e}")

if not os.path.exists(lock_file_path) or "-" not in (open(lock_file_path, 'r', encoding='utf-8').read() if os.path.exists(lock_file_path) else ""):
    with open(lock_file_path, 'w', encoding='utf-8') as f:
        f.write(f"{current_month}-{current_token}")
