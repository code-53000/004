from sqlalchemy import Column, String, Integer, Text, ForeignKey, Date
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


class WaterTestBatch(BaseModel):
    __tablename__ = "water_test_batches"

    batch_no = Column(String(50), unique=True, nullable=False, comment="送检批次号")
    test_date = Column(Date, nullable=False, comment="检测日期")
    sample_date = Column(Date, nullable=False, comment="采样日期")
    lab_name = Column(String(100), comment="检测机构")
    report_url = Column(String(500), comment="检测报告地址")
    overall_result = Column(String(20), default="pending", nullable=False, comment="总体结果：pending-待出, qualified-合格, unqualified-不合格")
    remark = Column(Text, comment="备注")

    tester_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    tester = relationship("User", foreign_keys=[tester_id], back_populates="test_batches")
    test_items = relationship("WaterTestItem", back_populates="batch", cascade="all, delete-orphan")
