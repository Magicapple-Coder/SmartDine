from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.repositories import marketing as marketing_repo
from app.schemas.marketing import CampaignCreate, CouponCreate


def list_campaigns(db: Session):
    return marketing_repo.list_campaigns(db)


def create_campaign(db: Session, body: CampaignCreate):
    return marketing_repo.create_campaign(db, **body.model_dump())


def _get_campaign_or_404(db: Session, campaign_id: int):
    campaign = marketing_repo.get_campaign(db, campaign_id)
    if campaign is None:
        raise HTTPException(status_code=404, detail="活动不存在")
    return campaign


def delete_campaign(db: Session, campaign_id: int):
    """删除活动连同其名下优惠券，券的领取/核销历史一并清除"""
    campaign = _get_campaign_or_404(db, campaign_id)
    marketing_repo.delete_coupons_by_campaign(db, campaign_id)
    marketing_repo.delete_campaign(db, campaign)


def _get_coupon_or_404(db: Session, coupon_id: int):
    coupon = marketing_repo.get_coupon(db, coupon_id)
    if coupon is None:
        raise HTTPException(status_code=404, detail="优惠券不存在")
    return coupon


def delete_coupon(db: Session, coupon_id: int):
    coupon = _get_coupon_or_404(db, coupon_id)
    marketing_repo.delete_coupon(db, coupon)


def list_coupons(db: Session, campaign_id: int | None = None):
    return marketing_repo.list_coupons(db, campaign_id)


def create_coupon(db: Session, body: CouponCreate):
    campaign = marketing_repo.get_campaign(db, body.campaign_id)
    if campaign is None:
        raise HTTPException(status_code=404, detail="所属活动不存在")
    return marketing_repo.create_coupon(db, **body.model_dump())


def claim_coupon(db: Session, coupon_id: int):
    """顾客领取优惠券（需求文档 3.5、4.6）"""
    coupon = _get_coupon_or_404(db, coupon_id)
    return marketing_repo.claim_coupon(db, coupon)


def redeem_coupon(db: Session, coupon_id: int):
    """下单结账时核销优惠券，同步累计活动销量（需求文档 3.5）"""
    coupon = _get_coupon_or_404(db, coupon_id)
    if coupon.redeemed >= coupon.claimed:
        raise HTTPException(status_code=400, detail="优惠券未领取或已核销")
    coupon = marketing_repo.redeem_coupon(db, coupon)
    campaign = marketing_repo.get_campaign(db, coupon.campaign_id)
    if campaign is not None:
        marketing_repo.increment_sold(db, campaign)
    return coupon
