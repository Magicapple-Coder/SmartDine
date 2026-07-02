# dify/ —— Dify 工作流与知识库语料

存放 4 个智能体在 Dify 平台落地所需的提示词设计、节点编排说明与知识库语料草稿。
实际运行时需登录自托管 Dify（Linux 虚拟机），手动创建对应应用并粘贴下方内容；
创建完成后将各应用的 API Key 填入 `backend/.env` 的 `DIFY_*_KEY` 配置项。

```
dify/
├── prompts/                       # 各智能体的系统提示词 + 节点编排建议
│   ├── order_recommendation.md    # 点餐推荐智能体（Chatflow），对应需求文档 5.1
│   ├── stock_forecast.md          # 库存预测智能体（Workflow），对应需求文档 5.2
│   ├── service_handling.md        # 客服处理智能体（Chatflow+分流），对应需求文档 5.3
│   └── analytics.md               # 经营分析智能体（Chatflow 查数 + Workflow 摘要），对应需求文档 5.4
└── knowledge_base/                # 知识库语料草稿（示例内容，实际门店需替换为真实信息）
    ├── menu_intro.md              # 菜单文字说明（菜品做法/口感等，配合点餐推荐智能体）
    ├── store_faq.md               # 门店常见问题（营业时间/预订/支付/过敏原等）
    └── policy.md                  # 退换货、优惠券、会员等级与投诉处理政策
```

## 落地步骤

1. 在 Dify 控制台分别创建 4 个应用：点餐推荐（Chatflow）、库存预测（Workflow）、
   客服处理（Chatflow）、经营分析（Chatflow + Workflow 各一个，或合并为一个多入口应用）。
2. 按各 `prompts/*.md` 中的「节点编排」搭建 HTTP 请求节点（调用本项目后端 `GET /api/v1/...`
   只读接口）与 LLM 节点，并粘贴对应「系统提示词」。
3. 点餐推荐、客服处理两个应用挂载 `knowledge_base/` 下对应的语料文件作为知识库。
4. 发布应用后，复制各应用的 API Key，填入 `backend/.env`：
   `DIFY_ORDER_KEY` / `DIFY_STOCK_KEY` / `DIFY_SERVICE_KEY` / `DIFY_ANALYTICS_KEY`。
5. 业务后端通过 `backend/app/agents/gateway.py` 统一调用，小程序/管理端均不直连 Dify
   （系统设计说明书 5.0.1、7.3）。
