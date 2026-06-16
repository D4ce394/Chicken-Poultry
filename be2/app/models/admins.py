from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from models.auth import Base  # pastikan konsisten dengan shared Base yang kamu gunakan

class Admin(Base):
    __tablename__ = "admins"

    admin_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password_hash = Column(Text, nullable=False)
    role = Column(String(20), default="admin")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
