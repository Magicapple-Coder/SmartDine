import { wxLogin } from './api/request'

App({
  globalData: {
    token: wx.getStorageSync('sd_token') || '',
    tableId: wx.getStorageSync('sd_table_id') || null,
    cart: wx.getStorageSync('sd_cart') || [], // [{dish_id, name, price, qty, note}]
    orderHistory: wx.getStorageSync('sd_order_history') || [], // [order_id]，本机下单记录
  },

  onLaunch(options) {
    // 扫码进店：scene 携带桌台号，对应需求文档 4.1 扫码点餐
    const tableNo = options.query && options.query.table
    if (tableNo) {
      this.globalData.tableId = tableNo
      wx.setStorageSync('sd_table_id', tableNo)
    }
    if (!this.globalData.token) {
      this.loginSilently()
    }
  },

  // 小程序登录：wx.login() 换 code，交给后端 /auth/wx-login 换取 JWT（需求文档 2.3、4.6）
  loginSilently() {
    wx.login({
      success: (res) => {
        if (!res.code) return
        wxLogin(res.code)
          .then((data) => {
            this.globalData.token = data.access_token
            wx.setStorageSync('sd_token', data.access_token)
          })
          .catch(() => {})
      },
    })
  },

  // 购物车操作；qty<=0 时移除
  addToCart(item) {
    const cart = this.globalData.cart
    const existing = cart.find((c) => c.dish_id === item.dish_id && c.note === item.note)
    if (existing) {
      existing.qty += item.qty
    } else {
      cart.push(item)
    }
    this.persistCart()
  },

  updateCartQty(dishId, qty) {
    let cart = this.globalData.cart
    if (qty <= 0) {
      cart = cart.filter((c) => c.dish_id !== dishId)
    } else {
      const item = cart.find((c) => c.dish_id === dishId)
      if (item) item.qty = qty
    }
    this.globalData.cart = cart
    this.persistCart()
  },

  clearCart() {
    this.globalData.cart = []
    this.persistCart()
  },

  persistCart() {
    wx.setStorageSync('sd_cart', this.globalData.cart)
  },

  // 后端订单接口未要求绑定登录身份，本机历史订单号通过本地存储维护，供「我的订单」页展示
  addOrderHistory(orderId) {
    const history = [orderId, ...this.globalData.orderHistory.filter((id) => id !== orderId)]
    this.globalData.orderHistory = history
    wx.setStorageSync('sd_order_history', history)
  },
})
