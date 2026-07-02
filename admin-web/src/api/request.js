import axios from 'axios'
import router from '../router'
import { useUserStore } from '../store/user'
import { toast } from '../utils/toast'

const request = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api/v1/merchant',
  timeout: 15000,
})

request.interceptors.request.use((config) => {
  const userStore = useUserStore()
  if (userStore.token) {
    config.headers.Authorization = `Bearer ${userStore.token}`
  }
  return config
})

// 统一解析后端 {code, message, data} 响应结构（核心响应封装见系统设计说明书 8.1）
request.interceptors.response.use(
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
      router.push('/login')
    }
    toast.error(error.response?.data?.message || error.message || '网络错误')
    return Promise.reject(error)
  },
)

export default request
