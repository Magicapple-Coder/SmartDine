import request from './request'

export function login(account, password) {
  return request.post('/auth/login', { account, password })
}
