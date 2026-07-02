import { post } from '../../api/request'
import { formatMoney } from '../../utils/util'

Page({
  data: {
    cart: [],
    total: 0,
    submitting: false,
  },

  onShow() {
    this.refresh()
  },

  refresh() {
    const cart = getApp().globalData.cart
    const total = cart.reduce((sum, c) => sum + c.price * c.qty, 0)
    this.setData({ cart, total: total.toFixed(2) })
  },

  onChangeQty(e) {
    const { id, delta } = e.currentTarget.dataset
    const item = this.data.cart.find((c) => c.dish_id === id)
    if (!item) return
    getApp().updateCartQty(id, item.qty + Number(delta))
    this.refresh()
  },

  onRemove(e) {
    getApp().updateCartQty(e.currentTarget.dataset.id, 0)
    this.refresh()
  },

  goMenu() {
    wx.switchTab({ url: '/pages/menu/menu' })
  },

  // 下单并发起支付：对应需求文档 4.3，POST /api/v1/orders 创建订单
  submitOrder() {
    if (this.data.cart.length === 0 || this.data.submitting) return
    this.setData({ submitting: true })
    const tableId = getApp().globalData.tableId
    const items = this.data.cart.map((c) => ({ dish_id: c.dish_id, qty: c.qty, note: c.note || '' }))
    post('/orders', { table_id: tableId ? Number(tableId) : null, items })
      .then((order) => this.pay(order))
      .catch(() => this.setData({ submitting: false }))
  },

  // 正式上线需替换为微信支付统一下单 + wx.requestPayment 真实支付流程；
  // 当前以「确认支付」模拟收银台收款，便于先打通点餐主链路。
  pay(order) {
    wx.showModal({
      title: '确认支付',
      content: `订单金额 ${formatMoney(order.amount)}，确认支付？`,
      success: (res) => {
        if (res.confirm) {
          post(`/orders/${order.order_id}/status?pay_status=1`).finally(() => {
            getApp().clearCart()
            getApp().addOrderHistory(order.order_id)
            this.setData({ submitting: false })
            wx.switchTab({ url: '/pages/order/order' })
          })
        } else {
          this.setData({ submitting: false })
        }
      },
    })
  },
})
