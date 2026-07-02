/** 平台管理端 API（V2.0 新增）—— 使用独立 axios 实例，baseURL 指向平台端 */
import axios from 'axios'
import router from '../router'
import { useUserStore } from '../store/user'
import { toast } from '../utils/toast'

const http = axios.create({
  baseURL: '/api/v1/platform',
  timeout: 15000,
})

http.interceptors.request.use((config) => {
  const userStore = useUserStore()
  if (userStore.token) {
    config.headers.Authorization = `Bearer ${userStore.token}`
  }
  return config
})

http.interceptors.response.use(
  (response) => {
    const { code, message, data } = response.data
    if (code !== 0) {
      toast.error(message || '请求失败')
      return Promise.reject(new Error(message || '请求失败'))
    }
    return data
  },
  (error) => {
    if (error.response?.status === 401) {
      const userStore = useUserStore()
      userStore.logout()
      router.push('/platform/login')
    }
    toast.error(error.response?.data?.message || error.message || '网络错误')
    return Promise.reject(error)
  },
)

/** 平台管理员登录 */
export function platformLogin(username, password) {
  return http.post('/auth/login', { username, password })
}

/** 平台运营总览 */
export function platformDashboard() {
  return http.get('/dashboard')
}

/** 商户列表 */
export function listMerchants(status) {
  return http.get('/merchants', { params: { status } })
}

/** 商户详情 */
export function getMerchant(merchantId) {
  return http.get(`/merchants/${merchantId}`)
}

/** 审核通过商户 */
export function approveMerchant(merchantId) {
  return http.put(`/merchants/${merchantId}/approve`)
}

/** 驳回商户 */
export function rejectMerchant(merchantId, reason) {
  return http.put(`/merchants/${merchantId}/reject`, { reason })
}

/** 停用商户 */
export function disableMerchant(merchantId) {
  return http.put(`/merchants/${merchantId}/disable`)
}

/** 启用商户 */
export function enableMerchant(merchantId) {
  return http.put(`/merchants/${merchantId}/enable`)
}
