from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import get_db
from app.core.response import ok
from app.schemas.marketing import CampaignCreate, CampaignOut, CouponCreate, CouponOut
from app.services import marketing as marketing_service

router = APIRouter(tags=["营销"])


@router.get("/campaigns")
def list_campaigns(db: Session = Depends(get_db)):
    campaigns = marketing_service.list_campaigns(db)
    return ok([CampaignOut.model_validate(c).model_dump() for c in campaigns])


@router.post("/campaigns")
def create_campaign(body: CampaignCreate, db: Session = Depends(get_db)):
    campaign = marketing_service.create_campaign(db, body)
    return ok(CampaignOut.model_validate(campaign).model_dump())


@router.delete("/campaigns/{campaign_id}")
def delete_campaign(campaign_id: int, db: Session = Depends(get_db)):
    marketing_service.delete_campaign(db, campaign_id)
    return ok(None)


@router.get("/coupons")
def list_coupons(campaign_id: int | None = None, db: Session = Depends(get_db)):
    coupons = marketing_service.list_coupons(db, campaign_id)
    return ok([CouponOut.model_validate(c).model_dump() for c in coupons])


@router.post("/coupons")
def create_coupon(body: CouponCreate, db: Session = Depends(get_db)):
    coupon = marketing_service.create_coupon(db, body)
    return ok(CouponOut.model_validate(coupon).model_dump())


@router.delete("/coupons/{coupon_id}")
def delete_coupon(coupon_id: int, db: Session = Depends(get_db)):
    marketing_service.delete_coupon(db, coupon_id)
    return ok(None)


@router.post("/coupons/{coupon_id}/claim")
def claim_coupon(coupon_id: int, db: Session = Depends(get_db)):
    coupon = marketing_service.claim_coupon(db, coupon_id)
    return ok(CouponOut.model_validate(coupon).model_dump())


@router.post("/coupons/{coupon_id}/redeem")
def redeem_coupon(coupon_id: int, db: Session = Depends(get_db)):
    coupon = marketing_service.redeem_coupon(db, coupon_id)
    return ok(CouponOut.model_validate(coupon).model_dump())
