from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from models.auth import Base  # gunakan shared Base

class Device(Base):
    __tablename__ = "devices"

    device_id = Column(Integer, primary_key=True, autoincrement=True)
    device_name = Column(String(100), nullable=False)
    device_token = Column(Text, unique=True)
    location = Column(String(100))
    status = Column(Integer, default=1)
    last_sync = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
