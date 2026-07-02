# SmartDine（智餐 AI）· 项目开发文档

**版本 V2.0 · 2026年7月1日 · 第⑥小组**

| | |
|---|---|
| **版本** | V2.0 |
| **课程团队** | 第⑥小组 |
| **团队成员** | 黄岑果（组长）<br/>黄禹菲<br/>夏思凯 |
| **编写日期** | 2026年7月1日 |

---

## 目  录

- [1. 开发环境搭建](#1-开发环境搭建)
    - [1.1 环境要求](#11-环境要求)
    - [1.2 后端环境](#12-后端环境)
    - [1.3 管理端前端环境](#13-管理端前端环境)
    - [1.4 小程序环境](#14-小程序环境)
    - [1.5 Dify 环境](#15-dify-环境)
    - [1.6 数据库初始化](#16-数据库初始化)
- [2. 技术栈与版本](#2-技术栈与版本)
- [3. 项目结构详解](#3-项目结构详解)
    - [3.1 总体结构](#31-总体结构)
    - [3.2 后端（backend/）](#32-后端backend)
    - [3.3 管理端前端（admin-web/）](#33-管理端前端admin-web)
    - [3.4 小程序（miniprogram/）](#34-小程序miniprogram)
    - [3.5 Dify（dify/）](#35-difydify)
    - [3.6 数据库脚本（sql/）](#36-数据库脚本sql)
    - [3.7 项目文档（docs/）](#37-项目文档docs)
- [4. 开发规范与约定](#4-开发规范与约定)
    - [4.1 后端开发规范](#41-后端开发规范)
    - [4.2 前端开发规范](#42-前端开发规范)
    - [4.3 小程序开发规范](#43-小程序开发规范)
    - [4.4 Dify 工作流开发规范](#44-dify-工作流开发规范)
    - [4.5 Git 协作规范](#45-git-协作规范)
- [5. 核心设计模式](#5-核心设计模式)
    - [5.1 五层架构](#51-五层架构)
    - [5.2 多租户数据隔离](#52-多租户数据隔离)
    - [5.3 级联安全删除](#53-级联安全删除)
    - [5.4 智能体接入唯一化](#54-智能体接入唯一化)
    - [5.5 统一响应结构](#55-统一响应结构)
- [6. 各模块开发指南](#6-各模块开发指南)
    - [6.1 新增业务模块步骤](#61-新增业务模块步骤)
    - [6.2 后端开发指南](#62-后端开发指南)
    - [6.3 管理端开发指南](#63-管理端开发指南)
    - [6.4 小程序开发指南](#64-小程序开发指南)
    - [6.5 Dify 工作流开发指南](#65-dify-工作流开发指南)
- [7. 构建与部署](#7-构建与部署)
    - [7.1 后端部署](#71-后端部署)
    - [7.2 管理端部署](#72-管理端部署)
    - [7.3 小程序发布](#73-小程序发布)
    - [7.4 Dify 部署](#74-dify-部署)
- [8. 两周开发计划](#8-两周开发计划)
    - [8.1 总体策略](#81-总体策略)
    - [8.2 第 1 周详细安排](#82-第-1-周详细安排)
    - [8.3 第 2 周详细安排](#83-第-2-周详细安排)
    - [8.4 成员分工](#84-成员分工)
    - [8.5 风险预案](#85-风险预案)
- [9. V1.0 → V2.0 代码改造清单](#9-v10-v20-代码改造清单)
    - [9.1 Phase 1：多商户底座（Day 1-2）](#91-phase-1多商户底座day-1-2)
    - [9.2 Phase 2：数据模型扩展（Day 3）](#92-phase-2数据模型扩展day-3)
    - [9.3 Phase 3：Dify 工作流 V2（Day 4）](#93-phase-3dify-工作流-v2day-4)
    - [9.4 Phase 4：前端改造（Day 5-6）](#94-phase-4前端改造day-5-6)
- [10. 当前完成度与待办](#10-当前完成度与待办)
    - [10.1 V1.0 已完成](#101-v10-已完成)
    - [10.2 V2.0 待开发](#102-v20-待开发)
    - [10.3 已知问题与简化](#103-已知问题与简化)
- [11. 附录](#11-附录)
    - [附录 A：环境变量清单](#附录-a环境变量清单)
    - [附录 B：常用命令速查](#附录-b常用命令速查)
    - [附录 C：页面—功能—智能体对照表](#附录-c页面功能智能体对照表)

---

<a id="1-开发环境搭建"></a>
# 1. 开发环境搭建

<a id="11-环境要求"></a>
## 1.1 环境要求

| 工具 | 版本要求 | 用途 |
|---|---|---|
| Python | 3.12+ | 后端服务 |
| Node.js | 18+ | 管理端前端构建 |
| MySQL | 8.0 | 数据库（云端，老师提供） |
| Redis | 7.x（可选） | 会话缓存与热点数据 |
| 微信开发者工具 | 最新稳定版 | 小程序开发与预览 |
| Dify | 1.x 自托管（Docker Compose） | AI 工作流编排 |
| Git | 2.x | 版本控制 |

<a id="12-后端环境"></a>
## 1.2 后端环境

```bash
# 1. 进入后端目录
cd backend

# 2. 创建虚拟环境
python -m venv venv

# 3. 激活虚拟环境
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 4. 安装依赖
pip install -r requirements.txt

# 5. 配置环境变量
copy .env.example .env
# 编辑 .env，填入：
#   - DATABASE_URL（云端 MySQL 连接信息）
#   - JWT_SECRET（JWT 签名密钥）
#   - DIFY_BASE_URL + 各智能体 API Key
#   - WECHAT_APPID / WECHAT_SECRET

# 6. 初始化数据库（按顺序执行 sql/ 下的建表脚本，见 1.6 节）

# 7. 启动服务
uvicorn app.main:app --reload --port 8000

# 8. 验证
curl http://127.0.0.1:8000/health
# 预期返回: {"code":0, "message":"ok", "data":null}
```

<a id="13-管理端前端环境"></a>
## 1.3 管理端前端环境

```bash
# 1. 进入管理端目录
cd admin-web

# 2. 安装依赖
npm install

# 3. 启动开发服务器
npm run dev
# 默认在 http://127.0.0.1:5173 打开

# 4. 生产构建
npm run build
# 输出到 dist/ 目录
```

**登录方式**：用 `sql/03_other.sql` 中 `staff` 表的账号登录。V2.0 增加了平台端（`/platform/login`）和商户端（`/merchant/login`）分离登录。

<a id="14-小程序环境"></a>
## 1.4 小程序环境

1. 下载并安装「微信开发者工具」稳定版
2. 选择「导入项目」，目录选择 `miniprogram/`
3. AppID 使用测试号或占位 `touristappid`（项目已配置 `urlCheck: false` 允许本地预览）
4. 确认 `miniprogram/api/request.js` 中 `BASE_URL` 指向本机后端：
   ```javascript
   const BASE_URL = 'http://127.0.0.1:8000/api/v1';
   ```
5. 开发者工具登录微信账号后即可在模拟器/真机预览

<a id="15-dify-环境"></a>
## 1.5 Dify 环境

Dify 部署在本地 Linux 虚拟机（Docker Compose 自托管），与后端通过内网通信。

```bash
# 在 Linux 虚拟机上：
git clone https://github.com/langgenius/dify.git
cd dify/docker
docker compose up -d

# 确认服务运行
docker compose ps
```

部署完成后：
1. 浏览器访问 Dify 控制台（默认 `http://虚拟机IP:3000`）
2. 分别创建 4 个应用（见 `dify/prompts/*.md` 的编排说明）
3. 挂载知识库（`dify/knowledge_base/`）
4. 发布后复制各应用的 API Key 填入 `backend/.env`

参见 [dify/README.md](../dify/README.md) 了解详细步骤。

<a id="16-数据库初始化"></a>
## 1.6 数据库初始化

连接老师提供的云端 MySQL 8.0 数据库后，**按编号顺序**执行建表脚本：

```sql
-- 执行顺序（必须严格按此顺序，后序脚本依赖前序表结构）：
source sql/00_platform.sql;        -- V2.0 新增：平台层表（merchant, platform_admin）
source sql/01_menu_inventory.sql;  -- 菜品与库存核心表
source sql/02_order.sql;           -- 订单核心表
source sql/03_other.sql;           -- 其余业务表
source sql/04_agent_v2.sql;        -- V2.0 新增：智能体扩展表
```

| 脚本 | 包含表 | V2.0 变更 |
|---|---|---|
| `00_platform.sql` | `merchant`, `platform_admin` | ★ 新建 |
| `01_menu_inventory.sql` | `dish`, `ingredient`, `dish_ingredient`(BOM), `stock_log` | 全部加 `merchant_id`；dish 加 `cost_price/nutrition/recommended_weight/total_sales` |
| `02_order.sql` | `order`, `order_item` | 全部加 `merchant_id`；order 加 `discount_amount/actual_amount/is_group_order/member_count` |
| `03_other.sql` | `dining_table`, `reservation`, `supplier`, `member`, `member_merchant`, `staff`, `schedule`, `campaign`, `coupon`, `service_ticket`, `review`, `agent_config`, `agent_log` | 全部加 `merchant_id`；supplier 加评分字段；dining_table 加 `qr_code_url`；member 拆分为平台级+商户级 |
| `04_agent_v2.sql` | `dish_pairing`, `recommendation_log`, `ab_experiment` | ★ 新建 |

完整字段含义与 ALTER 语句见《系统设计说明书》第 4 章。

---

<a id="2-技术栈与版本"></a>
# 2. 技术栈与版本

| 类别 | 技术方案 | 版本 |
|---|---|---|
| 后端框架 | FastAPI | 0.115+ |
| ORM | SQLAlchemy | 2.0 |
| 数据库 | MySQL | 8.0（云端） |
| 缓存 | Redis | 7.x（可选） |
| 鉴权 | JWT（python-jose）+ bcrypt | — |
| 定时任务 | APScheduler | 3.x |
| HTTP 客户端 | httpx | 0.27+ |
| 管理端前端 | Vue 3 + Vite + Pinia + Vue Router | Vue 3.5+ / Vite 6+ |
| 用户端 | 微信小程序原生框架 | 最新基础库 |
| AI 编排 | Dify（Docker Compose 自托管） | 1.x |
| 推荐算法 | Python scikit-learn（轻量协同过滤） | 1.5+ |
| 语音识别 | 微信同声传译插件 | — |

---

<a id="3-项目结构详解"></a>
# 3. 项目结构详解

<a id="31-总体结构"></a>
## 3.1 总体结构

```
smartdine/
├── backend/           # FastAPI 后端服务（业务 API + 智能体网关 + 定时任务）
├── admin-web/         # Vue 3 管理端前端（平台端 + 商户端）
├── miniprogram/       # 微信小程序用户端（顾客扫码点餐 / 客服 / 会员）
├── dify/              # Dify 提示词设计、节点编排说明、知识库语料草稿
├── sql/               # 建表与初始化脚本（5 份）
├── docs/              # 项目文档（需求 / 设计 / 开发）
├── .gitignore
└── README.md          # 项目总览
```

<a id="32-后端backend"></a>
## 3.2 后端（backend/）

```
backend/
├── requirements.txt         # Python 依赖清单
├── .env.example             # 环境变量样例
└── app/
    ├── __init__.py           # 包标识（空）
    ├── main.py               # FastAPI 入口：创建 app、注册 CORS、注册路由、启动定时任务、
    │                          #   租户中间件、全局异常处理器、/health 健康检查
    ├── core/                 # 横切关注点——配置、安全、依赖注入、统一响应
    │   ├── config.py         #   Settings：从 .env 加载配置，提供 database_url
    │   ├── deps.py           #   V2: engine/SessionLocal/Base，get_db_with_tenant()
    │   ├── tenant.py         #   ★ V2.0 新增：租户中间件（ContextVar + BaseHTTPMiddleware）
    │   ├── security.py       #   V2: 密码哈希、JWT（含 merchant_id）、三类鉴权依赖
    │   └── response.py       #   统一响应 ok()/fail()，{code, message, data}
    ├── api/v1/               # 路由层：参数校验与编排，不写业务逻辑
    │   ├── platform/         #   ★ V2.0 新增：平台管理端 API
    │   │   ├── auth.py       #     平台管理员登录
    │   │   ├── merchants.py  #     商户入驻审核/列表/状态管理
    │   │   └── dashboard.py  #     平台运营总览
    │   ├── merchant/         #   ★ V2.0 重构：原 api/v1/* → merchant/*，全部带 merchant_id
    │   │   ├── auth.py       #     商户员工登录
    │   │   ├── dish.py       #     菜品 CRUD（含 V2 扩展字段）
    │   │   ├── order.py      #     订单管理（含群体点餐字段）
    │   │   ├── table.py      #     桌台管理（含 QR 码）
    │   │   ├── inventory.py  #     库存管理（含供应商评分）
    │   │   ├── member.py     #     会员管理（平台级+商户级）
    │   │   ├── marketing.py  #     营销活动与优惠券
    │   │   ├── staff.py      #     员工与排班
    │   │   ├── service.py    #     客服工单
    │   │   └── agent.py      #     智能体入口（V2 增强 + A/B 实验）
    │   └── customer/         #   ★ V2.0 新增：用户端 API（不校验 merchant 归属）
    │       ├── auth.py       #     微信登录/手机验证码登录
    │       ├── menu.py       #     商户菜单浏览/LBS 附近商户
    │       ├── order.py      #     顾客下单（双通道统一入口）
    │       ├── service.py    #     客服消息（对接客服智能体）
    │       └── member.py     #     个人中心（跨商户会员档案）
    ├── schemas/              # Pydantic DTO，与 api/v1 三组路由一一对应
    ├── services/             # 业务逻辑与事务编排
    ├── repositories/         # 数据访问层（V2: 所有查询强制 merchant_id）
    ├── models/               # ORM 数据模型（含 V2.0 全部新表/字段）
    ├── agents/               # 智能体网关——业务系统与 Dify 的唯一桥梁
    │   ├── gateway.py        #   V2: Dify Chatflow/Workflow 调用封装，注入 merchant 上下文
    │   └── recommender.py    #   ★ V2.0 新增：混合推荐引擎（多路召回→融合→精排）
    └── tasks/                # 定时任务
        └── scheduler.py      #   V2: 按商户执行——库存预测(9:00)、经营摘要(22:00)、主动客服(每5分)
```

<a id="33-管理端前端admin-web"></a>
## 3.3 管理端前端（admin-web/）

```
admin-web/
├── package.json              # 依赖：vue/vue-router/pinia/axios
├── index.html                # SPA 入口 HTML
├── vite.config.js            # Vite 构建配置
├── public/                   # 静态资源
└── src/
    ├── main.js               # 应用入口：创建 Vue 实例，挂载 Pinia/Router
    ├── App.vue               # 根组件：<router-view/> + 全局 <ToastStack/>
    ├── style.css             # 全局样式：设计令牌（--ink/--paper/--brand 等色板）
    │                          #   + .btn/.card/.tag 等通用类 + .spin/.loading-block 加载态
    ├── router/
    │   └── index.js          # V2: 路由表——/platform/* + /merchant/*，独立登录与权限守卫
    ├── store/
    │   ├── user.js           # V2: platform_admin/merchant_id 标识，token/role
    │   └── app.js            # 门店名称、侧边栏折叠状态
    ├── components/
    │   ├── ToastStack.vue    # 自定义轻提示组件
    │   └── LoadingBlock.vue  # 区块级加载占位
    ├── utils/
    │   ├── index.js          # 通用工具函数
    │   ├── toast.js          # 轻提示方法（success/error/info）
    │   └── pending.js        # usePending()：按 key 跟踪异步操作，驱动按钮 loading 态
    ├── api/
    │   ├── request.js        # Axios 实例：注入 JWT、解析 {code,message,data}、401 退出
    │   ├── platform.js       # ★ V2.0 新增：平台端 API
    │   └── merchant/         # V2: 原 api/* 迁移
    │       ├── auth.js / dish.js / order.js / table.js /
    │       ├── inventory.js / member.js / marketing.js /
    │       ├── staff.js / agent.js
    │       └── experiment.js # ★ V2.0 新增：A/B 实验 API
    └── views/
        ├── platform/         # ★ V2.0 新增：平台管理端页面
        │   ├── Login.vue
        │   ├── Dashboard.vue
        │   ├── Merchants.vue
        │   └── Settings.vue
        └── merchant/         # V2: 原 views/ 迁移
            ├── Login.vue
            ├── layout/Layout.vue
            ├── Dashboard.vue       # V2: 增强——推荐采纳率 + 智能体动态流
            ├── Dish.vue            # V2: 增强——推荐权重/营养信息/成本价
            ├── Order.vue
            ├── Table.vue           # V2: 增强——QR 码展示
            ├── Marketing.vue
            ├── Inventory.vue       # V2: 增强——供应商评分/预测天数
            ├── Member.vue          # V2: 增强——流失风险标记
            ├── Staff.vue
            ├── Settings.vue        # V2: 增强——智能体参数配置
            └── agents/
                ├── OrderAgent.vue       # V2: 增强——推荐策略可视化
                ├── StockAgent.vue       # V2: 增强——多因子预测对照
                ├── ServiceAgent.vue     # V2: 增强——流失预警列表
                ├── AnalyticsAgent.vue   # V2: 增强——What-if 模拟入口
                └── ExperimentAgent.vue  # ★ V2.0 新增：A/B 实验管理
```

<a id="34-小程序miniprogram"></a>
## 3.4 小程序（miniprogram/）

```
miniprogram/
├── project.config.json      # 微信开发者工具项目配置
├── app.js                   # V2: 微信登录、扫码解析、购物车/订单历史、最近商户
├── app.json                 # V2: 9 个页面注册 + tabBar
├── app.wxss                 # 全局样式（与 admin-web 共用设计令牌）
├── api/
│   └── request.js           # wx.request 封装：JWT 注入、{code,message,data} 解析
├── utils/
│   └── util.js              # formatMoney / formatDateTime
└── pages/                   # 9 个业务页面（V2.0 新增 index + search）
    ├── index/               # ★ V2.0 新增：附近商户/选店首页
    ├── search/              # ★ V2.0 新增：商户搜索
    ├── menu/                # V2: 菜单浏览 +「AI 点餐」入口
    ├── dish/                # 菜品详情
    ├── chat/                # V2: 对话点餐增强（推荐卡片/语音/群体/营养条）
    ├── cart/                # V2: 购物车（双通道同步）
    ├── order/               # 订单跟踪
    ├── service/             # V2: 客服增强（主动通知）
    └── mine/                # V2: 跨商户会员中心
```

<a id="35-difydify"></a>
## 3.5 Dify（dify/）

```
dify/
├── prompts/                 # 4 个智能体的系统提示词 + V2 节点编排说明
│   ├── order_recommendation.md
│   ├── stock_forecast.md
│   ├── service_handling.md
│   └── analytics.md
└── knowledge_base/          # 知识库语料草稿（V2: 按商户维度组织）
    ├── menu_intro.md
    ├── store_faq.md
    └── policy.md
```

<a id="36-数据库脚本sql"></a>
## 3.6 数据库脚本（sql/）

```
sql/
├── 00_platform.sql          # ★ V2.0 新增：merchant, platform_admin
├── 01_menu_inventory.sql    # V2: dish, ingredient, dish_ingredient, stock_log
├── 02_order.sql             # V2: order, order_item
├── 03_other.sql             # V2: 其余 11 张业务表
└── 04_agent_v2.sql          # ★ V2.0 新增：dish_pairing, recommendation_log, ab_experiment
```

<a id="37-项目文档docs"></a>
## 3.7 项目文档（docs/）

```
docs/
├── README.md                # 文档索引与阅读指南
├── SRS.md                   # 软件需求规格说明书 V2.0
├── SystemDesign.md           # 系统设计说明书 V2.0
└── Development.md           # 本文件——项目开发文档
```

---

<a id="4-开发规范与约定"></a>
# 4. 开发规范与约定

<a id="41-后端开发规范"></a>
## 4.1 后端开发规范

### 4.1.1 分层职责

新增一个功能时**严格从下往上**依次补齐五层：

```
models        →  定义 ORM 数据模型，对应数据库表结构
repositories  →  数据访问层（SQLAlchemy 增删改查），隔离数据库细节
services      →  业务逻辑与事务编排（状态机、库存联动、积分计算等）
schemas       →  Pydantic DTO（请求/响应模型）
api/v1        →  路由层：仅做参数校验与编排，不写业务逻辑
```

**原则**：路由层不能包含任何数据库查询或业务判断；Service 层可以调用多个 Repository。

### 4.1.2 命名规范

| 层级 | 命名规则 | 示例 |
|---|---|---|
| Model | 单数大驼峰 | `class Dish(Base)` |
| Repository | `{Entity}Repository` | `class DishRepository` |
| Service | `{Entity}Service` | `class DishService` |
| Schema 请求 | `{Entity}Create/Update/Query` | `class DishCreate(BaseModel)` |
| Schema 响应 | `{Entity}Response` | `class DishResponse(BaseModel)` |
| API 路由函数 | `{动作}_{实体}` | `def create_dish()`、`def list_dishes()` |
| API 路径 | RESTful 复数 | `GET /dishes`、`POST /dishes` |

### 4.1.3 V2.0 租户查询模式

所有 Repository 查询必须带上 `merchant_id` 过滤：

```python
# backend/app/repositories/dish.py (V2)
class DishRepository:
    def get_by_merchant(self, db: Session, merchant_id: int, **filters):
        query = db.query(Dish).filter(Dish.merchant_id == merchant_id)
        # ... 其他过滤条件
        return query.all()

    def get_by_id(self, db: Session, dish_id: int, merchant_id: int):
        return db.query(Dish).filter(
            Dish.dish_id == dish_id,
            Dish.merchant_id == merchant_id
        ).first()
```

### 4.1.4 统一响应格式

所有接口返回：
```json
{"code": 0, "message": "ok", "data": {...}}
```

- `code=0` 表示成功；`code` 非 0 为业务错误
- 使用 `core/response.py` 的 `ok(data)` / `fail(message, code)`

<a id="42-前端开发规范"></a>
## 4.2 前端开发规范

### 4.2.1 API 调用规范

- 所有 API 请求通过 `api/request.js` 的 Axios 实例发起
- JWT 由拦截器自动注入，401 自动退出登录
- 统一解析 `{code, message, data}` 结构
- 每个业务模块在 `api/` 下独立一个 js 文件

### 4.2.2 加载状态规范

- **按钮级**：使用 `usePending()` 跟踪异步操作，请求未返回前禁用按钮并显示旋转图标
- **区块级**：列表/网格加载时仅数据区域使用 `<LoadingBlock/>` 占位，工具栏/筛选器始终保持可见
- **页面级**：避免整页闪烁/跳动，静态结构始终渲染

### 4.2.3 样式规范

- 使用 `style.css` 中的设计令牌变量（`--ink`/`--paper`/`--brand` 等）
- 通用组件使用预定义的 `.btn`/`.card`/`.tag` 等 class
- 不引入第三方 UI 组件库（Element Plus 已移除）
- 平台端与商户端共享同一套设计令牌

<a id="43-小程序开发规范"></a>
## 4.3 小程序开发规范

- 每个页面含 `.js`/`.json`/`.wxml`/`.wxss` 四件套
- 网络请求统一使用 `api/request.js` 封装的 `wxRequest`
- 样式与 admin-web 共用设计令牌变量
- 所有页面 JS 提交前通过 `node --check` 语法校验

<a id="44-dify-工作流开发规范"></a>
## 4.4 Dify 工作流开发规范

- 智能体**不直连数据库**——通过 HTTP 节点调用后端 API 获取上下文
- 智能体结果**不自动执行不可逆操作**（退款/下单/发送）——默认作为建议，人工确认
- 每个智能体的系统提示词维护在 `dify/prompts/` 下，与 Dify 控制台内容保持一致
- 知识库按商户维度创建独立知识库

<a id="45-git-协作规范"></a>
## 4.5 Git 协作规范

- 提交粒度：一个功能点一次提交
- 提交信息格式：`[模块] 动作描述`，如 `[backend] 新增 dish 表的 merchant_id 隔离`
- 忽略文件：`backend/venv/`、`__pycache__/`、`*.pyc`、`.env`、`node_modules/`、`dist/`

---

<a id="5-核心设计模式"></a>
# 5. 核心设计模式

<a id="51-五层架构"></a>
## 5.1 五层架构

```
api/v1/{platform,merchant,customer}/*  →  路由层：参数校验
schemas/*                                →  Pydantic DTO
services/*                               →  业务逻辑、事务编排
repositories/*                           →  SQLAlchemy 增删改查
models/*                                 →  ORM 表映射
```

新增功能从下往上补齐五层。V2.0 在 `api/v1` 下新增三组路由前缀区分平台端/商户端/用户端。

<a id="52-多租户数据隔离"></a>
## 5.2 多租户数据隔离（V2.0 新增）

四层隔离策略保证各商户数据完全独立：

| 隔离层 | 策略 | 实现 |
|---|---|---|
| 数据库层 | `WHERE merchant_id = ?` | ORM Repository 查询自动注入 |
| 缓存层 | Key 前缀 `{merchant_id}:` | Redis key 命名规范 |
| 文件存储 | 目录 `/{merchant_id}/` | 上传路径校验前缀 |
| API 网关 | JWT → ContextVar → 中间件 | `core/tenant.py` |

JWT Payload 结构：
```json
{
  "sub": "staff_id",
  "merchant_id": 1001,
  "role": "店长",
  "platform_admin": false
}
```

<a id="53-级联安全删除"></a>
## 5.3 级联安全删除

8 类实体（活动/优惠券/菜品/桌台/预订/食材/供应商/员工）的删除遵循三种策略：

1. **阻断+友好提示**：数据仍被引用时返回 400 + 明确原因
2. **级联删除子项**：先删从表数据再删主表（活动→优惠券、桌台→预订、员工→排班、菜品→BOM）
3. **外键置空**：可选关联置 NULL（删除供应商→食材的 `supplier_id` 置空）

<a id="54-智能体接入唯一化"></a>
## 5.4 智能体接入唯一化

所有 Dify 调用集中在 `agents/gateway.py`，小程序/管理端均不直连 Dify。V2.0 每次调用注入 merchant 上下文。

```python
class DifyGateway:
    async def chat_order(self, message, merchant_id, member_id, table_id, session_id, cart):
        inputs = {
            "merchant_id": merchant_id,
            "menu_context": await self._get_menu_context(merchant_id),
            "member_preferences": await self._get_member_preferences(member_id),
            "hot_items": await self._get_hot_items(merchant_id),
        }
        return await self._call_chatflow(settings.DIFY_ORDER_KEY, message, inputs, session_id)
```

<a id="55-统一响应结构"></a>
## 5.5 统一响应结构

- 成功：`ok(data)` → `{"code": 0, "message": "ok", "data": {...}}`
- 失败：`fail(msg, code)` → `{"code": 非0, "message": "...", "data": null}`
- HTTPException 由全局异常处理器转换为统一格式

---

<a id="6-各模块开发指南"></a>
# 6. 各模块开发指南

<a id="61-新增业务模块步骤"></a>
## 6.1 新增业务模块步骤

以新增「供应商管理」为例：

```
1. sql/  →  编写 CREATE TABLE 语句，确定字段与索引
2. models/  →  class Supplier(Base)，定义 ORM 映射
3. repositories/  →  class SupplierRepository，实现 get/list/create/update/delete
4. services/  →  class SupplierService，实现业务校验（如删除时置空引用食材的外键）
5. schemas/  →  SupplierCreate/SupplierUpdate/SupplierResponse
6. api/v1/merchant/  →  router，注册 GET/POST/PUT/DELETE 路由
7. main.py  →  注册路由到 app
```

<a id="62-后端开发指南"></a>
## 6.2 后端开发指南

### 6.2.1 现有模块清单

| 模块 | API 路径 | 关键功能 |
|---|---|---|
| 认证 | `/api/v1/merchant/auth` | 商户员工登录、JWT 签发 |
| 菜品 | `/api/v1/merchant/dishes` | CRUD + 推荐权重/营养信息 + BOM |
| 订单 | `/api/v1/merchant/orders` | 列表/详情/状态流转/退款 |
| 桌台 | `/api/v1/merchant/tables` | 开台/结账/清理/预订/QR码 |
| 库存 | `/api/v1/merchant/inventory` | 食材/出入库/供应商（含评分） |
| 会员 | `/api/v1/merchant/members` | 平台级档案 + 商户级积分等级 |
| 营销 | `/api/v1/merchant/marketing` | 活动/优惠券 CRUD + 核销 |
| 员工 | `/api/v1/merchant/staff` | 员工 CRUD + 排班 |
| 客服 | `/api/v1/merchant/service` | 工单队列/处理完成 |
| 智能体 | `/api/v1/merchant/agent` | 4 个对话/触发入口 + 配置 + A/B 实验 |
| 平台 | `/api/v1/platform/*` | 商户审核/列表/状态 + 平台运营总览 |
| 用户端 | `/api/v1/customer/*` | 选店/菜单/下单/客服/会员 |

### 6.2.2 启动与调试

```bash
cd backend
venv\Scripts\activate
uvicorn app.main:app --reload --port 8000
```

Swagger 文档：`http://127.0.0.1:8000/docs`

### 6.2.3 单元测试

```bash
# 导入校验
python -c "from app.main import app"

# 运行单测（如已编写）
pytest app/tests/ -v
```

<a id="63-管理端开发指南"></a>
## 6.3 管理端开发指南

### 6.3.1 V2.0 路由结构

```
/                        → 重定向到 /platform 或 /merchant
/platform/login          → 平台管理员登录
/platform/dashboard      → 平台运营总览
/platform/merchants      → 商户管理（审核/列表/状态）
/platform/settings       → 平台设置

/merchant/login          → 商户员工登录
/merchant/dashboard      → 商户运营总览（V2 增强）
/merchant/dishes         → 菜品管理（V2 增强）
/merchant/orders         → 订单管理
/merchant/tables         → 桌台管理（V2 增强）
/merchant/marketing      → 营销活动
/merchant/inventory      → 库存管理（V2 增强）
/merchant/members        → 会员管理（V2 增强）
/merchant/staff          → 员工管理
/merchant/agents/order   → 点餐推荐工作台（V2 增强）
/merchant/agents/stock   → 库存预测工作台（V2 增强）
/merchant/agents/service → 客服处理工作台（V2 增强）
/merchant/agents/analytics → 经营分析工作台（V2 增强）
/merchant/agents/experiments → A/B 实验管理（★ 新增）
/merchant/settings       → 系统设置（V2 增强）
```

### 6.3.2 启动与构建

```bash
cd admin-web
npm install
npm run dev      # 开发
npm run build    # 生产构建（已验证可成功构建）
```

<a id="64-小程序开发指南"></a>
## 6.4 小程序开发指南

### 6.4.1 V2.0 核心流程

```
打开小程序 → LBS 获取位置 → 展示附近商户（index 页）
  → 选择商户进入菜单（menu 页）
  → 传统浏览加购 或 点击「🤖 AI 点餐」切换对话通道（chat 页）
  → 购物车双通道同步 → 下单支付（模拟）→ 查单评价
  → 在线客服（service 页）→ 跨商户会员中心（mine 页）
```

### 6.4.2 本地预览

微信开发者工具 → 导入项目 → 选择 `miniprogram/` 目录 → 扫码登录即可预览。

### 6.4.3 上线前准备

1. 将 `api/request.js` 的 `BASE_URL` 换成正式 HTTPS 后端域名
2. 在微信小程序后台配置服务器合法域名
3. 将 `project.config.json` 的 `appid` 换成正式注册的小程序 AppID
4. 接入微信支付真实签名流程

<a id="65-dify-工作流开发指南"></a>
## 6.5 Dify 工作流开发指南

### 6.5.1 四个智能体 V2.0 概览

| 智能体 | 类型 | V1.0 节点 | V2.0 节点 | 核心升级 |
|---|---|---|---|---|
| 点餐推荐 | Chatflow | 6 | 10+ | 多路召回(CF+CB+KG)→融合→精排+MMR→LLM策略调控 |
| 库存预测 | Workflow | 5 | 12+ | 时序特征→分段预测→LLM校准→供应商匹配→损耗/替代方案 |
| 客服处理 | Chatflow | 6 | 12+ | 深层意图+情绪趋势→多路RAG→归因→流失预警→分流+挽回 |
| 经营分析 | Chatflow+Workflow | 4+4 | 8+8 | 异常检测+下钻→菜单工程BCG→RFM→排班建议 |

### 6.5.2 点餐推荐 Chatflow V2 节点链路

```
[开始] → [多模态预处理] → [场景与意图识别(LLM)]
    → [用户画像获取(HTTP)] + [实时菜单获取(HTTP)]
    → [协同过滤召回(CODE)] ─┐
    → [内容推荐召回(CODE)] ─┼→ [多路融合去重(CODE)]
    → [规则图谱召回(CODE)] ─┘       │
                                     ▼
    → [精排(CODE)] → [LLM策略调控+理由生成(LLM)]
    → [安全检查(IF/ELSE)] → [推荐日志记录(HTTP)]
    → [回复生成(LLM)] → [结束]
```

### 6.5.3 库存预测 Workflow V2 节点链路

```
[开始] → [数据准备(HTTP×3并行)]
    ├─ 近90日销量明细
    ├─ 当前库存+BOM+临期数据
    └─ 供应商信息+促销计划
    ↓
[时序特征工程(CODE)] → [分段预测(CODE)] → [LLM预测校准(LLM)]
    ↓
[可用天数与状态判定(CODE)] → 充足/预警/紧张/即将售罄/临期
    ↓
[供应商匹配与评分(CODE)] → [采购建议生成(LLM)]
[损耗消化建议(LLM)] → 临期食材关联菜品促销
[替代方案建议(LLM)] → 即将售罄食材替代推荐
    ↓
[回写(HTTP)] → [结束]
```

### 6.5.4 客服处理 Chatflow V2 节点链路

```
[开始] → [语言检测(LLM)] → [深层意图分类(LLM)]
    ├─ 咨询/投诉/建议/预订/催单/退款请求
    └─ 子类别（投诉→上菜延迟/口味/分量/服务/卫生）
    ↓
[情绪评估(LLM)] ← 当前消息情绪 + 会话级情绪趋势
    ↓
[FAQ多路检索(RAG×2)] ── 商户FAQ + 通用餐饮知识库
[订单/会员查询(HTTP)] ── 如有订单上下文
    ↓
[归因分析(LLM)] ── 投诉类：定位问题环节
[流失风险评估(CODE+LLM)] ── RFM + 投诉次数 + 消费趋势
    ↓
[话术草拟(LLM)]
    ├─ 咨询→FAQ答案
    ├─ 投诉→致歉+归因+解决方案+补偿建议
    └─ 高流失风险→追加挽回话术+专属优惠券
    ↓
[分流判定(IF/ELSE)]
    ├─ 高置信FAQ+低情绪 → 自动回复
    ├─ 中情绪/涉及金额 → 草稿待人工确认
    └─ 强情绪/安全相关 → 强制转人工+紧急标记
    ↓
[工单回写(HTTP)] → [结束]
```

### 6.5.5 经营分析 V2 节点链路

**(A) 自然语言查数 Chatflow：**
```
[开始] → [问题理解与拆解(LLM)]
    → [数据查询(HTTP/CODE)] ── 受控查询模板
    → [数据洞察(LLM)] → [结束]
```

**(B) 经营摘要 Workflow（定时）：**
```
[开始] → [多源汇总(HTTP×4并行)]
    ├─ 订单与营收 / 评价与情感 / 客流与时段 / 库存与采购
    ↓
[KPI计算(CODE)] ── 营收/订单/客单价/好评率/翻台率/库存周转 + 环比
[异常检测(CODE+LLM)] ── 自动下钻至菜品/时段/客群 + 根因分析
[菜单工程分析(CODE)] ── BCG矩阵：明星/金牛/问题/瘦狗
[RFM客群分析(CODE)] ── 三维分群+流失风险
    ↓
[趋势与洞察(LLM)] ── 经营摘要 + 优化建议
[排班建议(LLM)] ── 结合客流高峰
    ↓
[回写(HTTP)] → [结束]
```

---

<a id="7-构建与部署"></a>
# 7. 构建与部署

<a id="71-后端部署"></a>
## 7.1 后端部署

```
┌────────────────────────────────────┐
│  Linux 服务器（或 Windows Server）  │
│  ┌──────────────────────────────┐  │
│  │  Nginx（反向代理+静态资源）    │  │
│  │  ├─ /api/* → uvicorn :8000   │  │
│  │  ├─ /admin → admin-web dist/ │  │
│  │  └─ /uploads → 文件目录      │  │
│  └──────────────────────────────┘  │
│  ┌──────────────────────────────┐  │
│  │  FastAPI (uvicorn :8000)     │  │
│  └──────────────────────────────┘  │
│  ┌──────────────────────────────┐  │
│  │  MySQL 8.0 (:3306)           │  │
│  └──────────────────────────────┘  │
└────────────────────────────────────┘
```

```bash
# 生产化启动（Linux）
cd backend
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

<a id="72-管理端部署"></a>
## 7.2 管理端部署

```bash
cd admin-web
npm run build
# 将 dist/ 部署到 Nginx 的 /admin 路径下
```

<a id="73-小程序发布"></a>
## 7.3 小程序发布

1. 确保 `api/request.js` 的 `BASE_URL` 为正式 HTTPS 域名
2. 确保 `project.config.json` 的 `appid` 为注册 AppID
3. 在微信小程序后台配置服务器合法域名
4. 微信开发者工具 → 上传 → 提交审核

<a id="74-dify-部署"></a>
## 7.4 Dify 部署

```bash
# Linux 虚拟机（Docker Compose）
cd dify/docker
docker compose up -d
```

Dify API 对内暴露端口供后端调用，不对外网开放。

---

<a id="8-两周开发计划"></a>
# 8. 两周开发计划

> 本章与《软件需求规格说明书》第 9 章保持一致。

<a id="81-总体策略"></a>
## 8.1 总体策略

**团队配置：** 3 人（黄岑果、黄禹菲、夏思凯），全员全栈参与，按模块分工并行开发。

**每天一个关键交付**，前后端并行 + Dify 工作流穿插进行。第 1 周搭建底座与业务模块，第 2 周攻坚智能体与用户端，最后两天集中联调测试与准备演示。

<a id="82-第-1-周详细安排"></a>
## 8.2 第 1 周详细安排

| 天数 | 阶段 | 黄岑果（组长） | 黄禹菲 | 夏思凯 | 里程碑交付物 |
|---|---|---|---|---|---|
| **Day 1** | 环境与数据库 | 项目脚手架搭建（FastAPI + Vue3 项目初始化）；Dify 环境部署与验证 | 数据库设计与建表（全部实体 + merchant_id 隔离）；初始数据准备 | 管理端 UI 框架搭建（Vue3 路由/布局/权限骨架）；商户管理端页面框架 | ✅ 三端项目跑通 ✅ 数据库建表完成 ✅ Dify 可用 |
| **Day 2** | 多商户底座 | 后端：商户入驻 API（注册/审核/状态）、多租户中间件（自动注入 merchant_id） | 后端：菜品 + 订单 + 桌台 API（全部带 merchant_id 隔离） | 平台管理端页面（商户审核/列表/状态管理）；商户管理端：菜品管理页 | ✅ 多租户数据隔离可用 ✅ 商户入驻流程跑通 ✅ 平台端+商户端基础页面 |
| **Day 3** | 业务模块 API | 后端：库存 + 会员 + 员工 API；智能体调用网关层（统一调用 Dify 的 service 封装） | 后端：营销活动 API；Dify 知识库搭建（菜单 FAQ 语料 × 2 个模拟商户） | 商户管理端：订单管理 + 桌台管理 + 库存管理页面 | ✅ 全部业务 API 可用 ✅ 管理端核心页面完成 ✅ 知识库就绪 |
| **Day 4** | Dify 智能体设计 | **点餐推荐 Chatflow V2**（意图识别 + RAG 菜单检索 + LLM 推荐 + 订单操作 + 回复生成，6 节点） | **客服处理 Chatflow V2**（消息分类 + 情绪识别 + FAQ 检索 + 话术草拟 + 分流判定 + 工单回写，6 节点） | **库存预测 Workflow**（数据拉取 + 消耗预测代码 + 可用天数 + LLM 采购建议 + 回写，5 节点）；**经营摘要 Workflow**（多源汇总 + KPI 计算 + LLM 洞察 + 回写，4 节点） | ✅ 四个智能体 Dify 工作流初版完成 ✅ 后端与 Dify 调用联通 |
| **Day 5** | 管理端联调 | 管理端与后端 API 联调（菜品/订单/库存/会员完整 CRUD 流程） | 智能体工作台页面（点餐推荐 + 库存预测 + 客服处理 + 经营分析）与后端智能体接口联调 | 智能体参数配置页 + 运营总览（KPI 卡片 + 智能体动态流） | ✅ 管理端全部页面与后端联通 ✅ 智能体工作台可从管理端触发 |
| **Day 6** | 用户端开发 | 用户端小程序框架搭建 + 商户选择/附近商户页面 + 扫码进入 | **对话点餐核心页面**（聊天界面 + 推荐卡片 + 购物车摘要 + 语音输入按钮） | 用户端：购物车 + 下单支付 + 订单跟踪页面 | ✅ 用户端框架完成 ✅ 对话点餐界面完成 |
| **Day 7** | 缓冲与修补 | 第 1 周遗留问题修补；代码 review；接口文档整理 | 管理端 UI 细节打磨；用户端页面补充 | 数据库初始演示数据准备（2 个模拟商户 × 20+ 菜品 × 50+ 订单） | ✅ 第 1 周全部交付物达标 |

<a id="83-第-2-周详细安排"></a>
## 8.3 第 2 周详细安排

| 天数 | 阶段 | 黄岑果（组长） | 黄禹菲 | 夏思凯 | 里程碑交付物 |
|---|---|---|---|---|---|
| **Day 8** | 点餐智能体深度联调 | 点餐 Chatflow 调优（提示词精调、RAG 检索准确性测试、推荐理由质量检查）；冷启动策略实现 | 用户端对话点餐与 Dify 联调（SSE 流式输出、推荐卡片渲染、购物车同步） | 库存预测 Workflow 调优（预测公式校准、预警阈值调试、采购建议合理性检查） | ✅ 点餐对话端到端跑通 ✅ 推荐采纳率可测量 ✅ 库存预测产出合理 |
| **Day 9** | 客服 + 经营智能体联调 | 客服 Chatflow 调优（分类准确率、情绪识别、分流逻辑）；主动服务定时任务开发 | 用户端客服页面联调；客服工作台（管理端）与工单流程联通 | 经营分析 Workflow 调优（KPI 计算校准、异常检测逻辑、自然语言查数联调） | ✅ 客服端到端跑通 ✅ 经营分析产出摘要与图表 |
| **Day 10** | 用户端闭环联调 | 用户端完整流程串联：选店→扫码→对话点餐→下单→支付（模拟）→查单→评价→客服 | 会员中心页面（积分/等级/优惠券/偏好管理）；群体点餐基础流程 | 订单状态实时推送（管理端出餐状态变更→用户端更新）；催单功能 | ✅ 用户端核心闭环跑通 ✅ 会员体系可用 ✅ 实时状态推送可用 |
| **Day 11** | 管理端 + 平台端完善 | 商户管理端功能补全（营销活动/员工排班/系统设置/角色权限） | 平台管理端完整流程（商户入驻→审核→开通→停用）；平台运营总览 | 智能体运行监控面板（各智能体调用次数/成功率/采纳率/耗时统计 + 运行日志列表） | ✅ 管理端全部模块可用 ✅ 平台端商户生命周期管理完整 ✅ 智能体监控可观测 |
| **Day 12** | 测试与修复 | 端到端功能测试（按验收指标逐项检查）；Bug 修复 | 多商户数据隔离测试（跨商户越权访问、数据泄露检查）；边界场景测试 | 性能优化（智能体响应时长优化、数据库查询索引优化）；UI 适配 | ✅ 核心功能测试通过 ✅ 多商户隔离验证通过 ✅ 性能达标 |
| **Day 13** | 演示准备 | 演示脚本编写（按「顾客扫码→对话点餐→下单→后厨出餐→客服→经营分析」的故事线串联） | 演示数据精修（2 个商户的完整经营数据，含多日订单/评价/库存变动，确保智能体产出精彩） | 演示环境部署（确保 Dify + 后端 + 前端均可稳定运行）；答辩 PPT 制作 | ✅ 演示脚本定稿 ✅ 演示数据就绪 ✅ 答辩 PPT 初版 |
| **Day 14** | 最终演练 | 全流程演练（模拟答辩：15 分钟演示 + 5 分钟 Q&A）；突发问题修复 | 文档完善（SRS + 系统设计说明书 + 本开发文档终稿 + 接口文档 + 部署文档） | PPT 终稿 + 演示录屏备份 | ✅ 演练通过 ✅ 全部文档交付 ✅ 可演示状态 |

<a id="84-成员分工"></a>
## 8.4 成员分工

| 成员 | 主攻方向 | 关键产出 |
|---|---|---|
| **黄岑果（组长）** | 后端架构 + 多租户 + 点餐推荐智能体 + 演示 | FastAPI 全部 API、多租户中间件、Dify 点餐 Chatflow V2、演示脚本 |
| **黄禹菲** | 管理端前端 + 客服智能体 + Dify 知识库 + 用户端对话页 | 平台端+商户端全部页面、Dify 客服 Chatflow V2、用户端对话点餐核心页 |
| **夏思凯** | 用户端小程序 + 库存/经营智能体 + 数据库 + PPT | 用户端完整小程序、Dify 库存+经营 Workflow V2、数据库设计、答辩 PPT |

<a id="85-风险预案"></a>
## 8.5 风险预案

| 风险 | 概率 | 预案 |
|---|---|---|
| Dify 部署/稳定性问题 | 中 | Day 1 提前验证；准备 Dify Docker Compose 一键部署脚本；如 Dify 不可用，改用后端直接调用 LLM API + 硬编码工作流逻辑作为 Plan B |
| 点餐推荐对话体验不达标 | 中 | Day 8 集中调优；若混合推荐引擎来不及，先上线「RAG + LLM」简化版（保证演示效果），协同过滤可后续迭代 |
| 微信小程序审核/支付接入延迟 | 高 | 支付使用模拟/沙箱环境；小程序使用体验版/开发版演示（无需审核） |
| 用户端小程序开发进度落后 | 中 | Day 6–7 集中人力突击；优先保障对话点餐核心链路，次要页面可简化 |

---

<a id="9-v10-v20-代码改造清单"></a>
# 9. V1.0 → V2.0 代码改造清单

> 本章与《系统设计说明书》第 12 章保持一致。共 39 项，按依赖顺序排列，每天一个 Phase。

<a id="91-phase-1多商户底座day-1-2"></a>
## 9.1 Phase 1：多商户底座（Day 1-2）

| 序号 | 改造项 | 文件 | 说明 |
|---|---|---|---|
| 1 | 新建 `merchant`/`platform_admin` 表 | `sql/00_platform.sql` | 执行建表 |
| 2 | 全部业务表加 `merchant_id` 列 | `sql/01~03` ALTER TABLE | 批量 ALTER |
| 3 | 新增租户中间件 | `backend/app/core/tenant.py` | ContextVar + middleware |
| 4 | 修改 JWT 签发逻辑 | `backend/app/core/security.py` | payload 增加 `merchant_id`、`platform_admin` |
| 5 | 修改 `get_db` 依赖 | `backend/app/core/deps.py` | 从 ContextVar 获取 merchant_id |
| 6 | Repository 层加租户过滤 | `backend/app/repositories/*.py` | 所有查询方法加 `merchant_id` 参数 |
| 7 | 平台端登录 API | `backend/app/api/v1/platform/auth.py` | 新建 |
| 8 | 商户入驻/审核 API | `backend/app/api/v1/platform/merchants.py` | 新建 |
| 9 | 原 API 路径迁移 | `backend/app/main.py` 路由注册 | `/api/v1/*` → `/api/v1/merchant/*` |
| 10 | 平台管理端页面 | `admin-web/src/views/platform/` | 新建 Login/Dashboard/Merchants |

<a id="92-phase-2数据模型扩展day-3"></a>
## 9.2 Phase 2：数据模型扩展（Day 3）

| 序号 | 改造项 | 文件 | 说明 |
|---|---|---|---|
| 11 | `dish` 表加列 | `sql/01` ALTER | cost_price/nutrition/recommended_weight/total_sales |
| 12 | `order` 表加列 | `sql/02` ALTER | discount_amount/actual_amount/is_group_order/member_count |
| 13 | `supplier` 表加列 | `sql/03` ALTER | on_time_rate/quality_score/price_stability |
| 14 | `dining_table` 加列 | `sql/03` ALTER | qr_code_url |
| 15 | `member` 表拆分 | `sql/03` CREATE + 迁移脚本 | member + member_merchant |
| 16 | 推荐/A/B表 | `sql/04_agent_v2.sql` | dish_pairing/recommendation_log/ab_experiment |
| 17 | 更新 ORM 模型 | `backend/app/models/*.py` | 对应新增/修改字段 |
| 18 | 更新 Schema | `backend/app/schemas/*.py` | 对应新增字段 |

<a id="93-phase-3dify-工作流-v2day-4"></a>
## 9.3 Phase 3：Dify 工作流 V2（Day 4）

| 序号 | 改造项 | 文件 | 说明 |
|---|---|---|---|
| 19 | 点餐 Chatflow V2 节点 | Dify 控制台 | 增加多路召回与精排节点 |
| 20 | 库存 Workflow V2 节点 | Dify 控制台 | 增加多因子特征与校准 |
| 21 | 客服 Chatflow V2 节点 | Dify 控制台 | 增加流失预警与主动服务 |
| 22 | 经营分析 V2 节点 | Dify 控制台 | 增加异常检测与 What-if |
| 23 | 更新提示词 | `dify/prompts/*.md` | 各智能体系统提示词替换为 V2 版本 |
| 24 | 更新知识库 | `dify/knowledge_base/` | 按商户维度组织语料 |
| 25 | 升级 gateway.py | `backend/app/agents/gateway.py` | 增加 merchant 上下文注入、V2 输入变量 |

<a id="94-phase-4前端改造day-5-6"></a>
## 9.4 Phase 4：前端改造（Day 5-6）

| 序号 | 改造项 | 文件 | 说明 |
|---|---|---|---|
| 26 | 平台端路由+守卫 | `admin-web/src/router/index.js` | 增加 platform 路由组 |
| 27 | 平台端 API | `admin-web/src/api/platform.js` | 新建 |
| 28 | 平台端页面 | `admin-web/src/views/platform/*` | 3 个页面 |
| 29 | 商户端路由调整 | `admin-web/src/router/index.js` | 路径前缀加 /merchant |
| 30 | 商户端 API 路径调整 | `admin-web/src/api/merchant/*` | 迁移 + 路径更新 |
| 31 | 菜品管理页增强 | `admin-web/.../Dish.vue` | 推荐权重/营养信息/成本价表单 |
| 32 | 库存管理页增强 | `admin-web/.../Inventory.vue` | 供应商评分列/预测天数 |
| 33 | A/B 实验页 | `admin-web/.../agents/ExperimentAgent.vue` | 新建 |
| 34 | 运营总览增强 | `admin-web/.../Dashboard.vue` | 智能体动态/KPI增强 |
| 35 | 小程序选店首页 | `miniprogram/pages/index/` | 新建 |
| 36 | 小程序菜单页 V2 | `miniprogram/pages/menu/` | AI 入口按钮 |
| 37 | 小程序对话页 V2 | `miniprogram/pages/chat/` | 推荐卡片/群体入口/营养条 |
| 38 | 小程序客服页 V2 | `miniprogram/pages/service/` | 主动通知 |
| 39 | 小程序会员中心 V2 | `miniprogram/pages/mine/` | 跨商户积分/偏好管理 |

---

<a id="10-当前完成度与待办"></a>
# 10. 当前完成度与待办

<a id="101-v10-已完成"></a>
## 10.1 V1.0 已完成

- ✅ 后端：9 个业务模块（菜品/订单/桌台/库存/会员/营销/员工/认证/客服工单）+ 智能体网关与配置均已实现五层完整代码，通过导入校验与关键业务逻辑单测
- ✅ 删除功能：8 类实体均已支持级联安全删除，全局异常处理器透传错误信息
- ✅ 管理端：登录/布局/运营总览/7 个业务管理页面/4 个智能体工作台/系统设置，`npm run build` 通过；已移除 Element Plus，改为自研 CSS 设计系统
- ✅ 小程序：7 个业务页面全部实现，语法校验通过；已按管理端设计语言完成视觉重设计，可通过微信开发者工具本地预览
- ✅ 数据库：三份建表脚本覆盖全部数据实体
- ✅ Dify：4 个智能体 V1.0 提示词、节点编排建议与知识库语料草稿

<a id="102-v20-待开发"></a>
## 10.2 V2.0 待开发

按两周计划执行，详见第 8 章和第 9 章：

- 🔲 **Day 1-2**：多商户底座（10 项）
- 🔲 **Day 3**：数据模型扩展（8 项）
- 🔲 **Day 4**：Dify 工作流 V2（7 项）
- 🔲 **Day 5-6**：前端改造（14 项）
- 🔲 **Day 7-11**：智能体联调、用户端闭环、管理端完善
- 🔲 **Day 12-14**：测试修复、演示准备、文档完善

<a id="103-已知问题与简化"></a>
## 10.3 已知问题与简化

| 问题 | 说明 | 影响范围 |
|---|---|---|
| 微信支付模拟 | 当前以管理端/小程序「确认支付」模拟收款，未接入真实微信支付统一下单签名与 `wx.requestPayment`（需商户号与证书） | 演示可用，上线需接入 |
| 客服分类兜底 | 后端以关键词规则兜底判定 `category/sentiment/to_human`，V2.0 将在 Dify Chatflow 内通过 LLM 节点实现结构化分类替换 | V1.0 可用，V2.0 升级 |
| 订单历史本地存储 | 后端订单创建不强制绑定会员身份，历史订单号由小程序本地存储维护 | 少量订单丢失风险 |
| 推荐冷启动 | 混合推荐引擎在新商户/新用户场景下使用热销+规则兜底策略，协同过滤需积累足够交互数据后生效 | Day 8 联调时处理 |
| 多商户初始数据 | 平台审核通过后自动创建默认菜品分类与桌台模板，完整初始化脚本待 Day 1-2 实现 | — |

---

<a id="11-附录"></a>
# 11. 附录

<a id="附录-a环境变量清单"></a>
## 附录 A：环境变量清单

`backend/.env` 完整配置项：

```bash
# 数据库
DATABASE_URL=mysql+pymysql://user:pass@host:3306/smartdine

# JWT
JWT_SECRET=your-secret-key
JWT_ALGORITHM=HS256
JWT_EXPIRE_HOURS=24

# Dify
DIFY_BASE_URL=http://192.168.x.x:5001/v1
DIFY_ORDER_KEY=app-xxxx          # 点餐推荐
DIFY_STOCK_KEY=app-xxxx          # 库存预测
DIFY_SERVICE_KEY=app-xxxx        # 客服处理
DIFY_ANALYTICS_KEY=app-xxxx      # 经营分析
DIFY_TIMEOUT=15

# 微信
WECHAT_APPID=wx***
WECHAT_SECRET=***

# Redis（可选）
REDIS_URL=redis://localhost:6379/0
```

<a id="附录-b常用命令速查"></a>
## 附录 B：常用命令速查

```bash
# --- 后端 ---
cd backend
venv\Scripts\activate                           # 激活虚拟环境
uvicorn app.main:app --reload --port 8000       # 启动开发服务器
python -c "from app.main import app"            # 导入校验
curl http://127.0.0.1:8000/health               # 健康检查
curl http://127.0.0.1:8000/docs                 # Swagger 文档

# --- 管理端 ---
cd admin-web
npm install                                      # 安装依赖
npm run dev                                      # 启动开发服务器（:5173）
npm run build                                    # 生产构建 → dist/
node -e "require('./src/router/index.js')"       # JS 语法校验

# --- 小程序 ---
# 微信开发者工具 → 导入项目 → 选择 miniprogram/
# 所有页面 JS 语法校验：
for f in miniprogram/pages/*/*.js; do node --check "$f"; done

# --- 数据库 ---
# 连接云端 MySQL 后按顺序执行：
source sql/00_platform.sql;
source sql/01_menu_inventory.sql;
source sql/02_order.sql;
source sql/03_other.sql;
source sql/04_agent_v2.sql;

# --- Git ---
git status
git add <files>
git commit -m "[模块] 动作描述"
```

<a id="附录-c页面功能智能体对照表"></a>
## 附录 C：页面—功能—智能体对照表

| 管理端页面 | 核心功能 | 关联智能体 |
|---|---|---|
| **平台—运营总览** | 平台 KPI、商户分布、待审核 | — |
| **平台—商户管理** | 商户审核、列表、状态管理 | — |
| **平台—系统设置** | 平台信息、管理员账号 | — |
| 商户—运营总览 | 经营 KPI、常用操作、智能体协同、趋势与动态 | 全部（状态/动态展示） |
| 商户—菜品管理 | 菜品 CRUD、标签/过敏原/营养信息、BOM、推荐权重 | 点餐推荐、库存预测（数据源） |
| 商户—订单管理 | 订单跟踪、状态流转、退款 | 点餐推荐、经营分析（数据源） |
| 商户—桌台管理 | 台位状态、QR 码、预订 | 客服处理（预订） |
| 商户—营销活动 | 券/套餐/促销与核销统计 | 经营分析（效果评估）、点餐推荐（联动） |
| 商户—库存管理 | 食材库存、出入库、供应商（含评分） | 库存预测、点餐推荐（实时库存） |
| 商户—会员管理 | 档案、等级、积分、流失预警 | 点餐推荐（偏好）、经营分析 |
| 商户—员工管理 | 账号、角色、排班、工时 | 经营分析（排班建议） |
| 商户—点餐推荐工作台 | 代客点餐、智能推荐、群体点餐、订单联动 | **点餐推荐智能体** |
| 商户—库存预测工作台 | 消耗预测、可用天数、采购建议、损耗消化 | **库存预测智能体** |
| 商户—客服处理工作台 | 消息收件箱、分流、话术草拟、主动服务 | **客服处理智能体** |
| 商户—经营分析工作台 | 自然语言查数、KPI、异常检测、What-if、菜单工程 | **经营分析智能体** |
| 商户—AI 实验管理 | A/B 实验创建、流量分配、结果对比 | 点餐推荐（A/B 测试） |
| 商户—系统设置 | 商户信息、角色权限、智能体参数 | 全部（参数配置） |

---

（文档结束）
