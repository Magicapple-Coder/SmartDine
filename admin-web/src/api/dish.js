import request from './request'

export const listAllDishes = () => request.get('/dishes/all')
export const createDish = (data) => request.post('/dishes', data)
export const updateDish = (dishId, data) => request.put(`/dishes/${dishId}`, data)
export const setDishStatus = (dishId, status) => request.post(`/dishes/${dishId}/status`, null, { params: { status } })
export const deleteDish = (dishId) => request.delete(`/dishes/${dishId}`)
