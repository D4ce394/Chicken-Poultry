from typing import List, Optional
from be2.app.schemas.attendance_logs_schemas import AttendanceLogCreate, AttendanceLog, AttendanceLogUpdate

class AttendanceService:
    def __init__(self):
        self.logs = []
        self.counter = 1

    async def create_log(self, data: AttendanceLogCreate) -> AttendanceLog:
        log = AttendanceLog(
            id=self.counter,
            user_id=data.user_id,
            timestamp=data.timestamp,
            status=data.status,
            note=data.note
        )
        self.logs.append(log)
        self.counter += 1
        return log

    async def get_logs(self) -> List[AttendanceLog]:
        return self.logs

    async def get_log_by_id(self, log_id: int) -> Optional[AttendanceLog]:
        for log in self.logs:
            if log.id == log_id:
                return log
        return None

    async def update_log(self, log_id: int, data: AttendanceLogUpdate) -> Optional[AttendanceLog]:
        for idx, log in enumerate(self.logs):
            if log.id == log_id:
                updated_log = log.copy(update=data.dict(exclude_unset=True))
                self.logs[idx] = updated_log
                return updated_log
        return None

    async def delete_log(self, log_id: int) -> bool:
        for idx, log in enumerate(self.logs):
            if log.id == log_id:
                del self.logs[idx]
                return True
        return False

attendance_service = AttendanceService()