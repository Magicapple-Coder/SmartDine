from sqlalchemy.orm import Session

from app.core.tenant import current_merchant_id
from app.models.marketing import Campaign, Coupon


def _mid() -> int:
    return current_merchant_id.get() or 1


def list_campaigns(db: Session):
    mid = _mid()
    return db.query(Campaign).filter(Campaign.merchant_id == mid).all()


def get_campaign(db: Session, campaign_id: int) -> Campaign | None:
    mid = _mid()
    return db.query(Campaign).filter(Campaign.campaign_id == campaign_id, Campaign.merchant_id == mid).first()


def create_campaign(db: Session, **kwargs) -> Campaign:
    kwargs.setdefault("merchant_id", _mid())
    campaign = Campaign(**kwargs)
    db.add(campaign)
    db.commit()
    db.refresh(campaign)
    return campaign


def list_coupons(db: Session, campaign_id: int | None = None):
    mid = _mid()
    query = db.query(Coupon).filter(Coupon.merchant_id == mid)
    if campaign_id is not None:
        query = query.filter(Coupon.campaign_id == campaign_id)
    return query.all()


def get_coupon(db: Session, coupon_id: int) -> Coupon | None:
    mid = _mid()
    return db.query(Coupon).filter(Coupon.coupon_id == coupon_id, Coupon.merchant_id == mid).first()


def create_coupon(db: Session, **kwargs) -> Coupon:
    kwargs.setdefault("merchant_id", _mid())
    coupon = Coupon(**kwargs)
    db.add(coupon)
    db.commit()
    db.refresh(coupon)
    return coupon


def claim_coupon(db: Session, coupon: Coupon) -> Coupon:
    coupon.claimed = coupon.claimed + 1
    db.commit()
    db.refresh(coupon)
    return coupon


def redeem_coupon(db: Session, coupon: Coupon) -> Coupon:
    coupon.redeemed = coupon.redeemed + 1
    db.commit()
    db.refresh(coupon)
    return coupon


def increment_sold(db: Session, campaign: Campaign) -> Campaign:
    campaign.sold = campaign.sold + 1
    db.commit()
    db.refresh(campaign)
    return campaign


def delete_coupon(db: Session, coupon: Coupon) -> None:
    db.delete(coupon)
    db.commit()


def delete_coupons_by_campaign(db: Session, campaign_id: int) -> None:
    mid = _mid()
    db.query(Coupon).filter(Coupon.campaign_id == campaign_id, Coupon.merchant_id == mid).delete()
    db.commit()


def delete_campaign(db: Session, campaign: Campaign) -> None:
    db.delete(campaign)
    db.commit()
