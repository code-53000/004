from sqlalchemy import Column, String
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


class Village(BaseModel):
    __tablename__ = "villages"

    name = Column(String(100), unique=True, nullable=False, comment="村组名称")
    code = Column(String(50), unique=True, nullable=False, comment="村组编码")

    wells = relationship("Well", back_populates="village")
