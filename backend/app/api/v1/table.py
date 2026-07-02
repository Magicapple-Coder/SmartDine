from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import get_db
from app.core.response import ok
from app.schemas.table import ReservationCreate, ReservationOut, TableCreate, TableOut
from app.services import table as table_service

router = APIRouter(prefix="/tables", tags=["桌台"])


@router.get("")
def list_tables(db: Session = Depends(get_db)):
    tables = table_service.list_tables(db)
    return ok([TableOut.model_validate(t).model_dump() for t in tables])


@router.post("")
def create_table(body: TableCreate, db: Session = Depends(get_db)):
    table = table_service.create_table(db, body)
    return ok(TableOut.model_validate(table).model_dump())


@router.delete("/{table_id}")
def delete_table(table_id: int, db: Session = Depends(get_db)):
    table_service.delete_table(db, table_id)
    return ok(None)


@router.post("/{table_id}/open")
def open_table(table_id: int, order_id: int | None = None, db: Session = Depends(get_db)):
    table = table_service.open_table(db, table_id, order_id)
    return ok(TableOut.model_validate(table).model_dump())


@router.post("/{table_id}/checkout")
def checkout_table(table_id: int, db: Session = Depends(get_db)):
    table = table_service.checkout_table(db, table_id)
    return ok(TableOut.model_validate(table).model_dump())


@router.post("/{table_id}/clean")
def clean_table(table_id: int, db: Session = Depends(get_db)):
    table = table_service.clean_table(db, table_id)
    return ok(TableOut.model_validate(table).model_dump())


@router.post("/reservations")
def create_reservation(body: ReservationCreate, db: Session = Depends(get_db)):
    """顾客/客服智能体创建预订，写入对应桌台（需求文档 3.4、5.3）"""
    reservation = table_service.create_reservation(db, body)
    return ok(ReservationOut.model_validate(reservation).model_dump())


@router.get("/reservations")
def list_reservations(table_id: int | None = None, db: Session = Depends(get_db)):
    reservations = table_service.list_reservations(db, table_id)
    return ok([ReservationOut.model_validate(r).model_dump() for r in reservations])


@router.delete("/reservations/{reservation_id}")
def delete_reservation(reservation_id: int, db: Session = Depends(get_db)):
    table_service.delete_reservation(db, reservation_id)
    return ok(None)
