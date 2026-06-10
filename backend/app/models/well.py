from sqlalchemy import Column, String, Integer, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


class Well(BaseModel):
    __tablename__ = "wells"

    well_code = Column(String(50), unique=True, nullable=False, comment="井编号")
    location = Column(String(255), nullable=False, comment="位置")
    longitude = Column(String(30), comment="经度")
    latitude = Column(String(30), comment="纬度")
    household_count = Column(Integer, nullable=False, comment="供水户数")
    equipment_status = Column(String(20), default="normal", nullable=False, comment="设备状态：normal-正常, faulty-故障, maintenance-维护中")
    photo_url = Column(String(500), comment="巡检照片地址")
    drainage_status = Column(String(20), default="normal", nullable=False, comment="周边排水状态：normal-正常, blocked-堵塞, poor-较差")
    cover_status = Column(String(20), default="normal", nullable=False, comment="井盖状态：normal-正常, damaged-损坏, missing-丢失")
    pump_status = Column(String(20), default="normal", nullable=False, comment="抽水泵状态：normal-正常, faulty-故障, offline-离线")
    hidden_dangers = Column(Text, comment="问题隐患")
    rectification_responsible = Column(String(50), comment="整改负责人")
    last_inspection_date = Column(DateTime, comment="上次巡检日期")
    next_inspection_date = Column(DateTime, comment="下次巡检日期")
    inspection_overdue = Column(Integer, default=0, nullable=False, comment="是否逾期未巡检：0-否, 1-是")

    village_id = Column(Integer, ForeignKey("villages.id"), nullable=False)
    well_type_id = Column(Integer, ForeignKey("well_types.id"), nullable=False)

    village = relationship("Village", back_populates="wells")
    well_type = relationship("WellType", back_populates="wells")
    inspections = relationship("InspectionRecord", back_populates="well", cascade="all, delete-orphan")
    test_items = relationship("WaterTestItem", back_populates="well")
