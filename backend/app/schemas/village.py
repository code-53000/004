from datetime import datetime
from pydantic import BaseModel


class VillageBase(BaseModel):
    name: str
    code: str


class VillageCreate(VillageBase):
    pass


class Village(VillageBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
