from typing import Optional
from datetime import datetime
from pydantic import BaseModel


class WellBase(BaseModel):
    well_code: str
    location: str
    longitude: Optional[str] = None
    latitude: Optional[str] = None
    household_count: int
    equipment_status: str = "normal"
    photo_url: Optional[str] = None
    drainage_status: str = "normal"
    cover_status: str = "normal"
    pump_status: str = "normal"
    hidden_dangers: Optional[str] = None
    rectification_responsible: Optional[str] = None
    village_id: int
    well_type_id: int


class WellCreate(WellBase):
    pass


class WellUpdate(BaseModel):
    location: Optional[str] = None
    longitude: Optional[str] = None
    latitude: Optional[str] = None
    household_count: Optional[int] = None
    equipment_status: Optional[str] = None
    photo_url: Optional[str] = None
    drainage_status: Optional[str] = None
    cover_status: Optional[str] = None
    pump_status: Optional[str] = None
    hidden_dangers: Optional[str] = None
    rectification_responsible: Optional[str] = None
    village_id: Optional[int] = None
    well_type_id: Optional[int] = None


class WellListResponse(WellBase):
    id: int
    inspection_overdue: int
    last_inspection_date: Optional[datetime]
    next_inspection_date: Optional[datetime]
    village_name: Optional[str]
    well_type_name: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class Well(WellBase):
    id: int
    inspection_overdue: int
    last_inspection_date: Optional[datetime]
    next_inspection_date: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
