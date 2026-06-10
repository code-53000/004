from sqlalchemy import Column, String, Float, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


class WaterTestItem(BaseModel):
    __tablename__ = "water_test_items"

    measured_value = Column(Float, nullable=False, comment="检测值")
    is_qualified = Column(Integer, nullable=False, comment="是否合格：0-不合格, 1-合格, 2-待判定")
    judgment_basis = Column(String(200), comment="判定依据")

    well_id = Column(Integer, ForeignKey("wells.id"), nullable=False)
    batch_id = Column(Integer, ForeignKey("water_test_batches.id"), nullable=False)
    standard_id = Column(Integer, ForeignKey("water_quality_standards.id"), nullable=False)

    well = relationship("Well", back_populates="test_items")
    batch = relationship("WaterTestBatch", back_populates="test_items")
    standard = relationship("WaterQualityStandard", back_populates="test_items")
