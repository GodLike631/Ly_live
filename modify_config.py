import os
import re
import random
import string
import glob
import datetime

cnb_path = 'datas/cnb.json'
haitun_path = 'datas/haitun.json'

# 控制开关和追踪器的文件路径
lock_file_path = 'datas/控制开关.txt'
tracker_path = 'datas/最新接口文件名.txt'

# ====================================================================
# ⏰ 【方案 A 定时自动脱壳机制：老杨TV无18 + 严格 3 位随机字符定制版】
# ====================================================================
today = datetime.datetime.now()
is_reset_day = (today.day == 1)  # 🌟 默认每月 1 号全自动定时洗牌

current_token = ""

# 1. 优先读取现有的控制开关
if os.path.exists(lock_file_path):
    with open(lock_file_path, 'r', encoding='utf-8') as f:
        current_token = f.read().strip()

# 🌟【核心纠偏】：如果发现旧暗号长度不是严格的 3 位，强行作废重抽
if len(current_token) != 3:
    current_token = ""

# 2. 如果今天是一号，或者暗号为空/不合规，立刻启动 3 位随机数抽签
if is_reset_day or not current_token:
    current_token = ''.join(random.choices(string.ascii_lowercase + string.digits, k=3))
    with open(lock_file_path, 'w', encoding='utf-8') as f:
        f.write(current_token)
    print(f"⏰ 【密锁自动生成】当前绿色版已锁定 3 位新密锁: {current_token}")

# 👑 严格按照老杨的要求：固定的品牌前缀 + 3位乱码尾缀
output_filename = f"老杨TV无18{current_token}.json"
output_path = f"datas/{output_filename}"

# ====================================================================
# 🛡️ 【斩草除根：旧线及历史垃圾自动物理清除雷达】
# ====================================================================
old_configs = glob.glob('datas/老杨TV无18*.json')
for old_file in old_configs:
    if os.path.basename(old_file) != output_filename:
        try:
            os.remove(old_file)
            print(f"🗑️ 【物理强擦】已成功抹除绿色版过期旧线: {old_file}")
        except Exception as e:
            pass

# 顺手全面清理历史可能遗留的 config_ 开头或 local_config 垃圾
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

# ====================================================================
# 1. 精准提取海豚源（利用括号抵消原理，100% 完整提取不截断）
# ====================================================================
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

# ====================================================================
# 【海豚专属尾缀手术】在合并前，单独为海豚的线路名称末尾加上 ｜Tg：@huliys9
# ====================================================================
name_regex = r'"name"\s*:\s*"([^"]+)"'
if haitun_sites_text:
    haitun_sites_text = re.sub(name_regex, r'"name": "\1｜Tg：@huliys9"', haitun_sites_text)
if haitun_lives_text:
    haitun_lives_text = re.sub(name_regex, r'"name": "\1｜Tg：@huliys9"', haitun_lives_text)

# ====================================================================
# 2. 逆向无缝注入
# ====================================================================
final_json_text = text_cnb

if haitun_sites_text and '"sites": [' in final_json_text:
    haitun_sites_text = haitun_sites_text.rstrip(',')
    final_json_text = final_json_text.replace('"sites": [', f'"sites": [\n    {haitun_sites_text},\n    ', 1)

if haitun_lives_text and '"lives": [' in final_json_text:
    haitun_lives_text = haitun_lives_text.rstrip(',')
    final_json_text = final_json_text.replace('"lives": [', f'"lives": [\n    {haitun_lives_text},\n    ', 1)

# ====================================================================
# 3. 🛡️ 【全局上帝视角净网】：逐行扫描整个合并后的文件，彻底剿灭 🔞 和 18+
# ====================================================================
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

# ====================================================================
# 4. 靶向拦截手术：修复 4K 专线特权解密依赖
# ====================================================================
final_json_text = final_json_text.replace(
    '"key": "hajim-腾讯备"', 
    '"spider": "./tvbox.jar",\n           "key": "hajim-腾讯备"'
)
final_json_text = final_json_text.replace(
    '"key": "茫茫"', 
    '"spider": "./tvbox.jar",\n        "key": "茫茫"'
)

# ====================================================================
# 5. 全方位无死角路径清洗
# ====================================================================
final_json_text = final_json_text.replace('./spider.jar', 'https://cnb.cool/fish2018/xs/-/git/raw/main/spider.jar')
final_json_text = final_json_text.replace('./XBPQ/', 'https://cnb.cool/fish2018/xs/-/git/raw/main/XBPQ/')
final_json_text = final_json_text.replace('./XYQHiker/', 'https://cnb.cool/fish2018/xs/-/git/raw/main/XYQHiker/')
final_json_text = final_json_text.replace('./js/', 'https://cnb.cool/fish2018/xs/-/git/raw/main/js/')
final_json_text = final_json_text.replace('./json/', 'https://cnb.cool/fish2018/xs/-/git/raw/main/json/')
final_json_text = final_json_text.replace('./py/', 'https://cnb.cool/fish2018/xs/-/git/raw/main/py/')

# ====================================================================
# 6. 定制老杨自用全量缝合专线 brand 头部
# ====================================================================
final_json_text = final_json_text.replace(
    '"logo": "http://127.0.0.1:9978/file/TVBox/logo.png"', 
    '"logo": "https://img.naixiai.cn/2026/06/18/IMG_6638.jpeg"'
)

if '"warningText":' not in final_json_text:
    thanks_warning = (
        '👑 特别致谢与版权声明\\n'
        '本接口的诞生离不开大后方两位业内顶流技术大佬的无私奉献，特此致谢：\\n'
        '🐋 感谢鱼佬的付出\\n'
        '源码基础与发布主页: fish2018/webhtv\\n'
        '版本发布绝对地址: fish2018/webhtv/releases\\n'
        'Telegram 官方群组: 👉 https://t.me/webhtv\\n'
        '🐬 感谢海豚佬的付出\\n'
        '核心仓库主页: FGBLH/GHK\\n'
        '数据源直链地址: FGBLH/GHK/海豚.json\\n'
        'Telegram 官方群组: 👉 https://t.me/hshsjk9'
    )
    final_json_text = final_json_text.replace(
        '{\n    "spider":',
        f'{{\n    "warningText": "{thanks_warning}",\n    "spider":'
    )

# ====================================================================
# 7. 全方位名称大清洗与品牌脱敏手术
# ====================================================================
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
    return f'"name": "🦋{name_val}{tg_suffix}"'

final_json_text = re.sub(r'"name"\s*:\s*"([^"]+)"', clean_and_add_butterfly, final_json_text)

final_json_text = final_json_text.replace(
    '"name": "🦋爱奇艺｜Tg：@huliys9"',
    '"name": "🦋爱奇艺｜此接口非原创，合并自海豚佬和鱼佬接口，感谢两位大佬的付出，如有侵权，联系删除｜@huliys9"'
)

# ====================================================================
# 8. 安全、高效地消除尾部及多余逗号瑕疵
# ====================================================================
final_json_text = final_json_text.replace('[\n    ,', '[')
final_json_text = final_json_text.replace('[\n,', '[')
final_json_text = final_json_text.replace(',\n    ]', '\n    ]')
final_json_text = final_json_text.replace(',\n  ]', '\n  ]')
final_json_text = re.sub(r'\[\s*,', '[', final_json_text)
final_json_text = re.sub(r',\s*\]', '\n  ]', final_json_text)

# 写入带有品牌特征的乱码绿色版文件
with open(output_path, 'w', encoding='utf-8') as f:
    f.write(final_json_text)

# 登记在追踪器里
with open(tracker_path, 'w', encoding='utf-8') as f:
    f.write(output_filename)

print(f"🎉 【老杨TV无18纯净版】同步成功！当前出库配置名: {output_path}")
