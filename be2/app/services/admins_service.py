from typing import List, Optional
from be2.app.schemas.admins_schemas import AdminCreate, Admin, AdminUpdate
from datetime import datetime

class AdminsService:
    def __init__(self):
        self.admins = []
        self.counter = 1

    async def create_admin(self, data: AdminCreate) -> Admin:
        admin = Admin(
            id=self.counter,
            username=data.username,
            email=data.email,
            password=data.password,  # In production, hash the password!
            created_at=datetime.now(),
            is_active=True
        )
        self.admins.append(admin)
        self.counter += 1
        return admin

    async def get_admins(self) -> List[Admin]:
        return self.admins

    async def get_admin_by_id(self, admin_id: int) -> Optional[Admin]:
        for admin in self.admins:
            if admin.id == admin_id:
                return admin
        return None

    async def update_admin(self, admin_id: int, data: AdminUpdate) -> Optional[Admin]:
        for idx, admin in enumerate(self.admins):
            if admin.id == admin_id:
                updated_admin = admin.copy(update=data.dict(exclude_unset=True))
                self.admins[idx] = updated_admin
                return updated_admin
        return None

    async def delete_admin(self, admin_id: int) -> bool:
        for idx, admin in enumerate(self.admins):
            if admin.id == admin_id:
                del self.admins[idx]
                return True
        return False

admins_service = AdminsService()