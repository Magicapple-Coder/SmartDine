import request from './request'

export const listOrders = (params) => request.get('/orders', { params })
export const getOrder = (orderId) => request.get(`/orders/${orderId}`)
export const updateOrderStatus = (orderId, params) => request.post(`/orders/${orderId}/status`, null, { params })
export const deleteOrder = (orderId) => request.delete(`/orders/${orderId}`)
export const listReviews = () => request.get('/orders/reviews')
