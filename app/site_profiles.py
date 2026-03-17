SITE_ORDER = [
    "danbooru",
    "safebooru",
    "zerochan",
    "hpoi",
    "yandere",
    "konachan",
    "myfigurecollection",
    "anilist",
    "sketchfab",
]

HOME_SITE_ORDER = ["all", *SITE_ORDER]


SITE_PROFILES = {
    "all": {
        "label": "All",
        "title": "跨站混合搜索",
        "description": "自然输入关键词，系统会按公开站点分别解释并聚合结果。",
        "best_for": "适合还不确定想看图、角色图集还是手办条目时使用。",
        "examples": ["初音未来", "asuna", "genshin impact", "良笑 初音"],
        "hint_tags": ["角色名", "作品名", "作者名", "商品名"],
    },
    "danbooru": {
        "label": "Danbooru",
        "title": "标签结构最强的图站",
        "description": "更适合按角色、作品、画师和标签搜索，细粒度标签最丰富。",
        "best_for": "角色图、作品 fanart、作者风格图。",
        "examples": ["asuna_(sao)", "genshin_impact", "raiden_shogun", "mika_pikazo"],
        "hint_tags": ["角色", "作品", "画师", "tag"],
        "supports_mixed_home": True,
    },
    "safebooru": {
        "label": "Safebooru",
        "title": "更偏安全向的 booru 图站",
        "description": "适合快速找公开安全向的角色和作品图片。",
        "best_for": "角色图、作品图、通用标签图像。",
        "examples": ["asuna", "fate series", "blue archive", "miku"],
        "hint_tags": ["角色", "作品", "标签"],
        "supports_mixed_home": True,
    },
    "zerochan": {
        "label": "Zerochan",
        "title": "角色 / 作品导向更明显的图集站",
        "description": "更适合直接搜角色名和作品名，角色图集感更强。",
        "best_for": "角色图集、作品图集、壁纸式浏览。",
        "examples": ["Asuna", "Genshin Impact", "Hatsune Miku", "Azur Lane"],
        "hint_tags": ["角色", "作品"],
        "supports_mixed_home": True,
    },
    "hpoi": {
        "label": "Hpoi",
        "title": "中文手办与模型资料站",
        "description": "适合搜角色、商品名、厂商、系列，结果更偏手办与模型条目。",
        "best_for": "手办候选、厂商条目、再版关注。",
        "examples": ["初音未来", "良笑", "F:NEX", "尼尔 2B 手办"],
        "hint_tags": ["角色", "商品名", "厂商", "系列"],
        "supports_mixed_home": True,
    },
    "yandere": {
        "label": "Yande.re",
        "title": "高质量二次元图站",
        "description": "适合按角色、作品和标签快速找高分辨率插画。",
        "best_for": "高清图、壁纸图、tag 搜索。",
        "examples": ["asuna", "hatsune_miku", "blue_archive", "genshin_impact"],
        "hint_tags": ["角色", "作品", "tag"],
        "supports_mixed_home": True,
    },
    "konachan": {
        "label": "Konachan",
        "title": "壁纸导向图站",
        "description": "适合搜壁纸式图像和经典 tag 图站内容。",
        "best_for": "壁纸图、角色图、tag 搜索。",
        "examples": ["asuna", "hatsune_miku", "azur_lane", "landscape"],
        "hint_tags": ["角色", "作品", "tag"],
        "supports_mixed_home": True,
    },
    "myfigurecollection": {
        "label": "MyFigureCollection",
        "title": "手办资料与收藏社区",
        "description": "适合搜角色手办、PVC、比例款和品牌条目。",
        "best_for": "手办条目、系列手办、角色手办。",
        "examples": ["asuna figure", "miku scale figure", "good smile asuna", "alter saber"],
        "hint_tags": ["角色", "商品名", "厂商", "系列"],
        "supports_mixed_home": True,
    },
    "anilist": {
        "label": "AniList",
        "title": "公开 API 动画数据库",
        "description": "适合快速搜动画作品并拿到封面、类型和状态。",
        "best_for": "动画条目、番剧搜索、作品发现。",
        "examples": ["Sword Art Online", "Asuna", "Blue Archive", "Frieren"],
        "hint_tags": ["动画", "作品", "角色"],
        "supports_mixed_home": True,
    },
    "sketchfab": {
        "label": "Sketchfab",
        "title": "公开 3D 模型平台",
        "description": "适合找 3D 角色模型、资产和可预览模型。",
        "best_for": "3D 模型、角色资产、展示模型。",
        "examples": ["anime girl", "miku", "sci-fi character", "mecha"],
        "hint_tags": ["3D", "角色", "模型"],
        "supports_mixed_home": True,
    },
}


def sites_for_mode(site_mode: str | None) -> list[str]:
    if not site_mode or site_mode == "all":
        return SITE_ORDER.copy()
    return [site_mode] if site_mode in SITE_ORDER else [SITE_ORDER[0]]
