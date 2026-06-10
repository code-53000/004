from datetime import datetime
from pydantic import BaseModel


class WaterQualityStandardBase(BaseModel):
    indicator_name: str
    indicator_code: str
    unit: str
    limit_value: float
    comparison_type: str = "<="
    category: str
    priority: int = 1


class WaterQualityStandardCreate(WaterQualityStandardBase):
    pass


class WaterQualityStandard(WaterQualityStandardBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
