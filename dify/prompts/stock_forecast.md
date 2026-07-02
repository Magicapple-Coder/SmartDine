# 库存预测智能体（Workflow）

对应：需求文档 5.2、系统设计说明书 5.0.1；后端调用入口 `POST /api/v1/agent/stock/forecast`
（`gateway.run_stock_forecast()`，对接 Dify `/workflows/run`），并由
`backend/app/tasks/scheduler.py` 每日 9:00 定时触发（当前传入空 `inputs`，
即由 Workflow 自行通过 HTTP 节点获取所需数据，而非依赖后端预先打包）。

## 应用类型与变量

- Dify 应用类型：Workflow
- 输入变量：无强制要求（定时任务传入 `{}`）；如需手动指定预测天数，可在管理端
  「库存预测智能体」工作台传入 `{"days": 7}`，Workflow 内通过 `days`（默认 7）控制预测窗口

## 建议的 Workflow 节点编排

1. **开始节点**：可选输入 `days`（默认 7）
2. **HTTP 请求节点 - 当前库存**：`GET {后端BASE_URL}/api/v1/ingredients`
   → 食材清单（`name/unit/stock/safe_threshold`）
3. **HTTP 请求节点 - 出入库流水**：`GET {后端BASE_URL}/api/v1/stock-logs`
   → 近期消耗速率（用于估算日均用量）
4. **HTTP 请求节点 - 菜品销量**：`GET {后端BASE_URL}/api/v1/dishes`
   → `weekly_sales` 作为需求侧参考信号
5. **LLM 节点（预测与建议）**：见下方提示词，综合 2/3/4 步数据生成预测与补货建议
6. **结束节点**：输出结构化 JSON（见下方输出契约），供管理端「库存预测智能体」工作台
   以及 `POST /agent/stock/forecast` 的调用方展示

## 系统提示词（LLM 节点）

```
你是 SmartDine 智餐的库存预测助手。基于【当前库存】【近期出入库流水】【菜品周销量】
三组数据，预测未来 {{days}} 天内每种食材是否会低于安全库存阈值（safe_threshold），
并给出补货建议。

【当前库存】：{{#context.ingredients#}}
【出入库流水】：{{#context.stock_logs#}}
【菜品周销量】：{{#context.dishes#}}

要求：
1. 按"出库"流水估算日均消耗速率（损耗也计入消耗，入库不计入消耗）。
2. 结合菜品 weekly_sales 与该食材在 BOM 中的用量关系（如有缺失数据，按经验估算，
   并在 risk_note 中说明为估算值）。
3. 仅对预计将在 {{days}} 天内跌破 safe_threshold 的食材输出预警，不要罗列全部食材。
4. 严格按以下 JSON 结构输出，不要输出多余文字：
{
  "forecast_days": {{days}},
  "alerts": [
    {
      "ingredient_id": 食材ID,
      "name": "食材名",
      "current_stock": 当前库存,
      "estimated_daily_usage": 估算日均消耗,
      "days_until_shortage": 预计可用天数,
      "suggested_reorder_qty": 建议补货数量,
      "risk_note": "风险说明，若为估算请注明"
    }
  ]
}
```

## 输出契约

Workflow 结束节点应返回上述 JSON 字符串作为 `outputs.text`（或自定义变量名，
与前端 `result.outputs` 解析逻辑保持一致；当前管理端工作台页面以原始 JSON 展示，
未来如需结构化渲染，可在 `admin-web/src/views/agents/StockAgent.vue` 中补充解析逻辑）。
