from sqlalchemy import Column, String, Integer, Text, ForeignKey, Date
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


class RectificationRecord(BaseModel):
    __tablename__ = "rectification_records"

    rectification_date = Column(Date, comment="整改完成日期")
    measures = Column(Text, nullable=False, comment="整改措施")
    result = Column(Text, comment="整改结果")
    photo_url = Column(String(500), comment="整改后照片地址")
    status = Column(String(20), default="pending", nullable=False, comment="状态：pending-待整改, in_progress-整改中, completed-已完成, verified-已验收")
    verification_remark = Column(Text, comment="验收备注")

    inspection_id = Column(Integer, ForeignKey("inspection_records.id"), nullable=False)
    rectifier_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    inspection = relationship("InspectionRecord", back_populates="rectifications")
    rectifier = relationship("User", foreign_keys=[rectifier_id], back_populates="rectifications")
