from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from models.auth import Base
from sqlalchemy import Boolean

class NotificationLog(Base):
    __tablename__ = "notification_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False)
    email_sent = Column(Boolean, default=False)
    message = Column(Text, nullable=True)