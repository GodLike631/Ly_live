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
# ⏰ 【安全阀门升级：绿色版方案 A 确保 1 号早晚双跑只洗一次牌】
# ====================================================================
today = datetime.datetime.now()
is_reset_day = (today.day == 1)

current_token = ""

if os.path.exists(lock_file_path):
    with open(lock_file_path, 'r', encoding='utf-8') as f:
        current_token = f.read().strip()

if len(current_token) != 3:
    current_token = ""

if is_reset_day and len(current_token) == 3:
    print(f"🔒 【安全阀拦截】今日 1 号已在早晨完成大洗牌，晚上保持原暗号不再重复抽签: {current_token}")
else:
    if is_reset_day or not current_token:
        current_token = ''.join(random.choices(string.ascii_lowercase + string.digits, k=3))
        with open(lock_file_path, 'w', encoding='utf-8') as f:
            f.write(current_token)
        print(f"⏰ 【密锁自动生成】已生成绿色版严格 3 位新密锁: {current_token}")

# 🎯 严格保真绿色版输出配置名[cite: 5]
output_filename = f"老杨TV无18{current_token}.json"
output_path = f"datas/{output_filename}"

# ====================================================================
# 🛡️ 【黑科技：绿色版过期旧线一键调包为纯文字滚动大轰炸】
# ====================================================================
old_configs = glob.glob('datas/老杨TV无18*.json')
for old_file in old_configs:
    if os.path.basename(old_file) != output_filename:
        try:
            # 🌟 彻底抛弃图片链接，无18版群优专属纯文字高能预警盒子[cite: 5]
            trap_json = {
                "spider": "", 
                "notice": "⚠️ 警告：当前“老杨TV”专线密码已过期断流！老链接已彻底作废！\n\n最新密码加QQ群“532637640”获取",
                "warningText": "👑 特别提示：加QQ群“532637640”获取",
                "sites": [
                    {
                        "key": "老杨绿色纯文字提示",
                        "name": "🚨 加QQ群“532637640”获取最新密码",
                        "type": 3,
                        "api": "csp_JuDou",
                        "searchable": 0,
                        "quickSearch": 0,
                        "filterable": 0
                    },
                    {
                        "key": "老杨绿色纯文字提示2",
                        "name": "🚨 不要看这里了 ➡️ 链接已断 ｜ 加QQ群“532637640”获取最新密码",
                        "type": 3,
                        "api": "csp_JuDou",
                        "searchable": 0,
                        "quickSearch": 0,
                        "filterable": 0
                    }
                ],
                "lives": [
                    {
                        "group": "🚨 接口过期断流 ｜ 加QQ群“532637640”获取最新密码",
                        "channels": [
                            {
                                "name": "👉 当前线路已过期 ➡️ 加QQ群“532637640”获取最新密码",
                                "urls": [
                                    "http://127.0.0.1"
                                ]
                            }
                        ]
                    }
                ]
            }
            with open(old_file, 'w', encoding='utf-8') as f:
                json.dump(trap_json, f, ensure_ascii=False, indent=4)
            print(f"📡 【金蝉脱壳】已成功将绿色版过期旧线调包为纯文字大轰炸: {old_file}")
        except Exception as e:
            pass

for garbage in ['datas/local_config.json', *glob.glob('datas/config_*.json')]:
    try: os.remove(garbage)
    except: pass


def read_file_text(path):
    if not os.path.exists(path):
        return ""
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

text_cnb = read_file_text(cnb_path)
text_haitun = read_file_text(haitun_path)

def get_array_inner_text(content, key):
    split_key = f'"{key}": ['
    if split_key not in content:
        return ""
    
    start_idx = content.find(split_key) + len(split_key)
    bracket_count = 1
    end_idx = start_idx
    
    while end_idx < len(content):
        if content[end_idx] == '[':
            bracket_count += 1
        elif content[end_idx] == ']':
            bracket_count -= 1
            if bracket_count == 0:
                break
        end_idx += 1
        
    return content[start_idx:end_idx].strip()

haitun_sites_text = get_array_inner_text(text_haitun, "sites")
haitun_lives_text = get_array_inner_text(text_haitun, "lives")

name_regex = r'"name"\s*:\s*"([^"]+)"'
if haitun_sites_text:
    haitun_sites_text = re.sub(name_regex, r'"name": "\1｜Tg：@huliys9"', haitun_sites_text)
if haitun_lives_text:
    haitun_lives_text = re.sub(name_regex, r'"name": "\1｜Tg：@huliys9"', haitun_lives_text)

# 🚀 【安全补丁】：为了规避下面18净化代码对引流后缀的误杀，这里先用安全密文命名
country_live_dict = {
    "name": "乡村电视安全防屏蔽占位符",
    "type": 0,
    "playerType": 2,
    "ua": "okhttp",
    "url": "https://gh-proxy.com/https://raw.githubusercontent.com/GodLike631/test/refs/heads/main/datas/%E4%B9%A1%E6%9D%91%E7%94%B5%E8%A7%86.txt"
}

# 🔬 【对象级精准排队手术：死死焊接在绿色版 lives 数组的第 6 位】
final_lives_text = ""
if haitun_lives_text:
    try:
        haitun_lives_json = json.loads(f"[{haitun_lives_text}]")
        # 🎯 精准排位：在 Python 数组索引 5 处切入乡村电视
        haitun_lives_json.insert(5, country_live_dict)
        final_lives_text = ",\n    ".join([json.dumps(item, ensure_ascii=False, indent=4) for item in haitun_lives_json])
    except Exception as e:
        final_lives_text = haitun_lives_text

final_json_text = text_cnb

if haitun_sites_text and '"sites": [' in final_json_text:
    haitun_sites_text = haitun_sites_text.rstrip(',')
    final_json_text = final_json_text.replace('"sites": [', f'"sites": [\n    {haitun_sites_text},\n    ', 1)

# 将包含了安全防屏蔽占位符的海豚直播底座灌回大文本里
if final_lives_text and '"lives": [' in final_json_text:
    final_lives_text = final_lives_text.rstrip(',')
    final_json_text = final_json_text.replace('"lives": [', f'"lives": [\n    {final_lives_text},\n    ', 1)

# 🛡️ 绿色版专属核心：全自动全盘物理擦除大底包里的 18 禁不健康元素[cite: 5]
raw_lines = final_json_text.splitlines()
skip_indices = set()

for i, line in enumerate(raw_lines):
    if "🔞" in line or "18+" in line:
        if "{" in line and "}" in line:
            skip_indices.add(i)
        else:
            start = i
            while start >= 0 and "{" not in raw_lines[start]:
                start -= 1
            end = i
            while end < len(raw_lines) and "}" not in raw_lines[end]:
                end += 1
            
            if start >= 0 and end < len(raw_lines):
                for r in range(start, end + 1):
                    skip_indices.add(r)

clean_lines = [line for i, line in enumerate(raw_lines) if i not in skip_indices]
final_json_text = '\n'.join(clean_lines)

# 🎯 【靶向解密还原】：在18级不健康净化手术全部做完后，再把乡村电视的名字完美解密恢复成原貌！
final_json_text = final_json_text.replace("乡村电视安全防屏蔽占位符", "乡村电视 ｜Tg：@huliys9")

final_json_text = final_json_text.replace(
    '"key": "hajim-腾讯备"', 
    '"spider": "./tvbox.jar",\n           "key": "hajim-腾讯备"'
)
final_json_text = final_json_text.replace(
    '"key": "茫茫"', 
    '"spider": "./tvbox.jar",\n        "key": "茫茫"'
)

final_json_text = final_json_text.replace('./spider.jar', 'https://cnb.cool/fish2018/xs/-/git/raw/main/spider.jar')
final_json_text = final_json_text.replace('./XBPQ/', 'https://cnb.cool/fish2018/xs/-/git/raw/main/XBPQ/')
final_json_text = final_json_text.replace('./XYQHiker/', 'https://cnb.cool/fish2018/xs/-/git/raw/main/XYQHiker/')
final_json_text = final_json_text.replace('./js/', 'https://cnb.cool/fish2018/xs/-/git/raw/main/js/')
final_json_text = final_json_text.replace('./json/', 'https://cnb.cool/fish2018/xs/-/git/raw/main/json/')
final_json_text = final_json_text.replace('./py/', 'https://cnb.cool/fish2018/xs/-/git/raw/main/py/')

final_json_text = final_json_text.replace(
    '"logo": "http://127.0.0.1:9978/file/TVBox/logo.png"', 
    '"logo": "https://img.naixiai.cn/2026/06/18/IMG_6638.jpeg"'
)

# ====================================================================
# 🎯 强力拦截注入开机公告[cite: 5]
# ====================================================================
if '"warningText":' not in final_json_text:
    thanks_warning = (
        '👑 特别致谢与版权声明\\n'
        '本接口的诞生离不开大后方几位业内顶流技术大佬的无私奉献，特此致谢：\\n'
        '🐋 感谢鱼佬的付出\\n'
        '源码基础与发布主页: fish2018/webhtv\\n'
        '版本发布绝对地址: fish2018/webhtv/releases\\n'
        'Telegram 官方群组: 👉 https://t.me/webhtv\\n'
        '🐬 感谢海豚佬的付出\\n'
        '核心仓库主页: FGBLH/GHK\\n'
        '数据源直链地址: FGBLH/GHK/海豚.json\\n'
        'Telegram 官方群组: 👉 https://t.me/hshsjk9'
    )
    
    welcome_notice = (
        '👑 欢迎使用【老杨TV粉丝专属绿色纯净线】！'
        '本接口由老杨TV结合海 豚大佬＆鱼佬的优质资源缝合而成，纯净无广告！'
        '🚨 重要提示：本接口密码不定期全自动更换！如果遇到失效或断流，请及时回 Telegram 频道（@huliys9）或微信群获取当前最新密码！'
    )
    
    final_json_text = final_json_text.replace(
        '{\n    "spider":',
        f'{{\n    "notice": "{welcome_notice}",\n    "warningText": "{thanks_warning}",\n    "spider":'
    )

final_json_text = final_json_text.replace('🐬', '')
final_json_text = final_json_text.replace('海豚影视', '')
final_json_text = final_json_text.replace('海豚', '')
final_json_text = final_json_text.replace('完全免费，如有收费的都是骗子', '')
final_json_text = final_json_text.replace('交流群 TG：@hshsjk9', '')

def clean_and_add_butterfly(match):
    name_val = match.group(1)
    tg_suffix = ""
    if "｜Tg：@huliys9" in name_val:
        name_val = name_val.replace("｜Tg：@huliys9", "")
        tg_suffix = "｜Tg：@huliys9"
        
    for char in ['丨', '┃', ' ']:
        name_val = name_val.strip(char)
        
    name_val = re.sub(r'\s+', ' ', name_val)
    return f'"name": "🦋 {name_val}{tg_suffix}"'

# 🚀 【核心性能调优：直播间安全隔离壁垒】
# 只对前半段 sites（点播组）进行加蝴蝶与空气动力学规范化包装。
# 后半段 lives 内部所有的具体节目清单 100% 保持纯净明文状态，保障国内老电视盒子加载秒开、决不卡死！
if '"sites": [' in final_json_text and '"lives": [' in final_json_text:
    parts = final_json_text.split('"lives": [', 1)
    parts[0] = re.sub(r'"name"\s*:\s*"([^"]+)"', clean_and_add_butterfly, parts[0])
    final_json_text = '"lives": ['.join(parts)
else:
    final_json_text = re.sub(r'"name"\s*:\s*"([^"]+)"', clean_and_add_butterfly, final_json_text)

final_json_text = final_json_text.replace(
    '"name": "🦋 爱奇艺｜Tg：@huliys9"',
    '"name": "🦋 爱奇艺｜此接口非原创，合并自海豚佬和鱼佬接口，感谢两位大佬的付出，如有侵权，联系删除｜@huliys9"'
)

final_json_text = final_json_text.replace('有三级片', 'SP')

final_json_text = final_json_text.replace('[\n    ,', '[')
final_json_text = final_json_text.replace('[\n,', '[')
final_json_text = final_json_text.replace(',\n    ]', '\n    ]')
final_json_text = final_json_text.replace(',\n  ]', '\n  ]')
final_json_text = re.sub(r'\[\s*,', '[', final_json_text)
final_json_text = re.sub(r',\s*\]', '\n  ]', final_json_text)

with open(output_path, 'w', encoding='utf-8') as f:
    f.write(final_json_text)

with open(tracker_path, 'w', encoding='utf-8') as f:
    f.write(output_filename)

print(f"🎉 【绿色精简防屏蔽终极版】更新成功！配置名: {output_path}")
