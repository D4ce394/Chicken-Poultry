from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.sql import func
from models.auth import Base  # gunakan shared Base yang sama

class AttendanceLog(Base):
    __tablename__ = "attendance_logs"

    log_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False)
    device_id = Column(Integer, nullable=False)
    check_type = Column(String(50), nullable=False)  # contoh: "check-in", "check-out"
    confidence = Column(Float, nullable=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
