import request from './request'

export const listTables = () => request.get('/tables')
export const createTable = (data) => request.post('/tables', data)
export const openTable = (tableId, orderId) => request.post(`/tables/${tableId}/open`, null, { params: { order_id: orderId } })
export const checkoutTable = (tableId) => request.post(`/tables/${tableId}/checkout`)
export const cleanTable = (tableId) => request.post(`/tables/${tableId}/clean`)
export const listReservations = (tableId) => request.get('/tables/reservations', { params: { table_id: tableId } })
export const createReservation = (data) => request.post('/tables/reservations', data)
export const deleteTable = (tableId) => request.delete(`/tables/${tableId}`)
export const deleteReservation = (reservationId) => request.delete(`/tables/reservations/${reservationId}`)
