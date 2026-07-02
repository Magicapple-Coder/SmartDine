from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.tenant import current_merchant_id
from app.models.table import DiningTable, Reservation


def _mid() -> int:
    return current_merchant_id.get() or 1


def list_tables(db: Session) -> list[DiningTable]:
    mid = _mid()
    return list(db.scalars(select(DiningTable).where(DiningTable.merchant_id == mid).order_by(DiningTable.no)))


def get_table(db: Session, table_id: int) -> DiningTable | None:
    mid = _mid()
    return db.query(DiningTable).filter(DiningTable.table_id == table_id, DiningTable.merchant_id == mid).first()


def create_table(db: Session, no: str, seats: int) -> DiningTable:
    table = DiningTable(no=no, seats=seats, status=0, merchant_id=_mid())
    db.add(table)
    db.commit()
    db.refresh(table)
    return table


def update_status(db: Session, table: DiningTable, status: int, order_id: int | None = None) -> DiningTable:
    table.status = status
    table.current_order_id = order_id
    db.commit()
    db.refresh(table)
    return table


def create_reservation(
    db: Session,
    table_id: int,
    member_id: int | None,
    contact_name: str | None,
    contact_phone: str | None,
    reserve_time: datetime,
    guests: int,
) -> Reservation:
    reservation = Reservation(
        merchant_id=_mid(),
        table_id=table_id,
        member_id=member_id,
        contact_name=contact_name,
        contact_phone=contact_phone,
        reserve_time=reserve_time,
        guests=guests,
        status=0,
    )
    db.add(reservation)
    db.commit()
    db.refresh(reservation)
    return reservation


def list_reservations(db: Session, table_id: int | None = None) -> list[Reservation]:
    mid = _mid()
    stmt = select(Reservation).where(Reservation.merchant_id == mid)
    if table_id is not None:
        stmt = stmt.where(Reservation.table_id == table_id)
    return list(db.scalars(stmt.order_by(Reservation.reserve_time)))


def get_reservation(db: Session, reservation_id: int) -> Reservation | None:
    mid = _mid()
    return db.query(Reservation).filter(
        Reservation.reservation_id == reservation_id, Reservation.merchant_id == mid
    ).first()


def delete_reservation(db: Session, reservation: Reservation) -> None:
    db.delete(reservation)
    db.commit()


def delete_reservations_by_table(db: Session, table_id: int) -> None:
    mid = _mid()
    db.query(Reservation).filter(Reservation.table_id == table_id, Reservation.merchant_id == mid).delete()
    db.commit()


def delete_table(db: Session, table: DiningTable) -> None:
    db.delete(table)
    db.commit()
