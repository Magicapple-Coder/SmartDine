# SmartDine（智餐 AI）· 多商户餐厅一体化运营管理平台

**版本 V2.0 · 多商户 SaaS + AI 智能体深度升级**

面向中小餐饮门店的「AI 原生」多商户 SaaS 运营管理平台：平台管理端 + 商户管理端（Vue3）+ 用户端（微信小程序）+ 后端服务（FastAPI）+ 四个基于 Dify 的深度 AI 智能体（点餐推荐 / 库存预测 / 客服处理 / 经营分析）。

详细需求见 [docs/SRS.md](docs/SRS.md)，系统设计见 [docs/SystemDesign.md](docs/SystemDesign.md)，开发指南见 [docs/Development.md](docs/Development.md)。
本 README 提供整体架构图、核心设计模式、快速开始步骤，以及各模块的目录与文件级导览。

**V2.0 核心升级：** 多商户 SaaS 架构（平台+商户两层数据隔离）| 点餐推荐混合引擎（协同过滤+内容推荐+LLM策略调控）| 库存多因子时序预测 | 客服多轮对话+主动服务+流失预警 | 经营分析异常检测+What-if模拟

## 目录总览

```
smartdine/
├── backend/      # FastAPI 后端服务（业务 API + 智能体网关 + 定时任务）
├── admin-web/    # Vue 3 管理端前端（门店管理者使用的 Web 控制台）
├── miniprogram/  # 微信小程序用户端（顾客扫码点餐 / 客服 / 会员）
├── dify/         # Dify 提示词设计、节点编排说明、知识库语料草稿
├── sql/          # 建表与初始化脚本
├── docs/         # 需求 / 设计 / 开发文档
├── .gitignore
└── README.md     # 本文件
```

---

## 整体架构 —— 四端如何连起来

```
┌────────────────┐   微信登录 / 选店 / 扫码点餐 / 下单 / 客服      ┌──────────────────────┐
│ 微信小程序      │ ───────────────────────────────────────────▶  │                      │
│ (顾客端)       │ ◀───────────────────────────────────────────  │   FastAPI 后端        │      ┌───────────┐
└────────────────┘                                               │  backend/app/        │ ───▶ │  MySQL 8   │
                                                                 │  平台端 + 商户端 API  │ ◀─── │ (sql/*.sql)│
┌────────────────┐   商户员工登录 / 业务管理                       │  + 用户端 API         │      └───────────┘
│ 商户管理端      │ ───────────────────────────────────────────▶  │  + 多租户中间件       │
│ (店员/店长)    │ ◀───────────────────────────────────────────  └─────────┬────────────┘
└────────────────┘                                                        │ agents/gateway.py
                                                                          ▼
┌────────────────┐   平台管理员登录 / 商户审核                  ┌──────────────────────┐
│ 平台管理端      │ ──────────────────────────────────────────▶ │     Dify 平台         │
│ (超级管理员)   │ ◀──────────────────────────────────────────  │ 4 个智能体应用(V2)    │
└────────────────┘                                               │ Chatflow/Workflow    │
                                                                 └──────────────────────┘
```

- **平台端（V2.0 新增）**：超级管理员审核商户入驻、管理商户状态、查看平台运营数据。路由前缀 `/platform`，独立于商户端权限体系。
- **商户端**：各商户独立管理菜品/订单/桌台/库存/会员/员工/营销/智能体配置，数据通过 `merchant_id` 严格隔离。路由前缀 `/merchant`，所有 API 通过租户中间件自动注入隔离条件。
- **顾客侧**：小程序选店（LBS 附近商户）→ 菜单浏览（传统加购）+ 对话点餐（AI推荐）双通道 → 下单支付（模拟）→ 查单客服。购物车数据在传统菜单与 AI 对话双通道间实时同步。
- **AI 侧**：4 个智能体通过 `agents/gateway.py` 统一调用 Dify。**点餐推荐**为体验依赖（传统菜单兜底，AI通道提供个性化推荐/过敏原检测/群体点餐/智能凑单/营养管理等传统方式不可企及的能力）；**库存预测/客服处理/经营分析**为刚性依赖（其解决的多因子计算/并发响应/跨维度分析问题人工无法在合理时间内完成）。详见 SRS 5.0 节智能体依赖类型设计。

## 核心设计模式

- **多租户数据隔离（V2.0 新增）**：所有业务表以 `merchant_id` 作为租户隔离键，通过四层隔离策略保证数据安全——数据库层（ORM 查询自动注入 `WHERE merchant_id = ?`）、缓存层（Redis key 以 `{merchant_id}:` 为前缀）、文件存储层（`/{merchant_id}/` 目录隔离）、API 网关层（JWT 解析 → ContextVar → 中间件校验）。详见《系统设计说明书》第 3 章。
- **统一响应结构**：所有接口返回 `{code, message, data}`（`core/response.py` 的 `ok()` / `fail()`），`code=0` 表示成功。`main.py` 里还注册了一个全局 `HTTPException` 处理器，把 FastAPI 默认的 `{"detail": "..."}` 错误体也转换成同样的形状——这样无论是正常响应还是后端主动抛出的 400/404 错误，前端 axios 拦截器都只需要读 `message` 字段就能拿到人类可读的提示，不用为错误路径单独写一套解析逻辑。
- **五层架构**：`api/v1`（参数校验 / 路由）→ `schemas`（Pydantic DTO）→ `services`（业务规则、事务编排）→ `repositories`（SQLAlchemy 增删改查）→ `models`（ORM 表映射）。V2.0 在 `api/v1` 下新增 `platform/`、`merchant/`、`customer/` 三组路由前缀以区分平台端/商户端/用户端 API。新增一个功能通常要从下往上依次补齐这五层；例如本项目里的"删除"功能就是按这个顺序一路加上去的：先在 `repositories` 写 `delete_xxx()`，再在 `services` 加业务校验（能不能删、删了要不要带走别的数据），最后才在 `api/v1` 暴露一个 `DELETE` 路由。
- **级联安全删除的三种策略**（活动 / 优惠券 / 菜品 / 桌台 / 预订 / 食材 / 供应商 / 员工共 8 类"用户可自行创建"的实体，删除时统一遵循下面三种处理方式之一）：
  1. **阻断 + 友好提示**：数据仍被引用时不让删，例如菜品已有历史订单、桌台还在"就餐中"状态，捕获 `IntegrityError` 或提前判断后返回 400 而不是让数据库报 500。
  2. **级联删除子项**：先删掉"属于"它的从表数据，再删主表本身，例如删活动前先删它名下的优惠券，删桌台前先删它的预订记录，删员工前先删排班，删菜品前先删 BOM（`dish_ingredient`）行。
  3. **外键置空**：可选关联直接置 NULL，例如删除供应商时把引用它的食材的 `supplier_id` 置空，而不是连带把食材也删掉。
- **智能体接入点唯一化**：见上方"整体架构"一节——所有 Dify 调用都集中在 `agents/gateway.py`。

## 快速开始（本地从零跑起来）

1. **后端**（必须先启动，下面两端都依赖它）
   ```
   cd backend
   python -m venv venv && venv\Scripts\activate      # Windows；macOS/Linux 用 source venv/bin/activate
   pip install -r requirements.txt
   copy .env.example .env                             # 填入云端 MySQL 连接信息、JWT 密钥、Dify Key 等
   uvicorn app.main:app --reload --port 8000
   ```
   访问 `http://127.0.0.1:8000/health` 看到 `{"code":0,...}` 即正常；数据库需先按 `sql/00→01→02→03→04` 顺序建表（00 为 V2.0 新增平台层表，04 为智能体 V2 扩展表）。

2. **管理端**（依赖后端已启动）
   ```
   cd admin-web
   npm install
   npm run dev
   ```
   默认会在 `http://127.0.0.1:5173` 打开，用 `sql/03_other.sql` 里建的 staff 账号登录。

3. **小程序**（依赖后端已启动）
   - 用微信开发者工具「导入项目」选择 `miniprogram/` 目录（已包含 `project.config.json`，可以直接打开，无需先注册小程序账号）。
   - 确认 `miniprogram/api/request.js` 里的 `BASE_URL` 指向本机后端（本地预览默认即 `http://127.0.0.1:8000/api/v1`，已经配置 `urlCheck:false` 允许模拟器直连非 HTTPS 地址）。
   - 在开发者工具里用微信扫码登录账号后，即可在模拟器/真机上预览扫码点餐的完整流程。

4. **Dify 智能体**（可选；不连它点餐下单/库存/客服的基础流程也能跑通，只是"智能"对话与预测会报错）
   - 按 `dify/README.md` 在自托管 Dify 上创建 4 个应用，把各自的 API Key 填入 `backend/.env`。

---

## backend/ —— FastAPI 后端服务

```
backend/
├── requirements.txt    # Python 依赖清单（fastapi/sqlalchemy/pymysql/jose/passlib/httpx/apscheduler/redis 等）
├── .env.example        # 环境变量样例：云端 MySQL 连接、JWT 密钥、Dify 地址与各智能体应用密钥、微信参数
└── app/
    ├── __init__.py     # 包标识（空）
    ├── main.py         # FastAPI 入口：创建 app、注册 CORS 与全部 v1 路由（platform/merchant/customer 三组）、
    │                     #   启动定时任务、/health 健康检查、租户中间件注册、
    │                     #   全局异常处理器（HTTPException → 统一 {code,message,data} 错误体，见"核心设计模式"）
    ├── core/                       # 配置、安全、依赖注入、统一响应等横切关注点
    │   ├── config.py               # Settings：从 .env 加载数据库/JWT/Dify/微信配置，提供 database_url
    │   ├── deps.py                 # V2: SQLAlchemy engine/SessionLocal/Base，get_db_with_tenant() 多租户会话依赖
    │   ├── tenant.py               # ★ V2.0 新增：租户中间件（ContextVar + BaseHTTPMiddleware），
    │   │                             #   从 JWT 解析 merchant_id 自动注入请求上下文
    │   ├── security.py             # V2: 密码哈希(bcrypt)、JWT 签发（payload 含 merchant_id/platform_admin）、
    │   │                             #   get_current_merchant_staff/get_current_platform_admin/get_current_member 三类鉴权依赖
    │   └── response.py             # 统一响应封装 ok()/fail()，对应 {code, message, data} 结构（code=0 成功）
    ├── api/v1/                     # 路由层：仅做参数校验与编排，不写业务逻辑
    │   ├── platform/               # ★ V2.0 新增：平台管理端 API
    │   │   ├── auth.py             #   平台管理员登录
    │   │   ├── merchants.py        #   商户入驻审核/列表/状态管理
    │   │   └── dashboard.py        #   平台运营总览
    │   ├── merchant/               # ★ V2.0 重构：原 api/v1/* 迁移至此，全部注入 merchant_id 隔离
    │   │   ├── auth.py             #   认证：商户员工账号密码登录
    │   │   ├── dish.py             #   菜品：在售列表、全量列表、新增/编辑（含 cost_price/nutrition/recommended_weight）、上下架/删除
    │   │   ├── order.py            #   订单：下单、列表、详情、状态更新（含群体点餐字段）、提交评价
    │   │   ├── table.py            #   桌台：列表/新增/删除、开台/结账/清理、QR码生成、预订管理
    │   │   ├── inventory.py        #   库存：食材列表（含预测可用天数）、新增/删除、出入库登记、
    │   │   │                         #   供应商列表/新增/删除（含评分字段）
    │   │   ├── member.py           #   会员：平台级档案 + 商户级积分/等级/流失风险
    │   │   ├── marketing.py        #   营销：活动/优惠券的创建查询/删除（级联删优惠券）、领取与核销
    │   │   ├── staff.py            #   员工：员工列表/新增/删除（级联删排班）、排班列表/新增
    │   │   ├── service.py          #   客服工单：工单队列查询（按状态/是否待人工筛选）、标记处理完成
    │   │   └── agent.py            #   AI 智能体 V2：对话/触发入口 + 智能体启用配置查询与更新 + A/B 实验管理
    │   └── customer/               # ★ V2.0 新增：用户端 API（不校验 merchant 归属，顾客跨商户通用）
    │       ├── auth.py             #   微信登录（code2session 换 JWT）/ 手机验证码登录
    │       ├── menu.py             #   商户菜单浏览（支持 LBS 附近商户/搜索/分类筛选）
    │       ├── order.py            #   顾客下单（传统加购 + AI 推荐双通道统一入口）
    │       ├── service.py          #   客服消息（对接客服处理智能体）
    │       └── member.py           #   个人中心（平台级偏好 + 跨商户会员档案）
    ├── schemas/                    # Pydantic DTO（请求/响应模型），与 api/v1 三组路由一一对应
    │                               #   V2: 增加平台端 schema、全部业务 schema 增加 merchant_id 字段
    ├── services/                   # 业务逻辑与事务编排层（状态机校验、库存联动、积分/等级计算等）
    │                               #   V2: 增加租户隔离校验逻辑、平台审核流程
    ├── repositories/               # 数据访问层（SQLAlchemy ORM 增删改查），隔离数据库细节
    │                               #   V2: 所有查询方法强制带 merchant_id 过滤条件
    ├── models/                     # ORM 数据模型，对应 sql/ 下的表结构（含 V2.0 新增 merchant/platform_admin/
    │                               #   member_merchant/dish_pairing/recommendation_log/ab_experiment）
    ├── agents/                     # 智能体网关：业务系统与 Dify 的唯一桥梁
    │   ├── gateway.py              #   V2: 封装 Dify Chatflow（chat-messages）与 Workflow（workflows/run）调用，
    │   │                             #   注入 merchant 上下文（菜单/库存/偏好/促销），
    │   │                             #   提供 chat_order/chat_service/chat_analytics/run_stock_forecast/run_analytics_summary
    │   └── recommender.py          #   ★ V2.0 新增：混合推荐引擎（HybridRecommender）
    │                                 #   多路召回（协同过滤+内容推荐+规则图谱）→ 融合去重 → 多因子精排 + MMR 多样性
    └── tasks/                      # 定时任务
        └── scheduler.py            #   V2: APScheduler 按商户分别执行——库存预测（每日 9:00）、经营摘要（每日 22:00）、
                                    #     主动客服扫描（每 5 分钟扫描异常订单触发主动通知）
```

**模块完成情况（V1.0）**：菜品/订单/桌台/库存/会员/营销/员工/认证/客服工单/智能体网关与配置 —— 均已实现模型、schema、
repository、service、路由五层，并通过 `python -c "from app.main import app"` 导入校验与
`unittest.mock` 关键业务逻辑单测（状态机校验、库存不足拒绝、积分不足拒绝、优惠券未领取拒绝、
重复账号拒绝、评分范围校验、客服关键词分流等）。

**V2.0 改造要点**：按《系统设计说明书》第 12 章 39 项改造清单执行，核心变更包括：
- **Day 1-2（多商户底座）**：全部表加 `merchant_id`、新增 `merchant`/`platform_admin` 表、租户中间件、JWT 扩展、Repository 层租户过滤、平台端 API 与页面
- **Day 3（数据模型扩展）**：dish 加 `cost_price/nutrition/recommended_weight/total_sales`、order 加群体点餐字段、supplier 加评分字段、member 表拆分、新增推荐日志/A/B 实验表
- **Day 4（Dify V2）**：四个智能体工作流升级（点餐多路召回+精排、库存多因子预测+校准、客服流失预警+主动服务、经营分析异常检测+What-if）
- **Day 5-6（前端改造）**：平台端页面、商户端路径迁移、菜品/库存/运营总览增强、A/B 实验页、小程序选店首页/对话增强/客服升级

**待生产化事项（同 V1.0）**：微信支付真实签名流程（当前为模拟收款）、Dify 内部结构化分类与后端的对接方式、会员维度的订单历史查询。详见 backend 一节"已知简化/待生产化事项"。

**删除功能**：活动/优惠券/菜品/桌台/预订/食材/供应商/员工共 8 类"用户可自行创建"的实体均已补齐
`DELETE` 接口（见上方各文件注释），按"核心设计模式"一节列出的三种策略分别处理级联关系，
已逐个用 `curl -X DELETE` 验证过返回的统一错误结构（例如删除不存在的优惠券会返回
`{"code":404,"message":"优惠券不存在","data":null}`）。

**V2.0 已知简化/待生产化事项**：
- 微信支付：当前购物车下单后以管理端/小程序「确认支付」模拟收款（直接调用
  `POST /orders/{id}/status?pay_status=1`），尚未接入微信支付统一下单签名与
  `wx.requestPayment` 真实支付流程（需要真实商户号与证书，无法在当前环境验证签名正确性）。
- Dify 工作流：当前以关键词规则兜底客服分类（见 `services/service.py::_classify()`），
  V2.0 将在 Dify Chatflow 内通过 LLM 节点实现深层意图分类与情绪评估，替换后端的规则分类。
- 小程序「我的订单」：后端订单创建不强制绑定会员身份，历史订单号由小程序本地存储维护
  （见 `miniprogram/app.js::addOrderHistory()`），而非服务端按会员查询。
- 推荐冷启动：混合推荐引擎在新商户/新用户场景下使用热销+规则兜底策略，协同过滤需积累足够交互数据后生效。
- 多商户初始数据：平台审核通过后自动创建默认菜品分类与桌台模板，完整初始化脚本待 Day 1-2 实现。

**运行方式**：`cd backend && venv\Scripts\activate && uvicorn app.main:app --reload`，访问 `http://127.0.0.1:8000/health` 验证。

---

## admin-web/ —— Vue 3 管理端前端

```
admin-web/
├── package.json          # 依赖：vue/vue-router/pinia/axios；开发依赖：vite/eslint/prettier
│                           #   （echarts 仍列在依赖里，但当前图表全部是手写 SVG/CSS，未被实际引用，属遗留依赖）
├── index.html            # SPA 入口 HTML
├── vite.config.js        # Vite 构建配置
├── public/                # 静态资源
└── src/
    ├── main.js            # 应用入口：创建 Vue 实例，挂载 Pinia/Router
    ├── App.vue            # 根组件：<router-view/> + 全局 <ToastStack/>（自定义轻提示）
    ├── style.css          # 全局样式：设计令牌（--ink/--paper/--brand 等色板、圆角、阴影变量）+
    │                       #   .btn/.card/.tag 等通用类 + 按钮/区块加载态样式（.spin、.loading-block）
    ├── router/
    │   └── index.js       # V2: 路由表（平台端：/platform/* + 商户端：/merchant/*），
    │                       #   平台端/商户端独立登录与权限守卫
    ├── store/
    │   ├── user.js        # Pinia：V2 增加 platform_admin/merchant_id 标识，token/role，login()/logout()
    │   └── app.js          # Pinia：门店名称、侧边栏折叠状态
    ├── components/
    │   ├── ToastStack.vue  # 自定义轻提示组件，配合 utils/toast.js 使用
    │   └── LoadingBlock.vue # 区块级加载占位（旋转图标 + "加载中…"），用在表格/网格的数据区域
    ├── utils/
    │   ├── index.js        # 通用工具函数
    │   ├── toast.js         # 轻提示方法（success/error/info），驱动 ToastStack
    │   └── pending.js       # usePending() 组合式函数：按 key 跟踪进行中的异步操作，
    │                         #   驱动按钮级 loading 态（:disabled + 旋转图标）
    ├── api/
    │   ├── request.js     # Axios 实例：注入 JWT、解析 {code,message,data}、401 自动退出登录
    │   ├── platform.js    # ★ V2.0 新增：平台端 API（商户审核/列表/状态/平台运营总览）
    │   └── merchant/      # V2: 原 api/* 迁移至 merchant/ 子目录
    │       ├── auth.js / dish.js / order.js / table.js / inventory.js /
    │       ├── member.js / marketing.js / staff.js / agent.js
    │       └── experiment.js   # ★ V2.0 新增：A/B 实验 API
    └── views/
        ├── platform/              # ★ V2.0 新增：平台管理端页面
        │   ├── Login.vue          #   平台管理员登录
        │   ├── Dashboard.vue      #   平台运营总览（商户数/订单量/GMV/待审核）
        │   ├── Merchants.vue      #   商户管理（审核/列表/状态变更）
        │   └── Settings.vue       #   平台设置
        └── merchant/              # V2: 原 views/ 迁移至 merchant/ 子目录
            ├── Login.vue              # 商户员工账号密码登录
            ├── layout/Layout.vue      # V2: 侧边栏 + 顶栏布局（商户 Logo/名称动态展示）
            ├── Dashboard.vue          # V2: 运营总览增强——KPI 卡片增加推荐采纳率 + 智能体动态流
            ├── Dish.vue                # V2: 菜品管理增强——推荐权重滑块/营养信息录入/成本价字段
            ├── Order.vue               # 订单管理：列表筛选、收款、推进出餐状态
            ├── Table.vue               # V2: 桌台管理——QR 码展示与下载
            ├── Marketing.vue           # 营销活动：活动与优惠券的创建查询/删除
            ├── Inventory.vue           # V2: 库存管理增强——供应商评分列/预测可用天数
            ├── Member.vue              # V2: 会员管理增强——流失风险标记/商户级积分等级
            ├── Staff.vue               # 员工管理：员工/排班，员工可删除
            ├── Settings.vue            # V2: 系统设置增强——智能体参数配置（推荐策略权重/安全库存系数/自动回复阈值等）
            └── agents/                 # V2: 5 个智能体工作台（管理端预览调试，正式入口在小程序/由后端调用）
                ├── OrderAgent.vue       # 点餐推荐：对话预览 + 推荐策略可视化
                ├── StockAgent.vue       # 库存预测：触发 Workflow + 多因子预测对照
                ├── ServiceAgent.vue     # 客服处理：对话预览 + 工单队列处理 + 流失预警列表
                ├── AnalyticsAgent.vue   # 经营分析：自然语言查数 + What-if 模拟入口
                └── ExperimentAgent.vue  # ★ V2.0 新增：A/B 实验管理（创建/流量分配/结果对比/一键应用）
```

**设计系统**：早期版本基于 Element Plus，现已完全移除，替换为贴合设计原型图的自定义 CSS 设计系统
（`style.css` 里的色板/圆角/阴影变量 + 一套 `.btn/.card/.tag` 等通用类），消息提示与图表也都换成了
自研的 `ToastStack.vue` 和手写 SVG/CSS，整个管理端不再依赖任何第三方 UI 组件库。平台端与商户端共享同一套设计令牌，视觉风格统一。

**V2.0 路由结构**：
- `/platform/login` → 平台管理员登录
- `/platform/dashboard` → 平台运营总览
- `/platform/merchants` → 商户管理（审核/列表/状态）
- `/merchant/login` → 商户员工登录
- `/merchant/dashboard` → 商户运营总览（V2 增强：推荐采纳率 + 智能体动态流）
- `/merchant/dishes`、`/merchant/orders`、`/merchant/tables`、`/merchant/marketing`、`/merchant/inventory`、`/merchant/members`、`/merchant/staff` → 各业务模块（路径统一加 `/merchant` 前缀）
- `/merchant/agents/order`、`/merchant/agents/stock`、`/merchant/agents/service`、`/merchant/agents/analytics`、`/merchant/agents/experiments` → 5 个智能体工作台（含新增 A/B 实验）
- `/merchant/settings` → 系统设置（V2 增强：智能体参数配置）

**加载状态**：所有"新增/编辑/删除"类按钮通过 `usePending()` 按操作 key（例如 `` `delete-${id}` ``）
跟踪是否进行中，请求未返回前按钮保持禁用并显示旋转图标；所有列表/网格页面进入时由一个
`pageLoading` ref 控制——**只有数据区域**（表格的 `<tbody>`、卡片网格）在加载时显示
`<LoadingBlock/>` 占位，工具栏、筛选器、"新增"按钮等静态结构始终保持可见，避免整页闪烁/跳动。

**运行方式**：`cd admin-web && npm run dev`；生产构建 `npm run build`（已验证可成功构建）。

---

## miniprogram/ —— 微信小程序用户端

```
miniprogram/
├── project.config.json   # 微信开发者工具项目配置（appid 用本地占位 touristappid，未注册线上账号；
│                           #   urlCheck:false 允许模拟器请求 127.0.0.1 等非备案域名，仅用于本地预览）
├── app.js               # V2: 全局逻辑——微信登录（code2session 换 JWT）、扫码桌台号解析（含 merchant_id）、
│                           #   购物车/订单历史本地存储、最近访问商户记录
├── app.json              # V2: 全局配置——9 个页面注册（新增 index 选店首页 + search 商户搜索）+
│                           #   tabBar（点餐/订单/客服/我的）
├── app.wxss               # 全局样式：与 admin-web 共用同一套设计令牌（色板/圆角/阴影），保持两端视觉一致；
│                           #   提供 .card/.tag/.primary-btn/.stepper/.empty-state 及对话页公共样式等通用类
├── api/
│   └── request.js        # wx.request 封装：统一注入 JWT、解析 {code,message,data}、wxLogin()、
│                           #   BASE_URL（目前临时指向本机 http://127.0.0.1:8000，正式部署需换回真实 HTTPS 域名）
├── utils/
│   └── util.js           # formatMoney / formatDateTime
└── pages/                # 9 个业务页面（V2.0 新增 2 个），均含 .js/.json/.wxml/.wxss 四件套
    ├── index/             # ★ V2.0 新增：附近商户/选店首页（LBS 获取位置 → 展示附近商户列表 →
    │                       #   按品类筛选/搜索 → 最近访问/收藏商户 → 点击进入商户菜单）
    ├── search/            # ★ V2.0 新增：商户搜索（按名称/品类搜索）
    ├── menu/              # V2: 扫码首页 + 分类菜单浏览 + 直接加购（需求文档 4.1）；
    │                       #   底部常驻「🤖 AI 点餐」按钮切换至对话通道；菜品排序由推荐引擎个性化生成
    ├── dish/               # 菜品详情：数量/备注/过敏原提示/营养信息，加入购物车
    ├── chat/               # V2: 对话式智能点餐增强——推荐富卡片展示（图片+价格+理由）、语音输入按钮、
    │                       #   群体点餐模式入口、底部购物车摘要、实时营养摘要条、过敏原警告 banner
    ├── cart/               # 购物车：数量调整、下单（POST /orders）、确认支付（模拟收款，见后端说明）；
    │                       #   V2: 购物车数据在传统菜单与 AI 对话双通道间实时同步
    ├── order/              # 订单跟踪与历史订单（本地维护订单号列表）、出餐状态展示、提交评价
    ├── service/            # V2: 在线客服增强——对接客服处理智能体 Chatflow V2（多轮对话 + 主动通知）
    └── mine/               # V2: 会员中心增强——手机号注册/登录、跨商户积分/等级/储值展示、
                            #   口味偏好/忌口/健康目标编辑（需求文档 4.6）
```

**视觉设计**：所有页面已按 admin-web 的设计语言重新美化过（卡片化布局、品牌色强调、空状态插画、
对话页头像气泡等），不再是早期默认无样式的纯列表/纯按钮界面。

**V2.0 核心流程**：打开小程序 → LBS 获取位置 → 展示附近商户（index 页）→ 选择商户进入菜单（menu 页）
→ 传统浏览加购 或 点击「🤖 AI 点餐」切换对话通道（chat 页）→ 购物车双通道同步 → 下单支付 → 查单评价
→ 在线客服（service 页）→ 跨商户会员中心（mine 页）。

**本地预览**：项目里已经包含 `project.config.json`，可以直接用微信开发者工具「导入项目」打开
（不需要注册小程序账号，用占位 `touristappid` 即可；开发者工具登录账号后扫码就能在手机上预览）。

**上线前需要做的事**：把 `api/request.js` 里的 `BASE_URL` 换回真实后端域名（需 HTTPS，并在小程序
后台配置合法域名），并把 `project.config.json` 的 `appid` 换成正式注册的小程序 appid。
所有页面 JS 已通过 `node --check` 语法校验。

---

## dify/ —— Dify 提示词、节点编排与知识库语料

```
dify/
├── prompts/                       # 4 个智能体的系统提示词 + V2 节点编排说明
│   ├── order_recommendation.md    # 点餐推荐 Chatflow V2（多模态预处理→意图识别→多路召回(CF+CB+KG)
│   │                               #   →融合去重→精排→LLM策略调控+理由生成→安全检查→推荐日志）
│   ├── stock_forecast.md          # 库存预测 Workflow V2（并行HTTP数据拉取→时序特征工程→分段预测
│   │                               #   →LLM校准→可用天数判定→供应商匹配→采购建议→损耗/替代方案）
│   ├── service_handling.md        # 客服处理 Chatflow V2（意图分类→情绪评估→FAQ多路RAG→归因分析
│   │                               #   →流失风险评估→话术草拟→分流判定→工单回写）
│   └── analytics.md               # 经营分析：Chatflow V2 自然语言查数 + Workflow V2 经营摘要
│                                   #   （多源汇总→KPI计算→异常检测+归因→菜单工程→RFM→排班建议）
└── knowledge_base/                # 知识库语料草稿（V2: 按商户维度组织，示例内容需替换为真实门店信息）
    ├── menu_intro.md              # 菜单文字说明（菜品做法/口感/搭配建议，配合点餐推荐 RAG 检索）
    ├── store_faq.md               # 门店常见问题（营业时间/预订/支付/过敏原/停车/WiFi等）
    └── policy.md                  # 退换货、优惠券、会员等级与投诉处理政策
```

**V2.0 工作流升级要点**（详见《系统设计说明书》第 8 章）：

| 智能体 | V1.0 节点数 | V2.0 节点数 | V2.0 核心升级 |
|---|---|---|---|
| 点餐推荐 | 6 节点 | 10+ 节点 | 多路召回（CF+CB+KG）→融合去重→多因子精排+MMR多样性→LLM策略调控 |
| 库存预测 | 5 节点 | 12+ 节点 | 时序特征工程→分段预测→LLM校准→供应商评分匹配→损耗消化/替代方案 |
| 客服处理 | 6 节点 | 12+ 节点 | 深层意图+情绪趋势→多路RAG→归因分析→流失预警→分流+挽回话术 |
| 经营分析 | 4+4 节点 | 8+8 节点 | 异常检测+自动下钻→菜单工程BCG→RFM客群→排班建议 |

落地步骤见 `dify/README.md`：登录自托管 Dify 创建对应应用、按编排说明搭建节点并粘贴提示词、
挂载知识库（按商户维度创建独立知识库）、发布后将 API Key 填入 `backend/.env`。

---

## sql/ —— 建表与初始化脚本

```
sql/
├── 00_platform.sql        # ★ V2.0 新增：平台层表——merchant（商户信息/状态）、platform_admin（平台管理员）
├── 01_menu_inventory.sql  # V2: 菜品与库存核心表——dish（新增 cost_price/nutrition/recommended_weight/
│                           #   total_sales/merchant_id）、ingredient（新增 merchant_id）、
│                           #   dish_ingredient BOM（新增 merchant_id）、stock_log（新增 merchant_id）
├── 02_order.sql           # V2: 订单核心表——order（新增 merchant_id/discount_amount/actual_amount/
│                           #   is_group_order/member_count）、order_item（新增 merchant_id）
├── 03_other.sql           # V2: 其余表——dining_table（新增 merchant_id/qr_code_url）、reservation、
│                           #   supplier（新增 merchant_id/on_time_rate/quality_score/price_stability）、
│                           #   member 拆分（平台级 member + 商户级 member_merchant）、staff、schedule、
│                           #   campaign、coupon、service_ticket、review、agent_config、agent_log
│                           #   （全部新增 merchant_id）
└── 04_agent_v2.sql        # ★ V2.0 新增：智能体扩展表——dish_pairing（菜品搭配知识图谱）、
                            #   recommendation_log（推荐日志）、ab_experiment（A/B 实验管理）
```

**初始化方式**：连接老师提供的云端 MySQL 8.0 数据库后，按 00→01→02→03→04 顺序执行。
V2.0 所有业务表均包含 `merchant_id BIGINT NOT NULL` 作为租户隔离键，并建立对应索引。
完整字段含义与 ALTER 语句见《系统设计说明书》第 4 章。

---

## docs/ —— 项目文档

```
docs/
├── README.md        # 文档索引（阅读顺序建议 + V2.0 核心变更速览）
├── SRS.md           # V2.0 软件需求规格说明书（完整需求文档，含两周开发计划）
├── SystemDesign.md  # V2.0 系统设计说明书（架构/数据库/接口/Dify工作流设计/39项代码改造清单）
└── Development.md   # V2.0 项目开发文档（环境搭建/开发规范/模块指南/构建部署/命令速查）
```

**文档关系**：
- [docs/README.md](docs/README.md) —— 文档入口：阅读顺序建议、V1.0 vs V2.0 变更速览
- [SRS.md](docs/SRS.md) —— 定义"做什么"：功能需求、智能体工作流、数据实体、两周开发计划
- [SystemDesign.md](docs/SystemDesign.md) —— 定义"怎么做"：架构设计、数据库 DDL、后端/前端/小程序改造方案、API 规范、V1.0→V2.0 代码改造清单（39 项，按 Phase 1-4 排列）
- [Development.md](docs/Development.md) —— 开发实战手册：环境搭建步骤、项目结构详解、开发规范与约定、各模块开发指南、构建部署方案、两周详细计划、39 项改造清单逐项对照、常用命令速查
- 本 README.md —— 项目总览：架构图、目录导览、快速开始、各模块完成情况

> 完整的两周开发计划（每日分工表、里程碑、风险预案）见 [SRS 第 9 章](docs/SRS.md) 和 [Development.md 第 8 章](docs/Development.md)。
> 39 项 V1.0→V2.0 代码改造清单（逐项对照、按 Phase 排列）见 [SystemDesign 第 12 章](docs/SystemDesign.md) 和 [Development.md 第 9 章](docs/Development.md)。

---

## 根目录其他文件

- `.gitignore` —— 忽略 `backend/venv/`、`__pycache__/`、`*.pyc`、`.env`、`node_modules/`、`dist/`、`.DS_Store`
- `README.md` —— 本文件，项目结构与文件级导览

---

## 当前完成度

### V1.0（已完成）

- ✅ 后端：9 个业务模块（菜品/订单/桌台/库存/会员/营销/员工/认证/客服工单）+ 智能体网关与配置
  均已实现五层完整代码，导入校验与关键业务逻辑单测通过
- ✅ 删除功能：活动/优惠券/菜品/桌台/预订/食材/供应商/员工共 8 类实体均已支持级联安全删除，
  并配合全局异常处理器把错误信息透传给前端
- ✅ 管理端：登录、布局、运营总览、7 个业务管理页面、4 个智能体工作台、系统设置，`npm run build` 验证通过；
  已移除 Element Plus，改为自研 CSS 设计系统
- ✅ 小程序：7 个业务页面全部实现，语法校验通过；已按管理端设计语言完成视觉重设计，
  并已可通过微信开发者工具本地预览（含 `project.config.json`）
- ✅ 数据库：三份建表脚本覆盖需求文档全部数据实体
- ✅ Dify：4 个智能体 V1.0 提示词、节点编排建议与知识库语料草稿
- ✅ 文档：V2.0 SRS + V2.0 系统设计说明书 + 本 README

### V2.0（待开发——按两周计划执行）

- 🔲 Phase 1（Day 1-2）：多商户底座——`merchant`/`platform_admin` 表、全部表加 `merchant_id`、租户中间件、JWT 扩展、平台端 API 与页面
- 🔲 Phase 2（Day 3）：数据模型扩展——dish/order/supplier 加列、member 拆分、新增推荐/A/B 实验表
- 🔲 Phase 3（Day 4）：Dify 工作流 V2——四个智能体升级至 10+ 节点深度编排
- 🔲 Phase 4（Day 5-6）：前端改造——平台端页面、商户端路径迁移、页面增强、A/B 实验页、小程序选店首页/对话增强
- 🔲 Day 7-11：智能体联调、用户端闭环、管理端完善
- 🔲 Day 12-14：测试修复、演示准备、文档完善

**遗留事项**（见上方 backend「V2.0 已知简化/待生产化事项」）：微信支付真实签名流程、
Dify 内部结构化分类与后端的对接方式、会员维度的订单历史查询、推荐冷启动策略、多商户初始数据脚本。
小程序上线前还需把 `BASE_URL` 与 `project.config.json` 的 `appid` 换成正式值（见上方 miniprogram 一节）。
