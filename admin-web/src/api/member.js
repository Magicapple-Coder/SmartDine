import request from './request'

export const listMembers = () => request.get('/members')
export const getMember = (memberId) => request.get(`/members/${memberId}`)
export const createMember = (data) => request.post('/members', data)
export const updateMember = (memberId, data) => request.put(`/members/${memberId}`, data)
export const adjustPoints = (memberId, data) => request.post(`/members/${memberId}/points`, data)
