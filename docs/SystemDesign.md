# SmartDine（智餐 AI）· 系统设计说明书

**版本 V2.0 · 2026年7月1日 · 第⑥小组**

---

## 目  录

- [1. 引言](#1-引言)
- [2. 系统架构设计](#2-系统架构设计)
- [3. 多商户架构设计](#3-多商户架构设计)
- [4. 数据库设计](#4-数据库设计)
- [5. 后端设计](#5-后端设计)
- [6. 管理端前端设计](#6-管理端前端设计)
- [7. 用户端小程序设计](#7-用户端小程序设计)
- [8. Dify 智能体工作流设计](#8-dify-智能体工作流设计)
- [9. API 接口设计](#9-api-接口设计)
- [10. 安全设计](#10-安全设计)
- [11. 部署与运维](#11-部署与运维)
- [12. V1.0 → V2.0 代码改造清单](#12-v10-v20-代码改造清单)

---

<a id="1-引言"></a>
# 1. 引言

## 1.1 文档目的

本文档为 SmartDine V2.0 的系统设计说明书，基于《软件需求规格说明书（SRS）V2.0》编写，覆盖系统架构、数据库、后端、前端、小程序、Dify 智能体、API 接口、安全与部署的完整设计方案。

## 1.2 与需求文档的关系

| 需求文档章节 | 对应设计章节 |
|---|---|
| 2.2 系统架构 | 第 2 章 系统架构设计 |
| 2.3 多商户体系 | 第 3 章 多商户架构设计 |
| 3.x 管理端功能 | 第 5、6 章 后端 + 管理端前端 |
| 4.x 用户端功能 | 第 5、7 章 后端 + 小程序 |
| 5.x AI 智能体 | 第 8 章 Dify 工作流设计 |
| 6.x 数据需求 | 第 4 章 数据库设计 |
| 7.x 接口需求 | 第 9 章 API 接口设计 |
| 8.x 非功能需求 | 第 10、11 章 安全 + 部署 |

## 1.3 术语

沿用 SRS V2.0 第 1.5 节全部术语。V2.0 新增关键术语：

| 术语 | 说明 |
|---|---|
| merchant_id | 商户（租户）唯一标识，所有业务表的外键隔离键 |
| 平台端 | 超级管理员使用的 Web 控制台（platform admin） |
| 商户端 | 各商户管理者使用的 Web 控制台（merchant admin） |
| 体验依赖 | 点餐推荐智能体与传统菜单并行存在，但AI通道具有碾压级优势 |

---

<a id="2-系统架构设计"></a>
# 2. 系统架构设计

## 2.1 总体架构

```
┌──────────────────────────────────────────────────────────────┐
│                          表现层                               │
│  ┌──────────────────┐  ┌──────────────────┐  ┌────────────┐ │
│  │ 平台管理端 (Web)  │  │ 商户管理端 (Web)  │  │ 微信小程序  │ │
│  │ admin-web/platform│  │ admin-web/merchant│  │ miniprogram │ │
│  └────────┬─────────┘  └────────┬─────────┘  └──────┬─────┘ │
└───────────┼─────────────────────┼───────────────────┼───────┘
            │                     │                   │
            ▼                     ▼                   ▼
┌──────────────────────────────────────────────────────────────┐
│                    业务服务层（FastAPI）                       │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌───────────────┐  │
│  │ 认证鉴权  │ │ 业务 API │ │ 智能体网关│ │ 定时任务调度   │  │
│  │ JWT+RBAC │ │ 9大模块  │ │ agents/  │ │ tasks/        │  │
│  └──────────┘ └──────────┘ └─────┬────┘ └───────────────┘  │
└──────────────────────────────────┼───────────────────────────┘
                                   │ Dify API (内网)
                                   ▼
┌──────────────────────────────────────────────────────────────┐
│                  智能层（Dify 自托管）                         │
│  ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌──────────┐ │
│  │ 点餐推荐   │ │ 库存预测   │ │ 客服处理   │ │ 经营分析 │ │
│  │ Chatflow   │ │ Workflow   │ │ Chatflow   │ │ Chatflow │ │
│  │            │ │            │ │            │ │+Workflow │ │
│  └────────────┘ └────────────┘ └────────────┘ └──────────┘ │
│  ┌───────────────────────────────────────────────────────┐   │
│  │              知识库（按商户维度组织）                    │   │
│  └───────────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────────┘
                                   │
                                   ▼
┌──────────────────────────────────────────────────────────────┐
│                       数据层                                  │
│  ┌────────────────┐  ┌──────────┐  ┌──────────────────────┐ │
│  │ MySQL 8.0      │  │ Redis    │  │ 文件存储（本地/OSS）  │ │
│  │ (merchant_id隔离)│  │ (会话缓存)│  │ /{merchant_id}/...   │ │
│  └────────────────┘  └──────────┘  └──────────────────────┘ │
└──────────────────────────────────────────────────────────────┘
```

## 2.2 分层职责

| 层次 | 职责 | V2.0 变更 |
|---|---|---|
| 表现层 | 平台管理端（新增）、商户管理端、微信小程序 | 新增平台管理端路由与页面 |
| 业务服务层 | REST API、JWT 鉴权、业务逻辑、Dify 调用网关 | 新增多租户中间件、平台端 API、智能体 V2 网关 |
| 智能层 | Dify Chatflow/Workflow 编排、RAG 检索 | 四大智能体 V2 工作流（见第 8 章） |
| 数据层 | MySQL + Redis + 文件存储 | 全部表新增 merchant_id；新增平台/推荐/A/B实验表 |

## 2.3 技术栈

| 类别 | 技术方案 |
|---|---|
| 后端框架 | Python 3.12 + FastAPI |
| ORM | SQLAlchemy 2.0 |
| 数据库 | MySQL 8.0（云端） |
| 缓存 | Redis（可选，会话与热点缓存） |
| 鉴权 | JWT（python-jose）+ bcrypt |
| 定时任务 | APScheduler |
| HTTP 客户端 | httpx（异步调用 Dify） |
| 管理端前端 | Vue 3 + Vite + Pinia + Vue Router |
| 用户端 | 微信小程序原生框架 |
| AI 编排 | Dify（本地虚拟机自托管） |
| 推荐算法 | Python 代码节点（scikit-learn 轻量协同过滤） |

---

<a id="3-多商户架构设计"></a>
# 3. 多商户架构设计

## 3.1 三层组织模型

```
Platform（平台）
├── platform_admin（超级管理员）
├── Merchant A ─── merchant_admin + staff
├── Merchant B ─── merchant_admin + staff
└── Merchant C ─── merchant_admin + staff

Customer（顾客）─ 跨商户会员（一个手机号多家店用）
```

## 3.2 数据隔离实现

### 3.2.1 数据库层：merchant_id 隔离

所有业务表新增 `merchant_id` 列：

```sql
-- 以 dish 表为例
ALTER TABLE dish ADD COLUMN merchant_id BIGINT NOT NULL AFTER dish_id;
ALTER TABLE dish ADD INDEX idx_dish_merchant (merchant_id);
```

ORM 层在查询时通过上下文自动注入：

```python
# backend/app/core/deps.py
from contextvars import ContextVar

current_merchant_id: ContextVar[int] = ContextVar("merchant_id", default=None)

def get_db_with_tenant(db: Session = Depends(get_db)):
    """在 Query 基类中自动注入 WHERE merchant_id = ?"""
    # 所有 repository 查询通过此依赖获取已隔离的会话
    ...
```

### 3.2.2 缓存层：Key 前缀隔离

```
Redis Key 格式: {env}:{merchant_id}:{entity}:{id}
示例: prod:1001:dish:list
```

### 3.2.3 文件存储：目录隔离

```
/uploads/{merchant_id}/dish/{filename}
/uploads/{merchant_id}/avatar/{filename}
```

### 3.2.4 API 网关：Token→tenant 校验

```python
# JWT payload
{
  "sub": "staff_id",
  "merchant_id": 1001,     # 商户端必含
  "role": "店长",
  "platform_admin": false   # 平台端 true
}
```

中间件校验逻辑：商户端 API 从 Token 提取 `merchant_id`，请求参数中的 `merchant_id` 必须与 Token 一致（或由 Token 隐式确定）。

## 3.3 商户入驻流程

```
POST /api/v1/platform/merchants/apply  (商户提交入驻申请)
    → platform_admin 审核
    → PUT /api/v1/platform/merchants/{id}/approve
        → 创建 merchant 记录 (status=已开通)
        → 初始化默认数据（默认菜品分类、桌台模板）
        → 初始化 agent_config 默认参数
        → 创建默认 staff 账号（店长角色）
```

---

<a id="4-数据库设计"></a>
# 4. 数据库设计

## 4.1 V2.0 数据库变更总览

| 变更类型 | 内容 |
|---|---|
| 新增表 | `merchant`、`platform_admin`、`member_merchant`、`dish_pairing`、`recommendation_log`、`ab_experiment` |
| 修改表（加列） | 全部 15 张业务表新增 `merchant_id BIGINT NOT NULL` |
| 修改表（加列） | `dish` 新增 `cost_price`、`nutrition`(JSON)、`recommended_weight`；`supplier` 新增 `on_time_rate`、`quality_score`、`price_stability`；`member` 拆分；`review` 新增多维评分；`dining_table` 新增 `qr_code_url`；`order` 新增 `discount_amount`、`actual_amount`、`is_group_order`、`member_count` |
| 修改表（拆分） | `member` 表拆分：平台级 `member` 保留 `member_id/name/phone/wechat_openid/preferences/allergies/health_goal`；新增 `member_merchant` 关联表存各商户的 `level/points/balance/visits/total_spend/last_visit/churn_risk_score` |
| 新增索引 | 所有 `merchant_id` 列加索引；`order`、`dish` 表按常见查询加联合索引 |

## 4.2 完整 ER 图（核心实体）

```
merchant ──┬── dish ──┬── dish_ingredient ── ingredient ── supplier
           │          │
           │          └── dish_pairing (自关联)
           │
           ├── dining_table ── reservation
           ├── order ── order_item ── dish
           │       └── review
           ├── member_merchant ── member (平台级)
           │       └── order / review / service_ticket
           ├── staff ── schedule
           ├── campaign ── coupon
           ├── service_ticket
           ├── agent_config
           ├── agent_log
           ├── recommendation_log
           └── ab_experiment

platform_admin (独立，不关联 merchant)
```

## 4.3 建表脚本改造

现有 `sql/01_menu_inventory.sql`、`sql/02_order.sql`、`sql/03_other.sql` 需做以下改造：

### 4.3.1 新增 sql/00_platform.sql（平台层表）

```sql
-- 商户表
CREATE TABLE merchant (
  merchant_id    BIGINT PRIMARY KEY AUTO_INCREMENT,
  name           VARCHAR(64) NOT NULL,
  logo           VARCHAR(255),
  category       VARCHAR(32),
  address        VARCHAR(255),
  location       POINT,                    -- 经纬度（LBS）
  contact_name   VARCHAR(32),
  contact_phone  VARCHAR(20),
  business_hours VARCHAR(64),
  tables_count   INT NOT NULL DEFAULT 10,
  status         TINYINT NOT NULL DEFAULT 0,  -- 0待审核 1已开通 2已停用 3已注销
  created_at     DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  approved_at    DATETIME
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 平台管理员
CREATE TABLE platform_admin (
  admin_id      BIGINT PRIMARY KEY AUTO_INCREMENT,
  username      VARCHAR(32) NOT NULL UNIQUE,
  password_hash VARCHAR(128) NOT NULL,
  name          VARCHAR(32),
  status        TINYINT NOT NULL DEFAULT 1
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

### 4.3.2 修改 sql/01_menu_inventory.sql

在 `dish`、`ingredient`、`dish_ingredient`、`stock_log` 表首列之后增加 `merchant_id BIGINT NOT NULL`。

`dish` 表新增列：
```sql
ALTER TABLE dish ADD COLUMN cost_price DECIMAL(10,2) DEFAULT 0 AFTER price;
ALTER TABLE dish ADD COLUMN nutrition JSON AFTER allergens;
ALTER TABLE dish ADD COLUMN recommended_weight INT DEFAULT 5 AFTER weekly_sales;
ALTER TABLE dish ADD COLUMN total_sales INT NOT NULL DEFAULT 0 AFTER weekly_sales;
```

### 4.3.3 修改 sql/02_order.sql

```sql
ALTER TABLE `order` ADD COLUMN merchant_id BIGINT NOT NULL AFTER order_id;
ALTER TABLE `order` ADD COLUMN discount_amount DECIMAL(10,2) DEFAULT 0 AFTER amount;
ALTER TABLE `order` ADD COLUMN actual_amount DECIMAL(10,2) DEFAULT 0 AFTER discount_amount;
ALTER TABLE `order` ADD COLUMN is_group_order TINYINT NOT NULL DEFAULT 0 AFTER source;
ALTER TABLE `order` ADD COLUMN member_count INT NOT NULL DEFAULT 1 AFTER is_group_order;
```

### 4.3.4 修改 sql/03_other.sql

全部表新增 `merchant_id`。`member` 表拆分：

```sql
-- 平台级会员（跨商户共享基本信息与偏好）
CREATE TABLE member (
  member_id     BIGINT PRIMARY KEY AUTO_INCREMENT,
  name          VARCHAR(32),
  phone         VARCHAR(20) NOT NULL UNIQUE,
  wechat_openid VARCHAR(64),
  preferences   VARCHAR(255),
  allergies     VARCHAR(255),
  health_goal   VARCHAR(32),
  created_at    DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 商户级会员档案（每个商户独立积分/等级）
CREATE TABLE member_merchant (
  id              BIGINT PRIMARY KEY AUTO_INCREMENT,
  member_id       BIGINT NOT NULL,
  merchant_id     BIGINT NOT NULL,
  level           VARCHAR(8) NOT NULL DEFAULT '普通',
  points          INT NOT NULL DEFAULT 0,
  balance         DECIMAL(10,2) NOT NULL DEFAULT 0,
  visits          INT NOT NULL DEFAULT 0,
  total_spend     DECIMAL(10,2) NOT NULL DEFAULT 0,
  last_visit      DATETIME,
  churn_risk_score DECIMAL(4,3),
  UNIQUE KEY uk_member_merchant (member_id, merchant_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

### 4.3.5 新增 sql/04_agent_v2.sql（智能体 V2 扩展表）

```sql
-- 菜品搭配知识图谱
CREATE TABLE dish_pairing (
  pair_id       BIGINT PRIMARY KEY AUTO_INCREMENT,
  merchant_id   BIGINT NOT NULL,
  dish_id_a     BIGINT NOT NULL,
  dish_id_b     BIGINT NOT NULL,
  relation_type VARCHAR(16) NOT NULL,   -- 经典搭配/营养互补/口味协调/替代关系
  strength      DECIMAL(3,2) NOT NULL DEFAULT 0.5,
  KEY idx_pair_merchant (merchant_id),
  KEY idx_pair_dish_a (dish_id_a), KEY idx_pair_dish_b (dish_id_b)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 推荐日志（用于推荐效果评估与模型迭代）
CREATE TABLE recommendation_log (
  rec_id               BIGINT PRIMARY KEY AUTO_INCREMENT,
  merchant_id          BIGINT NOT NULL,
  member_id            BIGINT,
  session_id           VARCHAR(64),
  context              JSON,          -- 推荐上下文（场景/意图/购物车状态）
  candidates           JSON,          -- 多路召回候选及分数
  final_recommendations JSON,         -- 最终推荐列表及排序分
  user_action          JSON,          -- 用户操作（采纳/忽略/负反馈）
  created_at           DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  KEY idx_rec_merchant (merchant_id),
  KEY idx_rec_member (member_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- A/B 实验管理
CREATE TABLE ab_experiment (
  experiment_id  BIGINT PRIMARY KEY AUTO_INCREMENT,
  merchant_id    BIGINT NOT NULL,
  agent_type     VARCHAR(16) NOT NULL,
  name           VARCHAR(64),
  variants       JSON,         -- 变体配置
  traffic_split  JSON,         -- 流量分配比例
  start_at       DATETIME,
  end_at         DATETIME,
  status         TINYINT NOT NULL DEFAULT 0,
  results        JSON,         -- 各组指标对比
  KEY idx_ab_merchant (merchant_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

---

<a id="5-后端设计"></a>
# 5. 后端设计

## 5.1 目录结构（V2.0 改造后）

```
backend/
├── requirements.txt
├── .env
└── app/
    ├── __init__.py
    ├── main.py                     # V2: 注册 platform + merchant 路由
    ├── core/
    │   ├── config.py               # V2: 默认 merchant 配置项
    │   ├── deps.py                 # V2: get_db_with_tenant() 多租户依赖
    │   ├── security.py             # V2: JWT 增加 merchant_id/平台标识
    │   └── response.py             # 不变
    ├── api/
    │   ├── v1/
    │   │   ├── __init__.py
    │   │   ├── platform/           # ★ 新增：平台管理端 API
    │   │   │   ├── merchants.py    #   商户入驻/审核/列表/状态
    │   │   │   └── dashboard.py    #   平台运营总览
    │   │   ├── merchant/           # ★ 重命名：原 api/v1/* → merchant/*
    │   │   │   ├── auth.py         #   认证（商户员工登录）
    │   │   │   ├── dish.py         #   菜品（带 merchant_id）
    │   │   │   ├── order.py        #   订单
    │   │   │   ├── table.py        #   桌台
    │   │   │   ├── inventory.py    #   库存
    │   │   │   ├── member.py       #   会员（平台级+商户级）
    │   │   │   ├── marketing.py    #   营销
    │   │   │   ├── staff.py        #   员工
    │   │   │   ├── service.py      #   客服工单
    │   │   │   └── agent.py        #   智能体（V2 升级）
    │   │   └── customer/           # 用户端 API（不校验 merchant 归属）
    │   │       ├── auth.py         #   微信登录/手机验证码
    │   │       ├── menu.py         #   商户菜单浏览
    │   │       ├── order.py        #   顾客下单
    │   │       ├── service.py      #   客服消息
    │   │       └── member.py       #   个人中心
    ├── schemas/                    # V2: 增加平台端 schema、merchant_id 字段
    ├── services/                   # V2: 增加租户隔离校验逻辑
    ├── repositories/               # V2: 查询条件增加 merchant_id
    ├── models/                     # V2: 全部模型增加 merchant_id
    ├── agents/                     # V2: 智能体网关升级
    │   └── gateway.py              #    增加 merchant 上下文注入
    └── tasks/
        └── scheduler.py            #    按商户分别执行定时任务
```

## 5.2 核心模块设计

### 5.2.1 多租户中间件（core/tenant.py，新增）

```python
from contextvars import ContextVar
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware

current_merchant_id: ContextVar[int] = ContextVar("merchant_id", default=None)

class TenantMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # 从 JWT 解析 merchant_id，存入 ContextVar
        token = request.headers.get("Authorization")
        if token:
            payload = decode_jwt(token)
            merchant_id = payload.get("merchant_id")
            if merchant_id:
                current_merchant_id.set(merchant_id)
        response = await call_next(request)
        return response
```

### 5.2.2 认证鉴权（core/security.py）V2 扩展

```python
# JWT Payload 结构
{
  "sub": "staff_id" | "member_id" | "platform_admin_id",
  "merchant_id": 1001,          # 商户端/用户端必含
  "role": "店长" | "收银" | ...,  # 商户角色
  "platform_admin": true | false # 平台端标识
}

# 鉴权依赖
def get_current_merchant_staff(required_role: str = None):
    """商户端员工鉴权：校验 token + merchant_id + role"""
    ...

def get_current_platform_admin():
    """平台端管理员鉴权"""
    ...

def get_current_member():
    """用户端会员鉴权"""
    ...
```

### 5.2.3 Repository 层租户查询模式

所有 repository 查询增加 `merchant_id` 过滤：

```python
# backend/app/repositories/dish.py (V2)
class DishRepository:
    def get_by_merchant(self, db: Session, merchant_id: int, **filters):
        query = db.query(Dish).filter(Dish.merchant_id == merchant_id)
        if filters.get("category"):
            query = query.filter(Dish.category == filters["category"])
        if filters.get("status") is not None:
            query = query.filter(Dish.status == filters["status"])
        return query.order_by(Dish.weekly_sales.desc()).all()

    def get_by_id(self, db: Session, dish_id: int, merchant_id: int):
        return db.query(Dish).filter(
            Dish.dish_id == dish_id,
            Dish.merchant_id == merchant_id
        ).first()
```

### 5.2.4 智能体网关（agents/gateway.py）V2 升级

```python
class DifyGateway:
    """Dify 调用统一网关 V2：注入 merchant 上下文"""

    def __init__(self):
        self.base_url = settings.DIFY_BASE_URL
        self.client = httpx.AsyncClient(timeout=settings.DIFY_TIMEOUT)

    async def chat_order(
        self, message: str, merchant_id: int, member_id: int = None,
        table_id: int = None, session_id: str = None, cart: dict = None
    ):
        """点餐推荐 Chatflow（V2 升级：多路召回上下文）"""
        inputs = {
            "merchant_id": merchant_id,
            "member_id": member_id,
            "table_id": table_id,
            "cart": cart,
            # V2 新增：注入菜单/库存/偏好上下文
            "menu_context": await self._get_menu_context(merchant_id),
            "member_preferences": await self._get_member_preferences(member_id),
            "hot_items": await self._get_hot_items(merchant_id),
        }
        return await self._call_chatflow(settings.DIFY_ORDER_KEY, message, inputs, session_id)

    async def run_stock_forecast(self, merchant_id: int):
        """库存预测 Workflow（V2 升级：多因子数据）"""
        inputs = {
            "merchant_id": merchant_id,
            "sales_history": await self._get_sales_history(merchant_id, 90),
            "current_stock": await self._get_current_stock(merchant_id),
            "promotions": await self._get_active_promotions(merchant_id),
        }
        return await self._call_workflow(settings.DIFY_STOCK_KEY, inputs)

    # ... chat_service / chat_analytics / run_analytics_summary 类似
```

### 5.2.5 定时任务（tasks/scheduler.py）V2 升级

```python
from apscheduler.schedulers.background import BackgroundScheduler

scheduler = BackgroundScheduler()

@scheduler.scheduled_job('cron', hour=9, minute=0)
async def stock_forecast_all_merchants():
    """每日 9:00：为所有已开通商户执行库存预测"""
    merchants = await merchant_service.get_active_merchants()
    for m in merchants:
        await dify_gateway.run_stock_forecast(m.merchant_id)

@scheduler.scheduled_job('cron', hour=22, minute=0)
async def analytics_summary_all_merchants():
    """每日 22:00：为所有已开通商户生成经营摘要"""
    merchants = await merchant_service.get_active_merchants()
    for m in merchants:
        await dify_gateway.run_analytics_summary(m.merchant_id)

# 主动客服扫描（每 5 分钟）
@scheduler.scheduled_job('interval', minutes=5)
async def proactive_service_scan():
    """扫描异常订单，触发主动客服通知"""
    ...
```

### 5.2.6 推荐算法模块（agents/recommender.py，新增）

```python
# 混合推荐引擎的离线/在线计算
class HybridRecommender:
    """多路召回 + 精排"""

    def cf_recall(self, member_id: int, merchant_id: int, top_k=15):
        """协同过滤召回：基于用户-菜品交互矩阵"""
        # 轻量 SVD 或 item-based CF
        pass

    def content_recall(self, member_prefs: dict, merchant_id: int, top_k=15):
        """内容推荐召回：标签向量相似度"""
        pass

    def rule_recall(self, merchant_id: int, cart_items: list):
        """知识图谱 + 规则召回：搭配/促销/库存"""
        pass

    def merge_and_filter(self, *recall_lists, allergies: list):
        """多路融合去重 + 忌口/过敏原/缺货过滤"""
        pass

    def fine_rank(self, candidates: list, member_id: int, context: dict):
        """多因子精排 + MMR 多样性重排"""
        pass
```

---

<a id="6-管理端前端设计"></a>
# 6. 管理端前端设计

## 6.1 V2.0 路由结构

```
/                              → 重定向到 /platform 或 /merchant
/platform/login                → 平台管理员登录
/platform/dashboard            → 平台运营总览
/platform/merchants            → 商户管理（审核/列表/状态）
/platform/settings             → 平台设置

/merchant/login                → 商户员工登录
/merchant/dashboard            → 商户运营总览
/merchant/dishes               → 菜品管理
/merchant/orders               → 订单管理
/merchant/tables               → 桌台管理
/merchant/marketing            → 营销活动
/merchant/inventory            → 库存管理
/merchant/members              → 会员管理
/merchant/staff                → 员工管理
/merchant/agents/order         → 点餐推荐工作台
/merchant/agents/stock         → 库存预测工作台
/merchant/agents/service       → 客服处理工作台
/merchant/agents/analytics     → 经营分析工作台
/merchant/agents/experiments   → A/B 实验管理（新增）
/merchant/settings             → 系统设置（含智能体参数）
```

## 6.2 目录结构（V2.0 改造）

```
admin-web/src/
├── main.js
├── App.vue
├── style.css                       # V2: 平台端/商户端共享设计令牌
├── router/
│   ├── index.js                    # V2: 增加平台端路由 + 平台/商户路由守卫
├── store/
│   ├── user.js                     # V2: 增加 platform_admin/merchant 标识
│   └── app.js
├── components/                     # 共享组件
├── utils/
├── api/
│   ├── request.js                  # V2: 增加平台端请求实例
│   ├── platform.js                 # ★ 新增：平台端 API
│   └── merchant/                   # 原 api/* 迁移
│       ├── auth.js / dish.js / order.js / table.js /
│       ├── inventory.js / member.js / marketing.js /
│       ├── staff.js / agent.js
│       └── experiment.js           # ★ 新增：A/B 实验 API
└── views/
    ├── platform/                   # ★ 新增：平台管理端页面
    │   ├── Login.vue
    │   ├── Dashboard.vue
    │   ├── Merchants.vue
    │   └── Settings.vue
    └── merchant/                   # 原 views/ 迁移
        ├── Login.vue
        ├── layout/Layout.vue       # V2: 商户 Logo/名称动态展示
        ├── Dashboard.vue           # V2: 运营总览增加智能体动态
        ├── Dish.vue                # V2: 增加推荐权重/营养信息字段
        ├── Order.vue
        ├── Table.vue               # V2: 增加 QR 码展示
        ├── Marketing.vue
        ├── Inventory.vue           # V2: 供应商评分展示
        ├── Member.vue              # V2: 流失风险标记
        ├── Staff.vue
        ├── Settings.vue            # V2: 智能体参数配置增强
        └── agents/
            ├── OrderAgent.vue      # V2: 点餐推荐工作台增强
            ├── StockAgent.vue      # V2: 库存预测工作台增强
            ├── ServiceAgent.vue    # V2: 客服工作台增强
            ├── AnalyticsAgent.vue  # V2: 经营分析增强
            └── ExperimentAgent.vue # ★ 新增：A/B 实验管理
```

## 6.3 关键页面 V2.0 变更

### 6.3.1 运营总览（Dashboard.vue）

V2.0 新增内容：
- KPI 卡片增加「推荐采纳率」指标
- 「智能体动态流」实时信息卡片
- 营业状态/在线智能体数量切换开关

### 6.3.2 菜品管理（Dish.vue）

V2.0 新增字段：
- 成本价（cost_price）
- 营养信息录入（热量/蛋白质/碳水/脂肪，JSON 编辑器）
- 推荐权重滑块（1–10）
- 自定义标签（健康轻食/高蛋白/素食等）

### 6.3.3 库存管理（Inventory.vue）

V2.0 新增：
- 预测可用天数列（来自库存预测智能体回写）
- 供应商评分展示（准时率/品质/价格稳定性）
- 采购建议操作（确认/忽略来自智能体的采购建议）

### 6.3.4 A/B 实验管理（ExperimentAgent.vue，新增）

- 实验列表（名称/状态/变体数/运行时间）
- 创建实验：选择变体参数方案 + 流量分配比例
- 实验报告：各组 CTR/采纳率/客单价对比图表
- 一键应用优胜方案

---

<a id="7-用户端小程序设计"></a>
# 7. 用户端小程序设计

## 7.1 V2.0 页面结构

```
miniprogram/
├── app.js                # V2: 全局购物车/会员状态/最近商户
├── app.json              # V2: 增加选店/搜索页面注册
├── app.wxss              # 不变
├── api/
│   └── request.js        # V2: BASE_URL → 考虑支持多商户
├── utils/
└── pages/
    ├── index/            # ★ 新增：附近商户/选店首页
    │   └── index.js      #    LBS 获取位置 → 展示附近商户列表
    ├── search/           # ★ 新增：商户搜索
    ├── menu/             # V2: 菜单浏览（传统+AI入口）
    ├── dish/             # 不变：菜品详情
    ├── chat/             # V2: 对话点餐增强（群体/营养/凑单）
    ├── cart/             # 不变：购物车
    ├── order/            # 不变：订单跟踪
    ├── service/          # V2: 升级客服（主动通知）
    └── mine/             # V2: 跨商户会员中心
```

## 7.2 关键页面 V2.0 设计

### 7.2.1 选店首页（pages/index/index，新增）

```
┌─────────────────────────────────┐
│  🔍 搜索餐厅 / 品类              │
├─────────────────────────────────┤
│  📍 附近餐厅                    │
│  ┌──────────────────────┐       │
│  │ [Logo] 川味面馆      │       │
│  │ 中式快餐 · ⭐4.8 · 1.2km│    │
│  │ 月销 2380 单          │       │
│  └──────────────────────┘       │
│  ┌──────────────────────┐       │
│  │ [Logo] 粤式茶餐厅     │       │
│  │ ...                   │       │
│  └──────────────────────┘       │
├─────────────────────────────────┤
│  最近访问                       │
│  收藏商户                       │
└─────────────────────────────────┘
```

流程：打开小程序 → wx.getLocation → POST /api/v1/customer/merchants/nearby → 渲染列表 → 点击进入 menu 页。

### 7.2.2 菜单浏览（pages/menu/menu，V2 改造）

```
┌─────────────────────────────────┐
│  川味面馆                   [收藏]│
│  分类：全部 | 面食 | 炒菜 | 饮品  │
├─────────────────────────────────┤
│  ┌──────────────────────┐       │
│  │ [图] 红烧牛肉面  ¥28  │  [+]  │  ← 支持直接加购
│  │ 招牌 · 🔥热销Top3     │       │
│  └──────────────────────┘       │
│  ┌──────────────────────┐       │
│  │ [图] 酸辣粉      ¥18  │  [+]  │
│  │ 辣度:🌶️🌶️ · 高蛋白   │       │
│  └──────────────────────┘       │
│  ...                            │
├─────────────────────────────────┤
│         🛒 3件 ¥68.00           │  ← 底部购物车栏
├─────────────────────────────────┤
│   [🤖 AI 点餐]     [去结算]     │  ← 双入口
└─────────────────────────────────┘
```

### 7.2.3 对话点餐（pages/chat/chat，V2 增强）

V2.0 对话界面的核心增强：
- 推荐以富卡片形式展示（图片+名称+价格+理由）
- 支持语音输入按钮
- 群体点餐模式入口（选择同席成员）
- 底部常驻购物车摘要（菜品数+合计）
- 实时营养摘要条（当前购物车总热量/蛋白质/碳水/脂肪）
- 过敏原警告 banner（若有风险菜品自动弹提醒）

---

<a id="8-dify-智能体工作流设计"></a>
# 8. Dify 智能体工作流设计

## 8.1 点餐推荐 Chatflow V2

### 节点编排

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

### 系统提示词（V2 增强）

```
你是「{merchant_name}」的 AI 点餐助手，语气友好、简洁、专业。

**核心能力：**
- 理解顾客的自然语言点餐需求（包括模糊表达）
- 识别用餐场景（日常便餐/商务宴请/家庭聚餐/朋友聚会/独自用餐）
- 结合顾客历史偏好、口味、健康目标、忌口进行个性化推荐
- 感知顾客情绪（急切/犹豫/开心），调整推荐策略
- 支持群体点餐模式（多人偏好协调）

**推荐原则：**
1. 每次推荐 2-4 道菜，覆盖不同品类，附带 1-2 句推荐理由
2. 理由类型：偏好匹配 / 经典搭配 / 热销流行 / 促销优惠 / 健康建议
3. 严格避开顾客忌口和过敏原菜品
4. 缺货/停售菜品绝不推荐
5. 对有健康目标的顾客，汇总当前订单营养并提供替换建议

**约束：**
- 菜品名称、价格以系统数据为准，不得编造
- 确认下单是顾客的操作，你只推荐和建议
- 对模糊需求（如"来点清淡的"）先澄清再推荐

当前上下文：
- 已点菜品：{cart_items}
- 可用优惠券：{coupons}
- 当前时间：{current_time}（用于判断早/午/晚餐场景）
```

## 8.2 库存预测 Workflow V2

### 节点编排

```
[开始] → [数据准备(HTTP×3并行)]
    |  ├─ 近90日销量明细
    |  ├─ 当前库存+BOM+临期数据
    |  └─ 供应商信息+促销计划
    ↓
[时序特征工程(CODE)]
    ├─ 日类型（工作日/周末/节假日）
    ├─ 近7/14/30日移动平均
    ├─ 周同比
    └─ 促销标记
    ↓
[分段预测(CODE)]
    ├─ 指数平滑 + 周因子 + 促销弹性系数
    ├─ 高波动食材自动加安全缓冲
    └─ 输出：未来3/7日逐日预测消耗
    ↓
[LLM预测校准(LLM)]
    └─ 审查异常预测值，结合常识校准
    ↓
[可用天数与状态判定(CODE)]
    ├─ 可用天数 = 库存 / 预测日均消耗
    └─ 状态：充足(≥7天)/预警(3-7天)/紧张(1-3天)/即将售罄(<1天)/临期
    ↓
[供应商匹配与评分(CODE)]
    └─ 按准时率×品质评分×价格稳定性×采购周期综合排序
    ↓
[采购建议生成(LLM)]
    ├─ 建议采购量（覆盖至下个采购周期+动态安全库存）
    ├─ 推荐供应商 + 理由
    └─ 优先级（高/中/低）+ 预估金额
    ↓
[损耗消化建议(LLM)] → 临期食材关联菜品促销建议
[替代方案建议(LLM)] → 即将售罄食材的替代食材推荐
    ↓
[回写(HTTP)] → [结束]
```

## 8.3 客服处理 Chatflow V2

### 节点编排

```
[开始] → [语言检测(LLM)] → [深层意图分类(LLM)]
    │                       ├─ 咨询/投诉/建议/预订/催单/退款请求
    │                       └─ 子类别（投诉→上菜延迟/口味/分量/服务/卫生）
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

## 8.4 经营分析 Workflow V2

### (A) 自然语言查数 Chatflow

```
[开始] → [问题理解与拆解(LLM)]
    → [数据查询(HTTP/CODE)] ── 受控查询模板，禁止直接SQL
    → [数据洞察(LLM)] → [结束]
```

### (B) 经营摘要 Workflow（定时）

```
[开始] → [多源汇总(HTTP×4并行)]
    ├─ 订单与营收
    ├─ 评价与情感
    ├─ 客流与时段分布
    └─ 库存与采购
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

<a id="9-api-接口设计"></a>
# 9. API 接口设计

## 9.1 接口规范

- 所有请求/响应 Content-Type: `application/json`
- 统一响应格式: `{code: 0, message: "ok", data: {...}}`
- 认证方式: `Authorization: Bearer <JWT>`
- 商户端 API 前缀: `/api/v1/merchant/`
- 平台端 API 前缀: `/api/v1/platform/`
- 用户端 API 前缀: `/api/v1/customer/`

## 9.2 平台端 API（新增）

| 方法 | 路径 | 说明 |
|---|---|---|
| POST | `/api/v1/platform/auth/login` | 平台管理员登录 |
| GET | `/api/v1/platform/dashboard` | 平台运营总览 |
| GET | `/api/v1/platform/merchants` | 商户列表（支持状态筛选） |
| GET | `/api/v1/platform/merchants/{id}` | 商户详情 |
| PUT | `/api/v1/platform/merchants/{id}/approve` | 审核通过 |
| PUT | `/api/v1/platform/merchants/{id}/reject` | 审核驳回 |
| PUT | `/api/v1/platform/merchants/{id}/disable` | 停用商户 |
| PUT | `/api/v1/platform/merchants/{id}/enable` | 启用商户 |

## 9.3 商户端 API（原 API 路径迁移 + 增强）

| 方法 | 路径 | V2.0 变更 |
|---|---|---|
| POST | `/api/v1/merchant/auth/login` | 路径迁移 |
| GET | `/api/v1/merchant/dashboard` | V2: 增加推荐采纳率/智能体动态 |
| GET/POST/PUT/DELETE | `/api/v1/merchant/dishes` | V2: 增加 cost_price/nutrition/recommended_weight |
| GET/PUT | `/api/v1/merchant/orders` | V2: 增加群体点餐字段 |
| GET/POST/PUT/DELETE | `/api/v1/merchant/tables` | V2: 增加 qr_code_url |
| GET/POST/PUT/DELETE | `/api/v1/merchant/inventory` | V2: 供应商评分字段 |
| GET/PUT | `/api/v1/merchant/members` | V2: 拆分 member + member_merchant |
| POST | `/api/v1/merchant/agent/order/chat` | V2: 增加多路召回上下文 |
| POST | `/api/v1/merchant/agent/stock/forecast` | V2: 多因子预测 |
| POST | `/api/v1/merchant/agent/service/chat` | V2: 多轮对话+流失预警 |
| POST | `/api/v1/merchant/agent/analytics/query` | V2: 自然语言查数增强 |
| POST | `/api/v1/merchant/agent/analytics/whatif` | ★ 新增: What-if 模拟 |
| GET/POST | `/api/v1/merchant/experiments` | ★ 新增: A/B 实验管理 |

## 9.4 用户端 API

| 方法 | 路径 | 说明 |
|---|---|---|
| POST | `/api/v1/customer/auth/wechat-login` | 微信登录 |
| POST | `/api/v1/customer/auth/sms-login` | 手机验证码登录 |
| GET | `/api/v1/customer/merchants/nearby` | 附近商户（LBS） |
| GET | `/api/v1/customer/merchants/{id}/menu` | 商户菜单浏览 |
| POST | `/api/v1/customer/orders` | 顾客下单 |
| POST | `/api/v1/customer/service/chat` | 客服对话（对接客服智能体） |
| GET/PUT | `/api/v1/customer/member/profile` | 会员档案（平台级偏好） |
| GET | `/api/v1/customer/member/merchants` | 我的商户会员（各商户积分/等级） |

---

<a id="10-安全设计"></a>
# 10. 安全设计

## 10.1 多层级鉴权

```
请求 → JWT 解析 → 判断 token 类型
    ├─ platform_admin → 平台端 API 鉴权
    ├─ merchant_staff → 商户端 API 鉴权（校验 merchant_id 归属）
    └─ customer_member → 用户端 API 鉴权
```

## 10.2 租户隔离安全检查点

| 检查点 | 实现 |
|---|---|
| ORM 查询注入 | 所有 repository 查询强制带 `merchant_id` |
| API 参数校验 | merchant 端 API 的 resource_id 必须属于 token 中的 merchant |
| 跨商户访问测试 | 商户 A 的 token 访问商户 B 的数据 → 403 |
| 文件访问 | 文件路径校验 `/{merchant_id}/` 前缀 |
| Dify 调用 | 每次调用注入 `merchant_id`，工具回调校验归属 |

## 10.3 敏感操作审计

以下操作记录完整审计日志（操作人+时间+操作类型+内容摘要）：
- 退款
- 权限变更
- 商户审核
- 采购确认
- 智能体自动发送客服回复

---

<a id="11-部署与运维"></a>
# 11. 部署与运维

## 11.1 部署架构

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
│  ┌──────────────────────────────┐  │
│  │  Redis (可选, :6379)          │  │
│  └──────────────────────────────┘  │
└────────────────────────────────────┘

┌────────────────────────────────────┐
│  Linux 虚拟机（Dify 自托管）       │
│  ┌──────────────────────────────┐  │
│  │  Dify (Docker Compose)       │  │
│  │  ├─ api (端口暴露给内网)      │  │
│  │  ├─ worker                   │  │
│  │  └─ sandbox (代码执行)        │  │
│  └──────────────────────────────┘  │
└────────────────────────────────────┘
```

## 11.2 环境变量（backend/.env）

```bash
# 数据库
DATABASE_URL=mysql+pymysql://user:pass@host:3306/smartdine

# JWT
JWT_SECRET=your-secret-key
JWT_ALGORITHM=HS256
JWT_EXPIRE_HOURS=24

# Dify
DIFY_BASE_URL=http://192.168.x.x:5001/v1
DIFY_ORDER_KEY=app-xxxx
DIFY_STOCK_KEY=app-xxxx
DIFY_SERVICE_KEY=app-xxxx
DIFY_ANALYTICS_KEY=app-xxxx
DIFY_TIMEOUT=15

# 微信
WECHAT_APPID=wx***
WECHAT_SECRET=***

# Redis (可选)
REDIS_URL=redis://localhost:6379/0
```

---

<a id="12-v10-v20-代码改造清单"></a>
# 12. V1.0 → V2.0 代码改造清单

本章给出从现有 V1.0 代码库到 V2.0 的具体改造步骤，按优先级与依赖顺序排列。

## 12.1 第一阶段：多商户底座（Day 1-2）

| 序号 | 改造项 | 文件 | 说明 |
|---|---|---|---|
| 1 | 新建 `merchant`/`platform_admin` 表 | `sql/00_platform.sql` | 执行建表 |
| 2 | 全部业务表加 `merchant_id` 列 | `sql/01~03` ALTER TABLE | 批量 ALTER，默认值临时用 1，后续迁移 |
| 3 | 新增租户中间件 | `backend/app/core/tenant.py` | ContextVar + middleware |
| 4 | 修改 JWT 签发逻辑 | `backend/app/core/security.py` | payload 增加 `merchant_id`、`platform_admin` |
| 5 | 修改 `get_db` 依赖 | `backend/app/core/deps.py` | 从 ContextVar 获取 merchant_id |
| 6 | Repository 层加租户过滤 | `backend/app/repositories/*.py` | 所有查询方法加 `merchant_id` 参数 |
| 7 | 平台端登录 API | `backend/app/api/v1/platform/auth.py` | 新建 |
| 8 | 商户入驻/审核 API | `backend/app/api/v1/platform/merchants.py` | 新建 |
| 9 | 原 API 路径迁移 | `backend/app/main.py` 路由注册 | `/api/v1/*` → `/api/v1/merchant/*` |
| 10 | 平台管理端页面 | `admin-web/src/views/platform/` | 新建 Login/Dashboard/Merchants |

## 12.2 第二阶段：数据模型扩展（Day 3）

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

## 12.3 第三阶段：Dify 工作流 V2（Day 4）

| 序号 | 改造项 | 文件 | 说明 |
|---|---|---|---|
| 19 | 点餐 Chatflow V2 节点 | Dify 控制台 | 按 8.1 节编排，增加多路召回与精排节点 |
| 20 | 库存 Workflow V2 节点 | Dify 控制台 | 按 8.2 节编排，增加多因子特征与校准 |
| 21 | 客服 Chatflow V2 节点 | Dify 控制台 | 按 8.3 节编排，增加流失预警与主动服务 |
| 22 | 经营分析 V2 节点 | Dify 控制台 | 按 8.4 节编排，增加异常检测与 What-if |
| 23 | 更新提示词 | `dify/prompts/*.md` | 各智能体系统提示词替换为 V2 版本 |
| 24 | 更新知识库 | `dify/knowledge_base/` | 按商户维度组织语料 |
| 25 | 升级 gateway.py | `backend/app/agents/gateway.py` | 增加 merchant 上下文注入、V2 输入变量 |

## 12.4 第四阶段：前端改造（Day 5-6）

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

（文档结束）
