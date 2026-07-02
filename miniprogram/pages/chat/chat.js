import { post } from '../../api/request'

Page({
  data: {
    sessionId: '',
    conversationId: '',
    messages: [], // {role: 'user'|'agent', text}
    input: '',
    loading: false,
  },

  onLoad() {
    this.setData({
      sessionId: `mp-${Date.now()}-${Math.floor(Math.random() * 1000)}`,
      messages: [{ role: 'agent', text: '您好，我是点餐推荐助手，可以告诉我您的口味偏好或想吃的菜系～' }],
    })
  },

  onInput(e) {
    this.setData({ input: e.detail.value })
  },

  // 点餐推荐智能体对话，对应需求文档 5.1、POST /api/v1/agent/order/chat
  send() {
    const text = this.data.input.trim()
    if (!text || this.data.loading) return
    this.setData({
      messages: [...this.data.messages, { role: 'user', text }],
      input: '',
      loading: true,
    })
    post('/agent/order/chat', {
      message: text,
      session_id: this.data.sessionId,
      conversation_id: this.data.conversationId,
    })
      .then((result) => {
        this.setData({
          conversationId: result.conversation_id || this.data.conversationId,
          messages: [...this.data.messages, { role: 'agent', text: result.answer || '抱歉，暂时无法理解，请换个说法试试。' }],
        })
      })
      .finally(() => this.setData({ loading: false }))
  },

  goMenu() {
    wx.switchTab({ url: '/pages/menu/menu' })
  },
})
