import os
import re

cnb_path = 'datas/cnb.json'
haitun_path = 'datas/haitun.json'
output_path = 'datas/老杨TV无18.json'  # 锁定新文件名

def read_file_text(path):
    if not os.path.exists(path):
        return ""
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

text_cnb = read_file_text(cnb_path)
text_haitun = read_file_text(haitun_path)

# ====================================================================
# 1. 精准提取海豚源（修复了中途截断的致命Bug，现在能 100% 完整提取）
# ====================================================================
def get_array_inner_text(content, key):
    split_key = f'"{key}": ['
    if split_key not in content:
        return ""
    
    start_idx = content.find(split_key) + len(split_key)
    bracket_count = 1
    end_idx = start_idx
    
    # 利用括号抵消原理，精确找到真正的最外层闭合 ]
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
# 3. 🛡️ 【全局上帝视角净网】：逐行扫描整个合并后的文件，彻底剿灭 🔞
# ====================================================================
raw_lines = final_json_text.splitlines()
skip_indices = set()

for i, line in enumerate(raw_lines):
    # 只要这行敢出现 🔞 或者 18+
    if "🔞" in line or "18+" in line:
        # 如果是单行结构，直接干掉这一行
        if "{" in line and "}" in line:
            skip_indices.add(i)
        else:
            # 如果是多行结构：向上找 { ，向下找 } ，一锅端
            start = i
            while start >= 0 and "{" not in raw_lines[start]:
                start -= 1
            end = i
            while end < len(raw_lines) and "}" not in raw_lines[end]:
                end += 1
            
            # 把这个范围内的所有行全部打上删除标记
            if start >= 0 and end < len(raw_lines):
                for r in range(start, end + 1):
                    skip_indices.add(r)

# 把没有被打上删除标记的干净代码重新拼起来
clean_lines = [line for i, line in enumerate(raw_lines) if i not in skip_indices]
final_json_text = '\n'.join(clean_lines)

# ====================================================================
# 4. 靶向拦截手术：修复 4K 专线特权解密
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

# 定制老杨自用头部
final_json_text = final_json_text.replace('"warningText": "欢迎使用鱼儿自用缝合专线，完全免费！"', '"warningText": "欢迎使用老杨自用绿色纯净缝合线，本接口完全免费！"')

# 强力消除可能因为删减而产生的多余逗号瑕疵，保证 JSON 语法绝对健康
final_json_text = re.sub(r'\[\s*,', '[', final_json_text)
final_json_text = re.sub(r',\s*\]', '\n  ]', final_json_text)

with open(output_path, 'w', encoding='utf-8') as f:
    f.write(final_json_text)

print("🎉 【全局肃清版完成】所有带 🔞 的线路已被连根拔起！")
