# -*- coding: utf-8 -*-
"""
核心自动编译流主程序 (广告强力清洗修正版)
"""
import re
import os
import sys
import json
import time
import random
import string
import copy
import datetime
import logging
from pathlib import Path
from Crypto.Cipher import AES

# 引入优化请求库
import requests
from requests.adapters import HTTPAdapter
from urllib3.util import Retry

# 引入独立配置文件
import config

# ====================================================================
# 🎛️ 【高可用场景色彩日志控制中心】
# ====================================================================
class CustomFormatter(logging.Formatter):
    green = "\033[92m"
    cyan = "\033[96m"
    yellow = "\033[93m"
    red = "\033[91m"
    magenta = "\033[95m"
    reset = "\033[0m"
    base_fmt = "%(asctime)s [%(levelname)s] %(message)s"
    FORMATS = {
        logging.DEBUG: cyan + base_fmt + reset,
        logging.INFO: green + base_fmt + reset,
        logging.WARNING: yellow + base_fmt + reset,
        logging.ERROR: red + base_fmt + reset,
        logging.CRITICAL: magenta + base_fmt + reset
    }
    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno, self.base_fmt)
        formatter = logging.Formatter(log_fmt, datefmt='%Y-%m-%d %H:%M:%S')
        return formatter.format(record)

_logger = logging.getLogger("CompilerEngine")
_logger.setLevel(logging.DEBUG)
_logger.handlers.clear()
stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setFormatter(CustomFormatter())
_logger.addHandler(stream_handler)

def log_info(msg): _logger.info(msg)
def log_warning(msg): _logger.warning(msg)
def log_error(msg, exc_info=False): _logger.error(msg, exc_info=exc_info)
def log_critical(msg, exc_info=False): _logger.critical(msg, exc_info=exc_info)
def log_success(msg): _logger.info(f"✨ [SUCCESS] {msg}")
def log_network(msg): _logger.info(f"🌐 [NETWORK] {msg}")
def log_diff(msg):    _logger.info(f"📊 [DIFF_DET] {msg}")

# ====================================================================
# 📡 【统一网络环境初始化与高可用 Session 连接池】
# ====================================================================
HTTP_SESSION = requests.Session()
retries = Retry(total=3, backoff_factor=0.5, status_forcelist=[500, 502, 503, 504])
HTTP_SESSION.mount("http://", HTTPAdapter(max_retries=retries))
HTTP_SESSION.mount("https://", HTTPAdapter(max_retries=retries))

def send_telegram_request(token, chat_id, text):
    """使用统一 Session 高效下发 Telegram 通知"""
    if not token or not chat_id:
        log_warning("缺失 TG_TOKEN 或 TG_CHAT_ID，跳过发送 TG 通知。")
        return False
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {"chat_id": chat_id, "parse_mode": "Markdown", "text": text}
    try:
        log_network("正在向 TG 频道下发矩阵编译快报...")
        res = HTTP_SESSION.post(url, json=payload, timeout=config.TG_TIMEOUT)
        if res.status_code == 200:
            log_success("Telegram 通知在独立连接池中直发成功！")
            return True
        else:
            log_error(f"TG 接口响应异常: 状态码 {res.status_code}，死因: {res.text}")
    except Exception as e:
        log_error(f"Telegram 网络总线请求崩溃: {e}")
    return False
def decrypt_haitun_bytes(raw_bytes: bytes) -> dict:
    """
    海豚/三方加密底包解密与节点提纯引擎
    """
    try:
        # 1. 兼容 Hex 字符串转 Raw Bytes
        try:
            hex_str = raw_bytes.decode('utf-8', errors='ignore').strip()
            if all(c in "0123456789abcdefABCDEF" for c in hex_str[:40]):
                raw_bytes = bytes.fromhex(hex_str)
        except Exception:
            pass

        # 2. 截取 $# ... #$ 魔数与动态 Key
        start_idx = raw_bytes.find(b"$#")
        end_idx = raw_bytes.find(b"#$", start_idx + 2)
        
        if start_idx == -1 or end_idx == -1:
            return {}

        key_bytes = raw_bytes[start_idx + 2 : end_idx]
        payload_bytes = raw_bytes[end_idx + 2 :]

        # 3. 构造 16 字节 Key 与 IV ('0' 字符右侧补齐)
        key_16 = key_bytes.ljust(16, b'0')
        aligned_len = (len(payload_bytes) // 16) * 16
        aes_payload = payload_bytes[:aligned_len]

        # 4. 执行 AES-128-CBC 解密
        cipher = AES.new(key_16, AES.MODE_CBC, iv=key_16)
        decrypted_bytes = cipher.decrypt(aes_payload)

        # 5. 剥离 PKCS7 填充
        if decrypted_bytes:
            pad_len = decrypted_bytes[-1]
            if 1 <= pad_len <= 16:
                decrypted_bytes = decrypted_bytes[:-pad_len]

        text = decrypted_bytes.decode('utf-8', errors='ignore').strip()
        
        # 6. 精确定位 "logo" / "wallpaper" / "sites" 的起点，抛弃头部废料
        pos = -1
        for tag in ['"logo"', '"wallpaper"', '"sites"']:
            p = text.find(tag)
            if p != -1:
                if pos == -1 or p < pos:
                    pos = p

        if pos != -1:
            clean_json_str = "{\n    " + text[pos:]
        else:
            clean_json_str = text

        json_end = clean_json_str.rfind('}')
        if json_end != -1:
            clean_json_str = clean_json_str[:json_end + 1]

        # 7. 解析 JSON (支持容错降级)
        try:
            return json.loads(clean_json_str, strict=False)
        except Exception:
            clean_json_str = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', clean_json_str)
            return json.loads(clean_json_str, strict=False)

    except Exception as e:
        log_warning(f"解密上游底包失败: {e}")

    return {}
# ====================================================================
# 🛡️ 【智能容灾本地 JSON 安全加载模块】
# ====================================================================
def load_json_safe(file_path: Path) -> dict:
    """底包安全过滤器、自动解密与历史恢复引擎"""
    backup_path = file_path.parent / f"{file_path.stem}_backup{file_path.suffix}"
    current_data = None
    is_current_valid = False

    if file_path.exists():
        try:
            # 必须注意缩进！try: 内部必须缩进 4 个空格
            raw_bytes = file_path.read_bytes()
            try:
                # 1. 优先尝试按普通明文 JSON 读取
                current_data = json.loads(raw_bytes.decode('utf-8', errors='ignore'))
            except Exception:
                # 2. 若不是标准 JSON，调用解密引擎进行解密与提纯
                log_info(f"检测到底包 {file_path.name} 被加密，启动解密提纯引擎...")
                current_data = decrypt_haitun_bytes(raw_bytes)

            if isinstance(current_data, dict) and ("sites" in current_data or "lives" in current_data or "parses" in current_data):
                is_current_valid = True
            else:
                log_warning(f"底包 {file_path.name} 根节点不合规，标记为损坏源。")
        except Exception as e:
            log_warning(f"底包 {file_path.name} 读取/解密过程崩溃: {e}")

    if is_current_valid:
        try:
            backup_path.write_text(json.dumps(current_data, ensure_ascii=False, indent=4), encoding='utf-8')
            log_info(f"底包 {file_path.name} 安全复核通过，增量同步到本地备份链中。")
        except Exception as e:
            log_error(f"本地同步备份链写入失败: {e}")
        return current_data
    else:
        log_critical(f"上游数据源 {file_path.name} 彻底断流！启动自动化容灾降级...")
        if backup_path.exists():
            try:
                backup_data = json.loads(backup_path.read_text(encoding='utf-8'))
                log_success(f"容灾降级成功！已从历史干净数据中提取并重构底包: {backup_path.name}")
                file_path.write_text(json.dumps(backup_data, ensure_ascii=False, indent=4), encoding='utf-8')
                return backup_data
            except Exception:
                log_critical(f"致命灾难：本地老本数据 {backup_path.name} 也意外遭到物理损坏！")
        else:
            log_critical(f"致命灾难：本地库中未检索到任何备份副本 {backup_path.name}！")
        return {}
# ====================================================================
# ⏰ 【每月 1 号随机抽取双换锁日期（含跨月间隔>=10天安全防护）】
# ====================================================================
def generate_two_random_days(days_in_month, min_first_day=1):
    """
    在当月天数中，随机抽取两个间隔 >= 14 天的日期号。
    :param min_first_day: 第一个换锁日的最小允许日期（用于防止跨月换锁过于频繁）
    """
    valid_pairs = []
    start_day = max(1, min_first_day)
    
    for d1 in range(start_day, days_in_month + 1):
        for d2 in range(d1 + 14, days_in_month + 1):
            valid_pairs.append((d1, d2))
    
    # 如果受限于 min_first_day 导致无法抽取，保底降级选 11 和 25
    if not valid_pairs:
        return 11, min(25, days_in_month)
    
    return random.choice(valid_pairs)

def manage_monthly_token():
    """管理硬核密码生存控制中枢（严格北京时间，每月1号随机抽取两次换锁日期，含跨月防频繁换锁保护）"""
    # 🎯 1. 强制统一为北京时间 (UTC+8)
    tz_bj = datetime.timezone(datetime.timedelta(hours=8))
    now_bj = datetime.datetime.now(tz_bj)
    
    current_ym = now_bj.strftime("%Y%m")       # 如 '202609'
    current_date = now_bj.strftime("%Y%m%d")   # 如 '20260901'
    today_dt = now_bj.date()
    today_day = now_bj.day                     # 今天是当月第几天 (int)
    
    # 获取当月总天数
    if now_bj.month == 12:
        next_month_first = datetime.datetime(now_bj.year + 1, 1, 1, tzinfo=tz_bj)
    else:
        next_month_first = datetime.datetime(now_bj.year, now_bj.month + 1, 1, tzinfo=tz_bj)
    days_in_month = (next_month_first - datetime.datetime(now_bj.year, now_bj.month, 1, tzinfo=tz_bj)).days

    saved_ym = ""
    saved_count = 0
    day_a, day_b = 0, 0
    saved_last_date = ""
    saved_code = ""
    
    is_new_token_generated = False

    # 🎯 2. 解析本地存储记录 (datas/控制开关.txt)
    # 标准格式: YYYYMM-count-dayA-dayB-lastDate-code (例如: 202608-2-01-29-20260829-a1b)
    if config.LOCK_FILE_PATH.exists():
        content = config.LOCK_FILE_PATH.read_text(encoding='utf-8').strip()
        parts = content.split("-")
        
        if len(parts) == 6:
            saved_ym, saved_count_str, da_str, db_str, saved_last_date, saved_code = parts
            saved_count = int(saved_count_str) if saved_count_str.isdigit() else 0
            day_a = int(da_str) if da_str.isdigit() else 0
            day_b = int(db_str) if db_str.isdigit() else 0
        elif len(parts) == 2:
            saved_code = parts[1]
        else:
            saved_code = content

    # 🎯 3. 跨月检测与当月随机日期生成 (含跨月安全间隔 >= 10 天防频繁机制)
    if saved_ym != current_ym or day_a == 0 or day_b == 0:
        min_first_day = 1

        # 计算距离【上一次换锁】过去了多少天
        if saved_last_date:
            try:
                last_date_dt = datetime.datetime.strptime(saved_last_date, "%Y%m%d").date()
                days_since_last_change = (today_dt - last_date_dt).days
                
                # 🛡️ 跨月安全防护：如果距离上次换锁不足 10 天，推迟当月的第一个换锁日
                if days_since_last_change < 10:
                    needed_delay = 10 - days_since_last_change
                    min_first_day = today_day + needed_delay  # 强制第一个换锁日不能早于 min_first_day
                    log_warning(f"🛡️ 触发跨月保护！上月最后一次换锁是在 {saved_last_date}（仅隔 {days_since_last_change} 天），本月第一个换锁日将不早于 {min_first_day}号！")
            except Exception as e:
                log_error(f"解析上次换锁日期失败: {e}")

        # 🛡️ 特殊过渡保护（针对首日上线）：如果是上线当天且之前已有旧密码
        if today_day == 1 and saved_code and saved_ym == "":
            day_a = 1
            day_b = random.randint(15, days_in_month)
            saved_count = 1
            saved_last_date = current_date
            log_success(f"🛡️ 启动首日上线过渡保护！1号已计为第1次换锁，本月第2次换锁排班在: {day_b}号")
        else:
            # 根据安全最小起始日，随机抽取 DayA 和 DayB
            day_a, day_b = generate_two_random_days(days_in_month, min_first_day=min_first_day)
            saved_count = 0
            log_success(f"🎲 每月1号随机抽签完成！本月【北京时间】两次换锁排班日期为: {day_a}号 和 {day_b}号 (间隔 {day_b - day_a} 天)")
        
        saved_ym = current_ym

    # 🎯 4. 判定今天是否需要自动换锁
    should_reset = False
    new_count = saved_count

    if saved_last_date != current_date:
        if today_day == day_a and saved_count < 1:
            should_reset = True
            new_count = 1
            log_info(f"⏰ 命中当月第 1 次随机换锁日 ({day_a}号)！")
        elif today_day == day_b and saved_count < 2:
            should_reset = True
            new_count = 2
            log_info(f"⏰ 命中当月第 2 次随机换锁日 ({day_b}号)！")

    # 🎯 5. 执行换锁与写回控制文件
    if should_reset:
        current_token = ''.join(random.choices(string.ascii_lowercase + string.digits, k=config.TOKEN_LENGTH))
        lock_str = f"{current_ym}-{new_count}-{day_a:02d}-{day_b:02d}-{current_date}-{current_token}"
        config.LOCK_FILE_PATH.write_text(lock_str, encoding='utf-8')
        log_success(f"🔑 自动更换新密锁成功 (本月第{new_count}次更换)！新密锁为: {current_token}")
        is_new_token_generated = True
    else:
        if not saved_code or len(saved_code) != config.TOKEN_LENGTH:
            current_token = ''.join(random.choices(string.ascii_lowercase + string.digits, k=config.TOKEN_LENGTH))
            saved_last_date = current_date
        else:
            current_token = saved_code

        lock_str = f"{current_ym}-{saved_count}-{day_a:02d}-{day_b:02d}-{saved_last_date or current_date}-{current_token}"
        config.LOCK_FILE_PATH.write_text(lock_str, encoding='utf-8')

    # 🎯 6. 生成对应的输出文件名
    if current_token in ["全量版", "纯净版"]:
        full_output_filename = f"{config.BASE_OUTPUT_FULL}.json"
        clean_output_filename = f"{config.BASE_OUTPUT_CLEAN}.json"
    else:
        full_output_filename = f"{config.BASE_OUTPUT_FULL}{current_token}.json"
        clean_output_filename = f"{config.BASE_OUTPUT_CLEAN}{current_token}.json"

    return current_token, full_output_filename, clean_output_filename, is_new_token_generated
# ====================================================================
# 🛡️ 【过期接口金蝉脱壳爆破模块】
# ====================================================================
def execute_trap_boom(full_output_filename, clean_output_filename):
    """金蝉脱壳：全自动过期大轰炸覆盖机制"""
    if not config.DATA_DIR.exists():
        config.DATA_DIR.mkdir(parents=True, exist_ok=True)
        
    old_configs = list(config.DATA_DIR.glob(f'{config.BASE_OUTPUT_FULL}*.json')) + \
                  list(config.DATA_DIR.glob(f'{config.BASE_OUTPUT_CLEAN}*.json')) + \
                  list(config.DATA_DIR.glob('老杨TV*.json')) + \
                  list(config.DATA_DIR.glob('蝴蝶影视*.json'))

    for old_file in old_configs:
        if old_file.name != full_output_filename and old_file.name != clean_output_filename:
            try:
                trap_json = {
                    "spider": "", 
                    "notice": config.TRAP_NOTICE_TEXT,
                    "sites": [
                        {"key": "提示", "name": config.TRAP_SITE_NAME_1, "type": 3, "api": "csp_JuDou", "searchable": 0, "quickSearch": 0, "filterable": 0},
                        {"key": "提示2", "name": config.TRAP_SITE_NAME_2, "type": 3, "api": "csp_JuDou", "searchable": 0, "quickSearch": 0, "filterable": 0}
                    ],
                    "lives": [
                        {"group": config.TRAP_LIVE_GROUP, "channels": [{"name": config.TRAP_LIVE_CHANNEL, "urls": ["http://127.0.0.1"]}]}
                    ]
                }
                old_file.write_text(json.dumps(trap_json, ensure_ascii=False, indent=4), encoding='utf-8')
            except Exception:
                pass

    for garbage in config.DATA_DIR.glob('config_*.json'):
        try: garbage.unlink()
        except Exception: pass

# ====================================================================
# ⚙️ 【核心业务：对象级链式清洗与归类编译引擎】
# ====================================================================
def object_level_wash_and_compile():
    """100%纯内存对象流操作，杜绝二次重载"""
    # 🎯 1. 实时获取最新的过滤与清洗规则
    block_keywords = config.get_block_keywords()
    upstream_dirty_words = config.get_upstream_dirty_words()
    block_malicious_keywords = config.get_block_malicious_keywords()

    # 🎯 2. 加载四个底包 JSON
    json_cnb = load_json_safe(config.CNB_PATH)
    json_haitun = load_json_safe(config.HAITUN_PATH)
    json_lz = load_json_safe(config.LZ_PATH)
    json_dol2 = load_json_safe(config.dol2_PATH)

    # 🎯 3. 提前提取所有底包的 sites 和 lives 变量（确保在组合前全部定义完）
    cnb_sites = json_cnb.get("sites", [])
    cnb_lives = json_cnb.get("lives", [])

    haitun_sites = json_haitun.get("sites", [])
    haitun_lives = json_haitun.get("lives", [])

    lz_sites = json_lz.get("sites", [])

    dol2_sites = json_dol2.get("sites", [])
    dol2_lives = json_dol2.get("lives", [])

    # 处理 LZ 底包中的 NSFW 属性与 API 路径映射
    lz_nsfw_list = []
    for item in lz_sites:
        site_name = item.get("name", "")
        if "🔞" in site_name:
            item["name"] = f"{site_name.replace('🔞', '').strip()}｜🔞"
            api_str = item.get("api", "")
            if isinstance(api_str, str) and api_str.startswith("./"):
                if api_str.startswith("./py/"):
                    item["api"] = api_str.replace("./py/", "https://gh-proxy.com/https://raw.githubusercontent.com/ediart/tvbox/refs/heads/main/lz/py/")
                elif api_str.startswith("./js/"):
                    item["api"] = api_str.replace("./js/", "https://gh-proxy.com/https://raw.githubusercontent.com/ediart/tvbox/refs/heads/main/lz/js/")
                else:
                    item["api"] = api_str.replace("./", "https://gh-proxy.com/https://raw.githubusercontent.com/ediart/tvbox/refs/heads/main/lz/")
            lz_nsfw_list.append(item)

    # 🎯 4. 【全量物理清洗】：对所有上游点播源与直播源执行统一广告词清洗（拔除 🐬 等字符）
    all_raw_sites = haitun_sites + lz_nsfw_list + cnb_sites + dol2_sites
    for item in all_raw_sites:
        if "name" in item and isinstance(item["name"], str):
            for dirty in upstream_dirty_words:
                item["name"] = item["name"].replace(dirty, "")

    all_raw_lives = haitun_lives + cnb_lives + dol2_lives
    for item in all_raw_lives:
        if "name" in item and isinstance(item["name"], str):
            for dirty in upstream_dirty_words:
                item["name"] = item["name"].replace(dirty, "")

    # 合并并去重 parses 解析列表
    combined_parses = json_haitun.get("parses", []) + json_lz.get("parses", []) + json_cnb.get("parses", []) + json_dol2.get("parses", [])
    unique_parses = []
    seen_parse_names = set()
    for p in combined_parses:
        p_name = p.get("name", "")
        if p_name and p_name not in seen_parse_names:
            unique_parses.append(p)
            seen_parse_names.add(p_name)

    custom_keys = {site.get("key") for site in config.MY_CUSTOM_SITES if site.get("key")}
    clean_upstream_sites = [site for site in all_raw_sites if site.get("key") not in custom_keys]

    compiled_sites = []
    tg_tail_count = 0

    # 🎯 5. 逐个站点二次清洗与格式校验
    for site in clean_upstream_sites:
        name = site.get("name", "")
        if any(kw in name for kw in block_keywords) or any(mkw in name for mkw in block_malicious_keywords):
            continue

        for char in ['丨', '┃', ' ']: name = name.strip(char)
        name = re.sub(r'\s+', ' ', name)
        if config.MY_TG_SUFFIX in name:
            tg_tail_count += 1
            if tg_tail_count > 5: name = name.replace(config.MY_TG_SUFFIX, "").strip()

        if not name.startswith(config.LOGO_PREFIX):
            name = f"{config.LOGO_PREFIX} {name}"

        for src_word, dst_word in config.MY_NAME_REPLACEMENTS.items():
            name = name.replace(src_word, dst_word)

        site["name"] = name

        # 路径清洗补丁
        api_field = site.get("api", "")
        if isinstance(api_field, str):
            for pattern, target in config.PATH_REPLACEMENTS.items():
                api_field = re.sub(pattern, target, api_field)
            site["api"] = api_field

        ext_field = site.get("ext", "")
        if isinstance(ext_field, str):
            for pattern, target in config.PATH_REPLACEMENTS.items():
                ext_field = re.sub(pattern, target, ext_field)
            site["ext"] = ext_field
        elif isinstance(ext_field, dict):
            try:
                ext_str = json.dumps(ext_field, ensure_ascii=False)
                for pattern, target in config.PATH_REPLACEMENTS.items():
                    ext_str = re.sub(pattern, target, ext_str)
                site["ext"] = json.loads(ext_str)
            except Exception:
                pass

        if "PanWebShare" in site.get("api", ""):
            site["api"] = "csp_PanWebShare"
            site["changeable"] = 1
            if "jar" in site: site.pop("jar")

        if site.get("ext") == {}: site["ext"] = ""
        compiled_sites.append(site)

    # 动态加载分类规则定义
    category_rules = getattr(config, "CATEGORY_RULES", {})
    bucket_map = {category: [] for category in category_rules.keys()}
    bucket_map["综合"] = []
    bucket_map["福利"] = []

    no_search_kw = getattr(config, "NO_SEARCH_KEYWORDS", [])
    no_search_keys = getattr(config, "NO_SEARCH_KEYS", [])
    no_quick_keys = getattr(config, "NO_QUICK_SEARCH_KEYS", [])

    hot_video_site = None  # 用于单独提取置顶热门站

    for site in compiled_sites:
        s_key = site.get("key", "")
        s_name = site.get("name", "")

        # 自动化搜索控制打标
        if any(kw in s_name for kw in no_search_kw) or (s_key in no_search_keys):
            site["searchable"] = 0
            
        if s_key in no_quick_keys:
            site["quickSearch"] = 0

        # 🎯 提取置顶热门站（如豆瓣 JS）单独缓存，确保绝对 Pos 0 位置
        if s_key == config.HOT_VIDEO_KEY:
            site["name"] = config.HOT_VIDEO_SITE_NAME
            site["category"] = "综合"
            hot_video_site = site
            continue
        elif "豆瓣" in s_name and "首页" in s_name:
            site["name"] = f"{config.LOGO_PREFIX} 豆瓣 • 首页"
            site["category"] = "综合"
            site["searchable"] = 0
            bucket_map["综合"].append(site)
            continue
        elif s_key == "AQY":
            site["name"] = f"{config.LOGO_PREFIX} 爱奇艺 {config.MY_TG_SUFFIX}"

        is_guazi = "瓜子" in s_name or s_key == "GZ"
        is_nsfw = False if is_guazi else ("🔞" in s_name or "色播" in s_name or "av" in s_key.lower() or "瓜" in s_name or "爆料" in s_name or "chat" in s_key.lower() or "cam" in s_key.lower() or "panda" in s_key.lower() or "video" in s_key.lower() or "md" in s_key.lower())
        
        if is_nsfw:
            site["category"] = "福利"
            bucket_map["福利"].append(site)
            continue

        matched_category = None
        for category, keywords in config.CATEGORY_RULES.items():
            if any(kw in s_name or (kw in s_key.lower() if s_key else False) for kw in keywords):
                matched_category = category
                break
        
        if matched_category:
            site["category"] = matched_category
            if matched_category in ["少儿", "音乐"] or "dj" in s_name.lower():
                site["searchable"] = 0
            bucket_map[matched_category].append(site)
        else:
            site["category"] = "综合"
            bucket_map["综合"].append(site)

        if site.get("category") not in ["少儿", "音乐"] and "searchable" not in site:
            site["searchable"] = 1

    # ====================================================================
    # 🎯 排序核心逻辑实现：
    # 分类桶大顺序: 综合 -> 手工源插槽 -> 网盘/磁力 -> 短剧 -> 动漫 -> 体育/直播 -> 少儿 -> 音乐 -> 福利
    # ====================================================================

    # 1. 综合类内部三梯队精细化排序
    tier1_official_kw = ["爱奇艺", "腾讯", "优酷", "芒果", "官源", "解析", "AQY", "TX", "YK", "MG"]
    tier2_quality_kw = ["瓜子", "金牌", "可可", "骚火", "低端", "神马", "毒舌", "泥视频", "努努", "808", "布布", "追光", "韩小圈", "奇优", "永乐", "麦田"]

    comp_tier1, comp_tier2, comp_tier3 = [], [], []

    for site in bucket_map.get("综合", []):
        s_name = site.get("name", "")
        s_key = site.get("key", "")
        if any(kw in s_name or kw in s_key for kw in tier1_official_kw):
            comp_tier1.append(site)
        elif any(kw in s_name or kw in s_key for kw in tier2_quality_kw):
            comp_tier2.append(site)
        else:
            comp_tier3.append(site)

    sorted_综合 = comp_tier1 + comp_tier2 + comp_tier3

    # 2. 网盘/磁力类内部精细化排序 (盘搜/聚合类优先)
    search_netdisk_kw = ["搜", "盘", "聚合", "米搜", "趣盘", "百酷", "酷乐", "鬼鬼", "天翼", "百搜"]
    netdisk_tier1, netdisk_tier2 = [], []

    for site in bucket_map.get("网盘/磁力", []):
        s_name = site.get("name", "")
        if any(kw in s_name for kw in search_netdisk_kw):
            netdisk_tier1.append(site)
        else:
            netdisk_tier2.append(site)

    sorted_网盘 = netdisk_tier1 + netdisk_tier2

    # 3. 提取手工源 (排除 HOT_VIDEO_KEY)
    hot_key = getattr(config, "HOT_VIDEO_KEY", "js_douban")
    hot_name = getattr(config, "HOT_VIDEO_SITE_NAME", "")

    custom_hot_site = None
    normal_custom_sites = []

    for custom_site in config.MY_CUSTOM_SITES:
        site = custom_site.copy()
        s_key = site.get("key", "")
        if s_key and s_key == hot_key:
            site["name"] = hot_name or site.get("name")
            site["category"] = "综合"
            custom_hot_site = site
        else:
            if "searchable" not in site:
                site["searchable"] = 1
            normal_custom_sites.append(site)

    # 4. 组装全局有序线路列表
    ordered_sites = []

    # 4.1 位置 0: 固定置顶热门站 (如豆瓣)
    top_site = hot_video_site or custom_hot_site
    if top_site:
        ordered_sites.append(top_site)

    # 4.2 综合类 (官源第一梯队在 Pos 1 开排，后跟第二、三梯队)
    ordered_sites.extend(sorted_综合)

    # 4.3 插槽: 所有普通手工源放在综合类之后、网盘/磁力类之前
    ordered_sites.extend(normal_custom_sites)

    # 4.4 续接其余分类桶
    remaining_categories = ["网盘/磁力", "短剧", "动漫", "体育/直播", "少儿", "音乐", "福利"]
    for cate in remaining_categories:
        if cate == "网盘/磁力":
            ordered_sites.extend(sorted_网盘)
        elif cate in bucket_map:
            ordered_sites.extend(bucket_map[cate])

    # 直播源清洗与合并
    custom_live_names = {l.get("name", "") for l in config.MY_CUSTOM_LIVES if l.get("name")}
    clean_base_lives = [
        l for l in all_raw_lives
        if l.get("name") not in custom_live_names and not any(kw in l.get("name", "") for kw in block_malicious_keywords)
    ]
    clean_base_lives = [l for l in clean_base_lives if not any(kw.lower() in l.get("name", "").lower() for kw in block_keywords)]

    live_inserted_count = 0
    for custom_live in config.MY_CUSTOM_LIVES:
        l_site = custom_live.copy()
        l_name = l_site.get("name", "")
        if not l_name.startswith(config.LOGO_PREFIX):
            l_name = f"{config.LOGO_PREFIX} {l_name}"
        if config.MY_TG_SUFFIX not in l_name:
            l_name = f"{l_name}{config.MY_TG_SUFFIX}"
        l_site["name"] = l_name

        if "🔞" in l_name:
            clean_base_lives.append(l_site)
        else:
            idx = min(config.INSERT_POS + live_inserted_count, len(clean_base_lives))
            clean_base_lives.insert(idx, l_site)
            live_inserted_count += 1

    final_obj = copy.deepcopy(json_cnb)
    
    if hasattr(config, "DEFAULT_LOGO_URL") and config.DEFAULT_LOGO_URL:
        final_obj["logo"] = config.DEFAULT_LOGO_URL

    final_obj.update({
        "parses": unique_parses,
        "sites": ordered_sites,
        "lives": clean_base_lives
    })

    if "doh" in final_obj and isinstance(final_obj["doh"], list):
        for doh_item in final_obj["doh"]:
            if doh_item.get("url", "").endswith("/dns-quer"): doh_item["url"] = f"{doh_item['url']}y"
        if not any(d.get("name") == config.ALI_DOH_CONFIG["name"] for d in final_obj["doh"]):
            final_obj["doh"].insert(0, config.ALI_DOH_CONFIG)

    if "rules" in final_obj and isinstance(final_obj["rules"], list):
        current_rules = final_obj["rules"]
        ad_hosts = list(config.AD_HOSTS_LIST)
        for r in current_rules:
            if isinstance(r, dict) and "hosts" in r:
                for h in r["hosts"]:
                    if h not in ad_hosts: ad_hosts.append(h)
        js_rule = {"name": "云端高级去广告JS注入", "hosts": ad_hosts, "script": config.CUSTOM_AD_BLOCK_JS}
        final_obj["rules"] = [js_rule] + [r for r in current_rules if r.get("name") != "云端高级去广告JS注入"]

    final_obj["spider"] = config.GLOBAL_SPIDER_JAR

    for site in final_obj.get("sites", []):
        s_key = site.get("key", "")
        if s_key in ["hajim-腾讯备", "茫茫"]:
            site["spider"] = "./tvbox.jar"

    if "lives" in final_obj and isinstance(final_obj["lives"], list):
        clean_lives = []
        for live in final_obj["lives"]:
            if not live or not isinstance(live, dict) or len(live) == 0:
                continue
            clean_lives.append(live)
        final_obj["lives"] = clean_lives

    return final_obj

# ====================================================================
# 🔀 【双版本矩阵构建与差异下发调度中枢】
# ====================================================================
# 修复后的 generate_dashboard_html 函数
def generate_dashboard_html(current_token, ordered_obj):
    """自动生成两个不同的 Dashboard：公开主页 (index.html) + 专属运维后台 (admin_888.html)"""
    try:
        current_time = (datetime.datetime.utcnow() + datetime.timedelta(hours=8)).strftime("%Y-%m-%d %H:%M:%S")
        
        sites_list = ordered_obj.get("sites", [])
        lives_list = ordered_obj.get("lives", [])
        parse_cnt = len(ordered_obj.get("parses", []))
        
        json_files = sorted(list(config.DATA_DIR.glob("*.json")), key=lambda x: x.stat().st_mtime, reverse=True)
        
        # 读取公开主页隐藏明细的开关参数 (默认 True 显示，可在 settings.json 中配置 SHOW_PUBLIC_DETAILS: false 来隐藏)
        show_public_details = config.get_setting("SHOW_PUBLIC_DETAILS", True)

        # --------------------------------------------------------------------
        # 👑 1. 构建【专属运维控制台】的卡片 HTML
        # --------------------------------------------------------------------
        admin_cards_html = ""
        for json_file in json_files:
            size_kb = round(json_file.stat().st_size / 1024, 2)
            fname = json_file.name
            is_active = current_token in fname
            badge = '<span class="text-xs bg-blue-100 text-blue-600 px-2 py-0.5 rounded">最新版本</span>' if is_active else '<span class="text-xs bg-gray-100 text-gray-500 px-2 py-0.5 rounded">历史/陷阱</span>'
            safe_key = fname.replace('.', '_').replace('-', '_')

            admin_cards_html += f"""
            <div class="bg-white rounded-xl p-4 shadow-sm border border-gray-200 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                <div>
                    <div class="flex items-center gap-2">
                        <span class="font-semibold text-slate-800">{fname}</span>
                        {badge}
                        <span class="text-xs text-gray-400">{size_kb} KB</span>
                    </div>
                    <p class="text-xs text-gray-400 mt-1">https://lytvs.top/{fname}</p>
                </div>
                
                <div class="flex items-center gap-3">
                    <div class="text-right px-2">
                        <div class="text-[10px] text-gray-400">点击/获取量</div>
                        <div class="text-xs font-bold text-emerald-600" id="cnt_{safe_key}">-- 次</div>
                    </div>
                    <div class="flex gap-2">
                        <a href="/{fname}" target="_blank" onclick="hitCount('{safe_key}')" class="px-3 py-1.5 bg-blue-50 text-blue-600 rounded-lg text-xs font-medium hover:bg-blue-100">
                            预览 JSON
                        </a>
                        <button onclick="navigator.clipboard.writeText('https://lytvs.top/{fname}'); hitCount('{safe_key}'); alert('已复制该接口链接！')" class="px-3 py-1.5 bg-slate-800 text-white rounded-lg text-xs font-medium hover:bg-slate-700">
                            复制链接
                        </button>
                    </div>
                </div>
            </div>
            """

        # 渲染运维控制台 (admin_888.html)
        admin_html = config.DASHBOARD_HTML_TEMPLATE.format(
            build_time=current_time,
            site_cnt=len(sites_list),
            live_cnt=len(lives_list),
            parse_cnt=parse_cnt,
            current_token=current_token,
            file_num=len(json_files),
            file_cards=admin_cards_html,
            version=config.VERSION,
            qq_group=config.MY_QQ_GROUP,
            sites_json=json.dumps(sites_list, ensure_ascii=False),
            lives_json=json.dumps(lives_list, ensure_ascii=False)
        )
        
        secret_filename = "admin_888.html"
        admin_path = config.DATA_DIR / secret_filename
        admin_path.write_text(admin_html, encoding="utf-8")

        # --------------------------------------------------------------------
        # 🏡 2. 构建【粉丝/访客公开主页】的卡片 HTML & 开关控制
        # --------------------------------------------------------------------
        public_cards_html = ""
        for json_file in json_files:
            fname = json_file.name
            if current_token in fname:
                size_kb = round(json_file.stat().st_size / 1024, 2)
                is_full = "全量" in fname
                badge = '<span class="text-[10px] bg-rose-500/20 text-rose-300 border border-rose-500/30 px-2 py-0.5 rounded-full font-medium">🔞 全量推荐</span>' if is_full else '<span class="text-[10px] bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 px-2 py-0.5 rounded-full font-medium">🏡 客厅纯净</span>'
                
                # 🎯 修复关键点：先给变量设置默认值，防止发生 UnboundLocalError
                display_url = f"https://lytvs.top/{fname}"
                preview_href = f"/{fname}"
                is_masked_js = "false"
                target_attr = "target='_blank'"

                # 如果关闭了明细展示（隐秘模式），则覆盖变量
                if not show_public_details:
                    display_url = "https://lytvs.top/🔒链接已受保护_请加Telegram交流群获取最新接口"
                    preview_href = "javascript:alert('⚠️ 当前公开页已开启保护模式，请前往社群获取接口！');"
                    is_masked_js = "true"
                    target_attr = ""

                public_cards_html += f"""
                <div class="bg-slate-900/80 rounded-xl p-4 border border-slate-700/70 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                    <div class="space-y-1 overflow-hidden">
                        <div class="flex items-center gap-2">
                            <span class="font-bold text-white text-sm">{"老杨TV全量版" if is_full else "老杨TV纯净版"}</span>
                            {badge}
                        </div>
                        <p class="text-xs font-mono text-slate-400 truncate select-all">{display_url}</p>
                    </div>
                    <div class="flex items-center gap-2 flex-shrink-0">
                        <a href="{preview_href}" {target_attr} class="px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-lg text-xs font-medium border border-slate-600/60 transition">
                            预览
                        </a>
                        <button onclick="copyUrl('{display_url}', {is_masked_js})" class="px-3 py-1.5 bg-emerald-600 hover:bg-emerald-500 text-white rounded-lg text-xs font-bold shadow-lg shadow-emerald-600/20 transition flex items-center gap-1">
                            <i class="fa-regular fa-copy"></i>
                            复制链接
                        </button>
                    </div>
                </div>
                """

        # 根据开关设置密锁卡片的显示逻辑
        if show_public_details:
            lock_display_text = "🔒 *** 点击显示"
            lock_click_action = f"if(this.dataset.revealed==='true'){{this.innerText='🔒 *** 点击显示'; this.dataset.revealed='false';}}else{{this.innerText='{current_token}'; this.dataset.revealed='true';}}"
        else:
            lock_display_text = "🔒 加群获取"
            lock_click_action = f"alert('⚠️ 当前公开页已隐藏密锁！请前往 Telegram群组【@tvshare23】或 Telegram 频道获取。');"

        # 清理 Telegram 账号前缀，生成标准 https://t.me/xxx 超链接
        tg_channel_clean = config.MY_PROMO_CHANNEL.replace("@", "").strip()

        # 读取赞赏二维码 URL 与文案
        # 1. 确保在调用 .format(...) 之前，生成好了 donate_section_html 变量
        donate_qr_url = config.get_setting("DONATE_QR_URL", "").strip()
        donate_notice_text = config.get_setting("DONATE_NOTICE_TEXT", "☕ 如果觉得本专线对你有帮助，欢迎请作者喝杯咖啡支持服务器与域名续费～").strip()

        if donate_qr_url:
            donate_section_html = f"""
            <div class="bg-slate-900/60 border border-slate-700/60 rounded-xl p-4 text-center space-y-3">
                <p class="text-xs text-slate-300">{donate_notice_text}</p>
                <button onclick="toggleDonate()" class="px-4 py-2 bg-rose-600/20 hover:bg-rose-600/30 text-rose-300 border border-rose-500/30 rounded-xl text-xs font-bold transition inline-flex items-center gap-1.5 shadow-lg">
                    <i class="fa-solid fa-heart text-rose-500"></i>
                    赞赏支持作者 / 展开收款码
                </button>
                <div id="donate_qr_box" class="hidden pt-2 flex flex-col items-center justify-center">
                    <img src="{donate_qr_url}" alt="赞赏码" class="w-48 h-48 rounded-xl border-2 border-rose-500/40 shadow-2xl object-cover">
                    <p class="text-[10px] text-slate-500 mt-2">感谢您的认可与支持！</p>
                </div>
            </div>
            """
        else:
            donate_section_html = ""

        # 读取跑马灯流动公告
        marquee_text = config.get_setting(
            "MARQUEE_NOTICE_TEXT", 
            "📢 欢迎使用老杨TV专属缝合矩阵！本专线已完成全量广告清洗与无损极速重排，建议加社群获取最新变动！"
        ).strip()

        # 读取页脚版权文案（设置默认保底文本）
        footer_text = config.get_setting(
            "FOOTER_TEXT", 
            "© 2026 老杨TV · Powered by Serverless Matrix Architecture & Cloudflare Pages"
        ).strip()

        # 渲染公开主页 (index.html)
        public_html = config.PUBLIC_INDEX_HTML_TEMPLATE.format(
            build_time=current_time,
            site_cnt=len(sites_list),
            live_cnt=len(lives_list),
            parse_cnt=parse_cnt,
            lock_display_text=lock_display_text,
            lock_click_action=lock_click_action,
            file_cards=public_cards_html,
            donate_section_html=donate_section_html,
            marquee_text=marquee_text,
            footer_text=footer_text,  # 👈 传入页脚文案变量
            version=config.VERSION,
            qq_group=config.MY_QQ_GROUP,
            promo_channel=config.MY_PROMO_CHANNEL,
            tg_channel_clean=tg_channel_clean
        )

        public_index_path = config.DATA_DIR / "index.html"
        public_index_path.write_text(public_html, encoding="utf-8")

        log_success(f"双前端 Dashboard 成功生成！\n  👉 粉丝公开主页: datas/index.html (隐藏开关状态: {not show_public_details})\n  👑 专属运维后台: datas/{secret_filename}")
        
    except Exception as e:
        log_error(f"生成 Dashboard 页面崩溃: {e}", exc_info=True)


def build_and_dispatch_matrix(ordered_obj, current_token, full_out_name, clean_out_name, is_new_token_gen):
    """构建多通道分流，精准比对 Diff 并下发变更明细快报"""
    full_version_obj = copy.deepcopy(ordered_obj)
    full_version_obj["notice"] = config.WELCOME_NOTICE_FULL + config.THANKS_WARNING
    full_version_obj["wallpaper"] = config.WALLPAPER_FULL
    
    full_final_out = {"notice": full_version_obj.pop("notice")}
    full_final_out.update(full_version_obj)

    clean_version_obj = copy.deepcopy(ordered_obj)
    clean_version_obj["notice"] = config.WELCOME_NOTICE_CLEAN + config.THANKS_WARNING
    clean_version_obj["wallpaper"] = config.WALLPAPER_CLEAN
    
    # 🎯 动态获取最新的 NSFW 过滤词
    nsfw_keywords = config.get_nsfw_keywords()

    # 🟢 新代码：加入控制台白名单放行与 🔞 符号自动清洗逻辑
    nsfw_keywords = config.get_nsfw_keywords()
    white_list_keywords = config.get_allow_nsfw_keywords() # 从 config 动态读取控制台设置的白名单（如 ["易发"]）

    # 1. 过滤点播线路 (sites)
    clean_sites = []
    for s in clean_version_obj.get("sites", []):
        s_name = s.get("name", "")
        s_cat = s.get("category", "")
        s_key = s.get("key", "").lower()

        # 如果线路名称包含白名单关键词（例如“易发”）
        if any(wk in s_name for wk in white_list_keywords):
            site_copy = copy.deepcopy(s)
            site_copy["name"] = site_copy["name"].replace("🔞", "").strip() # 保留线路，把名字里的 🔞 去掉
            clean_sites.append(site_copy)
        # 如果不是白名单，且包含 NSFW 敏感词，则剔除
        elif any(kw in s_name or kw in s_cat or kw in s_key for kw in nsfw_keywords):
            continue
        # 普通正常线路直接保留
        else:
            clean_sites.append(s)

    # 2. 过滤直播线路 (lives)
    clean_lives = []
    for l in clean_version_obj.get("lives", []):
        l_name = l.get("name", "")

        # 如果直播源包含白名单关键词（例如“易发”）
        if any(wk in l_name for wk in white_list_keywords):
            live_copy = copy.deepcopy(l)
            live_copy["name"] = live_copy["name"].replace("🔞", "").strip() # 保留线路，把名字里的 🔞 去掉
            clean_lives.append(live_copy)
        # 如果不是白名单，且包含敏感词，则剔除
        elif any(kw in l_name for kw in nsfw_keywords):
            continue
        # 普通直播源保留
        else:
            clean_lives.append(l)

    # 把处理好的列表赋值给纯净版对象
    clean_version_obj["sites"] = clean_sites
    clean_version_obj["lives"] = clean_lives
    
    clean_final_out = {"notice": clean_version_obj.pop("notice")}
    clean_final_out.update(clean_version_obj)

    full_output_path = config.DATA_DIR / full_out_name
    clean_output_path = config.DATA_DIR / clean_out_name

    tg_token = os.getenv("TG_TOKEN")
    tg_chat_id = os.getenv("TG_CHAT_ID")
    repo_info = os.getenv("GITHUB_REPOSITORY", "GodLike631/Ly_me")
    branch_info = os.getenv("GITHUB_REF_NAME", "main")
    
    full_raw_url = f"https://raw.githubusercontent.com/{repo_info}/refs/heads/{branch_info}/datas/{full_out_name}"
    clean_raw_url = f"https://raw.githubusercontent.com/{repo_info}/refs/heads/{branch_info}/datas/{clean_out_name}"
    
    full_sub_url = f"{config.GITHUB_PROXY}{full_raw_url}" if config.GITHUB_PROXY else full_raw_url
    clean_sub_url = f"{config.GITHUB_PROXY}{clean_raw_url}" if config.GITHUB_PROXY else clean_raw_url
    
    current_time = (datetime.datetime.utcnow() + datetime.timedelta(hours=8)).strftime("%Y-%m-%d %H:%M")
    is_password_changed = False
    old_file_name = ""
    
    if config.TRACKER_PATH.exists():
        old_file_name = config.TRACKER_PATH.read_text(encoding='utf-8').strip()
    if old_file_name != full_out_name and old_file_name != "":
        is_password_changed = True

    if is_password_changed or is_new_token_gen:
        pwd_msg = config.TG_PWD_MSG_TEMPLATE.format(
            current_time=current_time, current_token=current_token,
            full_sub_url=full_sub_url, clean_sub_url=clean_sub_url
        )
        send_telegram_request(tg_token, tg_chat_id, pwd_msg)
    else:
        try:
            old_sites, old_lives = set(), set()
            old_file_path = config.DATA_DIR / old_file_name
            if old_file_path.exists():
                old_data = json.loads(old_file_path.read_text(encoding='utf-8'))
                old_sites = {s.get("name", "").strip() for s in old_data.get("sites", []) if s.get("name")}
                old_lives = {l.get("name", "").strip() for l in old_data.get("lives", []) if l.get("name")}

            new_sites = {s.get("name", "").strip() for s in full_final_out.get("sites", []) if s.get("name")}
            new_lives = {l.get("name", "").strip() for l in full_final_out.get("lives", []) if l.get("name")}

            added_sites, del_sites = sorted(list(new_sites - old_sites)), sorted(list(old_sites - new_sites))
            added_lives, del_lives = sorted(list(new_lives - old_lives)), sorted(list(old_lives - new_lives))

            if added_sites or del_sites or added_lives or del_lives:
                msg_lines = ["📝 *【 变动明细预览 】*", "📊 *━━━━━━━━━━━━━━*"]
                if added_sites or del_sites:
                    msg_lines.append("📺 *【点播线路变动】*")
                    if added_sites:
                        msg_lines.append("➕ *新增点播*：")
                        msg_lines.extend([f"  🟢 {name}" for name in added_sites[:config.TG_MAX_DISPLAY]])
                        if len(added_sites) > config.TG_MAX_DISPLAY: msg_lines.append(f"  ...等共 {len(added_sites)} 个源")
                    if del_sites:
                        if added_sites: msg_lines.append("")
                        msg_lines.append("➖ *剔除点播*：")
                        msg_lines.extend([f"  🔴 {name}" for name in del_sites[:config.TG_MAX_DISPLAY]])
                        if len(del_sites) > config.TG_MAX_DISPLAY: msg_lines.append(f"  ...等共 {len(del_sites)} 个源")
                    msg_lines.append("📊 *━━━━━━━━━━━━━━*")
                if added_lives or del_lives:
                    if len(msg_lines) > 2: msg_lines.append("")
                    msg_lines.append("📡 *【直播源站变动】*")
                    if added_lives:
                        msg_lines.append("➕ *新增直播*：")
                        msg_lines.extend([f"  🟢 {name}" for name in added_lives[:config.TG_MAX_DISPLAY]])
                        if len(added_lives) > config.TG_MAX_DISPLAY: msg_lines.append(f"  ...等共 {len(added_lives)} 个源")
                    if del_lives:
                        if added_lives: msg_lines.append("")
                        msg_lines.append("➖ *剔除直播*：")
                        msg_lines.extend([f"  🔴 {name}" for name in del_lives[:config.TG_MAX_DISPLAY]])
                        if len(del_lives) > config.TG_MAX_DISPLAY: msg_lines.append(f"  ...等共 {len(del_lives)} 个源")
                    msg_lines.append("📊 *━━━━━━━━━━━━━━*")

                full_msg = config.TG_UPDATE_MSG_TEMPLATE.format(
                    current_time=current_time, 
                    current_token=current_token,  # 🎯 补上这个缺失的变量！
                    detail_msg="\n".join(msg_lines),
                    full_sub_url=full_sub_url, 
                    clean_sub_url=clean_sub_url
                )
                send_telegram_request(tg_token, tg_chat_id, full_msg)
                # =========================================================
                # 🎯 2.【在此处插入】记录 Changelog 到 datas/changelog.json
                # =========================================================
                try:
                    logs_detail = []
                    if added_sites: logs_detail.append("🟢 新增点播: " + ", ".join(added_sites[:8]))
                    if del_sites:   logs_detail.append("🔴 剔除点播: " + ", ".join(del_sites[:8]))
                    if added_lives: logs_detail.append("📡 新增直播: " + ", ".join(added_lives[:8]))
                    if del_lives:   logs_detail.append("❌ 剔除直播: " + ", ".join(del_lives[:8]))

                    changelog_path = config.DATA_DIR / "changelog.json"
                    history_logs = []
                    if changelog_path.exists():
                        try:
                            history_logs = json.loads(changelog_path.read_text(encoding='utf-8'))
                        except Exception:
                            history_logs = []

                    new_log_entry = {
                        "time": current_time,
                        "version": config.VERSION,
                        "detail": "\n".join(logs_detail)
                    }

                    history_logs.insert(0, new_log_entry)
                    history_logs = history_logs[:3]  # 保持最新的 3 条记录
                    changelog_path.write_text(json.dumps(history_logs, ensure_ascii=False, indent=2), encoding='utf-8')
                    log_success("✨ 变动日志已同步更新写入 datas/changelog.json")
                except Exception as log_err:
                    log_error(f"写入 changelog.json 失败: {log_err}")
                # =========================================================
            else:
                log_diff("名录内容完全等价，智能拦截重复变更广播。")
        except Exception as e:
            log_error(f"比对 Diff 变动逻辑发生致命故障: {e}")

    full_output_path.write_text(json.dumps(full_final_out, ensure_ascii=False, indent=4), encoding='utf-8')
    clean_output_path.write_text(json.dumps(clean_final_out, ensure_ascii=False, indent=4), encoding='utf-8')
    config.TRACKER_PATH.write_text(full_out_name, encoding='utf-8')
    # --------------------------------------------------------------------
    # 🎯 【功能 6 追加】：多格式同步导出 (.m3u 与 .txt 直播订阅)
    # --------------------------------------------------------------------
    try:
        m3u_lines = ["#EXTM3U"]
        txt_lines = []
        
        for live in full_final_out.get("lives", []):
            if not isinstance(live, dict): continue
            gname = live.get("group", live.get("name", "未分类"))
            channels = live.get("channels", [])
            
            # 1. 如果是标准的 channels 嵌套结构
            if channels and isinstance(channels, list):
                for ch in channels:
                    cname = ch.get("name", "")
                    urls = ch.get("urls", [])
                    for url in urls:
                        m3u_lines.append(f'#EXTINF:-1 group-title="{gname}",{cname}')
                        m3u_lines.append(url)
                        txt_lines.append(f"{cname},{url}")
            # 2. 如果是单条直播源对象结构
            elif live.get("url"):
                cname = live.get("name", "")
                url = live.get("url", "")
                m3u_lines.append(f'#EXTINF:-1 group-title="自定义直播",{cname}')
                m3u_lines.append(url)
                txt_lines.append(f"{cname},{url}")

        m3u_out_path = config.DATA_DIR / "live.m3u"
        txt_out_path = config.DATA_DIR / "live.txt"
        
        m3u_out_path.write_text("\n".join(m3u_lines), encoding='utf-8')
        txt_out_path.write_text("\n".join(txt_lines), encoding='utf-8')
        log_success("✨ 多格式直播源已同步导出为 live.m3u 和 live.txt")
    except Exception as e:
        log_error(f"导出 M3U/TXT 发生异常: {e}")
    
    # 🎯 触发可视化页面生成
    site_cnt = len(full_final_out.get("sites", []))
    live_cnt = len(full_final_out.get("lives", []))
    parse_cnt = len(full_final_out.get("parses", []))
    # 🎯 替换原来的 generate_dashboard_html(...) 调用：
    # 变更为：
    generate_dashboard_html(current_token, full_final_out)

    return site_cnt, live_cnt, parse_cnt, full_output_path.stat().st_size

# ====================================================================
# 🚀 【程序统一总调度入口】
# ====================================================================
def main():
    start_time = time.time()
    try:
        log_info(f"====================================================")
        log_info(f"自动编译核心架构工程架设流 V{config.VERSION}")
        log_info(f"编译流构建序列日期: {config.BUILD_DATE}")
        log_info(f"====================================================")
        
        current_token, full_out_name, clean_out_name, is_new_token_gen = manage_monthly_token()
        execute_trap_boom(full_out_name, clean_out_name)
        ordered_obj = object_level_wash_and_compile()
        
        site_cnt, live_cnt, parse_cnt, file_size = build_and_dispatch_matrix(
            ordered_obj, current_token, full_out_name, clean_out_name, is_new_token_gen
        )
        
        today = datetime.datetime.now()
        if not config.LOCK_FILE_PATH.exists() or "-" not in config.LOCK_FILE_PATH.read_text(encoding='utf-8'):
            config.LOCK_FILE_PATH.write_text(f"{today.month}-{current_token}", encoding='utf-8')
            
        elapsed_time = time.time() - start_time
        log_success(f"编译总流水线平稳运行结束！【编译快报总览】:")
        print(f"\033[94m"
              f"  ⏱️  Compile Time : {elapsed_time:.2f} sec\n"
              f"  📺 Total Sites   : {site_cnt} channels\n"
              f"  📡 Total Lives   : {live_cnt} channels\n"
              f"  🥇 Total Parses  : {parse_cnt} objects\n"
              f"  💾 Output Weight : {file_size / 1024 / 1024:.2f} MB"
              f"\033[0m")
              
    except Exception as e:
        log_critical(f"核心编译主总线遭到未知突发崩溃: {e}", exc_info=True)

if __name__ == "__main__":
    main()
