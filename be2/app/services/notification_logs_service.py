# notification_logs_service

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List, Optional
from be2.app.models.notification_logs import NotificationLog as NotificationLogModel
from be2.app.schemas.notification_logs_schemas import (
    NotificationLogCreate,
    NotificationLogUpdate,
)

class NotificationLogsService:
    async def create_log(self, db: AsyncSession, data: NotificationLogCreate) -> NotificationLogModel:
        log = NotificationLogModel(**data.dict())
        db.add(log)
        await db.commit()
        await db.refresh(log)
        return log

    async def get_logs(self, db: AsyncSession) -> List[NotificationLogModel]:
        result = await db.execute(select(NotificationLogModel))
        return result.scalars().all()

    async def get_log_by_id(self, db: AsyncSession, log_id: int) -> Optional[NotificationLogModel]:
        result = await db.execute(
            select(NotificationLogModel).where(NotificationLogModel.id == log_id)
        )
        return result.scalar_one_or_none()

    async def update_log(self, db: AsyncSession, log_id: int, data: NotificationLogUpdate) -> Optional[NotificationLogModel]:
        log = await self.get_log_by_id(db, log_id)
        if not log:
            return None
        for key, value in data.dict(exclude_unset=True).items():
            setattr(log, key, value)
        await db.commit()
        await db.refresh(log)
        return log

    async def delete_log(self, db: AsyncSession, log_id: int) -> bool:
        log = await self.get_log_by_id(db, log_id)
        if not log:
            return False
        await db.delete(log)
        await db.commit()
        return