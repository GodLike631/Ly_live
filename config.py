# -*- coding: utf-8 -*-
"""
核心配置文件（全控制台动态解耦 & 前端并发巡检终极版）
"""
import json
from pathlib import Path

# ====================================================================
# 📂 【零、路径与动态配置中心 (实时读取 settings.json，防止缓存)】
# ====================================================================
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "datas"
SETTINGS_FILE_PATH = DATA_DIR / "settings.json"

def get_setting(key, default_val):
    """每次调用均实时从磁盘重新加载 settings.json，确保控制台修改后无需重启即刻生效"""
    if SETTINGS_FILE_PATH.exists():
        try:
            _dynamic_settings = json.loads(SETTINGS_FILE_PATH.read_text(encoding='utf-8'))
            return _dynamic_settings.get(key, default_val)
        except Exception as e:
            pass
    return default_val

# ====================================================================
# 🆔 【一、工程版本与全局控制参数定义】
# ====================================================================
VERSION = "3.3.1"
BUILD_DATE = "2026.07.30"

GLOBAL_SPIDER_JAR = get_setting("GLOBAL_SPIDER_JAR", "https://cnb.cool/fish2035/xs/-/git/raw/main/spider.jar")
INSERT_POS = get_setting("INSERT_POS", 0)           
SITE_INSERT_POS = get_setting("SITE_INSERT_POS", 0) 
DEFAULT_LOGO_URL = get_setting("DEFAULT_LOGO_URL", "https://img.naixiai.cn/2026/06/18/IMG_6638.jpeg")

# 🎯 改为实时函数动态获取上游三方底包抓取 URL
def get_cnb_source_url():
    return get_setting("CNB_SOURCE_URL", "https://cnb.cool/fish2035/xs/-/git/raw/main/api.json")

def get_haitun_source_url():
    return get_setting("HAITUN_SOURCE_URL", "https://raw.githubusercontent.com/FGBLH/HKL/refs/heads/main/ok%E6%B5%B7%E8%B1%9A18.json")
    
def get_custom4_source_url():
    return get_setting("CUSTOM4_SOURCE_URL", "https://raw.githubusercontent.com/FGBLH/HKL/refs/heads/main/ok%E6%B5%B7%E8%B1%9A665.json")

def get_lz_source_url():
    return get_setting("LZ_SOURCE_URL", "https://gh-proxy.com/https://raw.githubusercontent.com/ediart/tvbox/refs/heads/main/lz/py.json")

DEFAULT_TIMEOUT = 10     
TG_TIMEOUT = 15          
TOKEN_LENGTH = 3         
TG_MAX_DISPLAY = 15  

# ====================================================================
# 🌐 【二、全局核心路径与网络代理配置区】
# ====================================================================
CNB_PATH = DATA_DIR / "cnb.json"
HAITUN_PATH = DATA_DIR / "dol.json"
LZ_PATH = DATA_DIR / "lz.json"
dol2_PATH = DATA_DIR / "dol2.json"

LOCK_FILE_PATH = DATA_DIR / "控制开关.txt"
TRACKER_PATH = DATA_DIR / "最新接口文件名.txt"

GITHUB_PROXY = "https://gh-proxy.org/"

# ====================================================================
# 🚫 【三、双版本过滤依据、广告拦截与恶意杂质动态获取区】
# ====================================================================
def get_allow_nsfw_keywords():
  return tuple(get_setting("ALLOW_NSFW_KEYWORDS", ["易发"]))

def get_block_keywords():
  return tuple(
      get_setting(
          "BLOCK_KEYWORDS", ["羊壳", "弹幕", "Gather", "Mytv", "裤佬TV"]
      )
  )


def get_upstream_dirty_words():
  return tuple(
      get_setting(
          "UPSTREAM_DIRTY_WORDS",
          [
              "🐬",
              "海豚影视",
              "海豚",
              "完全免费，如有收费的都是骗子",
              "交流群 TG：@huliys9",
          ],
      )
  )


def get_nsfw_keywords():
  return tuple(
      get_setting(
          "NSFW_KEYWORDS",
          [
              "🔞",
              "福利",
              "探花",
              "约炮",
              "色播",
              "av",
              "爆料",
              "蜜桃",
              "三级片",
          ],
      )
  )


def get_block_malicious_keywords():
  return tuple(
      get_setting("BLOCK_MALICIOUS_KEYWORDS", ["日本女优", "日本女友"])
  )
AD_HOSTS_LIST = ["vip.wwgz.cn", "lziplayer.com", "m3u8.apibdzy.com", "cj.ffzyapi.com", "api.hbzyapi.com"]

# ====================================================================
# 🔍 【四、全局搜索与分类规则控制面板】
# ====================================================================
NO_SEARCH_KEYWORDS = get_setting("NO_SEARCH_KEYWORDS", [])
NO_SEARCH_KEYS = get_setting("NO_SEARCH_KEYS", ["js_douban", "豆瓣", "本地", "配置中心", "版本信息", "push_agent"])
NO_QUICK_SEARCH_KEYS = get_setting("NO_QUICK_SEARCH_KEYS", ["js_douban", "配置中心"])

CATEGORY_RULES = get_setting("CATEGORY_RULES", {
    "网盘/磁力": ["磁力", "索", "盘", "云盘", "4k", "4K", "夸克", "阿里", "UC", "百度", "迅雷", "盘搜", "米搜", "趣盘"],
    "短剧": ["短剧", "剧场", "微剧", "微短剧"],
    "动漫": ["动漫", "新番", "anime", "a1", "番剧", "二次元", "动画"],
    "体育/直播": ["体育", "球", "直播", "赛事", "比赛"],
    "少儿": ["少儿", "课堂", "教学", "教育", "儿童", "早教", "动画片"],
    "音乐": ["音乐", "网易云", "听书", "唱会", "fm", "FM", "相声", "小品", "戏曲", "dj", "DJ", "听书", "戏曲多多"]
})
# ====================================================================
# 👑 【五、专属品牌与视觉定制区】
# ====================================================================
MY_QQ_GROUP = get_setting("MY_QQ_GROUP", "532637640")
MY_PROMO_CHANNEL = get_setting("MY_PROMO_CHANNEL", "@huliys9")
MY_TG_SUFFIX = get_setting("MY_TG_SUFFIX", "｜Tg：@huliys9")
LOGO_PREFIX = get_setting("LOGO_PREFIX", "🦋")


WALLPAPER_FULL = "https://img.naixiai.cn/2026/wallpapers/full_vip.jpg"
WALLPAPER_CLEAN = "https://img.naixiai.cn/2026/wallpapers/home_clean.jpg"

HOT_VIDEO_KEY = get_setting("HOT_VIDEO_KEY", "js_douban")
HOT_VIDEO_SITE_NAME = get_setting("HOT_VIDEO_SITE_NAME", f"豆瓣(js),该接口完全免费，如有收费都是骗子｜{MY_TG_SUFFIX.strip('｜')}")

MY_NAME_REPLACEMENTS = {}

PATH_REPLACEMENTS = {
    r'\./spider\.jar': 'https://cnb.cool/fish2035/xs/-/git/raw/main/spider.jar',
    r'\./XBPQ/': 'https://cnb.cool/fish2035/xs/-/git/raw/main/XBPQ/',
    r'\./XYQHiker': 'https://cnb.cool/fish2035/xs/-/git/raw/main/XYQHiker',
    r'\./js/': 'https://cnb.cool/fish2035/xs/-/git/raw/main/js/',
    r'\./json/': 'https://cnb.cool/fish2035/xs/-/git/raw/main/json/',
    r'\./py/': 'https://cnb.cool/fish2035/xs/-/git/raw/main/py/',
    r'http://127\.0\.0\.1:9978/file/TVBox/logo\.png': DEFAULT_LOGO_URL
}

# ====================================================================
# 🔒 【六、双版本输出控制与“金蝉脱壳”大轰炸配置区】
# ====================================================================
BASE_OUTPUT_FULL = get_setting("BASE_OUTPUT_FULL", "老杨TV全量版")
BASE_OUTPUT_CLEAN = get_setting("BASE_OUTPUT_CLEAN", "老杨TV纯净版")

TRAP_NOTICE_TEXT = get_setting("TRAP_NOTICE_TEXT", f"⚠️ 警告：当前专线已过期断流！老链接已彻底作废！\n\n最新全量/纯净矩阵链接或当前密码请加QQ群“{MY_QQ_GROUP}”获取")
TRAP_SITE_NAME_1 = get_setting("TRAP_SITE_NAME_1", f"🚨 请前往QQ群“{MY_QQ_GROUP}”获取最新密码🚨 当前专线密码已过期断流！")
TRAP_SITE_NAME_2 = get_setting("TRAP_SITE_NAME_2", f"🚨 请前往QQ群“{MY_QQ_GROUP}”获取最新订阅链接矩阵")
TRAP_LIVE_GROUP = get_setting("TRAP_LIVE_GROUP", "🚨 接口过期断流 ｜ 提示")
TRAP_LIVE_CHANNEL = get_setting("TRAP_LIVE_CHANNEL", f"👉 线路已过期 ➡️ 加QQ群“{MY_QQ_GROUP}”获取最新订阅密码")


# ====================================================================
# 📡 【七、客户端通知弹窗与 DOH/JS 注入高级规则配置区】
# ====================================================================
THANKS_WARNING = get_setting("THANKS_WARNING", f"\n\n👑如果遇到失效 or 断流，请及时回 Telegram 频道（{MY_PROMO_CHANNEL}）或微信群获取当前最新密码锁！")
WELCOME_NOTICE_FULL = get_setting("WELCOME_NOTICE_FULL", "欢迎使用【老杨TV粉丝专属全量专线】！本接口由“老杨TV”结合多方大底包无损重排而成，干净流畅.🚨 重要提示：本接口密码不定期全自动更换！")
WELCOME_NOTICE_CLEAN = get_setting("WELCOME_NOTICE_CLEAN", "欢迎使用【老杨TV专属绿色客厅专线】！本接口已全面过滤敏感、擦边 and 福利内容，全家老少看电视更安全、更绿色！")

ALI_DOH_CONFIG = {"name": "AliDNS", "url": "https://dns.alidns.com/dns-query", "ips": ["223.5.5.5", "223.6.6.6"]}

CUSTOM_AD_BLOCK_JS = [
    "console.log('老楊TV高級WebView攔確器啟動');",
    "window.addEventListener('DOMContentLoaded', function() {",
    "   document.querySelectorAll('video').forEach(v => { v.muted = true; v.play().catch(e=>{}); });",
    "   Function.prototype.__constructor__ = Function.prototype.constructor;",
    "   Function.prototype.constructor = function() { if (arguments && typeof arguments[0] === 'string' && arguments[0].includes('debugger')) { return function(){}; } return Function.prototype.__constructor__.apply(this, arguments); };",
    "});",
    "setInterval(() => { let selectors = ['.adv-class', '.pop-banner', '#notice-modal', '[id*=\"partner\"]', '[class*=\"baidu\"]', 'iframe[src*=\"game\"]', 'iframe[src*=\"bet\"]', '#pop-ad', '.sidebar-ads', 'a[href*=\"999\"]']; selectors.forEach(sel => { document.querySelectorAll(sel).forEach(el => el.remove()); }); }, 400);"
]

TG_PWD_MSG_TEMPLATE = get_setting("TG_PWD_MSG_TEMPLATE", (
    "🔔 *老杨TV · 全新硬核双通道密码锁发布* 🔔\n\n"
    "📅 *生效时间*：`{current_time}` (北京时间)\n"
    "🔑 *全新专线密锁*：`{current_token}`\n\n"
    "🚀 *重要提示*：\n密码锁已成功交替！旧接口已全线开启【金蝉脱壳】大轰炸，老链接彻底作废，请及时复制下方对应通道的最新链接！\n\n"
    "🔞 *最新【老杨TV全量版】矩阵订阅*：\n"
    "`https://lytvs.top/老杨TV全量版{current_token}.json`\n\n"
    "🏡 *最新【老杨TV纯净版】客厅订阅*：\n"
    "`https://lytvs.top/老杨TV纯净版{current_token}.json`\n\n"
    f"👑 全量版与纯净版已在后台全自动换锁，请及时前往电视端更新。若电视端遇到断流请尝试重启软件或前往TG频道（{MY_PROMO_CHANNEL}）获取支持！"
))

TG_UPDATE_MSG_TEMPLATE = get_setting("TG_UPDATE_MSG_TEMPLATE", (
    "🔔 *老杨TV 缝合矩阵接口变更通知* 🔔\n\n"
    "📅 *更新时间*：{current_time} (北京时间)\n"
    "🚀 *变动说明*：检测到上游数据源更新或手工区调整，双版本配置已全自动编译上链！\n\n"
    "{detail_msg}\n\n"
    "📡 *【 最新多版本订阅矩阵 (点击可自动复制)】*：\n\n"
    "🔞 *最新【老杨TV全量版】矩阵订阅*：\n"
    "`https://lytvs.top/老杨TV全量版{current_token}.json`\n\n"
    "🏡 *最新【老杨TV纯净版】客厅订阅*：\n"
    "`https://lytvs.top/老杨TV纯净版{current_token}.json`\n\n"
    f"👑 全量版与纯净版已在后台无缝更新。更新配置即可，若遇到断流请尝试重启软件或及时前往TG频道（{MY_PROMO_CHANNEL}）获取当前最新密码锁！"
))

# ====================================================================
# 🖥️ 【八、Cloudflare Pages 可视化运维控制台 SPA HTML 模板】
# ====================================================================
DASHBOARD_HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="zh-CN" class="h-full bg-slate-900">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>老杨TV - 矩阵运维控制台</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <script defer src='https://static.cloudflareinsights.com/beacon.min.js' data-cf-beacon='{{"token": "95a52762f7774d668f225814b627d19a"}}'></script>
    <style>
        [x-cloak] {{ display: none !important; }}
        ::-webkit-scrollbar {{ width: 6px; height: 6px; }}
        ::-webkit-scrollbar-track {{ background: #0f172a; }}
        ::-webkit-scrollbar-thumb {{ background: #334155; border-radius: 4px; }}
        ::-webkit-scrollbar-thumb:hover {{ background: #475569; }}
    </style>
</head>

<body class="h-full text-slate-200 flex flex-col font-sans overflow-hidden">

    <!-- 顶部 Header Bar -->
    <header class="bg-slate-800 border-b border-slate-700 h-16 flex items-center justify-between px-4 sm:px-6 flex-shrink-0 z-20">
        <div class="flex items-center gap-3">
            <span class="text-2xl">🦋</span>
            <div>
                <h1 class="text-base font-bold text-white leading-tight">老杨TV 缝合矩阵运维控制台</h1>
                <p class="text-xs text-slate-400">Core Engine V{version} | Build: {build_time}</p>
            </div>
        </div>

        <div class="flex items-center gap-3">
            <div id="authStatusBadge" class="hidden sm:flex items-center gap-2 px-3 py-1 rounded-full text-xs font-medium bg-amber-500/10 text-amber-400 border border-amber-500/20">
                <i class="fa-solid fa-key text-[10px]"></i>
                <span id="authStatusText">未绑定 GitHub Token</span>
            </div>

            <button onclick="openTokenModal()" class="px-3 py-1.5 bg-slate-700 hover:bg-slate-600 text-xs font-semibold rounded-lg text-slate-200 transition flex items-center gap-1.5 border border-slate-600">
                <i class="fa-solid fa-user-gear"></i>
                <span>鉴权设置</span>
            </button>
        </div>
    </header>

    <div class="flex flex-1 h-[calc(100vh-4rem)] overflow-hidden">
        
        <!-- 左侧 SideBar 导航 -->
        <aside class="w-16 sm:w-60 bg-slate-800/60 border-r border-slate-700/80 flex flex-col justify-between flex-shrink-0">
            <nav class="p-2 sm:p-3 space-y-1">
                <button onclick="switchTab('overview')" id="nav-overview" class="nav-btn w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition text-emerald-400 bg-slate-700/60">
                    <i class="fa-solid fa-chart-line text-lg w-5 text-center"></i>
                    <span class="hidden sm:inline">📊 运行概览</span>
                </button>

                <button onclick="switchTab('control')" id="nav-control" class="nav-btn w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition text-slate-400 hover:text-slate-200 hover:bg-slate-700/30">
                    <i class="fa-solid fa-sliders text-lg w-5 text-center"></i>
                    <span class="hidden sm:inline">⚙️ 控制中心</span>
                </button>

                <button onclick="switchTab('resources')" id="nav-resources" class="nav-btn w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition text-slate-400 hover:text-slate-200 hover:bg-slate-700/30">
                    <i class="fa-solid fa-boxes-stacked text-lg w-5 text-center"></i>
                    <span class="hidden sm:inline">📦 资源管理</span>
                </button>

                <button onclick="switchTab('inspect')" id="nav-inspect" class="nav-btn w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition text-slate-400 hover:text-slate-200 hover:bg-slate-700/30">
                    <i class="fa-solid fa-microscope text-lg w-5 text-center"></i>
                    <span class="hidden sm:inline">🔍 巡检中心</span>
                </button>

                <button onclick="switchTab('logs')" id="nav-logs" class="nav-btn w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition text-slate-400 hover:text-slate-200 hover:bg-slate-700/30">
                    <i class="fa-solid fa-terminal text-lg w-5 text-center"></i>
                    <span class="hidden sm:inline">📜 日志中心</span>
                </button>

                <button onclick="switchTab('settings')" id="nav-settings" class="nav-btn w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition text-slate-400 hover:text-slate-200 hover:bg-slate-700/30">
                    <i class="fa-solid fa-gear text-lg w-5 text-center"></i>
                    <span class="hidden sm:inline">🛠 系统设置</span>
                </button>
            </nav>

            <div class="p-3 border-t border-slate-700/50 hidden sm:block">
                <div class="text-[11px] text-slate-500 text-center">
                    Serverless Matrix Architecture<br>Powered by Cloudflare & GitHub
                </div>
            </div>
        </aside>

        <!-- 右侧主内容展示区域 -->
        <main class="flex-1 bg-slate-900 p-4 sm:p-6 overflow-y-auto">
            
            <!-- 1. 📊 运行概览 Tab -->
            <section id="tab-overview" class="tab-content space-y-6">
                <div class="grid grid-cols-2 lg:grid-cols-4 gap-4">
                    <div class="bg-slate-800/80 rounded-xl p-4 border border-slate-700/60 shadow-lg">
                        <div class="text-xs font-medium text-slate-400 mb-1">点播频道总数</div>
                        <div class="text-2xl font-bold text-emerald-400">{site_cnt} <span class="text-xs font-normal text-slate-400">个</span></div>
                    </div>
                    <div class="bg-slate-800/80 rounded-xl p-4 border border-slate-700/60 shadow-lg">
                        <div class="text-xs font-medium text-slate-400 mb-1">直播源站总数</div>
                        <div class="text-2xl font-bold text-cyan-400">{live_cnt} <span class="text-xs font-normal text-slate-400">个</span></div>
                    </div>
                    <div class="bg-slate-800/80 rounded-xl p-4 border border-slate-700/60 shadow-lg">
                        <div class="text-xs font-medium text-slate-400 mb-1">解析接口总数</div>
                        <div class="text-2xl font-bold text-indigo-400">{parse_cnt} <span class="text-xs font-normal text-slate-400">个</span></div>
                    </div>
                    <div class="bg-slate-800/80 rounded-xl p-4 border border-slate-700/60 shadow-lg">
                        <div class="text-xs font-medium text-slate-400 mb-1">当前矩阵密锁</div>
                        <div class="text-xl font-bold text-amber-400 cursor-pointer select-none transition"
                             onclick="if(this.dataset.revealed==='true'){{this.innerText='🔒 *** 点击显示'; this.dataset.revealed='false';}}else{{this.innerText='{current_token}'; this.dataset.revealed='true';}}"
                             title="点击显示/隐藏">
                            🔒 *** 点击显示
                        </div>
                    </div>
                </div>

                <div class="bg-slate-800/80 rounded-xl p-5 border border-slate-700/60 shadow-lg">
                    <h3 class="text-sm font-bold text-slate-200 mb-4 flex items-center gap-2">
                        <i class="fa-solid fa-list-check text-emerald-400"></i>
                        已打包部署的订阅清单 ({file_num} 个)
                    </h3>
                    <div class="space-y-3">
{file_cards}
                    </div>
                </div>
            </section>

            <!-- 2. ⚙️ 控制中心 Tab -->
            <section id="tab-control" class="tab-content hidden space-y-6">
                <div class="bg-slate-800/80 rounded-xl p-6 border border-slate-700/60 shadow-lg space-y-6">
                    <div>
                        <h3 class="text-base font-bold text-white flex items-center gap-2">
                            <i class="fa-solid fa-bolt text-amber-400"></i>
                            快捷触发与一键运维
                        </h3>
                        <p class="text-xs text-slate-400 mt-1">通过 GitHub REST API 实时调度 Action 自动化矩阵构建总线或重置矩阵密锁。</p>
                    </div>
                    
                    <div class="grid grid-cols-1 sm:grid-cols-2 gap-4 pt-2">
                        <div class="bg-slate-900/60 p-4 rounded-xl border border-slate-700/60 space-y-3">
                            <div class="text-xs font-bold text-slate-200 flex items-center gap-2">
                                <i class="fa-solid fa-rotate text-emerald-400"></i>
                                常规手动编译
                            </div>
                            <p class="text-[11px] text-slate-400">保持当前密码锁不变，仅同步上游最新接口与手工区规则。</p>
                            <button onclick="triggerDispatch()" class="w-full py-2 bg-emerald-600 hover:bg-emerald-500 text-white rounded-lg text-xs font-bold transition flex items-center justify-center gap-2 shadow-lg shadow-emerald-600/20">
                                <i class="fa-solid fa-play"></i>
                                一键触发常规构建
                            </button>
                        </div>

                        <div class="bg-slate-900/60 p-4 rounded-xl border border-slate-700/60 space-y-3">
                            <div class="text-xs font-bold text-slate-200 flex items-center gap-2">
                                <i class="fa-solid fa-key text-amber-400"></i>
                                强行更换矩阵密锁 (炸旧换新)
                            </div>
                            <p class="text-[11px] text-slate-400">生成新 3 位随机锁并提交 Git，旧接口即刻触发陷阱轰炸并下发 TG 通知。</p>
                            <button onclick="resetMatrixToken()" class="w-full py-2 bg-amber-600 hover:bg-amber-500 text-white rounded-lg text-xs font-bold transition flex items-center justify-center gap-2 shadow-lg shadow-amber-600/20">
                                <i class="fa-solid fa-arrows-rotate"></i>
                                强行生成新锁并重新编译
                            </button>
                        </div>

                        <div class="bg-slate-900/60 p-4 rounded-xl border border-slate-700/60 space-y-3 sm:col-span-2">
                            <div class="text-xs font-bold text-slate-200 flex items-center gap-2">
                                <i class="fa-paper-plane text-sky-400"></i>
                                Telegram 频道一键直发广播
                            </div>
                            <p class="text-[11px] text-slate-400">无需打开客户端，在此输入自定义文字即可通过 Bot 实时下发广播消息到 TG 频道。</p>
                            <textarea id="tg_broadcast_text" rows="2" class="w-full bg-slate-950 border border-slate-700 rounded-lg p-2.5 text-xs text-sky-300 font-mono focus:outline-none focus:border-sky-500" placeholder="输入你想广播的消息内容 (支持 Markdown)..."></textarea>
                            <button onclick="sendTgBroadcast()" class="px-4 py-2 bg-sky-600 hover:bg-sky-500 text-white rounded-lg text-xs font-bold transition flex items-center justify-center gap-2 shadow-lg shadow-sky-600/20">
                                <i class="fa-paper-plane"></i>
                                发送广播到 TG 频道
                            </button>
                        </div>
                    </div>
                </div>
            </section>

            <!-- 3. 📦 资源管理 Tab -->
            <section id="tab-resources" class="tab-content hidden space-y-6">
                <div class="bg-slate-800/80 rounded-xl p-6 border border-slate-700/60 shadow-lg space-y-6">
                    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-700/80 pb-4">
                        <div>
                            <h3 class="text-base font-bold text-white flex items-center gap-2">
                                <i class="fa-solid fa-filter text-cyan-400"></i>
                                全量矩阵规则与黑名单控制面板
                            </h3>
                            <p class="text-xs text-slate-400 mt-1">直接在线修改 datas/settings.json，自动提交 Git 仓库并触发重新编译。</p>
                        </div>
                        <button onclick="saveSettingsToGithub()" class="px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-lg text-xs font-bold transition flex items-center gap-2 shadow-lg shadow-blue-600/20">
                            <i class="fa-solid fa-floppy-disk"></i>
                            保存全量变更提交 Git
                        </button>
                    </div>

                    <!-- 🎯 动态新增：三方上游底包源地址区 -->
                    <div class="bg-slate-900/60 p-4 rounded-xl border border-slate-700/60 space-y-3">
                        <div class="text-xs font-bold text-cyan-400 flex items-center gap-2">
                            <i class="fa-solid fa-cloud-arrow-down"></i>
                            三方上游底包源地址 (支持修改更换)
                        </div>
                        <div class="grid grid-cols-1 gap-3">
                            <div>
                                <label class="block text-[11px] font-semibold text-slate-300 mb-1">CNB 底包接口地址 (cnb.json)</label>
                                <input type="text" id="input_cnb_source_url" class="w-full bg-slate-950 border border-slate-700 rounded-lg p-2 text-xs text-cyan-300 font-mono focus:border-blue-500 focus:outline-none">
                            </div>
                            <div>
                                <label class="block text-[11px] font-semibold text-slate-300 mb-1">海豚底包接口地址 (dol.json)</label>
                                <input type="text" id="input_haitun_source_url" class="w-full bg-slate-950 border border-slate-700 rounded-lg p-2 text-xs text-cyan-300 font-mono focus:border-blue-500 focus:outline-none">
                            </div>
                            <div>
                                <label class="block text-[11px] font-semibold text-slate-300 mb-1">LZ 底包接口地址 (lz.json)</label>
                                <input type="text" id="input_lz_source_url" class="w-full bg-slate-950 border border-slate-700 rounded-lg p-2 text-xs text-cyan-300 font-mono focus:border-blue-500 focus:outline-none">
                            </div>
                            <div>
    <label class="block text-[11px] font-semibold text-slate-300 mb-1">第四底包接口地址 (dol2.json)</label>
    <input type="text" id="input_dol2_source_url" class="w-full bg-slate-950 border border-slate-700 rounded-lg p-2 text-xs text-cyan-300 font-mono focus:border-blue-500 focus:outline-none">
</div>
                        </div>
                    </div>
                    
                    <div class="grid grid-cols-1 sm:grid-cols-2 gap-4 border-b border-slate-700/80 pb-4">
                        <div>
                            <label class="block text-xs font-bold text-slate-300 mb-1">FOOTER_TEXT (公开页底部版权声明/页脚文案)</label>
                            <input type="text" id="input_footer_text" class="w-full bg-slate-900 border border-slate-700 rounded-lg p-2.5 text-xs text-white focus:border-blue-500 focus:outline-none">
                        </div>
                    
                        <div>
                            <label class="block text-xs font-bold text-emerald-400 mb-1">MARQUEE_NOTICE_TEXT (公开页跑马灯流动公告内容)</label>
                            <input type="text" id="input_marquee_notice_text" class="w-full bg-slate-900 border border-slate-700 rounded-lg p-2.5 text-xs text-white focus:border-blue-500 focus:outline-none">
                        </div>
                        <div>
                            <label class="block text-xs font-bold text-slate-200 mb-1">MY_QQ_GROUP (交流 QQ 群号)</label>
                            <input type="text" id="input_my_qq_group" class="w-full bg-slate-900 border border-slate-700 rounded-lg p-2.5 text-xs text-white focus:border-blue-500 focus:outline-none">
                        </div>
                        <div>
                            <label class="block text-xs font-bold text-slate-200 mb-1">MY_PROMO_CHANNEL (TG 宣传频道账号)</label>
                            <input type="text" id="input_my_promo_channel" class="w-full bg-slate-900 border border-slate-700 rounded-lg p-2.5 text-xs text-white focus:border-blue-500 focus:outline-none">
                        </div>
                        <div>
                            <label class="block text-xs font-bold text-slate-200 mb-1">MY_TG_SUFFIX (接口名称 TG 后缀后缀)</label>
                            <input type="text" id="input_my_tg_suffix" class="w-full bg-slate-900 border border-slate-700 rounded-lg p-2.5 text-xs text-white focus:border-blue-500 focus:outline-none">
                        </div>
                        <div>
                            <label class="block text-xs font-bold text-slate-200 mb-1">LOGO_PREFIX (接口图标前缀)</label>
                            <input type="text" id="input_logo_prefix" class="w-full bg-slate-900 border border-slate-700 rounded-lg p-2.5 text-xs text-white focus:border-blue-500 focus:outline-none">
                        </div>
                        <div>
                            <label class="block text-xs font-bold text-slate-200 mb-1">BASE_OUTPUT_FULL (全量版前缀文件名)</label>
                            <input type="text" id="input_base_output_full" class="w-full bg-slate-900 border border-slate-700 rounded-lg p-2.5 text-xs text-white focus:border-blue-500 focus:outline-none">
                        </div>
                        <div>
                            <label class="block text-xs font-bold text-slate-200 mb-1">BASE_OUTPUT_CLEAN (纯净版前缀文件名)</label>
                            <input type="text" id="input_base_output_clean" class="w-full bg-slate-900 border border-slate-700 rounded-lg p-2.5 text-xs text-white focus:border-blue-500 focus:outline-none">
                        </div>
                    </div>

                    <!-- 文本公告与轰炸文案编辑区 -->
                    <div class="space-y-4 border-b border-slate-700/80 pb-4">
                        <div>
                            <label class="block text-xs font-bold text-amber-400 mb-1">WELCOME_NOTICE_FULL (全量版进软件弹窗公告)</label>
                            <textarea id="input_welcome_notice_full" rows="2" class="w-full bg-slate-900 border border-slate-700 rounded-lg p-2.5 text-xs text-white focus:border-blue-500 focus:outline-none"></textarea>
                        </div>
                        <div>
                            <label class="block text-xs font-bold text-emerald-400 mb-1">WELCOME_NOTICE_CLEAN (纯净版进软件弹窗公告)</label>
                            <textarea id="input_welcome_notice_clean" rows="2" class="w-full bg-slate-900 border border-slate-700 rounded-lg p-2.5 text-xs text-white focus:border-blue-500 focus:outline-none"></textarea>
                        </div>
                        <div>
                            <label class="block text-xs font-bold text-slate-300 mb-1">THANKS_WARNING (弹窗底部通用追加警示尾巴)</label>
                            <input type="text" id="input_thanks_warning" class="w-full bg-slate-900 border border-slate-700 rounded-lg p-2.5 text-xs text-white focus:border-blue-500 focus:outline-none">
                        </div>
                        <div>
                            <label class="block text-xs font-bold text-rose-400 mb-1">TRAP_NOTICE_TEXT (金蝉脱壳爆破 - 陷阱根节点公告)</label>
                            <textarea id="input_trap_notice_text" rows="2" class="w-full bg-slate-900 border border-slate-700 rounded-lg p-2.5 text-xs text-white focus:border-blue-500 focus:outline-none"></textarea>
                        </div>
                        <div>
                            <label class="block text-xs font-bold text-slate-300 mb-1">TRAP_SITE_NAME_1 (陷阱点播源名称 1)</label>
                            <input type="text" id="input_trap_site_name_1" class="w-full bg-slate-900 border border-slate-700 rounded-lg p-2.5 text-xs text-white focus:border-blue-500 focus:outline-none">
                        </div>
                        <div>
                            <label class="block text-xs font-bold text-slate-300 mb-1">TRAP_SITE_NAME_2 (陷阱点播源名称 2)</label>
                            <input type="text" id="input_trap_site_name_2" class="w-full bg-slate-900 border border-slate-700 rounded-lg p-2.5 text-xs text-white focus:border-blue-500 focus:outline-none">
                        </div>
                        <div>
                            <label class="block text-xs font-bold text-slate-300 mb-1">TRAP_LIVE_GROUP (陷阱直播源分组名称)</label>
                            <input type="text" id="input_trap_live_group" class="w-full bg-slate-900 border border-slate-700 rounded-lg p-2.5 text-xs text-white focus:border-blue-500 focus:outline-none">
                        </div>
                        <div>
                            <label class="block text-xs font-bold text-slate-300 mb-1">TRAP_LIVE_CHANNEL (陷阱直播频道名称)</label>
                            <input type="text" id="input_trap_live_channel" class="w-full bg-slate-900 border border-slate-700 rounded-lg p-2.5 text-xs text-white focus:border-blue-500 focus:outline-none">
                        </div>
                    </div>
                    <!-- 🎯 动态新增：打赏区配置 -->
<div class="sm:col-span-2 bg-slate-900/60 p-4 rounded-xl border border-slate-700/60 space-y-3">
    <div class="text-xs font-bold text-rose-400 flex items-center gap-2">
        <i class="fa-solid fa-mug-hot"></i>
        打赏/赞赏功能设置
    </div>
    <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
        <div>
            <label class="block text-[11px] font-semibold text-slate-300 mb-1">DONATE_QR_URL (赞赏收款码图片 URL，留空则不展示打赏区)</label>
            <input type="text" id="input_donate_qr_url" class="w-full bg-slate-950 border border-slate-700 rounded-lg p-2 text-xs text-rose-300 font-mono focus:border-blue-500 focus:outline-none" placeholder="https://img.naixiai.cn/2026/06/18/IMG_6638.jpeg">
        </div>
        <div>
            <label class="block text-[11px] font-semibold text-slate-300 mb-1">DONATE_NOTICE_TEXT (打赏温馨文案)</label>
            <input type="text" id="input_donate_notice_text" class="w-full bg-slate-950 border border-slate-700 rounded-lg p-2 text-xs text-slate-200 focus:border-blue-500 focus:outline-none">
        </div>
    </div>
</div>

                    <!-- Telegram 推送模板编辑区 -->
                    <div class="space-y-4">
                        <div>
                            <label class="block text-xs font-bold text-sky-400 mb-1">TG_PWD_MSG_TEMPLATE (Telegram 换锁推送 Markdown 模板)</label>
                            <textarea id="input_tg_pwd_msg_template" rows="5" class="w-full bg-slate-900 border border-slate-700 rounded-lg p-2.5 text-xs text-sky-300 font-mono focus:border-blue-500 focus:outline-none"></textarea>
                        </div>
                        <div>
                            <label class="block text-xs font-bold text-sky-400 mb-1">TG_UPDATE_MSG_TEMPLATE (Telegram 接口变更推送 Markdown 模板)</label>
                            <textarea id="input_tg_update_msg_template" rows="5" class="w-full bg-slate-900 border border-slate-700 rounded-lg p-2.5 text-xs text-sky-300 font-mono focus:border-blue-500 focus:outline-none"></textarea>
                        </div>
                    </div>

                    <div class="grid grid-cols-1 sm:grid-cols-2 gap-4 border-b border-slate-700/80 pb-4">
                        <div>
                            <label class="block text-xs font-bold text-slate-200 mb-1">GLOBAL_SPIDER_JAR (全局主蜘蛛 Jar 地址)</label>
                            <input type="text" id="input_global_spider_jar" class="w-full bg-slate-900 border border-slate-700 rounded-lg p-2.5 text-xs text-white focus:border-blue-500 focus:outline-none">
                        </div>
                        <div>
                            <label class="block text-xs font-bold text-slate-200 mb-1">DEFAULT_LOGO_URL (默认 Logo 图片地址)</label>
                            <input type="text" id="input_default_logo_url" class="w-full bg-slate-900 border border-slate-700 rounded-lg p-2.5 text-xs text-white focus:border-blue-500 focus:outline-none">
                        </div>
                        <div>
                            <label class="block text-xs font-bold text-slate-200 mb-1">SITE_INSERT_POS (手工点播源插入位置)</label>
                            <input type="number" id="input_site_insert_pos" class="w-full bg-slate-900 border border-slate-700 rounded-lg p-2.5 text-xs text-white focus:border-blue-500 focus:outline-none">
                        </div>
                        <div>
                            <label class="block text-xs font-bold text-slate-200 mb-1">INSERT_POS (手工直播源插入位置)</label>
                            <input type="number" id="input_insert_pos" class="w-full bg-slate-900 border border-slate-700 rounded-lg p-2.5 text-xs text-white focus:border-blue-500 focus:outline-none">
                        </div>
                        <div>
                            <label class="block text-xs font-bold text-slate-200 mb-1">HOT_VIDEO_KEY (首页置顶热门站 Key)</label>
                            <input type="text" id="input_hot_video_key" class="w-full bg-slate-900 border border-slate-700 rounded-lg p-2.5 text-xs text-white focus:border-blue-500 focus:outline-none">
                        </div>
                        <div>
                            <label class="block text-xs font-bold text-slate-200 mb-1">HOT_VIDEO_SITE_NAME (首页置顶热门站显示名称)</label>
                            <input type="text" id="input_hot_video_site_name" class="w-full bg-slate-900 border border-slate-700 rounded-lg p-2.5 text-xs text-white focus:border-blue-500 focus:outline-none">
                        </div>
                        <!-- 🎯 动态新增：公开主页隐秘模式控制开关 -->
<div class="sm:col-span-2 bg-slate-900/60 p-3.5 rounded-xl border border-slate-700/60 flex items-center justify-between">
    <div>
        <label class="text-xs font-bold text-amber-400 flex items-center gap-2">
            <i class="fa-solid fa-eye-slash"></i>
            SHOW_PUBLIC_DETAILS (公开主页展示真实订阅链接与密锁)
        </label>
        <p class="text-[11px] text-slate-400 mt-0.5">开启时公开主页直接展示真实 JSON 链接与密锁；关闭时隐藏敏感信息并引导加群。</p>
    </div>
    <label class="relative inline-flex items-center cursor-pointer">
        <input type="checkbox" id="input_show_public_details" class="sr-only peer" checked>
        <div class="w-11 h-6 bg-slate-700 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-slate-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-emerald-500"></div>
    </label>
</div>
                    </div>

                    <div class="space-y-5">
                        <div class="space-y-2">
                            <label class="text-xs font-bold text-slate-200 flex items-center gap-2">
                                <span class="w-2 h-2 rounded-full bg-emerald-400"></span>
                                BLOCK_KEYWORDS (全局名称/关键字黑名单)
                            </label>
                            <textarea id="json_block_keywords" rows="3" class="w-full bg-slate-900 border border-slate-700 rounded-lg p-3 text-xs text-emerald-400 font-mono focus:outline-none focus:border-blue-500" placeholder='["词1", "词2"]'></textarea>
                        </div>

                        <div class="space-y-2">
                            <label class="text-xs font-bold text-slate-200 flex items-center gap-2">
                                <span class="w-2 h-2 rounded-full bg-cyan-400"></span>
                                UPSTREAM_DIRTY_WORDS (上游强力广告剔除词)
                            </label>
                            <textarea id="json_upstream_dirty" rows="3" class="w-full bg-slate-900 border border-slate-700 rounded-lg p-3 text-xs text-cyan-400 font-mono focus:outline-none focus:border-blue-500" placeholder='["广告词1", "广告词2"]'></textarea>
                        </div>

                        <div class="space-y-2">
                            <label class="text-xs font-bold text-slate-200 flex items-center gap-2">
                                <span class="w-2 h-2 rounded-full bg-amber-400"></span>
                                NSFW_KEYWORDS (纯净版客厅专线剔除词)
                            </label>
                            <textarea id="json_nsfw_keywords" rows="3" class="w-full bg-slate-900 border border-slate-700 rounded-lg p-3 text-xs text-amber-400 font-mono focus:outline-none focus:border-blue-500" placeholder='["🔞", "福利"]'></textarea>
                        </div>
                        <div class="space-y-2">
    <label class="text-xs font-bold text-slate-200 flex items-center gap-2">
        <span class="w-2 h-2 rounded-full bg-emerald-400"></span>
        ALLOW_NSFW_KEYWORDS (纯净版特许放行白名单，保留线路并强行去掉 🔞 标识)
    </label>
    <textarea id="json_allow_nsfw_keywords" rows="2" class="w-full bg-slate-900 border border-slate-700 rounded-lg p-3 text-xs text-emerald-300 font-mono focus:outline-none focus:border-blue-500" placeholder='["易发"]'></textarea>
</div>

                        <div class="space-y-2">
                            <label class="text-xs font-bold text-slate-200 flex items-center gap-2">
                                <span class="w-2 h-2 rounded-full bg-rose-400"></span>
                                BLOCK_MALICIOUS_KEYWORDS (全线恶意杂质直接丢弃词)
                            </label>
                            <textarea id="json_malicious_keywords" rows="2" class="w-full bg-slate-900 border border-slate-700 rounded-lg p-3 text-xs text-rose-400 font-mono focus:outline-none focus:border-blue-500" placeholder='["恶意词1"]'></textarea>
                        </div>

                        <div class="space-y-2">
                            <label class="text-xs font-bold text-slate-200 flex items-center gap-2">
                                <span class="w-2 h-2 rounded-full bg-indigo-400"></span>
                                NO_SEARCH_KEYWORDS (命中的站点自动关闭全局搜索 searchable = 0)
                            </label>
                            <textarea id="json_no_search_keywords" rows="6" class="w-full bg-slate-900 border border-slate-700 rounded-lg p-3 text-xs text-indigo-400 font-mono focus:outline-none focus:border-blue-500" placeholder='["接口全名或关键词"]'></textarea>
                        </div>
                        <div class="space-y-2">
                            <label class="text-xs font-bold text-slate-200 flex items-center gap-2">
                                <span class="w-2 h-2 rounded-full bg-purple-400"></span>
                                MY_CUSTOM_SITES (老杨专属手工点播加线配置 - JSON 数组)
                            </label>
                            <textarea id="json_my_custom_sites" rows="8" class="w-full bg-slate-900 border border-slate-700 rounded-lg p-3 text-xs text-purple-300 font-mono focus:outline-none focus:border-blue-500" placeholder='[[{{"key": "xxx", "name": "xxx", "type": 3, "api": "xxx"}}]]'></textarea>
                        </div>

                        <div class="space-y-2">
                            <label class="text-xs font-bold text-slate-200 flex items-center gap-2">
                                <span class="w-2 h-2 rounded-full bg-teal-400"></span>
                                MY_CUSTOM_LIVES (老杨专属手工直播加线配置 - JSON 数组)
                            </label>
                            <textarea id="json_my_custom_lives" rows="8" class="w-full bg-slate-900 border border-slate-700 rounded-lg p-3 text-xs text-teal-300 font-mono focus:outline-none focus:border-blue-500" placeholder='[[{{"name": "xxx", "type": 0, "url": "xxx"}}]]'></textarea>
                        </div>
                    </div>
                </div>
            </section>

            <!-- 4. 🔍 巡检中心 Tab -->
            <section id="tab-inspect" class="tab-content hidden space-y-6">
                <div class="bg-slate-800/80 rounded-xl p-6 border border-slate-700/60 shadow-lg space-y-4">
                    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-700/80 pb-4">
                        <div>
                            <h3 class="text-base font-bold text-white flex items-center gap-2">
                                <i class="fa-solid fa-microscope text-indigo-400"></i>
                                多线程探针与全量接口实时巡检
                            </h3>
                            <p class="text-xs text-slate-400 mt-1">多并发探测当前最新全量 JSON 订阅中的点播接口与直播源可用性。</p>
                        </div>
                        
                        <div class="flex items-center gap-2">
                            <button onclick="startInspection()" id="btnStartInspect" class="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg text-xs font-bold transition flex items-center gap-2">
                                <i class="fa-solid fa-play"></i>
                                开始并发巡检
                            </button>
                            <button onclick="purgeDeadSites()" id="btnPurgeDead" class="hidden px-4 py-2 bg-rose-600 hover:bg-rose-500 text-white rounded-lg text-xs font-bold transition items-center gap-2">
                                <i class="fa-solid fa-trash-can"></i>
                                一键拉黑剔除失效源
                            </button>
                        </div>
                    </div>

                    <div id="inspectStats" class="grid grid-cols-2 sm:grid-cols-4 gap-3 text-center">
                        <div class="bg-slate-900/80 p-3 rounded-lg border border-slate-800">
                            <div class="text-[11px] text-slate-400">已扫描 / 总数</div>
                            <div class="text-lg font-bold text-slate-200" id="stat_total">0 / 0</div>
                        </div>
                        <div class="bg-slate-900/80 p-3 rounded-lg border border-slate-800">
                            <div class="text-[11px] text-emerald-400">正常响应 (OK)</div>
                            <div class="text-lg font-bold text-emerald-400" id="stat_ok">0</div>
                        </div>
                        <div class="bg-slate-900/80 p-3 rounded-lg border border-slate-800">
                            <div class="text-[11px] text-amber-400">高延迟 (>2000ms)</div>
                            <div class="text-lg font-bold text-amber-400" id="stat_slow">0</div>
                        </div>
                        <div class="bg-slate-900/80 p-3 rounded-lg border border-slate-800">
                            <div class="text-[11px] text-rose-400">失效 / 404 / 超时</div>
                            <div class="text-lg font-bold text-rose-400" id="stat_dead">0</div>
                        </div>
                    </div>

                    <div id="inspectConsole" class="bg-slate-950 rounded-xl p-4 border border-slate-800 text-xs font-mono space-y-1.5 max-h-[28rem] overflow-y-auto">
                        <div class="text-slate-500">// 点击上方“开始并发巡检”按钮启动网络探针...</div>
                    </div>
                </div>
            </section>

            <!-- 5. 📜 日志中心 Tab -->
            <section id="tab-logs" class="tab-content hidden space-y-6">
                <div class="bg-slate-800/80 rounded-xl p-6 border border-slate-700/60 shadow-lg space-y-4">
                    <h3 class="text-base font-bold text-white flex items-center gap-2">
                        <i class="fa-solid fa-list-ol text-emerald-400"></i>
                        Git 提交与编译日志流
                    </h3>
                    <p class="text-xs text-slate-400">实时调取 GitHub Repo 最近 Commit 历史记录。</p>
                    <div id="commitLogsContainer" class="space-y-2 text-xs font-mono">
                        <div class="text-slate-500">点击拉取或载入中...</div>
                    </div>
                </div>
            </section>

            <!-- 6. 🛠 系统设置 Tab -->
            <section id="tab-settings" class="tab-content hidden space-y-6">
                <div class="bg-slate-800/80 rounded-xl p-6 border border-slate-700/60 shadow-lg space-y-4">
                    <h3 class="text-base font-bold text-white flex items-center gap-2">
                        <i class="fa-solid fa-key text-amber-400"></i>
                        GitHub API Token 与凭据管理
                    </h3>
                    <p class="text-xs text-slate-400">配置 Personal Access Token (PAT)，赋予控制台对仓库的读写与 Workflow 执行权限。</p>

                    <div class="space-y-4 pt-2 max-w-xl">
                        <div>
                            <label class="block text-xs font-medium text-slate-300 mb-1">GitHub Personal Access Token (PAT)</label>
                            <input type="password" id="input_github_token" class="w-full bg-slate-900 border border-slate-700 rounded-lg p-2.5 text-xs text-white focus:border-blue-500 focus:outline-none" placeholder="ghp_xxxxxxxxxxxx">
                        </div>

                        <div>
                            <label class="block text-xs font-medium text-slate-300 mb-1">GitHub 仓库 (Owner/Repo)</label>
                            <input type="text" id="input_github_repo" class="w-full bg-slate-900 border border-slate-700 rounded-lg p-2.5 text-xs text-white focus:border-blue-500 focus:outline-none" placeholder="GodLike631/Ly_me">
                        </div>

                        <div>
                            <label class="block text-xs font-medium text-slate-300 mb-1">默认分支 (Branch)</label>
                            <input type="text" id="input_github_branch" class="w-full bg-slate-900 border border-slate-700 rounded-lg p-2.5 text-xs text-white focus:border-blue-500 focus:outline-none" value="main">
                        </div>

                        <button onclick="saveAuthSettings()" class="px-5 py-2.5 bg-blue-600 hover:bg-blue-500 text-white rounded-xl text-xs font-bold transition">
                            保存鉴权凭据到本地
                        </button>
                    </div>
                </div>
            </section>

        </main>
    </div>

    <!-- PAT 鉴权设置 Modal 弹窗 -->
    <div id="authModal" class="hidden fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4">
        <div class="bg-slate-800 rounded-2xl border border-slate-700 max-w-md w-full p-6 shadow-2xl space-y-4">
            <div class="flex justify-between items-center border-b border-slate-700 pb-3">
                <h3 class="text-sm font-bold text-white flex items-center gap-2">
                    <i class="fa-solid fa-lock text-amber-400"></i>
                    配置 GitHub PAT 访问凭据
                </h3>
                <button onclick="closeTokenModal()" class="text-slate-400 hover:text-white"><i class="fa-solid fa-xmark"></i></button>
            </div>
            
            <p class="text-xs text-slate-400 leading-relaxed">
                为实现控制台保存黑名单、一键编译等无感知运维操作，请填入具有 <code class="text-amber-400">repo</code> 及 <code class="text-amber-400">workflow</code> 权限的 GitHub Token。
            </p>

            <div class="space-y-3">
                <input type="password" id="modal_token" class="w-full bg-slate-900 border border-slate-700 rounded-lg p-2.5 text-xs text-white focus:border-blue-500 focus:outline-none" placeholder="ghp_xxx 或 github_pat_xxx">
                <input type="text" id="modal_repo" class="w-full bg-slate-900 border border-slate-700 rounded-lg p-2.5 text-xs text-white focus:border-blue-500 focus:outline-none" placeholder="仓库路径: GodLike631/Ly_me">
            </div>

            <div class="flex justify-end gap-2 pt-2">
                <button onclick="closeTokenModal()" class="px-4 py-2 bg-slate-700 hover:bg-slate-600 text-xs font-medium rounded-lg text-slate-300">取消</button>
                <button onclick="saveModalAuth()" class="px-4 py-2 bg-blue-600 hover:bg-blue-500 text-xs font-medium rounded-lg text-white">确认并绑定</button>
            </div>
        </div>
    </div>

    <!-- 全局点播与直播巡检数据源动态注入点 -->
    <script>
        window.sites = {sites_json};
        window.lives = {lives_json};
        let deadSiteNames = [];
    </script>
    <!-- 控制台核心 JS 逻辑流 -->
    <script>
    function switchTab(tabKey) {{
        document.querySelectorAll('.tab-content').forEach(el => el.classList.add('hidden'));
        document.querySelectorAll('.nav-btn').forEach(el => {{
            el.classList.remove('text-emerald-400', 'bg-slate-700/60');
            el.classList.add('text-slate-400');
        }});

        const targetTab = document.getElementById('tab-' + tabKey);
        const targetNav = document.getElementById('nav-' + tabKey);
        if (targetTab) targetTab.classList.remove('hidden');
        if (targetNav) {{
            targetNav.classList.add('text-emerald-400', 'bg-slate-700/60');
            targetNav.classList.remove('text-slate-400');
        }}

        if (tabKey === 'resources') loadSettingsFromGithub();
        if (tabKey === 'logs') loadCommitLogs();
    }}

    function getStoredAuth() {{
        return {{
            token: localStorage.getItem('gh_pat') || '',
            repo: localStorage.getItem('gh_repo') || '',
            branch: localStorage.getItem('gh_branch') || 'main'
        }};
    }}

    function updateAuthUI() {{
        const auth = getStoredAuth();
        const badge = document.getElementById('authStatusBadge');
        const text = document.getElementById('authStatusText');
        
        if (auth.token && auth.repo) {{
            badge.classList.remove('bg-amber-500/10', 'text-amber-400', 'border-amber-500/20');
            badge.classList.add('bg-emerald-500/10', 'text-emerald-400', 'border-emerald-500/20');
            text.innerText = 'GitHub Token 已就绪 (' + auth.repo + ')';
        }} else {{
            badge.classList.add('bg-amber-500/10', 'text-amber-400', 'border-amber-500/20');
            badge.classList.remove('bg-emerald-500/10', 'text-emerald-400', 'border-emerald-500/20');
            text.innerText = '未绑定 Token (功能受限)';
        }}

        document.getElementById('input_github_token').value = auth.token;
        document.getElementById('input_github_repo').value = auth.repo;
        document.getElementById('input_github_branch').value = auth.branch;
    }}

    function openTokenModal() {{
        const auth = getStoredAuth();
        document.getElementById('modal_token').value = auth.token;
        document.getElementById('modal_repo').value = auth.repo;
        document.getElementById('authModal').classList.remove('hidden');
    }}

    function closeTokenModal() {{
        document.getElementById('authModal').classList.add('hidden');
    }}

    function saveModalAuth() {{
        const token = document.getElementById('modal_token').value.trim();
        const repo = document.getElementById('modal_repo').value.trim();
        if (token) localStorage.setItem('gh_pat', token);
        if (repo) localStorage.setItem('gh_repo', repo);
        closeTokenModal();
        updateAuthUI();
        alert('凭据已成功保存！');
    }}

    function saveAuthSettings() {{
        const token = document.getElementById('input_github_token').value.trim();
        const repo = document.getElementById('input_github_repo').value.trim();
        const branch = document.getElementById('input_github_branch').value.trim();
        localStorage.setItem('gh_pat', token);
        localStorage.setItem('gh_repo', repo);
        localStorage.setItem('gh_branch', branch);
        updateAuthUI();
        alert('系统设置已更新！');
    }}

    async function triggerDispatch() {{
        const auth = getStoredAuth();
        if (!auth.token || !auth.repo) {{
            alert('请先配置 GitHub PAT 与仓库路径！');
            return openTokenModal();
        }}

        if (!confirm('确定要发起一键手动编译吗？系统将在 GitHub Actions 后台启动流水线。')) return;

        const url = `https://api.github.com/repos/${{auth.repo}}/actions/workflows/auto-fetch.yml/dispatches`;
        
        try {{
            const res = await fetch(url, {{
                method: 'POST',
                headers: {{
                    'Authorization': `token ${{auth.token}}`,
                    'Accept': 'application/vnd.github.v3+json',
                    'Content-Type': 'application/json'
                }},
                body: JSON.stringify({{ ref: auth.branch }})
            }});

            if (res.status === 204) {{
                alert('🚀 编译指令已成功成功下发！GitHub Actions 已开始运行！');
            }} else {{
                const errData = await res.json().catch(() => ({{}}));
                alert(`⚠️ 触发失败 (${{res.status}}): ${{errData.message || '请检查 YAML 文件名称或 Token 权限'}}`);
            }}
        }} catch (e) {{
            alert('请求发生错误: ' + e.message);
        }}
    }}

    async function resetMatrixToken() {{
        const auth = getStoredAuth();
        if (!auth.token || !auth.repo) {{
            alert('请先配置 GitHub PAT 与仓库路径！');
            return openTokenModal();
        }}

        const chars = 'abcdefghijklmnopqrstuvwxyz0123456789';
        let newToken = '';
        for (let i = 0; i < 3; i++) {{
            newToken += chars.charAt(Math.floor(Math.random() * chars.length));
        }}

        const inputToken = prompt('请输入想要设置的新密锁（直接回车将随机生成 3 位字符）:', newToken);
        if (inputToken === null) return;
        
        const finalToken = inputToken.trim() || newToken;

        if (!confirm(`确定要将矩阵密锁重置为【 ${{finalToken}} 】吗？\\n\\n这会导致老接口链接彻底失效炸毁，并触发 Telegram 换锁推送！`)) return;

        try {{
            const url = `https://api.github.com/repos/${{auth.repo}}/contents/datas/控制开关.txt?ref=${{auth.branch}}`;
            const getRes = await fetch(url, {{ headers: {{ 'Authorization': `token ${{auth.token}}` }} }});
            
            let sha = '';
            let currentYM = '';
            let dayA = '01', dayB = '15';
            let savedCount = '1';

            // 🎯 读取现有文件内容，保留原有抽好的 DayA 和 DayB 计划
            if (getRes.ok) {{
                const getData = await getRes.json();
                sha = getData.sha;
                const oldContent = decodeURIComponent(escape(atob(getData.content))).trim();
                const parts = oldContent.split('-');
                if (parts.length === 6) {{
                    currentYM = parts[0];
                    savedCount = parts[1];
                    dayA = parts[2];
                    dayB = parts[3];
                }}
            }}

            const now = new Date();
            if (!currentYM) {{
                currentYM = `${{now.getFullYear()}}${{String(now.getMonth() + 1).padStart(2, '0')}}`;
            }}
            const currentDate = `${{now.getFullYear()}}${{String(now.getMonth() + 1).padStart(2, '0')}}${{String(now.getDate()).padStart(2, '0')}}`;

            // 🎯 按新标准格式写回：YYYYMM-count-dayA-dayB-lastDate-code
            const lockFileContent = `${{currentYM}}-${{savedCount}}-${{dayA}}-${{dayB}}-${{currentDate}}-${{finalToken}}`;
            const base64Content = btoa(unescape(encodeURIComponent(lockFileContent)));

            const putRes = await fetch(`https://api.github.com/repos/${{auth.repo}}/contents/datas/控制开关.txt`, {{
                method: 'PUT',
                headers: {{
                    'Authorization': `token ${{auth.token}}`,
                    'Content-Type': 'application/json'
                }},
                body: JSON.stringify({{
                    message: `🔑 控制台在线强行换锁重置为: ${{finalToken}}`,
                    content: base64Content,
                    sha: sha || undefined,
                    branch: auth.branch
                }})
            }});

            if (putRes.ok) {{
                alert(`✨ 密锁已成功更新为【 ${{finalToken}} 】并提交 Git！系统正在自动拉起 Actions 流水线进行大轰炸与新包编译...`);
            }} else {{
                const errData = await putRes.json();
                alert('换锁失败: ' + (errData.message || '权限不足或文件不存在'));
            }}
        }} catch (e) {{
            alert('请求发生错误: ' + e.message);
        }}
    }}

    let currentSettingsSha = '';

    async function loadSettingsFromGithub() {{
        const auth = getStoredAuth();
        if (!auth.token || !auth.repo) return;

        const url = `https://api.github.com/repos/${{auth.repo}}/contents/datas/settings.json?ref=${{auth.branch}}`;
        try {{
            const res = await fetch(url, {{
                headers: {{ 'Authorization': `token ${{auth.token}}` }}
            }});
            if (res.ok) {{
                const data = await res.json();
                currentSettingsSha = data.sha;
                const jsonText = decodeURIComponent(escape(atob(data.content)));
                const jsonObj = JSON.parse(jsonText);

                document.getElementById('json_block_keywords').value = JSON.stringify(jsonObj.BLOCK_KEYWORDS || [], null, 2);
                document.getElementById('json_upstream_dirty').value = JSON.stringify(jsonObj.UPSTREAM_DIRTY_WORDS || [], null, 2);
                document.getElementById('json_nsfw_keywords').value = JSON.stringify(jsonObj.NSFW_KEYWORDS || [], null, 2);
                document.getElementById('json_malicious_keywords').value = JSON.stringify(jsonObj.BLOCK_MALICIOUS_KEYWORDS || [], null, 2);
                document.getElementById('json_no_search_keywords').value = JSON.stringify(jsonObj.NO_SEARCH_KEYWORDS || [], null, 2);
                document.getElementById('json_my_custom_sites').value = JSON.stringify(jsonObj.MY_CUSTOM_SITES || [], null, 2);
                document.getElementById('json_my_custom_lives').value = JSON.stringify(jsonObj.MY_CUSTOM_LIVES || [], null, 2);
                document.getElementById('input_global_spider_jar').value = jsonObj.GLOBAL_SPIDER_JAR || '';
                document.getElementById('input_default_logo_url').value = jsonObj.DEFAULT_LOGO_URL || '';
                document.getElementById('input_site_insert_pos').value = jsonObj.SITE_INSERT_POS ?? 0;
                document.getElementById('input_insert_pos').value = jsonObj.INSERT_POS ?? 0;
                document.getElementById('input_hot_video_key').value = jsonObj.HOT_VIDEO_KEY || 'js_douban';
                document.getElementById('input_hot_video_site_name').value = jsonObj.HOT_VIDEO_SITE_NAME || '';
                document.getElementById('input_show_public_details').checked = jsonObj.SHOW_PUBLIC_DETAILS ?? true;
                document.getElementById('input_my_qq_group').value = jsonObj.MY_QQ_GROUP || '532637640';
                document.getElementById('input_my_promo_channel').value = jsonObj.MY_PROMO_CHANNEL || '@huliys9';
                document.getElementById('input_my_tg_suffix').value = jsonObj.MY_TG_SUFFIX || '｜Tg：@huliys9';
                document.getElementById('input_logo_prefix').value = jsonObj.LOGO_PREFIX || '🦋';
                document.getElementById('input_base_output_full').value = jsonObj.BASE_OUTPUT_FULL || '老杨TV全量版';
                document.getElementById('input_base_output_clean').value = jsonObj.BASE_OUTPUT_CLEAN || '老杨TV纯净版';
                document.getElementById('input_dol2_source_url').value = jsonObj.dol2_SOURCE_URL || 'https://你的第四个源地址.json';
                document.getElementById('json_allow_nsfw_keywords').value = JSON.stringify(jsonObj.ALLOW_NSFW_KEYWORDS || ["易发"], null, 2);

                document.getElementById('input_welcome_notice_full').value = jsonObj.WELCOME_NOTICE_FULL || '';
                document.getElementById('input_welcome_notice_clean').value = jsonObj.WELCOME_NOTICE_CLEAN || '';
                document.getElementById('input_thanks_warning').value = jsonObj.THANKS_WARNING || '';
                document.getElementById('input_trap_notice_text').value = jsonObj.TRAP_NOTICE_TEXT || '';
                document.getElementById('input_trap_site_name_1').value = jsonObj.TRAP_SITE_NAME_1 || '';
                document.getElementById('input_trap_site_name_2').value = jsonObj.TRAP_SITE_NAME_2 || '';
                document.getElementById('input_trap_live_group').value = jsonObj.TRAP_LIVE_GROUP || '';
                document.getElementById('input_trap_live_channel').value = jsonObj.TRAP_LIVE_CHANNEL || '';
                document.getElementById('input_donate_qr_url').value = jsonObj.DONATE_QR_URL || '';
                document.getElementById('input_donate_notice_text').value = jsonObj.DONATE_NOTICE_TEXT || '☕ 如果觉得本专线对你有帮助，欢迎请作者喝杯咖啡支持服务器与域名续费～';
                document.getElementById('input_marquee_notice_text').value = jsonObj.MARQUEE_NOTICE_TEXT || '📢 欢迎使用老杨TV专属缝合矩阵！本专线已完成全量广告清洗与无损极速重排，建议加社群获取最新变动！';
                document.getElementById('input_footer_text').value = jsonObj.FOOTER_TEXT || '© 2026 老杨TV · Powered by Serverless Matrix Architecture & Cloudflare Pages';
                

                document.getElementById('input_tg_pwd_msg_template').value = jsonObj.TG_PWD_MSG_TEMPLATE || '';
                document.getElementById('input_tg_update_msg_template').value = jsonObj.TG_UPDATE_MSG_TEMPLATE || '';

                
                
                // 🎯 动态读取 3 个底包源地址
                document.getElementById('input_cnb_source_url').value = jsonObj.CNB_SOURCE_URL || 'https://cnb.cool/fish2035/xs/-/git/raw/main/api.json';
                document.getElementById('input_haitun_source_url').value = jsonObj.HAITUN_SOURCE_URL || 'https://raw.githubusercontent.com/FGBLH/HKL/refs/heads/main/ok%E6%B5%B7%E8%B1%9A.json';
                document.getElementById('input_lz_source_url').value = jsonObj.LZ_SOURCE_URL || 'https://gh-proxy.com/https://raw.githubusercontent.com/ediart/tvbox/refs/heads/main/lz/py.json';
            }}
        }} catch (e) {{
            console.error('读取 settings.json 失败:', e);
        }}
    }}

    async function saveSettingsToGithub() {{
        const auth = getStoredAuth();
        if (!auth.token || !auth.repo) {{
            alert('请先配置 GitHub PAT！');
            return openTokenModal();
        }}

        try {{
            const blockKw = JSON.parse(document.getElementById('json_block_keywords').value);
            const upstreamDirty = JSON.parse(document.getElementById('json_upstream_dirty').value);
            const nsfwKw = JSON.parse(document.getElementById('json_nsfw_keywords').value);
            const maliciousKw = JSON.parse(document.getElementById('json_malicious_keywords').value);
            const noSearchKw = JSON.parse(document.getElementById('json_no_search_keywords').value);
            const customSites = JSON.parse(document.getElementById('json_my_custom_sites').value);
            const customLives = JSON.parse(document.getElementById('json_my_custom_lives').value);
            const allowNsfwKw = JSON.parse(document.getElementById('json_allow_nsfw_keywords').value);


            const url = `https://api.github.com/repos/${{auth.repo}}/contents/datas/settings.json?ref=${{auth.branch}}`;
            const getRes = await fetch(url, {{ headers: {{ 'Authorization': `token ${{auth.token}}` }} }});
            let existingSettings = {{}};
            if (getRes.ok) {{
                const getData = await getRes.json();
                currentSettingsSha = getData.sha;
                existingSettings = JSON.parse(decodeURIComponent(escape(atob(getData.content))));
            }}

            existingSettings.ALLOW_NSFW_KEYWORDS = allowNsfwKw;
            existingSettings.BLOCK_KEYWORDS = blockKw;
            existingSettings.UPSTREAM_DIRTY_WORDS = upstreamDirty;
            existingSettings.NSFW_KEYWORDS = nsfwKw;
            existingSettings.BLOCK_MALICIOUS_KEYWORDS = maliciousKw;
            existingSettings.NO_SEARCH_KEYWORDS = noSearchKw;
            existingSettings.MY_CUSTOM_SITES = customSites;
            existingSettings.MY_CUSTOM_LIVES = customLives;
            existingSettings.GLOBAL_SPIDER_JAR = document.getElementById('input_global_spider_jar').value.trim();
            existingSettings.DEFAULT_LOGO_URL = document.getElementById('input_default_logo_url').value.trim();
            existingSettings.SITE_INSERT_POS = parseInt(document.getElementById('input_site_insert_pos').value) || 0;
            existingSettings.INSERT_POS = parseInt(document.getElementById('input_insert_pos').value) || 0;
            existingSettings.HOT_VIDEO_KEY = document.getElementById('input_hot_video_key').value.trim();
            existingSettings.HOT_VIDEO_SITE_NAME = document.getElementById('input_hot_video_site_name').value.trim();
            existingSettings.SHOW_PUBLIC_DETAILS = document.getElementById('input_show_public_details').checked;
            existingSettings.MY_QQ_GROUP = document.getElementById('input_my_qq_group').value.trim();
            existingSettings.MY_PROMO_CHANNEL = document.getElementById('input_my_promo_channel').value.trim();
            existingSettings.MY_TG_SUFFIX = document.getElementById('input_my_tg_suffix').value.trim();
            existingSettings.LOGO_PREFIX = document.getElementById('input_logo_prefix').value.trim();
            existingSettings.BASE_OUTPUT_FULL = document.getElementById('input_base_output_full').value.trim();
            existingSettings.BASE_OUTPUT_CLEAN = document.getElementById('input_base_output_clean').value.trim();
            existingSettings.dol2_SOURCE_URL = document.getElementById('input_dol2_source_url').value.trim();

            existingSettings.WELCOME_NOTICE_FULL = document.getElementById('input_welcome_notice_full').value.trim();
            existingSettings.WELCOME_NOTICE_CLEAN = document.getElementById('input_welcome_notice_clean').value.trim();
            existingSettings.THANKS_WARNING = document.getElementById('input_thanks_warning').value.trim();
            existingSettings.TRAP_NOTICE_TEXT = document.getElementById('input_trap_notice_text').value.trim();
            existingSettings.TRAP_SITE_NAME_1 = document.getElementById('input_trap_site_name_1').value.trim();
            existingSettings.TRAP_SITE_NAME_2 = document.getElementById('input_trap_site_name_2').value.trim();
            existingSettings.TRAP_LIVE_GROUP = document.getElementById('input_trap_live_group').value.trim();
            existingSettings.TRAP_LIVE_CHANNEL = document.getElementById('input_trap_live_channel').value.trim();
            existingSettings.DONATE_QR_URL = document.getElementById('input_donate_qr_url').value.trim();
            existingSettings.DONATE_NOTICE_TEXT = document.getElementById('input_donate_notice_text').value.trim();
            existingSettings.MARQUEE_NOTICE_TEXT = document.getElementById('input_marquee_notice_text').value.trim();
            existingSettings.FOOTER_TEXT = document.getElementById('input_footer_text').value.trim();

            existingSettings.TG_PWD_MSG_TEMPLATE = document.getElementById('input_tg_pwd_msg_template').value.trim();
            existingSettings.TG_UPDATE_MSG_TEMPLATE = document.getElementById('input_tg_update_msg_template').value.trim();

            // 🎯 保存 3 个底包源地址
            existingSettings.CNB_SOURCE_URL = document.getElementById('input_cnb_source_url').value.trim();
            existingSettings.HAITUN_SOURCE_URL = document.getElementById('input_haitun_source_url').value.trim();
            existingSettings.LZ_SOURCE_URL = document.getElementById('input_lz_source_url').value.trim();

            const updatedContentStr = JSON.stringify(existingSettings, null, 2);
            const base64Content = btoa(unescape(encodeURIComponent(updatedContentStr)));

            const putRes = await fetch(`https://api.github.com/repos/${{auth.repo}}/contents/datas/settings.json`, {{
                method: 'PUT',
                headers: {{
                    'Authorization': `token ${{auth.token}}`,
                    'Content-Type': 'application/json'
                }},
                body: JSON.stringify({{
                    message: "🛠 控制台在线全量更新 datas/settings.json 矩阵规则配置",
                    content: base64Content,
                    sha: currentSettingsSha,
                    branch: auth.branch
                }})
            }});

            if (putRes.ok) {{
                alert('✨ 新规则已成功全量 Commit 保存至 Git 仓库！自动编译流程即将被触发。');
            }} else {{
                const err = await putRes.json();
                alert('保存失败: ' + (err.message || '格式错误或 SHA 冲突'));
            }}
        }} catch (e) {{
            alert('JSON 格式输入有误，请确保所有文本框内符合正确的 JSON 数组语法 (例如 ["词1", "词2"])：' + e.message);
        }}
    }}

    async function loadCommitLogs() {{
        const auth = getStoredAuth();
        const container = document.getElementById('commitLogsContainer');
        if (!auth.repo) {{
            container.innerHTML = '<div class="text-slate-500">未配置仓库信息</div>';
            return;
        }}

        container.innerHTML = '<div class="text-slate-500"><i class="fa-solid fa-spinner fa-spin"></i> 正在拉取 Commit 历史...</div>';

        const headers = {{}};
        if (auth.token) headers['Authorization'] = `token ${{auth.token}}`;

        try {{
            const res = await fetch(`https://api.github.com/repos/${{auth.repo}}/commits?per_page=8&sha=${{auth.branch}}`, {{ headers }});
            if (res.ok) {{
                const commits = await res.json();
                let html = '';
                commits.forEach((c, index) => {{
                    const msg = c.commit.message;
                    const date = new Date(c.commit.author.date).toLocaleString('zh-CN');
                    const author = c.commit.author.name;
                    const sha = c.sha;
                    const shortSha = sha.substring(0, 7);

                    html += `
                    <div class="bg-slate-900/90 rounded-lg p-3 border border-slate-800 flex justify-between items-center gap-3">
                        <div class="space-y-1 overflow-hidden">
                            <div class="font-bold text-slate-200 truncate">${{msg}}</div>
                            <div class="text-[10px] text-slate-500">作者: ${{author}} | 时间: ${{date}}</div>
                        </div>
                        <div class="flex items-center gap-2 flex-shrink-0">
                            <span class="px-2 py-1 bg-slate-800 text-blue-400 rounded text-[10px] font-mono">${{shortSha}}</span>
                            ${{index > 0 ? `<button onclick="rollbackToCommit('${{sha}}', '${{shortSha}}')" class="px-2 py-1 bg-amber-600/20 hover:bg-amber-600 text-amber-400 hover:text-white border border-amber-500/30 rounded text-[10px] transition">⏪ 回滚</button>` : '<span class="text-[10px] text-emerald-400 border border-emerald-500/20 px-2 py-0.5 rounded">当前版本</span>'}}
                        </div>
                    </div>
                    `;
                }});
                container.innerHTML = html;
            }} else {{
                container.innerHTML = '<div class="text-amber-400">拉取日志失败，请检查仓库路径或 Token</div>';
            }}
        }} catch (e) {{
            container.innerHTML = '<div class="text-rose-400">请求异常: ' + e.message + '</div>';
        }}
    }}

    async function rollbackToCommit(sha, shortSha) {{
        const auth = getStoredAuth();
        if (!auth.token || !auth.repo) {{
            alert('请先配置 GitHub PAT！');
            return openTokenModal();
        }}

        if (!confirm(`⚠️ 危险操作：确定要把 settings.json 恢复到历史版本 [ ${{shortSha}} ] 吗？\\n\\n恢复后系统将自动重新编译打包！`)) return;

        try {{
            const historicalUrl = `https://api.github.com/repos/${{auth.repo}}/contents/datas/settings.json?ref=${{sha}}`;
            const historyRes = await fetch(historicalUrl, {{ headers: {{ 'Authorization': `token ${{auth.token}}` }} }});
            
            if (!historyRes.ok) throw new Error("无法读取该提交节点下的 settings.json 历史文件");
            const historyData = await historyRes.json();

            const currentUrl = `https://api.github.com/repos/${{auth.repo}}/contents/datas/settings.json?ref=${{auth.branch}}`;
            const currentRes = await fetch(currentUrl, {{ headers: {{ 'Authorization': `token ${{auth.token}}` }} }});
            const currentData = await currentRes.json();

            const putRes = await fetch(`https://api.github.com/repos/${{auth.repo}}/contents/datas/settings.json`, {{
                method: 'PUT',
                headers: {{
                    'Authorization': `token ${{auth.token}}`,
                    'Content-Type': 'application/json'
                }},
                body: JSON.stringify({{
                    message: `⏪ 控制台在线回滚 settings.json 至历史版本 [${{shortSha}}]`,
                    content: historyData.content,
                    sha: currentData.sha,
                    branch: auth.branch
                }})
            }});

            if (putRes.ok) {{
                alert(`✨ 成功回滚至 [ ${{shortSha}} ]！编译流水线已触发，请稍等 1 分钟后刷新！`);
                loadCommitLogs();
            }} else {{
                alert('回滚提交失败，请检查 PAT 权限。');
            }}
        }} catch(e) {{
            alert('回滚失败: ' + e.message);
        }}
    }}

    async function sendTgBroadcast() {{
        const text = document.getElementById('tg_broadcast_text').value.trim();
        if (!text) return alert('请输入要广播的文本内容！');

        const auth = getStoredAuth();
        if (!auth.token || !auth.repo) {{
            alert('请先配置 GitHub PAT！');
            return openTokenModal();
        }}

        if (!confirm('确定要把此消息直接下发到 Telegram 频道吗？')) return;

        const url = `https://api.github.com/repos/${{auth.repo}}/dispatches`;
        try {{
            const res = await fetch(url, {{
                method: 'POST',
                headers: {{
                    'Authorization': `token ${{auth.token}}`,
                    'Accept': 'application/vnd.github.v3+json',
                    'Content-Type': 'application/json'
                }},
                body: JSON.stringify({{
                    event_type: 'tg_broadcast',
                    client_payload: {{ message: text }}
                }})
            }});

            if (res.status === 204) {{
                alert('🚀 广播指令已成功下发！Bot 正在向 TG 频道发送消息。');
                document.getElementById('tg_broadcast_text').value = '';
            }} else {{
                const errData = await res.json().catch(() => ({{}}));
                alert(`⚠️ 广播发送失败 (${{res.status}}): ${{errData.message || '请检查 Token 权限 (需 repo 权限)'}}`);
            }}
        }} catch(e) {{
            alert('请求发送失败: ' + e.message);
        }}
    }}

    // ====================================================================
    // 🔍 【巡检中心核心函数入口修补】
    // ====================================================================
    async function startInspection() {{
        const btnInspect = document.getElementById('btnStartInspect');
        const btnPurge = document.getElementById('btnPurgeDead');
        const consoleEl = document.getElementById('inspectConsole');
        
        btnInspect.disabled = true;
        btnInspect.classList.add('opacity-50');
        btnPurge.classList.add('hidden');
        consoleEl.innerHTML = '';
        deadSiteNames = [];

        const targets = [];
        (window.sites || []).forEach(s => {{
            let targetUrl = '';
            if (s.api && typeof s.api === 'string') {{
                if (s.api.startsWith('http')) {{
                    targetUrl = s.api;
                }} else if (s.api.startsWith('./')) {{
                    targetUrl = s.api.replace('./', 'https://cnb.cool/fish2035/xs/-/git/raw/main/');
                }}
            }}

            if (!targetUrl && s.ext) {{
                if (typeof s.ext === 'string') {{
                    if (s.ext.startsWith('http')) {{
                        targetUrl = s.ext;
                    }} else if (s.ext.startsWith('./')) {{
                        targetUrl = s.ext.replace('./', 'https://cnb.cool/fish2035/xs/-/git/raw/main/');
                    }}
                }}
            }}

            if (targetUrl) {{
                targets.push({{ name: s.name, url: targetUrl, type: '点播 API' }});
            }}
        }});

        (window.lives || []).forEach(l => {{
            if (l.url && typeof l.url === 'string') {{
                let liveUrl = l.url;
                if (liveUrl.startsWith('./')) {{
                    liveUrl = liveUrl.replace('./', 'https://cnb.cool/fish2035/xs/-/git/raw/main/');
                }}
                if (liveUrl.startsWith('http')) {{
                    targets.push({{ name: l.name, url: liveUrl, type: '直播源' }});
                }}
            }}
        }});

        const totalCnt = targets.length;
        document.getElementById('stat_total').innerText = `0 / ${{totalCnt}}`;
        let okCnt = 0, slowCnt = 0, deadCnt = 0, processed = 0;

        consoleEl.innerHTML += `<div class="text-emerald-400 font-bold">✨ 共解析出 ${{totalCnt}} 个独立远程接口与源站，并发线程池启动巡检...</div><br>`;

        const concurrencyLimit = 8;
        let index = 0;

        async function worker() {{
            while (index < targets.length) {{
                const item = targets[index++];
                const startTime = performance.now();
                let status = 'DEAD', ms = 0, colorClass = 'text-rose-400';

                try {{
                    const controller = new AbortController();
                    const timeoutId = setTimeout(() => controller.abort(), 6000);

                    await fetch(item.url, {{ method: 'HEAD', mode: 'no-cors', signal: controller.signal }});
                    clearTimeout(timeoutId);
                    
                    ms = Math.round(performance.now() - startTime);
                    if (ms > 2000) {{
                        status = 'SLOW';
                        colorClass = 'text-amber-400';
                        slowCnt++;
                    }} else {{
                        status = 'OK';
                        colorClass = 'text-emerald-400';
                        okCnt++;
                    }}
                }} catch (err) {{
                    ms = Math.round(performance.now() - startTime);
                    status = 'DEAD';
                    colorClass = 'text-rose-400';
                    deadCnt++;
                    deadSiteNames.push(item.name.replace("🦋", "").replace("｜Tg：@huliys9", "").trim());
                }}

                processed++;
                document.getElementById('stat_total').innerText = `${{processed}} / ${{totalCnt}}`;
                document.getElementById('stat_ok').innerText = okCnt;
                document.getElementById('stat_slow').innerText = slowCnt;
                document.getElementById('stat_dead').innerText = deadCnt;

                const logItem = document.createElement('div');
                logItem.className = 'flex justify-between items-center py-0.5 border-b border-slate-900/60';
                logItem.innerHTML = `
                    <span class="truncate max-w-[60%] text-slate-300">[${{item.type}}] ${{item.name}}</span>
                    <span class="${{colorClass}} font-bold font-mono">${{status}} (${{ms}}ms)</span>
                `;
                consoleEl.appendChild(logItem);
                consoleEl.scrollTop = consoleEl.scrollHeight;
            }}
        }}

        const workers = Array(concurrencyLimit).fill(0).map(() => worker());
        await Promise.all(workers);

        consoleEl.innerHTML += `<br><div class="text-cyan-400 font-bold">🏁 全量巡检完成！正常: ${{okCnt}} | 高延迟: ${{slowCnt}} | 失效: ${{deadCnt}}</div>`;
        btnInspect.disabled = false;
        btnInspect.classList.remove('opacity-50');

        if (deadCnt > 0) {{
            btnPurge.classList.remove('hidden');
            btnPurge.classList.add('flex');
            btnPurge.innerText = `一键拉黑剔除 ${{deadCnt}} 个失效源`;
        }}
    }}

    async function purgeDeadSites() {{
        if (deadSiteNames.length === 0) return;
        const auth = getStoredAuth();
        if (!auth.token || !auth.repo) {{
            alert('请先配置 GitHub PAT！');
            return openTokenModal();
        }}

        if (!confirm(`确定要将巡检出的 ${{deadSiteNames.length}} 个失效/404源加入 BLOCK_KEYWORDS 黑名单并提交 Git 吗？`)) return;

        try {{
            const cleanDeadKeywords = deadSiteNames.map(name => name.split('｜')[0].trim()).filter(Boolean);

            const url = `https://api.github.com/repos/${{auth.repo}}/contents/datas/settings.json?ref=${{auth.branch}}`;
            const getRes = await fetch(url, {{ headers: {{ 'Authorization': `token ${{auth.token}}` }} }});
            if (!getRes.ok) throw new Error('无法获取远程 settings.json');

            const getData = await getRes.json();
            const currentSha = getData.sha;
            const existingSettings = JSON.parse(decodeURIComponent(escape(atob(getData.content))));

            const currentBlocks = existingSettings.BLOCK_KEYWORDS || [];
            const mergedBlocks = Array.from(new Set([...currentBlocks, ...cleanDeadKeywords]));

            existingSettings.BLOCK_KEYWORDS = mergedBlocks;

            const updatedContentStr = JSON.stringify(existingSettings, null, 2);
            const base64Content = btoa(unescape(encodeURIComponent(updatedContentStr)));

            const putRes = await fetch(`https://api.github.com/repos/${{auth.repo}}/contents/datas/settings.json`, {{
                method: 'PUT',
                headers: {{
                    'Authorization': `token ${{auth.token}}`,
                    'Content-Type': 'application/json'
                }},
                body: JSON.stringify({{
                    message: `🔍 巡检自动化：拉黑剔除 ${{cleanDeadKeywords.length}} 个失效源站点`,
                    content: base64Content,
                    sha: currentSha,
                    branch: auth.branch
                }})
            }});

            if (putRes.ok) {{
                alert('✨ 已自动将失效源加入黑名单并提交 Git 仓库！Actions 编译流水线即将被触发。');
                document.getElementById('btnPurgeDead').classList.add('hidden');
            }} else {{
                alert('一键剔除提交失败');
            }}
        }} catch(e) {{
            alert('剔除提交失败: ' + e.message);
        }}
    }}

    document.addEventListener('DOMContentLoaded', () => {{
        updateAuthUI();
    }});
    </script>
</body>
</html>
"""

# ====================================================================
# ✍️ 【九、老杨专属点播手工加线区】
# ====================================================================
MY_CUSTOM_SITES = get_setting("MY_CUSTOM_SITES", [
    {
        "key": "采集合集py",
        "name": f"🦋采集合集(py)🔞｜{MY_TG_SUFFIX.strip('｜')}",
        "type": 3,
        "api": "https://gh-proxy.com/https://raw.githubusercontent.com/ediart/tvbox/refs/heads/main/lz/py/采集合集.py",
        "searchable": 1,
        "quickSearch": 1,
        "filterable": 1,
        "changeable": 1,
        "playerType": 2,
        "ext": "0"
    },
    {
        "key": "js_douban",
        "name": "🦋豆瓣(js)",
        "type": 3,
        "api": "https://gh-proxy.com/https://raw.githubusercontent.com/ediart/tvbox/refs/heads/main/lz/douban_min.js",
        "searchable": 0,
        "quickSearch": 0,
        "filterable": 1,
        "changeable": 0
    }
])

# ====================================================================
# 📺 【十、老杨专属直播手工加线区】
# ====================================================================
MY_CUSTOM_LIVES = get_setting("MY_CUSTOM_LIVES", [	
    {
        "name": "老杨TV",
        "type": 0,
        "url": "https://ghfast.top/https://raw.githubusercontent.com/GodLike631/Ly/refs/heads/Live/datas/custom_lives.m3u",
        "ua": "okhttp/5.3.2"
    },
    {
        "name": "央卫TV",
        "type": 0,
        "ua": "okhttp/5.3.2",
        "url": "http://47.120.41.246:8025/vip/jar/zb.php"
    },
    {
        "name": "咪咕",
        "type": 0,
        "ua": "okhttp/5.3.2",
        "url": "https://develop202.github.io/migu_video/interface.txt"
    },   
    {
        "name": "裤佬TV｜Tg：@huliys9",
        "type": 0,
        "ua": "okhttp",
        "url": "https://live.445569.xyz/live.m3u"
    },
    {
        "name": "综合直播",
        "type": 0,
        "playerType": 2,
        "url": "https://ghfast.top/https://raw.githubusercontent.com/develop202/migu_video/refs/heads/main/interface.txt",
        "ua": "bingcha/1.1 (mianfeifenxiang) "
    },    
    {
        "name": "Kimentanm",
        "type": 0,
        "url": "https://ghfast.top/https://raw.githubusercontent.com/Kimentanm/aptv/master/m3u/iptv.m3u",
        "playerType": 2
    },
    {
        "name": "超稳定流畅",
        "type": 0,
        "ua": "okhttp/5.3.2",
        "url": "https://ghfast.top/https://raw.githubusercontent.com/GodLike631/test/refs/heads/main/datas/%E8%B6%85%E7%A8%B3%E5%AE%9A%E6%B5%81%E7%95%85.txt"
    },
    {
        "name": "Gather「IPTV」(梯子）",
        "type": 3,
        "url": "https://iptv.1989.click/playlist.m3u",
        "epg":"https://material.1989.click/epg.xml.gz",
        "ua": "okhttp/3.8.1",
        "timeout": 10,
        "playerType": 2
    },
    {
        "name": "锋云直播",
        "type": 3,
        "url": "https://gh-proxy.org/https://raw.githubusercontent.com/807080747/zv/refs/heads/main/suale.txt",
        "ua": "okhttp/5.3.2",
        "timeout": 10,
        "playerType": 2
    },
    {
        "name": "最新电影",
        "type": 0,
        "ua": "okhttp/5.3.2",
        "url": "https://ghfast.top/https://raw.githubusercontent.com/GodLike631/Ly_18/refs/heads/main/datas/%E6%9C%80%E6%96%B0%E7%94%B5%E5%BD%B1.m3u"
    },  
    {
        "name": "海外频道（开梯）🔞",
        "type": 0,
        "ua": "okhttp/5.3.2",
        "url": "https://ghfast.top/https://raw.githubusercontent.com/yihad168/tv/refs/heads/main/live.m3u"
    },
    {
        "name": "国产直播🔞",
        "type": 0,
        "ua": "okhttp/5.3.2",
        "url": "https://ghfast.top/https://raw.githubusercontent.com/Ameria22/TV/refs/heads/main/data/01%E5%9B%BD%E4%BA%A7%E7%9B%B4%E6%92%AD_20260417_024507.m3u"
    },
    {
        "name": "国产精品🔞",
        "type": 0,
        "ua": "okhttp/5.3.2",
        "url": "https://ghfast.top/https://raw.githubusercontent.com/Ameria22/TV/refs/heads/main/data/01%E5%9B%BD%E4%BA%A7%E7%B2%BE%E5%93%81_20260417_024507.m3u"
    },
    {
        "name": "探花🔞",
        "type": 0,
        "ua": "okhttp/5.3.2",
        "url": "https://raw.githubusercontent.com/Ameria22/TV/refs/heads/main/data/01%E6%8E%A2%E8%8A%B1%E7%BA%A6%E7%82%AE_20260417_024507.m3u"
    },
    {
        "name": "欧美🔞",
        "type": 0,
        "ua": "okhttp/5.3.2",
        "url": "https://ghfast.top/https://raw.githubusercontent.com/Ameria22/TV/refs/heads/main/data/%E6%AC%A7%E7%BE%8E%E9%A2%91%E9%81%93.m3u"
    }
])
# ====================================================================
# 🌐 【十一、公开主页 (index.html) 前端 HTML 模板 (极客豪华三重奏版)】
# ====================================================================
PUBLIC_INDEX_HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="zh-CN" class="h-full">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>老杨TV - 专属缝合矩阵订阅导航</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script>
        tailwind.config = {{
            darkMode: 'class',
        }}
    </script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <script async src="//busuanzi.ibruce.info/busuanzi/2.3/busuanzi.pure.mini.js"></script>
</head>
<body class="bg-slate-900 text-slate-200 dark:bg-slate-900 dark:text-slate-200 transition-colors duration-300 min-h-screen flex flex-col items-center justify-between p-4 sm:p-8 font-sans relative overflow-x-hidden" id="main_body">

    <!-- 🌌 1. 科技风渐变光晕与背景网格 -->
    <div class="fixed inset-0 pointer-events-none z-0 overflow-hidden">
        <div class="absolute -top-40 -left-40 w-96 h-96 bg-emerald-500/10 rounded-full blur-3xl"></div>
        <div class="absolute -top-20 -right-20 w-96 h-96 bg-indigo-500/10 rounded-full blur-3xl"></div>
        <div class="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-full h-full bg-[radial-gradient(#334155_1px,transparent_1px)] [background-size:24px_24px] opacity-20"></div>
    </div>

    <!-- 主卡片容器 (包含毛玻璃与动态光影) -->
    <div class="max-w-3xl w-full bg-slate-800/80 dark:bg-slate-800/80 rounded-3xl p-6 sm:p-8 border border-slate-700/60 shadow-2xl space-y-6 my-auto backdrop-blur-xl relative overflow-hidden transition-all duration-300 z-10" id="main_card">
        
        <!-- 右上角：暗黑/亮色模式切换按钮 -->
        <button onclick="toggleTheme()" class="absolute top-5 right-5 w-9 h-9 rounded-2xl bg-slate-700/50 hover:bg-slate-600/50 border border-slate-600/50 flex items-center justify-center text-amber-400 transition shadow-inner" title="切换昼夜模式">
            <i class="fa-solid fa-moon text-sm" id="theme_icon"></i>
        </button>

        <!-- Header 品牌标头 -->
        <div class="text-center space-y-2 border-b border-slate-700/60 pb-5">
            <div class="inline-block p-3 bg-slate-700/40 rounded-2xl text-4xl shadow-inner border border-slate-600/40">🦋</div>
            <h1 class="text-2xl sm:text-3xl font-extrabold tracking-wide text-white" id="header_title">老杨TV · 专属矩阵订阅导航</h1>
            <p class="text-xs text-slate-400 font-mono">Core V{version} | Build: {build_time}</p>
            
            <!-- 🎯 边缘节点呼吸灯探针 + 更新日志按钮 -->
            <div class="flex items-center justify-center gap-2 mt-1">
                <div class="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-slate-900/60 border border-slate-700/60 text-[11px] text-slate-300">
                    <span class="relative flex h-2 w-2">
                      <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                      <span class="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
                    </span>
                    <span>边缘节点: <span class="text-emerald-400 font-bold">运行正常</span></span>
                    <span class="text-slate-600">|</span>
                    <span>延迟: <span class="text-emerald-400 font-mono font-bold" id="ping_time">--</span></span>
                </div>
                <button onclick="openChangelogModal()" class="px-3 py-1 rounded-full bg-indigo-500/10 hover:bg-indigo-500/20 border border-indigo-500/30 text-[11px] text-indigo-300 font-medium transition flex items-center gap-1 shadow-sm">
                    <i class="fa-solid fa-clock-rotate-left"></i>
                    更新日志
                </button>
            </div>
        </div>

        <!-- 1️⃣ 统计与快捷跳转区 (7 卡片自适应网格 + 数字滚动) -->
        <div class="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-7 gap-2.5 text-center">
            <div class="bg-slate-900/60 p-2.5 rounded-2xl border border-slate-700/50">
                <div class="text-[10px] text-slate-400">点播线路</div>
                <div class="text-base font-bold text-emerald-400 mt-0.5"><span id="count_sites" data-target="{site_cnt}">0</span> <span class="text-[10px] font-normal">个</span></div>
            </div>
            <div class="bg-slate-900/60 p-2.5 rounded-2xl border border-slate-700/50">
                <div class="text-[10px] text-slate-400">直播源站</div>
                <div class="text-base font-bold text-cyan-400 mt-0.5"><span id="count_lives" data-target="{live_cnt}">0</span> <span class="text-[10px] font-normal">个</span></div>
            </div>
            <div class="bg-slate-900/60 p-2.5 rounded-2xl border border-slate-700/50">
                <div class="text-[10px] text-slate-400">解析接口</div>
                <div class="text-base font-bold text-indigo-400 mt-0.5"><span id="count_parses" data-target="{parse_cnt}">0</span> <span class="text-[10px] font-normal">个</span></div>
            </div>
            <div class="bg-slate-900/60 p-2.5 rounded-2xl border border-slate-700/50">
                <div class="text-[10px] text-slate-400">当前密锁</div>
                <div class="text-xs font-bold text-amber-400 cursor-pointer select-none transition mt-1"
                     onclick="{lock_click_action}"
                     title="点击显示/隐藏">
                    {lock_display_text}
                </div>
            </div>
            <div class="bg-slate-900/60 p-2.5 rounded-2xl border border-slate-700/50">
                <div class="text-[10px] text-slate-400">访问总人次</div>
                <div class="text-base font-bold text-rose-400 mt-0.5">
                    <span id="busuanzi_value_site_pv">--</span> <span class="text-[10px] font-normal">次</span>
                </div>
            </div>
            <a href="https://t.me/tvshare23" target="_blank" class="bg-slate-900/60 hover:bg-sky-500/20 p-2.5 rounded-2xl border border-slate-700/50 hover:border-sky-500/40 transition group">
                <div class="text-[10px] text-slate-400 group-hover:text-sky-300">TG 交流群</div>
                <div class="text-xs font-bold text-sky-400 mt-1 truncate"><i class="fa-brands fa-telegram"></i> 群组</div>
            </a>
            <a href="https://t.me/{tg_channel_clean}" target="_blank" class="bg-slate-900/60 hover:bg-sky-500/20 p-2.5 rounded-2xl border border-slate-700/50 hover:border-sky-500/40 transition group">
                <div class="text-[10px] text-slate-400 group-hover:text-sky-300">TG 官方频道</div>
                <div class="text-xs font-bold text-sky-400 mt-1 truncate"><i class="fa-brands fa-telegram"></i> 频道</div>
            </a>
        </div>

        <!-- 🎯 新增：跑马灯流动公告栏 -->
        <div class="bg-emerald-500/10 border border-emerald-500/20 rounded-2xl p-2.5 px-4 flex items-center gap-3 overflow-hidden text-xs text-emerald-300">
            <i class="fa-solid fa-bullhorn text-emerald-400 animate-bounce"></i>
            <div class="overflow-hidden whitespace-nowrap w-full">
                <div class="inline-block animate-[marquee_20s_linear_infinite] hover:[animation-play-state:paused]">
                    {marquee_text}
                </div>
            </div>
        </div>

        <!-- 2️⃣ 订阅链接列表 -->
        <div class="space-y-3">
            <h2 class="text-sm font-bold text-slate-200 flex items-center gap-2">
                <i class="fa-solid fa-rss text-emerald-400"></i>
                最新可用矩阵订阅链接
            </h2>
            <div class="space-y-3">
{file_cards}
            </div>
        </div>

        <!-- 3️⃣ 打赏支持区域 -->
        {donate_section_html}

        <!-- 4️⃣ 公告引导区 -->
        <div class="bg-amber-500/10 border border-amber-500/20 rounded-2xl p-4 text-xs space-y-1.5 text-amber-200/90">
            <div class="font-bold text-amber-400 flex items-center gap-1.5">
                <i class="fa-solid fa-triangle-exclamation"></i>
                重要提示与使用说明
            </div>
            <p class="leading-relaxed">
                1. 本专线订阅密码不定期全自动跟进交替。若遇到电视端视频无法加载或断流，请及时更换最新的订阅链接！<br>
                2. 官方交流渠道（加群获取最新密锁/更新通知）：<br>
                   • Telegram 交流群：<a href="https://t.me/tvshare23" target="_blank" class="font-bold text-sky-400 hover:text-sky-300 underline underline-offset-2 transition"><i class="fa-brands fa-telegram"></i> tvshare23</a><br>
                   • Telegram 官方频道：<a href="https://t.me/{tg_channel_clean}" target="_blank" class="font-bold text-sky-400 hover:text-sky-300 underline underline-offset-2 transition"><i class="fa-brands fa-telegram"></i> {promo_channel}</a>
            </p>
        </div>

    </div>

    <!-- 页脚版权 (支持后台动态配置) -->
    <footer class="text-center text-[11px] text-slate-500 py-4 z-10">
        {footer_text}
    </footer>

    <style>
        @keyframes marquee {{
            0% {{ transform: translateX(100%); }}
            100% {{ transform: translateX(-100%); }}
        }}
    </style>

    <script>
    // 1. 探针实时延迟测量 + 数字动态滚动效果初始化
    document.addEventListener('DOMContentLoaded', () => {{
        const start = performance.now();
        fetch(window.location.href, {{ method: 'HEAD', cache: 'no-store' }}).then(() => {{
            const duration = Math.round(performance.now() - start);
            const pingEl = document.getElementById('ping_time');
            if (pingEl) pingEl.innerText = duration + 'ms';
        }}).catch(() => {{
            const pingEl = document.getElementById('ping_time');
            if (pingEl) pingEl.innerText = '15ms';
        }});

        // 启动数字滚动效果
        animateCount('count_sites');
        animateCount('count_lives');
        animateCount('count_parses');

        // 读取历史主题
        if (localStorage.getItem('theme') === 'light') {{
            setTheme('light');
        }}
    }});

    // ⚡ 核心：数字动态递增动画实现
    function animateCount(id) {{
        const el = document.getElementById(id);
        if (!el) return;
        const target = parseInt(el.getAttribute('data-target')) || 0;
        let current = 0;
        const duration = 1000; // 动画持续 1 秒
        const stepTime = 20;
        const increment = Math.ceil(target / (duration / stepTime)) || 1;

        const timer = setInterval(() => {{
            current += increment;
            if (current >= target) {{
                current = target;
                clearInterval(timer);
            }}
            el.innerText = current;
        }}, stepTime);
    }}

    // 2. 日夜主题切换逻辑
    function toggleTheme() {{
        const isDark = document.documentElement.classList.contains('dark');
        setTheme(isDark ? 'light' : 'dark');
    }}

    function setTheme(mode) {{
        const body = document.getElementById('main_body');
        const card = document.getElementById('main_card');
        const icon = document.getElementById('theme_icon');
        const title = document.getElementById('header_title');

        if (mode === 'light') {{
            document.documentElement.classList.remove('dark');
            body.className = "bg-slate-100 text-slate-800 min-h-screen flex flex-col items-center justify-between p-4 sm:p-8 font-sans transition-colors duration-300 relative overflow-x-hidden";
            card.className = "max-w-3xl w-full bg-white/80 rounded-3xl p-6 sm:p-8 border border-slate-200 shadow-xl space-y-6 my-auto backdrop-blur-xl relative overflow-hidden transition-all duration-300 z-10";
            icon.className = "fa-solid fa-sun text-sm text-amber-500";
            if (title) title.className = "text-2xl sm:text-3xl font-extrabold tracking-wide text-slate-800";
            localStorage.setItem('theme', 'light');
        }} else {{
            document.documentElement.classList.add('dark');
            body.className = "bg-slate-900 text-slate-200 min-h-screen flex flex-col items-center justify-between p-4 sm:p-8 font-sans transition-colors duration-300 relative overflow-x-hidden";
            card.className = "max-w-3xl w-full bg-slate-800/80 rounded-3xl p-6 sm:p-8 border border-slate-700/60 shadow-2xl space-y-6 my-auto backdrop-blur-xl relative overflow-hidden transition-all duration-300 z-10";
            icon.className = "fa-solid fa-moon text-sm text-amber-400";
            if (title) title.className = "text-2xl sm:text-3xl font-extrabold tracking-wide text-white";
            localStorage.setItem('theme', 'dark');
        }}
    }}

    function toggleDonate() {{
        const box = document.getElementById('donate_qr_box');
        if (box) box.classList.toggle('hidden');
    }}

    function copyUrl(url, isMasked) {{
        if (isMasked) {{
            alert('⚠️ 当前公开页已开启隐秘保护模式！\\n\\n请前往 Telegram 交流群或频道获取当前最新密锁订阅链接。');
            return;
        }}
        navigator.clipboard.writeText(url).then(() => {{
            alert('✨ 订阅链接已成功复制到剪贴板！');
        }}).catch(() => {{
            const input = document.createElement('input');
            input.value = url;
            document.body.appendChild(input);
            input.select();
            document.execCommand('copy');
            document.body.removeChild(input);
            alert('✨ 订阅链接已成功复制！');
        }});
    }}
    </script>
    <!-- 🎯 更新日志弹窗 (Changelog Modal) -->
    <div id="changelogModal" class="hidden fixed inset-0 bg-black/70 backdrop-blur-md z-50 flex items-center justify-center p-4">
        <div class="bg-slate-800 rounded-3xl border border-slate-700 max-w-lg w-full p-6 shadow-2xl space-y-4 max-h-[80vh] flex flex-col">
            <div class="flex justify-between items-center border-b border-slate-700 pb-3 flex-shrink-0">
                <h3 class="text-sm font-bold text-white flex items-center gap-2">
                    <i class="fa-solid fa-list-check text-emerald-400"></i>
                    矩阵更新与线路变动日志
                </h3>
                <button onclick="closeChangelogModal()" class="text-slate-400 hover:text-white"><i class="fa-solid fa-xmark"></i></button>
            </div>
            
            <div id="changelogContent" class="space-y-4 overflow-y-auto text-xs text-slate-300 pr-1">
                <div class="text-center py-6 text-slate-500"><i class="fa-solid fa-spinner fa-spin"></i> 正在加载最新变动明细...</div>
            </div>

            <div class="pt-2 border-t border-slate-700/60 flex justify-end flex-shrink-0">
                <button onclick="closeChangelogModal()" class="px-4 py-1.5 bg-slate-700 hover:bg-slate-600 text-xs font-medium rounded-xl text-slate-200">关闭</button>
            </div>
        </div>
    </div>

    <script>
    function openChangelogModal() {{
        document.getElementById('changelogModal').classList.remove('hidden');
        loadChangelogData();
    }}

    function closeChangelogModal() {{
        document.getElementById('changelogModal').classList.add('hidden');
    }}

    function loadChangelogData() {{
        const container = document.getElementById('changelogContent');
        fetch('/changelog.json?t=' + Date.now())
            .then(res => res.json())
            .then(data => {{
                if (!data || data.length === 0) {{
                    container.innerHTML = '<div class="text-center text-slate-500 py-4">暂无历史变动记录</div>';
                    return;
                }}
                let html = '';
                data.forEach(item => {{
                    html += `
                    <div class="bg-slate-900/60 p-3.5 rounded-2xl border border-slate-700/60 space-y-2">
                        <div class="flex justify-between items-center border-b border-slate-800 pb-2">
                            <span class="font-bold text-emerald-400">📅 ${{item.time}}</span>
                            <span class="text-[10px] bg-slate-800 text-slate-400 px-2 py-0.5 rounded-full font-mono">${{item.version || '编译构建'}}</span>
                        </div>
                        <div class="space-y-1 text-slate-300 whitespace-pre-wrap leading-relaxed">${{item.detail}}</div>
                    </div>
                    `;
                }});
                container.innerHTML = html;
            }})
            .catch(() => {{
                container.innerHTML = '<div class="text-center text-amber-400 py-4">无法获取变动明细记录</div>';
            }});
    }}
    </script>
</body>
</html>
"""

