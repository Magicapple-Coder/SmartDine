import request from './request'

export const listCampaigns = () => request.get('/campaigns')
export const createCampaign = (data) => request.post('/campaigns', data)
export const listCoupons = (campaignId) => request.get('/coupons', { params: { campaign_id: campaignId } })
export const createCoupon = (data) => request.post('/coupons', data)
export const deleteCampaign = (campaignId) => request.delete(`/campaigns/${campaignId}`)
export const deleteCoupon = (couponId) => request.delete(`/coupons/${couponId}`)
