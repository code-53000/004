from sqlalchemy import Column, String, Integer
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


class WellType(BaseModel):
    __tablename__ = "well_types"

    name = Column(String(50), unique=True, nullable=False, comment="井类型名称")
    inspection_cycle_days = Column(Integer, default=30, nullable=False, comment="巡检周期（天）")

    wells = relationship("Well", back_populates="well_type")
