from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from models.auth import Base  # gunakan Base yang sama

class Setting(Base):
    __tablename__ = "settings"

    setting_id = Column(Integer, primary_key=True, autoincrement=True)
    key = Column(String(50), unique=True, nullable=False)
    value = Column(Text, nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now())
