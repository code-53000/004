from datetime import datetime
from pydantic import BaseModel


class WellTypeBase(BaseModel):
    name: str
    inspection_cycle_days: int = 30


class WellTypeCreate(WellTypeBase):
    pass


class WellType(WellTypeBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
