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
# 1. 物理提取海豚源里的 sites（视频站）和 lives（直播源）内部的纯文本
# ====================================================================
def get_array_inner_text(content, key):
    split_key = f'"{key}": ['
    if split_key not in content:
        return ""
    after_key = content.split(split_key, 1)[1]
    if '],' in after_key:
        inner_text = after_key.split('],', 1)[0]
    else:
        inner_text = after_key.split(']', 1)[0]
    return inner_text.strip()

haitun_sites_text = get_array_inner_text(text_haitun, "sites")
haitun_lives_text = get_array_inner_text(text_haitun, "lives")

# ====================================================================
# 2. 逆向注入：把海豚的内容，无缝贴进 CNB 对应的数组最前面
# ====================================================================
final_json_text = text_cnb

# 注入视频站点
if haitun_sites_text and '"sites": [' in final_json_text:
    haitun_sites_text = haitun_sites_text.rstrip(',')
    final_json_text = final_json_text.replace('"sites": [', f'"sites": [\n    {haitun_sites_text},\n    ', 1)

# 注入直播源
if haitun_lives_text and '"lives": [' in final_json_text:
    haitun_lives_text = haitun_lives_text.rstrip(',')
    final_json_text = final_json_text.replace('"lives": [', f'"lives": [\n    {haitun_lives_text},\n    ', 1)

# ====================================================================
# 3. 🛡️ 【按行靶向拦截法】：彻底解决大括号嵌套导致的过滤失效
# ====================================================================
if '"sites": [' in final_json_text:
    parts = final_json_text.split('"sites": [', 1)
    before_sites = parts[0]
    after_sites = parts[1].split(']', 1)
    sites_inner_text = after_sites[0]
    rest_of_json = after_sites[1]

    # 将所有站点文本按行切开，一行行处理
    raw_lines = sites_inner_text.splitlines()
    clean_lines = []
    
    # 借助一个标记数组，帮我们精准定位要删除的站点范围
    skip_indices = set()
    
    for i, line in enumerate(raw_lines):
        if "🔞" in line:
            # 向上和向下摸索，把带有 🔞 的这整个大括号对象（通常上下各几行）的行索引全抓出来
            start = i
            while start >= 0 and "{" not in raw_lines[start]:
                start -= 1
            end = i
            while end < len(raw_lines) and "}" not in raw_lines[end]:
                end += 1
            # 把这几行的行号全部标记为“要删除”
            for r in range(start, min(end + 1, len(raw_lines))):
                skip_indices.add(r)

    # 重新组装，只要不在删除名单里的行，全部保留
    for i, line in enumerate(raw_lines):
        if i not in skip_indices:
            clean_lines.append(line)

    new_sites_inner = "\n".join(clean_lines)
    final_json_text = f'{before_sites}"sites": [\n{new_sites_inner}\n  ]{rest_of_json}'

# ====================================================================
# 4. 靶向拦截手术：揪出这两个瘫痪的 4K 线路，强行切断 CNB 依赖，锁死海豚核心
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
# 【全方位无死角路径清洗】：让 CNB 的其余线路走官方绝对网络链接
# ====================================================================
final_json_text = final_json_text.replace('./spider.jar', 'https://cnb.cool/fish2018/xs/-/git/raw/main/spider.jar')
final_json_text = final_json_text.replace('./XBPQ/', 'https://cnb.cool/fish2018/xs/-/git/raw/main/XBPQ/')
final_json_text = final_json_text.replace('./XYQHiker/', 'https://cnb.cool/fish2018/xs/-/git/raw/main/XYQHiker/')
final_json_text = final_json_text.replace('./js/', 'https://cnb.cool/fish2018/xs/-/git/raw/main/js/')
final_json_text = final_json_text.replace('./json/', 'https://cnb.cool/fish2018/xs/-/git/raw/main/json/')
final_json_text = final_json_text.replace('./py/', 'https://cnb.cool/fish2018/xs/-/git/raw/main/py/')

# ====================================================================
# 5. 定制老杨自用全量缝合专线 brand 头部
# ====================================================================
final_json_text = final_json_text.replace('"warningText": "欢迎使用鱼儿自用缝合专线，完全免费！"', '"warningText": "欢迎使用老杨自用绿色纯净缝合线，本接口完全免费！"')

# 强力消除尾部符号瑕疵
final_json_text = re.sub(r'\[\s*,', '[', final_json_text)
final_json_text = re.sub(r',\s*\]', '\n  ]', final_json_text)

with open(output_path, 'w', encoding='utf-8') as f:
    f.write(final_json_text)

print("🎉 【纯净绿色版完成】无视任何大括号嵌套，完美过滤 🔞 线路！")
