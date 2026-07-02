import { defineStore } from 'pinia'
import axios from 'axios'
import { useUserStore } from './user'

export const useAppStore = defineStore('app', {
  state: () => ({
    storeName: 'SmartDine 智餐',
    address: '',
    hours: '10:00 - 21:00',
    phone: '',
    sidebarCollapsed: false,
  }),
  actions: {
    toggleSidebar() {
      this.sidebarCollapsed = !this.sidebarCollapsed
    },
    /** 从后端加载门店信息 */
    async loadStoreInfo() {
      try {
        const userStore = useUserStore()
        const resp = await axios.get('/api/v1/merchant/profile', {
          headers: userStore.token ? { Authorization: `Bearer ${userStore.token}` } : {},
        })
        const data = resp.data.data
        if (data) {
          this.storeName = data.name || 'SmartDine 智餐'
          this.address = data.address || ''
          this.hours = data.business_hours || '10:00 - 21:00'
          this.phone = data.contact_phone || ''
        }
      } catch {
        // 静默失败：门店信息非关键
      }
    },
    /** 保存门店信息到后端 */
    async saveStoreInfo({ storeName, address, hours, phone }) {
      const userStore = useUserStore()
      const resp = await axios.put('/api/v1/merchant/profile',
        { name: storeName, address, business_hours: hours, contact_phone: phone },
        { headers: { Authorization: `Bearer ${userStore.token}` } },
      )
      const data = resp.data.data
      if (data) {
        this.storeName = data.name || storeName
        this.address = data.address || address
        this.hours = data.business_hours || hours
        this.phone = data.contact_phone || phone
      }
    },
  },
})
