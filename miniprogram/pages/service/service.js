import { post } from '../../api/request'

Page({
  data: {
    sessionId: '',
    conversationId: '',
    messages: [{ role: 'agent', text: '您好，我是智能客服，请问有什么可以帮您？' }],
    input: '',
    loading: false,
  },

  onLoad() {
    this.setData({ sessionId: `mp-service-${Date.now()}` })
  },

  onInput(e) {
    this.setData({ input: e.detail.value })
  },

  // 客服处理智能体对话，对应需求文档 5.3、POST /api/v1/agent/service/chat（后端会同步回写工单）
  send() {
    const text = this.data.input.trim()
    if (!text || this.data.loading) return
    this.setData({ messages: [...this.data.messages, { role: 'user', text }], input: '', loading: true })
    post('/agent/service/chat', {
      message: text,
      session_id: this.data.sessionId,
      conversation_id: this.data.conversationId,
      channel: '小程序',
    })
      .then((result) => {
        const messages = [...this.data.messages, { role: 'agent', text: result.reply }]
        if (result.to_human) {
          messages.push({ role: 'system', text: '已为您转接人工客服，工作人员将尽快与您联系～' })
        }
        this.setData({ conversationId: result.conversation_id || this.data.conversationId, messages })
      })
      .finally(() => this.setData({ loading: false }))
  },
})
