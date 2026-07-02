import request from './request'

export const listIngredients = (lowStockOnly) => request.get('/ingredients', { params: { low_stock_only: lowStockOnly } })
export const createIngredient = (data) => request.post('/ingredients', data)
export const recordStockLog = (data) => request.post('/stock-logs', data)
export const listStockLogs = (ingredientId) => request.get('/stock-logs', { params: { ingredient_id: ingredientId } })
export const listSuppliers = () => request.get('/suppliers')
export const createSupplier = (data) => request.post('/suppliers', data)
export const deleteIngredient = (ingredientId) => request.delete(`/ingredients/${ingredientId}`)
export const deleteSupplier = (supplierId) => request.delete(`/suppliers/${supplierId}`)
