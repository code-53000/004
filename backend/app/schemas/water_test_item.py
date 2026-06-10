from typing import Optional
from datetime import datetime
from pydantic import BaseModel


class WaterTestItemBase(BaseModel):
    measured_value: float
    well_id: int
    standard_id: int


class WaterTestItemCreate(WaterTestItemBase):
    pass


class WaterTestItem(WaterTestItemBase):
    id: int
    is_qualified: int
    judgment_basis: Optional[str]
    batch_id: int
    indicator_name: Optional[str]
    indicator_code: Optional[str]
    unit: Optional[str]
    limit_value: Optional[float]
    comparison_type: Optional[str]
    well_code: Optional[str]
    well_location: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
