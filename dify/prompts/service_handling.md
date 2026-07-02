# 客服处理智能体（Chatflow + 分流）

对应：需求文档 3.3、5.3；后端调用入口 `POST /api/v1/agent/service/chat`
（`gateway.chat_service()` 对接 Dify `/chat-messages`；后端 `app/services/service.py`
的 `handle_chat()` 会在拿到回复后写入 `service_ticket` 工单，并用关键词规则
兜底分类 `category/sentiment/to_human`，详见该文件 `_classify()` 的说明）。

## 应用类型与变量

- Dify 应用类型：Chatflow（内部包含问题分类 → 分流 → 知识库问答/转人工 提示）
- 会话输入变量：`session_id`
- 用户输入：`query`（顾客问题，如咨询/投诉/预订/建议）

## 建议的 Chatflow 节点编排

1. **开始节点**：接收 `query`、`session_id`
2. **问题分类节点（Question Classifier）**：将 `query` 分为「咨询」「投诉」「预订」「建议」四类
3. **分流（IF/ELSE）**：
   - 「投诉」且语气强烈 → 直接给出安抚话术，并在回复中提示"已为您转接人工"
   - 「预订」 → 引导顾客提供人数/时间/联系方式（实际预订写入由小程序端调用
     `POST /api/v1/tables/reservations` 完成，本智能体只负责对话引导）
   - 「咨询」「建议」 → 走知识库问答（挂载 `dify/knowledge_base/store_faq.md`、
     `dify/knowledge_base/policy.md`）
4. **LLM 回复节点**：见下方系统提示词
5. **直接回复节点**：返回最终话术

## 系统提示词（System Prompt）

```
你是 SmartDine 智餐餐厅的客服助手，负责解答顾客的咨询、处理投诉、引导预订与收集建议。

风格：礼貌、简洁、有同理心。遇到投诉时先安抚情绪，再说明处理方式；遇到无法在知识库中
找到答案的问题，坦诚告知会转人工跟进，不要编造门店政策或退款承诺。

知识库（退换货/优惠政策、门店 FAQ）已挂载，请优先基于检索结果回答；若检索结果为空，
回复"这个问题我暂时无法确定，已为您记录并转人工客服核实"。
```

## 与后端工单的对应关系

- 后端目前以关键词规则（投诉/退款/差评 → 投诉+强情绪+转人工；预订/订座 → 预订）作为
  `service_ticket.category/sentiment/to_human` 的兜底分类，独立于 Dify 内部的分类节点。
- 若希望以 Dify 的分类结果为准，可在 Chatflow 末尾通过"变量赋值"节点将分类结果放入
  `conversation_variables`，并扩展 `gateway.chat_service()` 的返回解析与
  `services/service.py::handle_chat()`，用 Dify 返回的字段替换关键词规则。
