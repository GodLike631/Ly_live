/**
 * 影视点播插件 - 移植自高考模拟爬虫
 */

const BACKUP_DOMAINS = [
    "ldngksapi.cc",
    "lagh23ksapi.cc",
    "ldagwhdgpi.cc",
    "lwetasdf3api.cc",
    "lwasga289api.cc",
    "lw2wthchhaapi.cc",
    "lwncnss3api.cc",
    "lw23412gaapi.cc"
];

const VOD_CLASSES = [
    '重口猎奇', '迷奸强奸', '校园霸凌', '真实乱伦', '监控偷拍', '学生破处',
    '淫荡孕妇', '萝莉', '小学', '初中', '高中', '小马', '人妖伪娘',
    '户外露出', '绿帽抓奸', '反差母犬', '少女媚黑', '暗网萝莉', '少女萝莉',
    '学生', '自慰', 'JK', '母子通奸', '父女禁恋', '兄妹相爱', '姐弟情深',
    '舅侄畸恋', '全家乱P', '师生淫乱', '偷窥偷拍', '裸聊实录', '主播大秀',
    '原创自拍', '车震野战', 'SM捆绑', '探花大神', '勾引搭讪', '最新热点',
    '独家精选', '学生校园', '网红网暴', '热门大瓜', '明星黑幕', '反差母狗',
    '领导干部', '百合', '足交', '丝袜', '内射', 'Cospaly', '换妻Club', '偷窥萝莉'
];

// ========== 辅助工具方法 ==========

function getUA() {
    const devices = [
        ["ONEPLUS A5000", "OPR6.170623.013"],
        ["Pixel 4", "QQ3A.200805.001"],
        ["SM-G973F", "QP1A.190711.020"],
        ["Mi 9", "PKQ1.181121.001"],
        ["Redmi Note 8", "QKQ1.200114.002"]
    ];
    const dev = devices[Math.floor(Math.random() * devices.length)];
    const androidVer = ["9", "10", "11", "12"][Math.floor(Math.random() * 4)];
    const chromeVer = 120 + Math.floor(Math.random() * 18);
    return `Mozilla/5.0 (Linux; Android ${androidVer}; ${dev[0]} Build/${dev[1]}; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/${chromeVer}.0.4000.100 Mobile Safari/537.36 uni-app Html5Plus/1.0 (Immersed/24.0)`;
}

// 递归查找字段
function findFirst(obj, key) {
    if (!obj) return null;
    if (typeof obj === 'object') {
        if (obj[key] !== undefined && obj[key] !== null && obj[key] !== "") {
            return String(obj[key]);
        }
        for (let k in obj) {
            let res = findFirst(obj[k], key);
            if (res !== null) return res;
        }
    }
    return null;
}

// 获取有效 Base URL（带缓存）
async function getBaseUrl() {
    let cached = $cache.get("working_base_url");
    if (cached) return cached;

    for (let domain of BACKUP_DOMAINS) {
        for (let proto of ['https', 'http']) {
            try {
                let testUrl = `${proto}://${domain}/api/setapp.php`;
                let res = await $fetch.get(testUrl, { headers: { "User-Agent": getUA() } });
                if (res && res.status_code === 200) {
                    let base = `${proto}://${domain}`;
                    $cache.set("working_base_url", base);
                    return base;
                }
            } catch (e) {}
        }
    }
    return "https://ldngksapi.cc";
}

// 注册获取 Token（带缓存）
async function getToken() {
    let cachedToken = $cache.get("app_auth_token");
    if (cachedToken) return cachedToken;

    const base = await getBaseUrl();
    const channels = ["", "default", "test", "vbtqg9d8"];
    
    for (let code of channels) {
        try {
            let res = await $fetch.post(
                `${base}/api/newreg.php`,
                `device=android&ntoken=&channel_code=${code}`,
                {
                    headers: {
                        "User-Agent": getUA(),
                        "Content-Type": "application/x-www-form-urlencoded"
                    }
                }
            );
            let body = typeof res.data === 'string' ? JSON.parse(res.data) : res.data;
            let tok = findFirst(body, "token");
            if (tok) {
                $cache.set("app_auth_token", tok);
                return tok;
            }
        } catch (e) {}
    }
    return "";
}

// 通用数据提取
function collectItems(obj, baseUrl) {
    let out = [];
    function walk(node) {
        if (!node) return;
        if (Array.isArray(node)) {
            node.forEach(walk);
        } else if (typeof node === 'object') {
            if (node.vod_id !== undefined && node.vod_id !== null && node.vod_id !== "") {
                let pic = node.vod_pic || node.vod_img || node.pic || node.cover || node.image || "";
                if (pic.startsWith("//")) pic = "https:" + pic;
                else if (pic.startsWith("/") && !pic.startsWith("//")) pic = baseUrl + pic;

                out.push({
                    vod_id: String(node.vod_id),
                    vod_name: String(node.vod_name || node.name || "未知"),
                    vod_pic: pic,
                    vod_remarks: String(node.vod_remarks || node.remarks || node.status || ""),
                    ext: { vod_id: String(node.vod_id) }
                });
            } else {
                for (let k in node) walk(node[k]);
            }
        }
    }
    walk(obj);
    return out;
}

// ========== 客户端必需实现的 5 个生命周期函数 ==========

// 1. 分类导航
async function getConfig() {
    const tabs = VOD_CLASSES.map(cls => ({
        name: cls,
        ext: { vodclass: cls }
    }));
    return jsonify({ tabs });
}

// 2. 列表加载（点击分类或加载更多）
async function getCards(ext) {
    const vodclass = ext.vodclass || VOD_CLASSES[0];
    const page = ext.page || 1;
    const offset = (page - 1) * 30;
    const base = await getBaseUrl();

    const postData = {
        num: String(offset),
        pid: "4",
        area: "全部",
        vodclass: vodclass,
        vodyear: "全部",
        sort: "1",
        type: "undefined"
    };

    try {
        const res = await $fetch.post(
            `${base}/api/vlist.php`,
            postData,
            {
                headers: {
                    "User-Agent": getUA(),
                    "Content-Type": "application/x-www-form-urlencoded"
                }
            }
        );
        const body = typeof res.data === 'string' ? JSON.parse(res.data) : res.data;
        const list = collectItems(body, base);
        return jsonify({ list });
    } catch (e) {
        return jsonify({ list: [] });
    }
}

// 3. 搜索内容
async function search(ext) {
    const keyword = typeof ext === 'string' ? ext : (ext.wd || ext.keyword || "");
    if (!keyword) return jsonify({ list: [] });

    const base = await getBaseUrl();
    let allMatches = [];

    // 匹配前若干个类目的结果
    for (let cls of VOD_CLASSES.slice(0, 8)) {
        try {
            const res = await $fetch.post(
                `${base}/api/vlist.php`,
                { num: "0", pid: "4", area: "全部", vodclass: cls, vodyear: "全部", sort: "1", type: "undefined" },
                { headers: { "User-Agent": getUA(), "Content-Type": "application/x-www-form-urlencoded" } }
            );
            const body = typeof res.data === 'string' ? JSON.parse(res.data) : res.data;
            const items = collectItems(body, base);
            for (let item of items) {
                if (item.vod_name.toLowerCase().includes(keyword.toLowerCase())) {
                    allMatches.push(item);
                }
            }
            if (allMatches.length >= 20) break;
        } catch (e) {}
    }

    return jsonify({ list: allMatches });
}

// 4. 获取详情与剧集列表
async function getTracks(ext) {
    const vid = ext.vod_id || ext;
    const base = await getBaseUrl();
    const token = await getToken();

    try {
        const res = await $fetch.post(
            `${base}/api/Get_vod_list.php`,
            `id=${vid}&token=${token}&channel=`,
            {
                headers: {
                    "User-Agent": getUA(),
                    "Content-Type": "application/x-www-form-urlencoded"
                }
            }
        );
        const body = typeof res.data === 'string' ? JSON.parse(res.data) : res.data;

        // 提取播放直链
        let playUrls = [];
        function extractUrls(node) {
            if (!node) return;
            if (typeof node === 'object') {
                if (node.vod_play_url) {
                    let parts = String(node.vod_play_url).split("#");
                    parts.forEach(p => {
                        let link = p.includes("$") ? p.split("$").pop() : p;
                        if (link && link.startsWith("http")) playUrls.push(link.trim());
                    });
                }
                for (let k in node) extractUrls(node[k]);
            }
        }
        extractUrls(body);
        playUrls = [...new Set(playUrls)];

        const tracks = playUrls.map((url, idx) => ({
            name: `第${idx + 1}集`,
            pan: "",
            ext: { play_url: url }
        }));

        let pic = findFirst(body, "vod_pic") || findFirst(body, "pic") || "";
        if (pic.startsWith("//")) pic = "https:" + pic;
        else if (pic.startsWith("/") && !pic.startsWith("//")) pic = base + pic;

        return jsonify({
            list: [
                {
                    title: "线路直连",
                    tracks: tracks
                }
            ],
            detail: {
                vod_id: String(vid),
                vod_name: findFirst(body, "vod_name") || "未知",
                vod_pic: pic,
                vod_overview: findFirst(body, "vod_content") || findFirst(body, "desc") || ""
            }
        });
    } catch (e) {
        return jsonify({ list: [] });
    }
}

// 5. 获取播放流信息
async function getPlayinfo(ext) {
    const url = ext.play_url || "";
    const base = await getBaseUrl();

    return jsonify({
        headers: [
            {
                "User-Agent": getUA(),
                "Referer": base
            }
        ],
        urls: [url]
    });
}
