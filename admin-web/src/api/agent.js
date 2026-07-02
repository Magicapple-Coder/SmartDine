// 智能体 API 占位层 —— 从设计原型匹配的静态 Mock 数据
// 智能体功能尚未实际接入 Dify，当前均为前端演示数据

import request from './request'

/** 获取智能体运行状态概览 */
export function getAgentStatus() {
  return Promise.resolve({
    order: { online: true, task_count: 54, label: '点餐推荐采纳' },
    stock: { online: true, task_count: 3, label: '采购建议待处理' },
    service: { online: true, task_count: 5, label: '待人工工单' },
    analytics: { online: true, task_count: 0, label: '今日摘要已生成' },
  })
}

/** 获取智能体动态日志 */
export function listAgentLogs() {
  return Promise.resolve([
    { time: '09:42', agent: '经营分析', color: 'var(--c-ana)', text: '生成今日经营摘要' },
    { time: '09:30', agent: '库存预测', color: 'var(--c-stock)', text: '牛肉低于安全线，生成采购建议' },
    { time: '09:15', agent: '客服处理', color: 'var(--c-svc)', text: '自动回复张先生营业时间咨询' },
    { time: '08:58', agent: '点餐推荐', color: 'var(--c-order)', text: '为顾客推荐酸梅汤，已加入订单' },
  ])
}

/** 点餐推荐 —— 获取推荐数据 */
export function getOrderRecommendations() {
  return Promise.resolve({
    summary: { total_impressions: 312, adopted: 54, rate: 17.3 },
    hot_items: ['招牌牛肉面', '麻辣香锅', '番茄牛腩煲', '老坛酸梅汤'],
    recommendations: [
      { id: 1, name: '椒麻鸡', price: 28, reason: '偏好匹配 — 顾客常点凉菜类', match: '高' },
      { id: 2, name: '老坛酸梅汤', price: 10, reason: '搭配推荐 — 与麻辣香锅搭配', match: '高' },
      { id: 3, name: '番茄牛腩煲', price: 38, reason: '热销菜品 — 本周售出 201 份', match: '中' },
      { id: 4, name: '蒜蓉西兰花', price: 16, reason: '健康推荐 — 均衡营养搭配', match: '中' },
    ],
  })
}

/** 库存预测 —— 获取预测数据 */
export function getStockForecast() {
  return Promise.resolve({
    alerts: [
      { name: '牛肉', stock: 12, unit: 'kg', safe: 20, priority: 'high', supplier: '鲜丰食材', days_left: 2 },
      { name: '酸梅汤料', stock: 8, unit: '包', safe: 15, priority: 'high', supplier: '源味食品', days_left: 3 },
      { name: '面粉', stock: 45, unit: 'kg', safe: 50, priority: 'mid', supplier: '粮芯商贸', days_left: 5 },
    ],
    forecast: [
      { day: '周一', demand: 18 }, { day: '周二', demand: 20 }, { day: '周三', demand: 22 },
      { day: '周四', demand: 19 }, { day: '周五', demand: 24 }, { day: '周六', demand: 28 },
      { day: '周日', demand: 26 },
    ],
    suggestions: [
      { priority: 'high', text: '牛肉建议采购 30kg（预计可用 5 天），建议 7 月 2 日前下单' },
      { priority: 'high', text: '酸梅汤料建议采购 20 包，当前库存仅剩 8 包' },
      { priority: 'mid', text: '面粉未来 5 天内将低于安全线，建议下周补货' },
    ],
  })
}

/** 客服处理 —— 获取工单列表 */
export function listServiceTickets() {
  return Promise.resolve([
    { id: 1, member: '张敏', channel: '微信', preview: '请问今天营业到几点？', category: '咨询', status: 'auto', time: '10:30', sentiment: '弱', to_human: 0 },
    { id: 2, member: '刘洋', channel: '支付宝', preview: '麻辣香锅太辣了，建议少放点辣椒...', category: '建议', status: 'auto', time: '10:15', sentiment: '弱', to_human: 0 },
    { id: 3, member: '孙强', channel: '微信', preview: '上菜太慢了，等了 40 分钟什么也没上！', category: '投诉', status: 'wait', time: '09:55', sentiment: '强', to_human: 1 },
    { id: 4, member: '周丽', channel: '微信', preview: '我预订明天的 6 人桌，大约晚上 7 点', category: '预订', status: 'rec2', time: '09:40', sentiment: '弱', to_human: 0 },
    { id: 5, member: '赵磊', channel: '小程序', preview: '番茄牛腩煲有牛肉过敏提示吗？', category: '咨询', status: 'auto', time: '09:20', sentiment: '弱', to_human: 0 },
    { id: 6, member: '吴芳', channel: '微信', preview: '昨天买的优惠券为什么用不了了？', category: '投诉', status: 'wait', time: '08:50', sentiment: '强', to_human: 1 },
  ])
}

/** 客服处理 —— 获取单个工单详情 */
export function getTicketDetail(ticketId) {
  const details = {
    1: {
      messages: [
        { from: 'customer', name: '张敏', text: '请问今天营业到几点？', time: '10:30' },
        { from: 'bot', text: '您好，本店今日营业时间为 10:00–21:00。欢迎光临！', time: '10:30' },
      ],
      analysis: { category: '咨询', sentiment: '弱', intent: '营业时间查询' },
      draft: '您好，本店每日营业时间为 10:00 至 21:00。期待为您服务！',
    },
    2: {
      messages: [
        { from: 'customer', name: '刘洋', text: '麻辣香锅太辣了，建议少放点辣椒...', time: '10:15' },
        { from: 'bot', text: '感谢您的宝贵建议！已记录反馈，会转交后厨团队调整口味。', time: '10:15' },
      ],
      analysis: { category: '建议', sentiment: '弱', intent: '口味反馈' },
      draft: '感谢您的反馈！我们会根据顾客建议优化菜品口味。',
    },
    3: {
      messages: [
        { from: 'customer', name: '孙强', text: '上菜太慢了，等了 40 分钟什么也没上！真的很失望。', time: '09:55' },
        { from: 'bot', text: '非常抱歉给您带来不便，您的反馈已紧急转交客服专员处理。', time: '09:56' },
        { from: 'customer', name: '孙强', text: '这不是一次两次了，上次也等了半小时。', time: '09:58' },
      ],
      analysis: { category: '投诉', sentiment: '强', intent: '上菜速度投诉 | 重复投诉' },
      draft: '孙先生，非常抱歉您再次遇到上菜延迟的问题。我们已通知前厅经理并赠送 30 元优惠券作为补偿，后厨正全力加速出餐。',
    },
    4: {
      messages: [
        { from: 'customer', name: '周丽', text: '我预订明天的 6 人桌，大约晚上 7 点到。', time: '09:40' },
        { from: 'bot', text: '已收到您的预订。明天 7 月 2 日 19:00，6 人桌已为您预留。到店时告知前台即可。', time: '09:40' },
      ],
      analysis: { category: '预订', sentiment: '弱', intent: '桌位预订' },
      draft: '已确认预订：7 月 2 日 19:00，6 人桌。如有变动请提前告知。',
    },
    5: {
      messages: [
        { from: 'customer', name: '赵磊', text: '番茄牛腩煲有牛肉过敏提示吗？', time: '09:20' },
        { from: 'bot', text: '番茄牛腩煲主要原料为牛肉和番茄。牛肉为常见过敏原之一，如您有牛肉过敏史，建议避免食用或替换为其他菜品。', time: '09:20' },
      ],
      analysis: { category: '咨询', sentiment: '弱', intent: '过敏原查询' },
      draft: '番茄牛腩煲含牛肉（过敏原）。如您有过敏顾虑，我们推荐尝试椒麻鸡或麻辣香锅（可选择不辣）。',
    },
    6: {
      messages: [
        { from: 'customer', name: '吴芳', text: '昨天买的优惠券为什么用不了了？扫码提示已过期。', time: '08:50' },
        { from: 'bot', text: '非常抱歉！已为您转接人工客服核实优惠券状态。', time: '08:51' },
      ],
      analysis: { category: '投诉', sentiment: '强', intent: '优惠券异常 | 涉及退款' },
      draft: '吴女士，经核查您的优惠券因系统延迟未刷新。现已恢复正常使用，有效期延长 3 天。给您带来不便深感抱歉。',
    },
  }
  return Promise.resolve(details[ticketId] || null)
}

/** 经营分析 —— 获取分析摘要 */
export function getAnalyticsSummary() {
  return Promise.resolve({
    kpis: [
      { label: '本周营收', value: '¥58,240', trend_up: true, pct: '12.5%' },
      { label: '日均订单', value: '136', trend_up: true, pct: '8.3%' },
      { label: '翻台率', value: '3.2', trend_up: false, pct: '0.3' },
      { label: '活跃会员', value: '427', trend_up: true, pct: '5.1%' },
    ],
    top_dishes: [
      { name: '招牌牛肉面', sales: 312, revenue: 8112 },
      { name: '麻辣香锅', sales: 268, revenue: 11256 },
      { name: '番茄牛腩煲', sales: 201, revenue: 7638 },
      { name: '椒麻鸡', sales: 176, revenue: 4928 },
    ],
    causes: [
      { label: '上菜延迟', pct: 32 },
      { label: '口味反馈', pct: 26 },
      { label: '环境嘈杂', pct: 18 },
      { label: '价格偏高', pct: 14 },
      { label: '服务态度', pct: 10 },
    ],
    insights: [
      '周六晚市翻台率达到峰值 4.1，建议周六增加兼职人手',
      '老坛酸梅汤近 7 天销量增长 23%，可考虑列入本周主推饮品',
      '麻辣香锅周末销量是工作日的 1.8 倍，周五备货量建议增加 40%',
      '会员复购率 6 月环比下降 3.5%，建议在下旬推出会员专属活动',
      '午餐时段（11:00-13:00）订单占比 52%，后厨可优化出餐流程',
    ],
  })
}

/** 客服工单统计（供角标和 Dashboard 使用） */
export function countPendingTickets() {
  return listServiceTickets().then((list) => ({
    total: list.length,
    pending: list.filter((t) => t.to_human === 1).length,
    auto: list.filter((t) => t.to_human === 0).length,
  }))
}
