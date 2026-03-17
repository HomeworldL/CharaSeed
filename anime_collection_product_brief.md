# 个人二次元电子收藏册项目整理

> 面向 Codex / vibe coding 的项目简报
>
> 目标不是做公共百科或全知资料库，而是做一个 **面向个人审美偏好的二次元收藏中枢**：支持多站点搜索、视觉预览、一键收藏、按角色/作品/类型整理，并逐步沉淀为未来可用于角色生成与电子手办生成的偏好资料库。

---

## 1. 项目定义

### 1.1 一句话定位

一个支持多站点搜索、视觉预览、一键收藏、偏好归档与日常发现的 **个人二次元电子收藏册**。

### 1.2 它不是什么

- 不是 MyAnimeList / AniDB 那样的公共资料库
- 不是 Danbooru 那样的公开图片数据库
- 不是单纯下载器
- 不是通用库存管理系统
- 不是第一天就做完的 AI 角色生成平台

### 1.3 它是什么

它更接近下面这几类产品的组合：

- **MoeLoader-P** 的多站点搜索与预览下载
- **Koillection** 的个人收藏管理思路
- **Yamtrack** 的条目与追踪视图
- **MyFigureCollection** 的角色/作品/手办关联感
- **Hydrus** 的本地收藏与标签归档能力

核心路径：

**收藏 → 整理 → 组织偏好 → 沉淀角色审美 → 辅助生成**

### 1.4 目标用户

- 喜欢角色、作画、设定、手办、模型、动画、游戏的人
- 想要“什么都能收”的个人收藏册，而不是公共百科
- 重视觉浏览，不想用太丑、太重、太像后台数据库的工具
- 未来希望把偏好沉淀为 AI 生成素材的人

---

## 2. 产品约束

### 2.1 设计约束

1. **以视觉为中心**
   - 预览图优先
   - 评分优先于长备注
   - 浏览流畅比字段齐全更重要

2. **先做轻规范，不做重知识图谱**
   - 第一版只保留必要结构
   - 允许同一条目同时关联角色、作品、来源站点、标签
   - 不强迫一开始把所有实体建成严格百科模型

3. **先做个人工具，不做公共平台**
   - 默认单用户或少量熟人共享
   - 不优先做社交、投稿审核、公共编辑

4. **发现与收藏同等重要**
   - 这个产品不只是“管理已有内容”
   - 还要支持“搜索、发现、候选、推荐、每日自动抓取”

5. **现在以收藏为核心，生成留接口**
   - 第一版不做网页端 LoRA 训练
   - 第一版不做 3D 生成闭环
   - 只保证未来数据结构能支持生成方向

### 2.2 工程约束

- 优先 Python 后端
- 前端不追求最复杂炫技，而追求可维护与好看
- 默认开源友好
- 默认本地部署或 Docker Compose 部署友好
- 不依赖某一个站点的私有 API 才能工作
- 尽量通过“聚合搜索 + 收藏卡片”来统一不同来源

### 2.3 数据约束

- 主对象不是“全局知识实体”，而是 **收藏卡片 / 收藏项**
- 条目可以来自图片站、手办站、动画条目站、模型站、商店页
- 条目可以挂在“角色页 / 作品页 / 原创设定页”等主题页下
- 允许同一条目被多个维度归类

---

## 3. 产品结构建议

### 3.1 两个核心域

#### A. 发现域

解决“我怎么找到东西”

包括：
- 多站点搜索
- 搜索结果统一预览
- 候选流
- 日常发现
- 自动搜索订阅

#### B. 收藏域

解决“我怎么把喜欢的东西变成自己的东西”

包括：
- 收藏卡片
- 角色归档
- 作品归档
- 类型归档
- 标签系统
- 评分系统
- 浏览与筛选

### 3.2 核心对象建议

#### 1. 收藏项 `items`

表示“我从某个来源收藏进来的一个对象”。

它可以是：
- 一张图
- 一个角色图集条目
- 一个手办商品页
- 一个模型资源页
- 一部动画/游戏条目页
- 一个原创角色概念

建议字段：

- `id`
- `title`
- `type`
- `preview_image`
- `source_site`
- `source_url`
- `rating`
- `tags`
- `created_at`
- `updated_at`
- `collected_at`
- `status`
- `entity_links`

#### 2. 主题页 `entities`

表示“我自己整理出的主题归档页”。

类型建议：
- `character`
- `work`
- `original`
- `artist`
- `series`

一个 entity 下面可以聚合多个 item。

#### 3. 搜索任务 `search_feeds`

表示“我想持续追踪的搜索关键词 / 搜索规则”。

建议字段：
- `id`
- `name`
- `query`
- `sites`
- `enabled`
- `schedule`
- `last_run_at`
- `last_result_count`

### 3.3 关系策略

不要一开始上很重的知识图谱。

建议采用：
- `items` 是核心
- `entities` 是归档页
- `items <-> entities` 多对多
- `items <-> tags` 多对多
- `items <-> images/assets` 一对多

这样既规范，又不会过重。

---

## 4. 完整功能蓝图

下面是长远完整功能，不代表第一版都做。

### 4.1 发现能力

- 多站点统一搜索
- 搜索结果卡片流
- 结果按站点 / 类型过滤
- 图片预览 / 大图查看
- 快速收藏
- 去重与相似结果聚合
- 保存搜索词
- 每日自动搜索
- 首页候选流
- 随机发现
- 基于已有关键词和高评分项目做推荐

### 4.2 收藏能力

- 一键收藏到仓库
- 收藏时补充角色 / 作品 / 类型 / 标签 / 评分
- 收藏状态
  - 已收藏
  - 想买
  - 想补图
  - 待整理
  - 已归档
- 多图附件
- 外部链接保存
- 下载记录
- 本地文件挂载

### 4.3 组织能力

- 按角色浏览
- 按作品浏览
- 按类型浏览
- 按标签浏览
- 按评分浏览
- 按来源站点浏览
- 时间线浏览
- 最近收藏
- 收藏总览 Dashboard
- 角色页 / 作品页 / 原创角色页

### 4.4 偏好沉淀

- 高分标签统计
- 喜好角色画像
- 喜好作品画像
- 偏好风格聚类
- 推荐候选
- “你最近更喜欢哪些元素”
- “你最常收藏的角色和作品”

### 4.5 未来生成方向

- 从高分条目提取生成提示词
- 角色卡导出
- 绑定 LoRA / 外部模型服务
- 图生图 / 角色生图接口位
- 电子手办概念页
- 未来 3D 生成接口位
- 未来动画生成接口位

---

## 5. 第一版 MVP

### 5.1 第一版目标

验证这个项目是不是一个真正好用的“个人二次元收藏册”。

### 5.2 第一版必须有的页面

#### 页面 1：发现页
- 搜索框
- 多站点结果流
- 统一结果卡片
- 大图预览
- 一键收藏

#### 页面 2：收藏库
- 已收藏条目流
- 按角色 / 作品 / 类型 / 标签 / 评分筛选
- 网格视图 / 列表视图

#### 页面 3：主题页
- 角色页
- 作品页
- 原创页
- 聚合展示该主题下的全部收藏项

#### 页面 4：收藏详情页
- 预览图
- 来源链接
- 所属角色
- 所属作品
- 标签
- 评分
- 相关项

### 5.3 第一版必须有的能力

- 多站点手动搜索
- 搜索结果统一显示
- 收藏时填写关键字段
  - 角色
  - 作品
  - 类型
  - 标签
  - 评分
- 收藏后统一归入仓库
- 日常浏览支持按：
  - 角色
  - 作品
  - 类型
  - 标签
  - 评分
- 基础去重
- 基础主题归档

### 5.4 第一版不做

- 公共百科级资料建模
- 全自动全网爬取
- 复杂知识图谱
- 网页端 LoRA 训练
- 3D 生成闭环
- 社交系统
- 复杂评论系统
- 过多长文本备注设计

---

## 6. 第二版建议增加的功能

### 6.1 发现增强

- 保存搜索词
- 搜索订阅
- 每日自动搜索
- 今日候选流
- 已看 / 未看
- 忽略 / 稍后再看
- 基于高评分条目的随机推荐

### 6.2 组织增强

- 更好的角色页 / 作品页
- 自动从已有条目推断角色 / 作品
- 标签推荐
- 相似条目推荐
- 收藏统计
- 时间轴视图

### 6.3 本地资源增强

- 本地目录挂载
- 下载记录
- 缩略图缓存
- 同步外部下载器结果

### 6.4 偏好建模增强

- 高评分关键词分析
- 风格偏好提取
- 角色偏好卡
- “你喜欢的元素”可视化

---

## 7. 可参考的网站与产品

下面是按用途整理的参考对象。

### 7.1 图片数据库 / 图片社区 / 图站

#### Pixiv
- 类型：创作者社区
- 用途：作者、插画、收藏、系列、排行
- 适合参考：作者页、作品页、发现流、收藏逻辑
- 说明：pixiv 官方应用称其为日本最大的创意社区之一，主打插画、漫画与创作发现。

#### Danbooru / Donmai
- 类型：标签型图片数据库
- 用途：协作标签、角色 / 作品 / 画师标签体系
- 适合参考：标签归档、tag type、pool、wiki、rating
- 说明：Danbooru 是典型 anime imageboard，核心价值是高结构化标签体系。

#### Gelbooru
- 类型：booru 图站
- 用途：标签搜索、大量图片归档
- 适合参考：程序化检索、booru 风格结果流

#### Safebooru
- 类型：safe-only booru
- 用途：更安全的图站筛选与浏览

#### Konachan / Yande.re
- 类型：壁纸型图站
- 用途：高分辨率 anime 壁纸与高清图片
- 适合参考：大图浏览与壁纸流布局

#### Zerochan
- 类型：角色/壁纸导向图站
- 用途：角色图、官方图、壁纸、fanart
- 适合参考：角色页与图集页视觉组织

#### E-shuushuu
- 类型：主题更窄的 anime 图站
- 用途：风格化图片收藏

#### MiniTokyo
- 类型：壁纸 / scan 社区
- 用途：高质量壁纸与扫描图

### 7.2 下载器 / 收藏工具

#### MoeLoader-P
- 类型：多站点图片浏览下载器
- 特点：图片参数过滤搜索、批量下载、预览图缩放、页码导航
- 适合参考：统一搜索 + 统一预览 + 快速收藏入口

#### Hydrus Network
- 类型：本地媒体收藏数据库
- 特点：像桌面上的 booru，用标签代替文件夹，支持 gallery 下载与 subscriptions
- 适合参考：本地归档、标签系统、订阅下载、长期收藏

#### imgbrd-grabber
- 类型：imageboard / booru 下载器
- 特点：适合批量抓取 booru 站点图片，文件命名与目录结构可定制
- 适合参考：booru 抓取器与下载队列

#### gallery-dl
- 类型：通用命令行图库下载器
- 特点：跨平台，支持大量站点，适合做后端抓取层参考
- 适合参考：站点适配器架构、下载任务模型

### 7.3 手办 / 周边 / 商品网站

#### Hpoi
- 类型：社区型手办与周边数据库
- 特点：中文语境里很常用，覆盖手办、模型、模玩百科、资讯、晒图与资料检索
- 适合参考：角色 / 作品 / 厂家 / 商品关联方式，中文社区收藏体验

#### MyFigureCollection
- 类型：社区型手办与周边数据库
- 特点：支持 collection manager、database、pictures、calendar、budget manager
- 适合参考：角色 / 作品 / 商品关联方式

#### AmiAmi
- 类型：商品与预售商店
- 特点：分类清晰，手办、可动、模型、预售、现货丰富
- 适合参考：商品卡片、筛选维度、价格与状态展示

#### Good Smile Company
- 类型：官方厂商站
- 适合参考：官方产品详情页、发售时间、角色与系列页

#### HobbySearch
- 类型：商品与模型商店
- 适合参考：发售日历、品类导航、模型分类

#### Tokyo Otaku Mode
- 类型：动漫商品商店与编辑内容平台
- 特点：兼具商城、专题、角色商品聚合与推荐内容
- 适合参考：专题运营位、角色商品集合页、推荐区块

#### Mandarake
- 类型：二手与收藏向综合商品站
- 特点：覆盖手办、同人志、漫画、赛璐璐片、玩具、周边与拍卖
- 适合参考：庞杂藏品的分类方式、二手商品信息组织、拍卖与现货共存模式

### 7.4 动漫 / 漫画 / 条目网站

#### AniList
- 类型：动漫漫画追踪与发现平台
- 适合参考：现代列表页、条目页、清单管理、发现页

#### MyAnimeList
- 类型：动漫漫画数据库与社区
- 适合参考：作品页、评分与收藏状态

#### AniDB
- 类型：更硬核的动画数据库
- 适合参考：结构化元数据与标签

#### Bangumi
- 类型：中文 ACG 条目与兴趣追踪社区
- 特点：覆盖动画、游戏、音乐、图书等条目，也支持用户收藏与进度管理
- 适合参考：多媒介统一条目系统、中文收藏状态、条目浏览器

#### Kitsu
- 类型：动漫漫画发现与追踪平台
- 特点：偏现代社交化风格，也提供公开 API 文档
- 适合参考：轻量现代化清单管理、API 驱动条目系统

#### Anime-Planet
- 类型：动漫漫画发现、推荐与清单平台
- 特点：强调推荐、标签、用户清单与发现体验
- 适合参考：推荐流、标签浏览、作品发现页

#### VNDB
- 类型：视觉小说数据库
- 特点：适合补足二次元收藏中 galgame / visual novel 这一路径
- 适合参考：更细粒度的作品、角色、发行与标签信息组织

### 7.5 模型 / 3D 资源网站

#### BOOTH
- 类型：创作者综合市场
- 特点：与 pixiv 生态联动，常见同人素材、数字商品、3D 配件、模型资源
- 适合参考：创作者页、商品页、数字资源售卖

#### Sketchfab
- 类型：3D 展示与分发平台
- 特点：Web 端 3D 预览能力很强
- 适合参考：3D 预览与模型详情页

#### CGTrader
- 类型：3D 模型市场
- 特点：大量模型可下载、定制与商用筛选
- 适合参考：3D 商品与文件信息组织

#### TurboSquid
- 类型：大型 3D 模型市场
- 特点：覆盖多种 DCC 与游戏引擎格式，偏专业生产与商用场景
- 适合参考：格式筛选、许可信息、文件规格展示

#### VRoid Hub
- 类型：3D 角色投稿与共享平台
- 特点：更偏日系虚拟形象与角色模型生态，和 VRM / 虚拟角色展示关联强
- 适合参考：角色模型页、预览方式、角色化 3D 资产管理

---

## 8. 推荐参考仓库

### 8.1 直接相关的产品/工具仓库

- `xplusky/MoeLoaderP`
- `danbooru/danbooru`
- `Bionus/imgbrd-grabber`
- `mikf/gallery-dl`
- `manami-project/anime-offline-database`
- `benjaminjonard/koillection`
- `FuzzyGrim/Yamtrack`

### 8.2 偏图片与标签体系

- `danbooru/danbooru`
- `KichangKim/DeepDanbooru`
- `AUTOMATIC1111/TorchDeepDanbooru`

### 8.3 偏收藏与下载

- `Bionus/imgbrd-grabber`
- `mikf/gallery-dl`
- `hydrusnetwork/hydrus`（官方站为主）

### 8.4 偏未来生成方向

- `AUTOMATIC1111/stable-diffusion-webui`
- `comfyanonymous/ComfyUI`
- `kohya-ss/sd-scripts`
- `RVC-Project/Retrieval-based-Voice-Conversion-WebUI`

---

## 9. 当前主流站点与工具分类总表

### 9.1 主流图片数据库 / 图片站

- Pixiv
- Danbooru
- Gelbooru
- Safebooru
- Konachan
- Yande.re
- Zerochan
- E-shuushuu
- MiniTokyo

### 9.2 主流下载器 / 收藏器

- MoeLoader-P
- Hydrus Network
- imgbrd-grabber
- gallery-dl
- PixivUtil2
- Hitomi Downloader（多站点下载器，偏下载管理）

### 9.3 主流手办 / 周边站

- MyFigureCollection
- AmiAmi
- Good Smile Company
- HobbySearch
- Tokyo Otaku Mode

### 9.4 主流动漫条目站

- AniList
- MyAnimeList
- AniDB
- Anime News Network Encyclopedia

### 9.5 主流模型 / 3D 站

- BOOTH
- Sketchfab
- CGTrader

---

## 10. 功能取舍建议

### 10.1 应该优先做的

- 搜索
- 视觉预览
- 一键收藏
- 收藏时填写关键字段
- 角色 / 作品 / 类型 / 标签 / 评分浏览
- 主题聚合页

### 10.2 应该推迟做的

- 复杂站点级深度适配
- 太重的资料库字段
- 社交功能
- 网页端训练 LoRA
- 3D 生成闭环

### 10.3 是否值得做

值得。

因为现有产品通常只覆盖其中一部分：
- 有的强在图片下载
- 有的强在本地收藏
- 有的强在条目追踪
- 有的强在手办信息

但“**面向个人审美偏好的统一二次元收藏中枢**”这个产品位仍然是存在的。

---

## 11. 推荐技术方向

### 11.1 务实技术栈

前端：
- React
- Vite
- Mantine
- TypeScript
- React Router
- TanStack Query

后端：
- FastAPI
- Pydantic
- SQLAlchemy 2.0 或 SQLModel
- Alembic

数据库：
- PostgreSQL
- 可选 Redis（第二阶段再加）

鉴权与登录：
- 初期：邮箱 / 用户名 + 密码登录
- 后续：OAuth 登录（GitHub / Google）
- 会话：JWT access token + refresh token，或服务端 session

部署：
- Docker Compose
- Nginx / Caddy 反向代理
- 对象存储或本地文件目录用于缩略图与缓存

### 11.2 作为未来网站是否合适

合适，而且这套方案比一开始做更重的全栈框架更稳。

原因：
- 你更希望主要用 Python
- 这个项目核心是搜索聚合、收藏管理、任务调度、偏好沉淀，不是 SSR 内容站
- React + Vite + Mantine 适合做登录后使用的 Web App
- FastAPI 很适合做用户系统、收藏 API、搜索任务、推荐流、后台定时任务
- PostgreSQL 足够支持 item / entity / tags / feeds / users / favorites 的关系模型
- 以后就算做成多用户网站，也只是把“单用户收藏册”扩展成“每个用户自己的收藏空间”，总体架构不用推翻

### 11.3 未来做网站时建议预留的结构

- `users`：用户表
- `sessions` 或 token 机制：登录态
- `collections`：用户收藏空间
- `items` 增加 `owner_id`
- `entities` 增加 `owner_id`
- `search_feeds` 增加 `owner_id`
- 图片缓存、缩略图、下载记录与用户隔离
- 首页候选流按用户偏好单独生成

### 11.4 当前不必过早做的

- 复杂权限系统
- 团队协作编辑
- 公开主页 / 社区动态
- 评论、关注、点赞
- 多租户 SaaS 级别架构

---

## 12. 给 Codex 的实现建议

### 12.1 第一轮实现目标

先只做：
- 登录页
- 搜索页
- 收藏库页
- 主题页
- 收藏详情页
- PostgreSQL 基础 schema
- 多站点搜索的 mock adapter
- 基础用户系统（单用户优先，但数据库按多用户留字段）

### 12.2 第一轮不要做

- 真正复杂的站点爬虫全集成
- 大而全的公共数据同步
- 推荐算法复杂版
- 生成模块
- 复杂权限系统
- OAuth 全家桶

### 12.3 最关键的开发顺序

1. 设计数据库 schema
2. 加入用户与登录模型
3. 搭基本 UI 和路由
4. 先做单站点 / mock 搜索
5. 打通“一键收藏 → 归档 → 浏览”闭环
6. 再加多个站点 adapter
7. 再加搜索订阅和候选流
8. 最后补推荐与偏好统计

### 12.4 建议 Codex 先拆成的模块

#### 前端模块
- `auth`：登录、登出、用户状态
- `discover`：搜索、结果流、筛选、预览
- `collection`：收藏库、过滤、排序、批量操作
- `entity`：角色页、作品页、原创页
- `item`：详情页、编辑抽屉、关联信息
- `shared`：卡片、对话框、标签、评分组件、图片灯箱

#### 后端模块
- `auth`：注册、登录、刷新 token、当前用户
- `users`：用户资料、偏好设置
- `items`：收藏项 CRUD
- `entities`：主题页 CRUD
- `tags`：标签 CRUD 与推荐
- `search`：多站点适配器、统一搜索接口
- `feeds`：保存搜索、自动任务、候选流
- `assets`：预览图缓存、本地资源、缩略图

#### 基础基础设施模块
- 数据库迁移
- 文件存储目录
- 定时任务 runner
- 统一日志
- 配置文件与环境变量

### 12.5 建议 Codex 第一轮优先产出

1. 后端目录结构
2. 数据表与 Alembic 初始迁移
3. FastAPI 基础 app
4. 登录接口与测试账户
5. 前端路由骨架
6. Discover / Collection 两个页面的静态 UI
7. 单站点 mock 搜索接口
8. 一键收藏流程
9. 收藏库筛选与详情页

### 12.6 建议 Codex 第一轮数据表

至少包括：
- `users`
- `items`
- `entities`
- `tags`
- `item_tags`
- `entity_links`
- `search_feeds`
- `search_results_cache`
- `assets`

### 12.7 建议 Codex 第一轮 API

- `POST /auth/login`
- `POST /auth/logout`
- `GET /auth/me`
- `GET /search`
- `POST /items`
- `GET /items`
- `GET /items/{id}`
- `PATCH /items/{id}`
- `GET /entities`
- `POST /entities`
- `GET /entities/{id}`
- `POST /feeds`
- `GET /feeds`

### 12.8 对 Codex 的风格要求

- 不要生成臃肿企业后台风 UI
- 界面要偏视觉收藏册，而不是纯表格系统
- 尽量使用卡片流、抽屉、图片预览、标签筛选
- 类型与状态字段先做轻量枚举，不要一开始做成超重 schema
- 所有站点 adapter 先做 mock 或 placeholder，接口要统一
- 代码结构优先清晰可维护，不追求一步到位

---

## 13. 可直接给 Codex 的项目描述

```text
Build an open-source web app called a personal anime collection hub.

Product definition:
This is not a public encyclopedia and not a universal metadata warehouse.
It is a personal visual collection scrapbook for anime and character enthusiasts.
It should help users search across multiple sites, preview results, collect favorite items, organize them by character / work / type / tags / rating, and gradually build a preference archive for future character generation.

Primary product goals:
- multi-site discovery
- unified preview cards
- one-click collect
- visual-first browsing
- lightweight structured metadata
- themed pages for characters and works
- future-ready preference modeling

This product should feel like a mix of:
- MoeLoader-P style discovery
- Koillection style personal collection management
- MyFigureCollection style character / work / figure association
- Hydrus style long-term archive thinking

Important constraints:
- Python backend preferred
- frontend should look modern, clean, visual, and pleasant
- do not make it look like a heavy enterprise admin panel
- first version is a login-based personal website
- design database with owner_id fields so multi-user support can be added later
- discovery and collection management are equally important
- comments and long notes are not important for V1
- rating, tags, preview images, source links, and entity links are important

Recommended stack:
- React + Vite + Mantine + TypeScript
- React Router
- TanStack Query
- FastAPI + Pydantic + SQLAlchemy
- PostgreSQL
- Alembic
- Docker Compose

V1 pages:
- Login page
- Discover page
- Collection page
- Entity page
- Item detail page

V1 capabilities:
- keyword search
- mock multi-site search adapters
- unified result cards
- image preview dialog
- one-click collect
- fill key fields when collecting: character, work, type, tags, rating
- browse collected items by character / work / type / tags / rating
- basic de-duplication
- lightweight entity pages

V1 should not include:
- full public database sync
- deep crawler integration for all sites
- complex recommendation algorithm
- LoRA training in web UI
- 3D generation pipeline
- social features
- complex permission system

Suggested backend modules:
- auth
- users
- items
- entities
- tags
- search
- feeds
- assets

Suggested frontend modules:
- auth
- discover
- collection
- entity
- item
- shared ui

Please first generate:
1. project folder structure
2. backend schema
3. Alembic initial migration
4. FastAPI starter app
5. frontend starter app with routing
6. Discover and Collection page UI
7. mock search adapter
8. collect flow
9. item detail page
```

---

## 14. 联网核实过的几个关键事实

- MoeLoader-P 官方页明确强调其支持图片参数过滤搜索、批量下载、预览图缩放、页码导航，并列出 Bilibili、Konachan、Yande.re、Safebooru、Danbooru、Gelbooru、Pixiv 等支持站点。 citeturn637320search0
- Hydrus 官方将自己描述为“像桌面上的 booru”，支持 gallery 下载与 subscriptions。 citeturn637320search1turn637320search5turn637320search11
- imgbrd-grabber 官方定位是 imageboard/booru downloader。 citeturn637320search2turn637320search6
- gallery-dl 官方定位是跨平台图片图库下载器。 citeturn637320search3turn637320search16
- MyFigureCollection 官方说明自己是 Japanese pop-culture goods collectors 的服务，并提供 collection manager、databases、pictures、calendar 等功能。 citeturn819998search0turn819998search12
- AniList 官方定位是 Track, Discover, Share Anime & Manga。 citeturn819998search2
- BOOTH 官方说明自己是与 pixiv 联动的创作物综合市场。 citeturn819998search3turn819998search7
- pixiv 官方应用介绍其为创作社区平台。 citeturn155381search2
- Danbooru 被广泛描述为以 anime 风格插画为主、以协作标签组织内容的 imageboard。 citeturn155381search3
- Sketchfab 和 CGTrader 分别可作为 3D 展示平台与 3D 模型市场参考。 citeturn155381search0turn155381search1

