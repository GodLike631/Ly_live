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
# ⏰ 【每月 1 号自动大洗牌与控制开关自动生成逻辑 - 引入月份判定版】
# ====================================================================
today = datetime.datetime.now()
current_month = str(today.month) 
is_reset_day = (today.day == 1)

saved_month = ""
saved_code = ""

# 1. 尝试读取现有的开关状态 (格式为 "月份-3位密码"，例如 "7-k9x")
if os.path.exists(lock_file_path):
    with open(lock_file_path, 'r', encoding='utf-8') as f:
        content = f.read().strip()
        if "-" in content:
            saved_month, saved_code = content.split("-", 1)
        else:
            # 如果里面是老脚本留下的纯文本或旧密码
            saved_code = content

# 🎯 判定：如果是 1 号，且记录的月份不是当前月份（说明是当月第一次跑，跨月了）
if is_reset_day and saved_month != current_month:
    # 随机生成 3 位新密码
    current_token = ''.join(random.choices(string.ascii_lowercase + string.digits, k=3))
    # 写入当前月份和新密码，例如 "7-k9x"
    with open(lock_file_path, 'w', encoding='utf-8') as f:
        f.write(f"{current_month}-{current_token}")
    print(f"⏰ 【每月1号全新硬核洗牌】检测到进入新月份 {current_month} 月！已全自动抽签生成本月新密锁: {current_token}")

# 🎯 判定：如果是 1 号的第二次及后续运行
elif is_reset_day and saved_month == current_month:
    current_token = saved_code
    print(f"🔒 【安全阀拦截】今日 1 号已经是当月第二次运行，保持原暗号: {current_token}")

# 🎯 平常日子
else:
    # 如果平时发现开关空了，或者里面还是旧的不带月份的密码，立刻初始化
    if not saved_code or len(saved_code) != 3 or "-" not in (content if os.path.exists(lock_file_path) else ""):
        current_token = ''.join(random.choices(string.ascii_lowercase + string.digits, k=3))
        with open(lock_file_path, 'w', encoding='utf-8') as f:
            f.write(f"{current_month}-{current_token}")
    else:
        current_token = saved_code
    print(f"📡 正常沿用本月密锁: {current_token}")

# 3. 🎯 严格判定最终输出的文件名（原汁原味：老杨TV纯净版）
if current_token in ["全量版", "纯净版"]:
    output_filename = "老杨TV纯净版.json"
else:
    output_filename = f"老杨TV纯净版{current_token}.json"

output_path = f"datas/{output_filename}"
print(f"🎯 最终结算 -> 目标输出：{output_filename}")

# ====================================================================
# 🛡️ 【金蝉脱壳：绿色版过期旧线一键调包为纯文字滚动大轰炸 - 沿用原脚本提示】
# ====================================================================
old_configs = glob.glob('datas/老杨TV纯净版*.json') + glob.glob('datas/老杨TV无18*.json')
for old_file in old_configs:
    if os.path.basename(old_file) != output_filename:
        try:
            trap_json = {
                "spider": "", 
                "notice": "⚠️ 警告：当前“老杨TV”绿色专线密码已过期断流！老链接已彻底作废！\n\n最新密码或纯净版链接加QQ群“532637640”获取",
                "warningText": "👑 特别提示：加QQ群“532637640”获取",
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

# 给海豚源打上后缀标签
for item in haitun_sites:
    if "name" in item:
        item["name"] = f"{item['name']}｜Tg：@huliys9"
for item in haitun_lives:
    if "name" in item:
        item["name"] = f"{item['name']}｜Tg：@huliys9"

# 精准插入“乡村电视占位符”到直播数组索引 5（第 6 位）
country_live_dict = {
    "name": "乡村电视安全防屏蔽占位符",
    "type": 0,
    "playerType": 2,
    "ua": "okhttp",
    "url": "https://gh-proxy.com/https://raw.githubusercontent.com/GodLike631/test/refs/heads/main/datas/%E4%B9%A1%E6%9D%91%E7%94%B5%E8%A7%86.txt"
}
if len(haitun_lives) >= 5:
    haitun_lives.insert(5, country_live_dict)
else:
    haitun_lives.append(country_live_dict)

# ====================================================================
# 🚀 数组大合并：【完美调整顺序】海豚排上面 ➡️ 最后接 cnb
# ====================================================================
cnb_sites = json_cnb.get("sites", [])
cnb_lives = json_cnb.get("lives", [])

json_cnb["sites"] = haitun_sites + cnb_sites
json_cnb["lives"] = haitun_lives + cnb_lives

# 转换为文本进行清洗与特调
final_json_text = json.dumps(json_cnb, ensure_ascii=False, indent=4)

# 补全关键 jar 依赖
final_json_text = final_json_text.replace('"key": "hajim-腾讯备"', '"spider": "./tvbox.jar",\n            "key": "hajim-腾讯备"')
final_json_text = final_json_text.replace('"key": "茫茫"', '"spider": "./tvbox.jar",\n            "key": "茫茫"')

# 净化海豚残留词
final_json_text = final_json_text.replace('🐬', '').replace('海豚影视', '').replace('海豚', '')
final_json_text = final_json_text.replace('完全免费，如有收费的都是骗子', '').replace('交流群 TG：@hshsjk9', '')

# 替换本地路径为绝对网络路径
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

# 绿色版开机公告注入 (原汁原味保留老杨TV公告)
thanks_warning = "👑 特别致谢与版权声明\n本接口的诞生离不开大后方几位业内顶流技术大佬的无私奉献，特此致谢：\n🐋 感谢鱼佬的付出\n源码基础与发布主页: fish2018/webhtv\n版本发布绝对地址: fish2018/webhtv/releases\nTelegram 官方群组: 👉 https://t.me/webhtv\n 感谢佬的付出\n核心仓库主页: FGBLH/GHK\n数据源直链地址: FGBLH/GHK/.json\nTelegram 官方群组: 👉 https://t.me/hshsjk9"
welcome_notice = "👑 欢迎使用【老杨TV粉丝专属绿色纯净线】！本接口由老杨TV结合海豚大佬＆鱼佬的优质资源缝合而成，纯净无广告！🚨 重要提示：本接口密码不定期全自动更换！如果遇到失效 or 断流，请及时回 Telegram 频道（@huliys9）或微信群获取当前最新密码！"

try:
    final_obj = json.loads(final_json_text)
    final_obj["notice"] = welcome_notice
    final_obj["warningText"] = thanks_warning
    
    ordered_obj = {}
    if "notice" in final_obj: ordered_obj["notice"] = final_obj.pop("notice")
    if "warningText" in final_obj: ordered_obj["warningText"] = final_obj.pop("warningText")
    ordered_obj.update(final_obj)
    
    # 🛡️ 绿色版专属核心：全自动全盘对象级物理擦除 18 禁不健康元素
    clean_sites = []
    for site in ordered_obj.get("sites", []):
        site_str = json.dumps(site, ensure_ascii=False)
        if "🔞" not in site_str and "18+" not in site_str and "有三级片" not in site_str:
            clean_sites.append(site)
            
    clean_lives = []
    for live in ordered_obj.get("lives", []):
        live_str = json.dumps(live, ensure_ascii=False)
        if "🔞" not in live_str and "18+" not in live_str and "有三级片" not in live_str:
            clean_lives.append(live)
            
    ordered_obj["sites"] = clean_sites
    ordered_obj["lives"] = clean_lives

    # 🎯 【靶向解密还原】：净化做完后，把乡村电视的名字完美恢复
    for live in ordered_obj.get("lives", []):
        if live.get("name") == "乡村电视安全防屏蔽占位符":
            live["name"] = "乡村电视 ｜Tg：@huliys9"

    # ====================================================================
    # 🌟【全新注入：深度大屏体验优化区】
    # ====================================================================
    try:
        # --- 1. 注入国内低延迟 AliDNS 到 doh 首位 ---
        if "doh" in ordered_obj and isinstance(ordered_obj["doh"], list):
            ali_doh = {
                "name": "AliDNS",
                "url": "https://dns.alidns.com/dns-query",
                "ips": ["223.5.5.5", "223.6.6.6"]
            }
            if not any(d.get("name") == "AliDNS" for d in ordered_obj["doh"]):
                ordered_obj["doh"].insert(0, ali_doh)

        # --- 2. 物理剔除直播 lives 列表末尾的无用空对象 {} 规避电视闪退 ---
        if "lives" in ordered_obj and isinstance(ordered_obj["lives"], list):
            ordered_obj["lives"] = [live for live in ordered_obj["lives"] if live]

        # --- 3. 站点名字精准裁切尾巴 + 智能排版自动分类 ---
        tg_tail_count = 0
        
        for site in ordered_obj.get("sites", []):
            if "name" in site:
                name_val = site["name"]
                
                # 去除杂质字符（原脚本基础美化）
                for char in ['丨', '┃', ' ']:
                    name_val = name_val.strip(char)
                name_val = re.sub(r'\s+', ' ', name_val)
                
                # 【保留前5个TG后缀】核心逻辑
                if "｜Tg：@huliys9" in name_val:
                    tg_tail_count += 1
                    if tg_tail_count > 5:
                        name_val = name_val.replace("｜Tg：@huliys9", "").strip()
                elif "｜Tg:@huliys9" in name_val:
                    tg_tail_count += 1
                    if tg_tail_count > 5:
                        name_val = name_val.replace("｜Tg:@huliys9", "").strip()

                # 前缀统一强制补全蝴蝶图标
                if not name_val.startswith("🦋"):
                    name_val = f"🦋 {name_val}"
                
                site["name"] = name_val

                # 【智能分类与搜索过滤】由于是纯净绿色版，剔除了成人分类
                s_key = site.get("key", "")
                s_genre = site.get("genre", "")
                
                if s_genre == "shortdrama" or "短剧" in name_val or "dj" in s_key.lower():
                    site["category"] = "短剧"
                elif "少儿" in name_val or "课堂" in name_val or "教学" in name_val:
                    site["category"] = "少儿"
                    site["searchable"] = 0  # 音乐、教育类不污染主页搜索
                    site["quickSearch"] = 0
                elif "音乐" in name_val or "网易云" in name_val or "听书" in name_val or "唱会" in name_val or "FM" in name_val:
                    site["category"] = "音乐"
                    site["searchable"] = 0
                    site["quickSearch"] = 0
                elif "动漫" in name_val or "新番" in name_val or "Anime" in s_key:
                    site["category"] = "动漫"
                elif "磁力" in name_val or "索" in name_val or "盘" in name_val or "云盘" in name_val or "4K" in name_val:
                    site["category"] = "网盘/磁力"
                elif "体育" in name_val or "球" in name_val or "直播" in name_val:
                    site["category"] = "体育/直播"
                else:
                    site["category"] = "综合"

        # 特殊指定大厂站点的固定还原命名
        for site in ordered_obj.get("sites", []):
            if "key" in site and site["key"] == "AQY":
                site["name"] = "🦋 爱奇艺｜此接口非原创，合并自海豚佬和鱼佬接口，感谢两位大佬的付出，如有侵权，联系删除｜@huliys9"
                site["category"] = "综合"

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

# 🌟 双重保险
if not os.path.exists(lock_file_path) or "-" not in (open(lock_file_path, 'r', encoding='utf-8').read() if os.path.exists(lock_file_path) else ""):
    with open(lock_file_path, 'w', encoding='utf-8') as f:
        f.write(f"{current_month}-{current_token}")
