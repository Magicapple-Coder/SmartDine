# 经营分析智能体（Chatflow 自然语言查数 + Workflow 经营摘要）

对应：需求文档 5.4(A)(B)；后端调用入口：
- `POST /api/v1/agent/analytics/query`（`gateway.chat_analytics()`，Chatflow，自然语言查数）
- 每日 22:00 定时触发 `gateway.run_analytics_summary()`（Workflow，经营摘要生成，
  见 `backend/app/tasks/scheduler.py`）

## A. 自然语言查数（Chatflow）

### 变量
- `session_id`；用户输入 `query`（如"上周哪个菜品销量最高""这个月差评主要原因是什么"）

### 节点编排
1. 开始节点接收 `query`
2. HTTP 请求节点按需调用后端只读接口获取数据，例如：
   - `GET /api/v1/orders` 订单与营业额
   - `GET /api/v1/dishes` 菜品销量（`weekly_sales`）
   - 差评归因（`review.cause`）暂无独立查询接口，如需统计需后续在 `order` 模块
     补充 `GET /api/v1/reviews` 列表接口
3. LLM 节点结合检索到的数据回答问题

### 系统提示词
```
你是 SmartDine 智餐的经营分析助手，基于提供的订单、菜品销量等数据回答门店经营问题。
只基于上下文中的真实数据作答，不得编造数字；如数据不足以回答，明确说明"当前数据
不足以回答该问题"，并建议管理员在管理端补充相应记录（如评价归因需要人工填写差评原因）。
回答应直接给出结论（数字/排名），再补充 1 句简要解读。
```

## B. 经营摘要生成（Workflow，每日定时）

### 节点编排
1. HTTP 请求节点：`GET /api/v1/orders` 获取近一日订单
2. HTTP 请求节点：`GET /api/v1/dishes` 获取菜品销量
3. LLM 节点：生成结构化经营日报（营业额、订单数、畅销/滞销菜品、待关注异常）
4. 结束节点输出 JSON 摘要（建议结构）：
```json
{
  "date": "汇总日期",
  "revenue": 当日营业额,
  "order_count": 当日订单数,
  "top_dishes": ["菜品1", "菜品2"],
  "slow_dishes": ["菜品3"],
  "alerts": ["需要关注的异常说明"]
}
```

该摘要当前由定时任务触发生成，尚未持久化到数据库或推送给管理端；如需在「运营总览」
页展示历史摘要，可后续在后端新增 `daily_summary` 表与查询接口。
