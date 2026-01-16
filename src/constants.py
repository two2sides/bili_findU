"""常量定义"""
DYNAMIC_TYPE_DICT = {
    "DYNAMIC_TYPE_NONE": "无效动态",
    "DYNAMIC_TYPE_FORWARD": "动态转发",
    "DYNAMIC_TYPE_AV": "投稿视频",
    "DYNAMIC_TYPE_PGC": "剧集（番剧、电影、纪录片）",
    "DYNAMIC_TYPE_COURSES": "TYPE_COURSES",
    "DYNAMIC_TYPE_WORD": "纯文字动态",
    "DYNAMIC_TYPE_DRAW": "带图动态",
    "DYNAMIC_TYPE_ARTICLE": "投稿专栏",
    "DYNAMIC_TYPE_MUSIC": "音乐",
    "DYNAMIC_TYPE_COMMON_SQUARE": "装扮/剧集点评/普通分享",
    "DYNAMIC_TYPE_COMMON_VERTICAL": "TYPE_COMMON_VERTICAL",
    "DYNAMIC_TYPE_LIVE": "直播间分享",
    "DYNAMIC_TYPE_MEDIALIST": "收藏夹",
    "DYNAMIC_TYPE_COURSES_SEASON": "课程",
    "DYNAMIC_TYPE_COURSES_BATCH": "TYPE_COURSES_BATCH",
    "DYNAMIC_TYPE_AD": "TYPE_AD",
    "DYNAMIC_TYPE_APPLET": "TYPE_APPLET",
    "DYNAMIC_TYPE_SUBSCRIPTION": "TYPE_SUBSCRIPTION",
    "DYNAMIC_TYPE_LIVE_RCMD": "直播开播",
    "DYNAMIC_TYPE_BANNER": "TYPE_BANNER",
    "DYNAMIC_TYPE_UGC_SEASON": "合集更新",
    "DYNAMIC_TYPE_SUBSCRIPTION_NEW": "TYPE_SUBSCRIPTION_NEW"
}
MAJOR_TYPE_DICT = {
    "ugc_season": "合集信息",
    "article": "专栏",
    "draw": "带图动态",
    "archive": "视频",
    "live_rcmd": "直播状态",
    "common": "一般类型",
    "pgc": "剧集更新",
    "courses": "课程",
    "music": "音频更新",
    "opus": "图文动态",
    "live": "直播间",
    "none": "动态失效"
}
CSV_HEADERS = ["时间", "类型", "文本内容", "转发/投稿", "主体类型", "转发/投稿源标题"]
BASE_URL = "https://api.bilibili.com/x/polymer/web-dynamic/v1/feed/space"
