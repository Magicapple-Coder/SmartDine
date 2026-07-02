import { get } from '../../api/request'

Page({
  data: {
    dish: null,
    qty: 1,
    note: '',
    totalPrice: '0.00',
  },

  onLoad(options) {
    const dishId = Number(options.id)
    // 菜品列表接口已含全部字段，详情页直接从列表中按 id 取（需求文档 4.1）
    get('/dishes').then((dishes) => {
      const dish = dishes.find((d) => d.dish_id === dishId)
      this.setData({ dish })
      this.refreshTotal()
    })
  },

  refreshTotal() {
    const { dish, qty } = this.data
    if (!dish) return
    this.setData({ totalPrice: (dish.price * qty).toFixed(2) })
  },

  onChangeQty(e) {
    const delta = Number(e.currentTarget.dataset.delta)
    this.setData({ qty: Math.max(1, this.data.qty + delta) })
    this.refreshTotal()
  },

  onInputNote(e) {
    this.setData({ note: e.detail.value })
  },

  addToCart() {
    const { dish, qty, note } = this.data
    getApp().addToCart({ dish_id: dish.dish_id, name: dish.name, price: dish.price, qty, note })
    wx.showToast({ title: '已加入购物车', icon: 'success' })
    wx.navigateBack()
  },
})
