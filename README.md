# CharaSeed

一个面向个人审美偏好的二次元收藏中枢 MVP。

## 当前能力
- 独立主页：今日候选流首页，支持实时刷新与单站展开
- 多源搜索：Danbooru、Safebooru、Zerochan、Hpoi
- 搜索结果统一预览与一键收藏
- 收藏库浏览与筛选
- 角色 / 作品主题页
- 收藏详情编辑与来源跳转

## 运行
```bash
uv sync
uv run uvicorn app.main:app --reload
```

默认地址：
`http://127.0.0.1:8000`

首页：
`http://127.0.0.1:8000/home`

搜索页：
`http://127.0.0.1:8000/discover`

## 目录
- `app/` 应用代码
- `docs/superpowers/specs/` 设计文档
- `anime_collection_product_brief.md` 产品简报
