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
# ⏰ 【每月 1 号自动大洗牌逻辑与绿色纯净版命名融合】
# ====================================================================
today = datetime.datetime.now()
is_reset_day = (today.day == 1)

# 默认状态
current_token = "全量版"

# 1. 先尝试读取现有的开关状态
if os.path.exists(lock_file_path):
    with open(lock_file_path, 'r', encoding='utf-8') as f:
        current_token = f.read().strip()

# 2. 如果是 1 号，且目前开关里还不是 3 位随机暗号（说明是当月第一次跑，或者是全量版/纯净版字样）
# 则强制触发大洗牌，自动抽签 3 位新密码并写入控制开关
if is_reset_day and (current_token in ["全量版", "纯净版"] or len(current_token) != 3):
    current_token = ''.join(random.choices(string.ascii_lowercase + string.digits, k=3))
    with open(lock_file_path, 'w', encoding='utf-8') as f:
        f.write(current_token)
    print(f"⏰ 【每月1号绿色版全自动洗牌】已触发！自动抽签生成本月新密锁并写入开关: {current_token}")
elif is_reset_day:
    print(f"🔒 【安全阀拦截】今日 1 号已在早晨完成绿色版大洗牌，晚上保持原暗号不再重复抽签: {current_token}")

# 3. 🎯 严格判定最终输出的文件名（固定带上“纯净版”）
if current_token in ["全量版", "纯净版"]:
    output_filename = "老杨TV纯净版.json"
else:
    output_filename = f"老杨TV纯净版{current_token}.json"

output_path = f"datas/{output_filename}"
print(f"🎯 最终结算 -> 目标输出：{output_filename}")

# ====================================================================
# 🛡️ 【金蝉脱壳：绿色版过期旧线一键调包为纯文字滚动大轰炸】
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
                    {"key": "老杨绿色纯文字提示", "name": "最新密码或纯净版链接加QQ群“532637640”获取", "type": 3, "api": "csp_JuDou", "searchable": 0, "quickSearch": 0, "filterable": 0},
                    {"key": "老杨绿色纯文字提示2", "name": "🚨 不要看这里了 ➡️ 请前往QQ群“532637640”获取最新动态", "type": 3, "api": "csp_JuDou", "searchable": 0, "quickSearch": 0, "filterable": 0}
                ],
                "lives": [
                    {"group": "🚨 接口过期断流 ｜ 提示", "channels": [{"name": "👉 当前线路已过期 ➡️ 请使用纯净版新链接", "urls": ["http://127.0.0.1"]}]}
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
# 🧠 【核心重构：正统 JSON 对象读取与合并逻辑】
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

# 1. 载入标准 JSON 对象
json_cnb = load_json_safe(cnb_path)
json_haitun = load_json_safe(haitun_path)

# 获取各自的列表
haitun_sites = json_haitun.get("sites", [])
haitun_lives = json_haitun.get("lives", [])

# 2. 给海豚源打上后缀标签
for item in haitun_sites:
    if "name" in item:
        item["name"] = f"{item['name']}｜Tg：@huliys9"
for item in haitun_lives:
    if "name" in item:
        item["name"] = f"{item['name']}｜Tg：@huliys9"

# 3. 精准插入“乡村电视占位符”到直播数组索引 5（第 6 位）
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
# 🚀 数组大合并
# ====================================================================
json_cnb["sites"] = haitun_sites
json_cnb["lives"] = haitun_lives

# ====================================================================
# 📝 转换为文本进行清洗与特调
# ====================================================================
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

# ====================================================================
# 🎯 强力拦截注入绿色版开机公告
# ====================================================================
thanks_warning = "👑 特别致谢与版权声明\n本接口的诞生离不开大后方几位业内顶流技术大佬的无私奉献，特此致谢：\n🐋 感谢鱼佬的付出\n源码基础与发布主页: fish2018/webhtv\n版本发布绝对地址: fish2018/webhtv/releases\nTelegram 官方群组: 👉 https://t.me/webhtv\n 感谢佬的付出\n核心仓库主页: FGBLH/GHK\n数据源直链地址: FGBLH/GHK/.json\nTelegram 官方群组: 👉 https://t.me/hshsjk9"
welcome_notice = "👑 欢迎使用【老杨TV粉丝专属绿色纯净线】！本接口由老杨TV结合海豚大佬＆鱼佬的优质资源缝合而成，纯净无广告！🚨 重要提示：本接口密码不定期全自动更换！如果遇到失效或断流，请及时回 Telegram 频道（@huliys9）或微信群获取当前最新密码！"

try:
    final_obj = json.loads(final_json_text)
    final_obj["notice"] = welcome_notice
    final_obj["warningText"] = thanks_warning
    
    ordered_obj = {}
    if "notice" in final_obj: ordered_obj["notice"] = final_obj.pop("notice")
    if "warningText" in final_obj: ordered_obj["warningText"] = final_obj.pop("warningText")
    ordered_obj.update(final_obj)
    
    # 🛡️ 绿色版专属核心：全自动全盘对象级物理擦除 18 禁不健康元素
    # 完美规避文本级切片对 JSON 闭合大括号的破坏
    clean_sites = []
    for site in ordered_obj.get("sites", []):
        site_str = json.dumps(site, ensure_ascii=False)
        if "🔞" not in site_str and "18+" not in site_str:
            clean_sites.append(site)
            
    clean_lives = []
    for live in ordered_obj.get("lives", []):
        live_str = json.dumps(live, ensure_ascii=False)
        if "🔞" not in live_str and "18+" not in live_str:
            clean_lives.append(live)
            
    ordered_obj["sites"] = clean_sites
    ordered_obj["lives"] = clean_lives

    # 🎯 【靶向解密还原】：净化做完后，把乡村电视的名字完美恢复
    for live in ordered_obj.get("lives", []):
        if live.get("name") == "乡村电视安全防屏蔽占位符":
            live["name"] = "乡村电视 ｜Tg：@huliys9"

    # 🦋 【高级加蝴蝶逻辑】：只加在 sites 里面
    for site in ordered_obj.get("sites", []):
        if "name" in site:
            name_val = site["name"]
            for char in ['丨', '┃', ' ']:
                name_val = name_val.strip(char)
            name_val = re.sub(r'\s+', ' ', name_val)
            if not name_val.startswith("🦋"):
                site["name"] = f"🦋 {name_val}"

    for site in ordered_obj.get("sites", []):
        if "key" in site and site["key"] == "AQY":
            site["name"] = "🦋 爱奇艺｜此接口非原创，合并自海豚佬和鱼佬接口，感谢两位大佬的付出，如有侵权，联系删除｜@huliys9"

    # 写出最终文件文本并做最后微调
    output_json_text = json.dumps(ordered_obj, ensure_ascii=False, indent=4)
    output_json_text = output_json_text.replace('有三级片', 'SP')

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(output_json_text)
        
    with open(tracker_path, 'w', encoding='utf-8') as f:
        f.write(output_filename)
        
    print(f"🎉 【绿色精简防屏蔽纯净版】更新成功！配置名: {output_path}")

except Exception as e:
    print(f"❌ 严重错误：最后的本地过滤渲染失败，原因: {e}")
