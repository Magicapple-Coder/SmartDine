from datetime import datetime

from pydantic import BaseModel, ConfigDict


class TableOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    table_id: int
    no: str
    seats: int
    status: int
    current_order_id: int | None = None


class TableCreate(BaseModel):
    no: str
    seats: int


class ReservationCreate(BaseModel):
    table_id: int
    member_id: int | None = None
    contact_name: str | None = None
    contact_phone: str | None = None
    reserve_time: datetime
    guests: int = 1


class ReservationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    reservation_id: int
    table_id: int
    contact_name: str | None = None
    contact_phone: str | None = None
    reserve_time: datetime
    guests: int
    status: int
