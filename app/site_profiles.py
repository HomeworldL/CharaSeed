SITE_ORDER = ["danbooru", "safebooru", "zerochan", "hpoi"]


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
}


def sites_for_mode(site_mode: str | None) -> list[str]:
    if not site_mode or site_mode == "all":
        return SITE_ORDER.copy()
    return [site_mode] if site_mode in SITE_ORDER else [SITE_ORDER[0]]
