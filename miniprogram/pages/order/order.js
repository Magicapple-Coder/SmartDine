import { get, post } from '../../api/request'
import { formatMoney } from '../../utils/util'

const PAY_STATUS_TEXT = ['待付', '已付', '退款']
const PAY_TAG_TYPE = ['warn', 'ok', 'bad']
const COOK_STATUS_TEXT = ['待餐', '出餐', '完成']

Page({
  data: {
    orders: [],
    reviewVisible: false,
    reviewOrderId: null,
    reviewScore: 5,
    reviewContent: '',
  },

  onShow() {
    this.loadOrders()
  },

  // 本机历史订单号逐一查询详情（需求文档 4.4 订单跟踪与历史订单）
  loadOrders() {
    const ids = getApp().globalData.orderHistory
    if (ids.length === 0) {
      this.setData({ orders: [] })
      return
    }
    Promise.all(ids.map((id) => get(`/orders/${id}`).catch(() => null))).then((list) => {
      const orders = list
        .filter(Boolean)
        .map((o) => ({
          ...o,
          payStatusText: PAY_STATUS_TEXT[o.pay_status],
          payTagType: PAY_TAG_TYPE[o.pay_status],
          cookStatusText: COOK_STATUS_TEXT[o.cook_status],
          amountText: formatMoney(o.amount),
        }))
      this.setData({ orders })
    })
  },

  openReview(e) {
    this.setData({ reviewVisible: true, reviewOrderId: e.currentTarget.dataset.id, reviewScore: 5, reviewContent: '' })
  },

  onScoreChange(e) {
    this.setData({ reviewScore: Number(e.currentTarget.dataset.score) })
  },

  onReviewInput(e) {
    this.setData({ reviewContent: e.detail.value })
  },

  submitReview() {
    post(`/orders/${this.data.reviewOrderId}/review`, { score: this.data.reviewScore, content: this.data.reviewContent }).then(() => {
      wx.showToast({ title: '感谢您的评价', icon: 'success' })
      this.setData({ reviewVisible: false })
    })
  },

  closeReview() {
    this.setData({ reviewVisible: false })
  },

  goMenu() {
    wx.switchTab({ url: '/pages/menu/menu' })
  },
})
