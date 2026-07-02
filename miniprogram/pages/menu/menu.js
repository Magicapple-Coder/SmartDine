import { get } from '../../api/request'

Page({
  data: {
    tableId: null,
    categories: [],
    activeCategory: '',
    dishes: [],
    cartCount: 0,
  },

  onLoad() {
    const app = getApp()
    this.setData({ tableId: app.globalData.tableId })
  },

  onShow() {
    this.loadDishes()
    this.refreshCartCount()
  },

  // 在售菜品列表，对应需求文档 4.1 扫码点餐 / GET /api/v1/dishes
  loadDishes() {
    get('/dishes').then((dishes) => {
      const categories = [...new Set(dishes.map((d) => d.category))]
      this.setData({
        dishes,
        categories,
        activeCategory: this.data.activeCategory || categories[0] || '',
      })
    })
  },

  refreshCartCount() {
    const cart = getApp().globalData.cart
    this.setData({ cartCount: cart.reduce((sum, c) => sum + c.qty, 0) })
  },

  onSwitchCategory(e) {
    this.setData({ activeCategory: e.currentTarget.dataset.category })
  },

  onTapDish(e) {
    wx.navigateTo({ url: `/pages/dish/dish?id=${e.currentTarget.dataset.id}` })
  },

  onQuickAdd(e) {
    const dish = e.currentTarget.dataset.dish
    getApp().addToCart({ dish_id: dish.dish_id, name: dish.name, price: dish.price, qty: 1, note: '' })
    this.refreshCartCount()
    wx.showToast({ title: '已加入购物车', icon: 'success' })
  },

  goChat() {
    wx.navigateTo({ url: '/pages/chat/chat' })
  },

  goCart() {
    wx.navigateTo({ url: '/pages/cart/cart' })
  },
})
