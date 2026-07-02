import request from './request'

export const listStaff = () => request.get('/staff')
export const createStaff = (data) => request.post('/staff', data)
export const updateStaff = (staffId, data) => request.put(`/staff/${staffId}`, data)
export const listSchedules = (staffId) => request.get('/staff/schedules', { params: { staff_id: staffId } })
export const createSchedule = (data) => request.post('/staff/schedules', data)
export const deleteStaff = (staffId) => request.delete(`/staff/${staffId}`)
