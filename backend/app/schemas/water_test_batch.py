from typing import Optional, List
from datetime import date, datetime
from pydantic import BaseModel
from app.schemas.water_test_item import WaterTestItem


class WaterTestBatchBase(BaseModel):
    batch_no: str
    test_date: date
    sample_date: date
    lab_name: Optional[str] = None
    report_url: Optional[str] = None
    remark: Optional[str] = None


class WaterTestBatchCreate(WaterTestBatchBase):
    pass


class WaterTestBatch(WaterTestBatchBase):
    id: int
    overall_result: str
    tester_id: int
    tester_name: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class WaterTestBatchWithItems(WaterTestBatch):
    test_items: List[WaterTestItem] = []

    class Config:
        orm_mode = True
