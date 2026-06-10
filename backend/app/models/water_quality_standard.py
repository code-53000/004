from sqlalchemy import Column, String, Float, Integer
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


class WaterQualityStandard(BaseModel):
    __tablename__ = "water_quality_standards"

    indicator_name = Column(String(100), unique=True, nullable=False, comment="指标名称")
    indicator_code = Column(String(50), unique=True, nullable=False, comment="指标编码")
    unit = Column(String(20), nullable=False, comment="单位")
    limit_value = Column(Float, nullable=False, comment="限值")
    comparison_type = Column(String(20), default="<=", nullable=False, comment="比较类型：<=, >=, <, >, ==")
    category = Column(String(50), nullable=False, comment="指标分类：微生物、毒理、感官、一般化学、放射性")
    priority = Column(Integer, default=1, nullable=False, comment="显示优先级")

    test_items = relationship("WaterTestItem", back_populates="standard")
