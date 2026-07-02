from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.repositories import table as table_repo
from app.schemas.table import ReservationCreate, TableCreate


def list_tables(db: Session):
    return table_repo.list_tables(db)


def create_table(db: Session, body: TableCreate):
    return table_repo.create_table(db, body.no, body.seats)


def _get_or_404(db: Session, table_id: int):
    table = table_repo.get_table(db, table_id)
    if table is None:
        raise HTTPException(status_code=404, detail="桌台不存在")
    return table


def open_table(db: Session, table_id: int, order_id: int | None = None):
    """开台：空闲/已预订 -> 就餐中（需求文档 3.4 状态操作）"""
    table = _get_or_404(db, table_id)
    if table.status not in (0, 2):
        raise HTTPException(status_code=400, detail="桌台当前状态不可开台")
    return table_repo.update_status(db, table, status=1, order_id=order_id)


def checkout_table(db: Session, table_id: int):
    """结账：就餐中 -> 待清理"""
    table = _get_or_404(db, table_id)
    if table.status != 1:
        raise HTTPException(status_code=400, detail="桌台未在就餐中，无法结账")
    return table_repo.update_status(db, table, status=3, order_id=None)


def clean_table(db: Session, table_id: int):
    """清理完成：待清理 -> 空闲"""
    table = _get_or_404(db, table_id)
    if table.status != 3:
        raise HTTPException(status_code=400, detail="桌台未处于待清理状态")
    return table_repo.update_status(db, table, status=0, order_id=None)


def create_reservation(db: Session, body: ReservationCreate):
    table = _get_or_404(db, body.table_id)
    reservation = table_repo.create_reservation(
        db, body.table_id, body.member_id, body.contact_name, body.contact_phone, body.reserve_time, body.guests
    )
    table_repo.update_status(db, table, status=2, order_id=table.current_order_id)
    return reservation


def list_reservations(db: Session, table_id: int | None = None):
    return table_repo.list_reservations(db, table_id)


def _get_reservation_or_404(db: Session, reservation_id: int):
    reservation = table_repo.get_reservation(db, reservation_id)
    if reservation is None:
        raise HTTPException(status_code=404, detail="预订不存在")
    return reservation


def delete_reservation(db: Session, reservation_id: int):
    reservation = _get_reservation_or_404(db, reservation_id)
    table_repo.delete_reservation(db, reservation)


def delete_table(db: Session, table_id: int):
    table = _get_or_404(db, table_id)
    if table.status == 1:
        raise HTTPException(status_code=400, detail="桌台就餐中，无法删除")
    table_repo.delete_reservations_by_table(db, table_id)
    table_repo.delete_table(db, table)
