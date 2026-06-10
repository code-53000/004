from typing import Optional
from datetime import date, datetime
from pydantic import BaseModel


class InspectionRecordBase(BaseModel):
    inspection_date: date
    cover_status: str
    pump_status: str
    drainage_status: str
    equipment_status: str
    photo_url: Optional[str] = None
    hidden_dangers: Optional[str] = None
    residual_chlorine: Optional[str] = None
    needs_rectification: int = 0
    rectification_deadline: Optional[date] = None
    well_id: int


class InspectionRecordCreate(InspectionRecordBase):
    pass


class InspectionRecordUpdate(BaseModel):
    cover_status: Optional[str] = None
    pump_status: Optional[str] = None
    drainage_status: Optional[str] = None
    equipment_status: Optional[str] = None
    photo_url: Optional[str] = None
    hidden_dangers: Optional[str] = None
    residual_chlorine: Optional[str] = None
    needs_rectification: Optional[int] = None
    rectification_deadline: Optional[date] = None
    status: Optional[str] = None


class InspectionRecord(InspectionRecordBase):
    id: int
    residual_chlorine_status: Optional[str]
    status: str
    inspector_id: int
    inspector_name: Optional[str]
    well_code: Optional[str]
    well_location: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
