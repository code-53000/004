from sqlalchemy import Column, String, Integer, Text, ForeignKey, DateTime, Date
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


class InspectionRecord(BaseModel):
    __tablename__ = "inspection_records"

    inspection_date = Column(Date, nullable=False, comment="巡检日期")
    cover_status = Column(String(20), nullable=False, comment="井盖状态")
    pump_status = Column(String(20), nullable=False, comment="抽水泵状态")
    drainage_status = Column(String(20), nullable=False, comment="周边排水状态")
    equipment_status = Column(String(20), nullable=False, comment="设备整体状态")
    photo_url = Column(String(500), comment="现场照片地址")
    hidden_dangers = Column(Text, comment="发现的问题隐患")
    residual_chlorine = Column(String(20), comment="余氯检测值")
    residual_chlorine_status = Column(String(20), comment="余氯状态：normal-正常, low-偏低, high-偏高")
    needs_rectification = Column(Integer, default=0, nullable=False, comment="是否需要整改：0-否, 1-是")
    rectification_deadline = Column(Date, comment="整改期限")
    status = Column(String(20), default="completed", nullable=False, comment="状态：completed-已完成, rectifying-整改中, rectified-已整改")

    well_id = Column(Integer, ForeignKey("wells.id"), nullable=False)
    inspector_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    well = relationship("Well", back_populates="inspections")
    inspector = relationship("User", foreign_keys=[inspector_id], back_populates="inspections")
    rectifications = relationship("RectificationRecord", back_populates="inspection", cascade="all, delete-orphan")
