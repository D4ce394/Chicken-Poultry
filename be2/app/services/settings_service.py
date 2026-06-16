# settings_service

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List, Optional
from be2.app.models.settings import Setting as SettingModel
from be2.app.schemas.settings_schemas import SettingCreate, SettingUpdate

class SettingsService:
    async def create_setting(self, db: AsyncSession, data: SettingCreate) -> SettingModel:
        setting = SettingModel(**data.dict())
        db.add(setting)
        await db.commit()
        await db.refresh(setting)
        return setting

    async def get_settings(self, db: AsyncSession) -> List[SettingModel]:
        result = await db.execute(select(SettingModel))
        return result.scalars().all()

    async def get_setting_by_id(self, db: AsyncSession, setting_id: int) -> Optional[SettingModel]:
        result = await db.execute(
            select(SettingModel).where(SettingModel.setting_id == setting_id)
        )
        return result.scalar_one_or_none()

    async def update_setting(self, db: AsyncSession, setting_id: int, data: SettingUpdate) -> Optional[SettingModel]:
        setting = await self.get_setting_by_id(db, setting_id)
        if not setting:
            return None
        for key, value in data.dict(exclude_unset=True).items():
            setattr(setting, key, value)
        await db.commit()
        await db.refresh(setting)
        return setting

    async def delete_setting(self, db: AsyncSession, setting_id: int) -> bool:
        setting = await self.get_setting_by_id(db, setting_id)
        if not setting:
            return False
        await db.delete(setting)
        await db.commit()
        return True

settings_service = SettingsService()