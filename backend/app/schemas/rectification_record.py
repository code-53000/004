from typing import Optional
from datetime import date, datetime
from pydantic import BaseModel


class RectificationRecordBase(BaseModel):
    measures: str
    result: Optional[str] = None
    photo_url: Optional[str] = None
    inspection_id: int


class RectificationRecordCreate(RectificationRecordBase):
    pass


class RectificationRecordUpdate(BaseModel):
    rectification_date: Optional[date] = None
    measures: Optional[str] = None
    result: Optional[str] = None
    photo_url: Optional[str] = None
    status: Optional[str] = None
    verification_remark: Optional[str] = None


class RectificationRecord(RectificationRecordBase):
    id: int
    rectification_date: Optional[date]
    status: str
    verification_remark: Optional[str]
    rectifier_id: int
    rectifier_name: Optional[str]
    inspection_date: Optional[date]
    well_code: Optional[str]
    well_location: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
