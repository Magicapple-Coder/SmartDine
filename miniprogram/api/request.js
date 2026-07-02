const BASE_URL = 'http://127.0.0.1:8000/api/v1' // 本地预览临时指向本机后端；部署后请替换为真实域名（需 HTTPS，小程序后台配置 request 合法域名）

function request(method, url, data = {}) {
  return new Promise((resolve, reject) => {
    const app = getApp()
    wx.request({
      url: `${BASE_URL}${url}`,
      method,
      data,
      header: {
        'content-type': 'application/json',
        ...(app.globalData.token ? { Authorization: `Bearer ${app.globalData.token}` } : {}),
      },
      success: (res) => {
        // 统一响应结构 {code, message, data}，code=0 表示成功（系统设计说明书 8.1）
        if (res.statusCode >= 200 && res.statusCode < 300 && res.data.code === 0) {
          resolve(res.data.data)
        } else {
          wx.showToast({ title: res.data.message || '请求失败', icon: 'none' })
          reject(res.data)
        }
      },
      fail: (err) => {
        wx.showToast({ title: '网络异常', icon: 'none' })
        reject(err)
      },
    })
  })
}

export const get = (url, params) => request('GET', url, params)
export const post = (url, data) => request('POST', url, data)
export const put = (url, data) => request('PUT', url, data)

export function wxLogin(code) {
  return request('POST', '/auth/wx-login', { code })
}
