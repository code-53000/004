from sqlalchemy import Column, String, Boolean
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


class User(BaseModel):
    __tablename__ = "users"

    username = Column(String(50), unique=True, nullable=False, comment="用户名")
    password_hash = Column(String(255), nullable=False, comment="密码哈希")
    full_name = Column(String(50), nullable=False, comment="真实姓名")
    role = Column(String(20), nullable=False, comment="角色：inspector-巡检, rectifier-整改, tester-送检, supervisor-监管")
    phone = Column(String(20), comment="联系电话")
    is_active = Column(Boolean, default=True, nullable=False)

    inspections = relationship("InspectionRecord", foreign_keys="InspectionRecord.inspector_id", back_populates="inspector")
    rectifications = relationship("RectificationRecord", foreign_keys="RectificationRecord.rectifier_id", back_populates="rectifier")
    test_batches = relationship("WaterTestBatch", foreign_keys="WaterTestBatch.tester_id", back_populates="tester")
