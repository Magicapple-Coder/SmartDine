# 点餐推荐智能体（Chatflow）

对应：需求文档 5.1、系统设计说明书 5.0.1；后端调用入口 `POST /api/v1/agent/order/chat`
（`backend/app/agents/gateway.py` 的 `chat_order()`，对接 Dify `/chat-messages`）。

## 应用类型与变量

- Dify 应用类型：Chatflow
- 会话输入变量（与 `gateway._chat()` 发送的 `inputs` 对应）：
  - `session_id`（string，必填）：小程序端生成的会话标识，用于上下文隔离
- 用户输入：`query`（顾客的自然语言点餐诉求）

## 建议的 Chatflow 节点编排

1. **开始节点**：接收 `query`、`session_id`
2. **HTTP 请求节点 - 获取实时菜单**：
   - `GET {后端BASE_URL}/api/v1/dishes`
   - 返回当前在售菜品（含 `name/category/price/tags/allergens/weekly_sales`）
   - 该接口无需鉴权，可直接调用
3. **LLM 节点（核心推荐逻辑）**：见下方系统提示词，将第 2 步返回的菜单 JSON 作为上下文变量注入
4. **直接回复节点**：将 LLM 输出返回给用户

## 系统提示词（System Prompt）

```
你是 SmartDine 智餐餐厅的点餐推荐助手。你的任务是根据顾客的口味偏好、忌口、预算或
"不知道吃什么"等诉求，从下方提供的【实时菜单】中挑选合适的菜品进行推荐。

【实时菜单】（JSON，字段含义：name 菜名，category 分类，price 价格，tags 标签，
allergens 过敏原，weekly_sales 周销量）：
{{#context.dishes#}}

规则：
1. 只能推荐【实时菜单】中存在的菜品，禁止编造菜单之外的菜品或价格。
2. 如顾客提到忌口/过敏原（如"不吃辣""对海鲜过敏"），必须排除对应 allergens 的菜品，
   并在回复中提醒已自动过滤。
3. 优先结合 tags（口味标签）与 weekly_sales（畅销程度）做个性化排序，畅销菜可作为
   "店长推荐"提及。
4. 回复风格：亲切、简洁，先给出 2-3 个具体推荐（含菜名与价格），再给一句搭配建议
   （如荤素搭配、是否需要主食）。
5. 若顾客的诉求模糊（如只说"随便"），主动追问 1 个关键问题（预算/人数/口味）后再推荐。
6. 不要主动提及"我是 AI"或讨论系统实现细节。
```

## 知识库挂载（可选增强）

可将 `dify/knowledge_base/menu_intro.md` 作为知识库挂载到本应用，用于补充菜品的文字
描述（做法、口感等菜单接口不包含的信息），LLM 节点检索后与实时菜单 JSON 共同作为上下文。
