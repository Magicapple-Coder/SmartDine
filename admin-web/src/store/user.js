import { defineStore } from 'pinia'
import { login as loginApi } from '../api/auth'
import { platformLogin as platformLoginApi } from '../api/platform'

export const useUserStore = defineStore('user', {
  state: () => ({
    token: localStorage.getItem('sd_token') || '',
    role: localStorage.getItem('sd_role') || '',
    isPlatformAdmin: localStorage.getItem('sd_is_platform') === 'true',  // V2.0 新增
    merchantId: localStorage.getItem('sd_merchant_id') || null,          // V2.0 新增
  }),
  getters: {
    isLoggedIn: (state) => !!state.token,
  },
  actions: {
    // 商户端登录
    async login(account, password) {
      const data = await loginApi(account, password)
      this.token = data.access_token
      this.role = data.role
      this.isPlatformAdmin = false
      localStorage.setItem('sd_token', data.access_token)
      localStorage.setItem('sd_role', data.role)
      localStorage.setItem('sd_is_platform', 'false')
    },

    // 平台端登录（V2.0 新增）
    async platformLogin(username, password) {
      const data = await platformLoginApi(username, password)
      this.token = data.access_token
      this.role = data.role
      this.isPlatformAdmin = true
      localStorage.setItem('sd_token', data.access_token)
      localStorage.setItem('sd_role', data.role)
      localStorage.setItem('sd_is_platform', 'true')
    },

    logout() {
      this.token = ''
      this.role = ''
      this.isPlatformAdmin = false
      this.merchantId = null
      localStorage.removeItem('sd_token')
      localStorage.removeItem('sd_role')
      localStorage.removeItem('sd_is_platform')
      localStorage.removeItem('sd_merchant_id')
    },
  },
})
