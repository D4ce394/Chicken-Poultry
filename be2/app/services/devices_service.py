from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import NoResultFound
from typing import List, Optional
from be2.app.models.devices import Device as DeviceModel
from be2.app.schemas.devices_schemas import DeviceCreate, DeviceUpdate

class DevicesService:
    async def create_device(self, db: AsyncSession, data: DeviceCreate) -> DeviceModel:
        device = DeviceModel(**data.dict())
        db.add(device)
        await db.commit()
        await db.refresh(device)
        return device

    async def get_devices(self, db: AsyncSession) -> List[DeviceModel]:
        result = await db.execute(select(DeviceModel))
        return result.scalars().all()

    async def get_device_by_id(self, db: AsyncSession, device_id: int) -> Optional[DeviceModel]:
        result = await db.execute(select(DeviceModel).where(DeviceModel.device_id == device_id))
        return result.scalar_one_or_none()

    async def update_device(self, db: AsyncSession, device_id: int, data: DeviceUpdate) -> Optional[DeviceModel]:
        device = await self.get_device_by_id(db, device_id)
        if not device:
            return None
        for key, value in data.dict(exclude_unset=True).items():
            setattr(device, key, value)
        await db.commit()
        await db.refresh(device)
        return device

    async def delete_device(self, db: AsyncSession, device_id: int) -> bool:
        device = await self.get_device_by_id(db, device_id)
        if not device:
            return False
        await db.delete(device)
        await db.commit()
        return True

devices_service = DevicesService()