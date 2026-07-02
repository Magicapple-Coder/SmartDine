import { get, post, put } from '../../api/request'

Page({
  data: {
    member: null,
    phone: '',
    name: '',
    avatarUrl: '',
    editingPreferences: false,
    preferences: '',
  },

  onShow() {
    this.setData({ avatarUrl: wx.getStorageSync('sd_avatar_url') || '' })
    const memberId = wx.getStorageSync('sd_member_id')
    if (memberId) {
      this.loadMember(memberId)
    }
  },

  // 头像选择组件直接返回微信用户头像的临时路径，无需手动上传/裁剪（仅本地展示，会员表暂无 avatar 字段）
  onChooseAvatar(e) {
    const { avatarUrl } = e.detail
    wx.setStorageSync('sd_avatar_url', avatarUrl)
    this.setData({ avatarUrl })
  },

  onInputPhone(e) {
    this.setData({ phone: e.detail.value })
  },

  onInputName(e) {
    this.setData({ name: e.detail.value })
  },

  // 会员注册/登录绑定：手机号已存在则直接取回档案（需求文档 3.7、4.6，POST /api/v1/members）
  bindPhone() {
    if (!this.data.phone) {
      wx.showToast({ title: '请输入手机号', icon: 'none' })
      return
    }
    post('/members', { phone: this.data.phone, name: this.data.name }).then((member) => {
      wx.setStorageSync('sd_member_id', member.member_id)
      this.setData({ member, preferences: member.preferences || '' })
    })
  },

  loadMember(memberId) {
    get(`/members/${memberId}`).then((member) => this.setData({ member, preferences: member.preferences || '' }))
  },

  editPreferences() {
    this.setData({ editingPreferences: true })
  },

  onInputPreferences(e) {
    this.setData({ preferences: e.detail.value })
  },

  savePreferences() {
    put(`/members/${this.data.member.member_id}`, { preferences: this.data.preferences }).then((member) => {
      this.setData({ member, editingPreferences: false })
      wx.showToast({ title: '已保存', icon: 'success' })
    })
  },

  logout() {
    wx.removeStorageSync('sd_member_id')
    this.setData({ member: null })
  },
})
