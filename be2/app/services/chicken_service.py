"""
Chicken Counting Service
Reads and processes chicken counting data from Firebase Realtime Database.
"""
import logging
from datetime import date as date_type
from typing import Optional
from app.services.firebase_service import firebase_service

logger = logging.getLogger(__name__)


def _parse_sessions(raw: dict, date_str: str) -> list[dict]:
    """Convert raw Firebase session dict into a sorted list of session dicts."""
    sessions = []
    for session_id, data in raw.items():
        sessions.append({
            "session_id": session_id,
            "date": date_str,
            "chicken_total": data.get("chicken_total", 0),
            "start_time": data.get("start_time"),
            "stop_time": data.get("stop_time"),
            "last_update": data.get("last_update"),
            "status": data.get("status"),
        })
    # Sort sessions by start_time descending (latest first)
    sessions.sort(key=lambda s: s.get("start_time") or "", reverse=True)
    return sessions


class ChickenService:
    """Business logic for chicken counting data"""

    def get_sessions_by_date(self, target_date: str) -> list[dict]:
        """
        Return all counting sessions for a specific date.

        Args:
            target_date: "YYYY-MM-DD"
        """
        if not firebase_service.is_ready:
            logger.warning("Firebase not ready — returning empty list.")
            return []

        try:
            raw = firebase_service.get_chicken_history(date=target_date)
            return _parse_sessions(raw, target_date)
        except Exception as e:
            logger.error(f"Error fetching sessions for {target_date}: {e}")
            return []

    def get_all_sessions(self) -> list[dict]:
        """Return all sessions across all dates, sorted by date and start_time descending."""
        if not firebase_service.is_ready:
            logger.warning("Firebase not ready — returning empty list.")
            return []

        try:
            raw_all = firebase_service.get_chicken_history()
            all_sessions = []
            for date_str, date_data in raw_all.items():
                if isinstance(date_data, dict):
                    all_sessions.extend(_parse_sessions(date_data, date_str))
            all_sessions.sort(
                key=lambda s: (s.get("date") or "", s.get("start_time") or ""),
                reverse=True,
            )
            return all_sessions
        except Exception as e:
            logger.error(f"Error fetching all sessions: {e}")
            return []

    def get_latest_count(self, target_date: Optional[str] = None) -> dict:
        """
        Return the latest session's chicken count.

        Args:
            target_date: "YYYY-MM-DD". Defaults to today.
        """
        date_str = target_date or str(date_type.today())

        if not firebase_service.is_ready:
            return {"date": date_str, "chicken_total": 0, "status": "Firebase not connected"}

        try:
            session = firebase_service.get_latest_session(date_str)
            if not session:
                return {"date": date_str, "chicken_total": 0, "status": "No data"}
            return {
                "date": date_str,
                "session_id": session.get("session_id"),
                "chicken_total": session.get("chicken_total", 0),
                "last_update": session.get("last_update"),
                "start_time": session.get("start_time"),
                "stop_time": session.get("stop_time"),
                "status": session.get("status"),
            }
        except Exception as e:
            logger.error(f"Error fetching latest count: {e}")
            return {"date": date_str, "chicken_total": 0, "status": f"Error: {e}"}

    _EXCLUDED_STATUSES = {"error", "dibatalkan"}

    def get_monthly_summary(self, year: Optional[int] = None) -> list[dict]:
        """Group daily summaries into monthly totals."""
        daily = self.get_summary_by_date()
        from collections import defaultdict
        monthly: dict = defaultdict(lambda: {"session_count": 0, "total_chickens": 0})
        _months = ["", "Januari", "Februari", "Maret", "April", "Mei", "Juni",
                   "Juli", "Agustus", "September", "Oktober", "November", "Desember"]
        for d in daily:
            try:
                y, m, _ = d["date"].split("-")
                if year and int(y) != year:
                    continue
                key = f"{y}-{m.zfill(2)}"
                monthly[key]["session_count"] += d["session_count"]
                monthly[key]["total_chickens"] += d["total_chickens"]
            except Exception:
                continue
        result = []
        for key in sorted(monthly.keys(), reverse=True):
            y, m = key.split("-")
            result.append({
                "year": int(y), "month": int(m),
                "month_name": _months[int(m)],
                "period": f"{_months[int(m)]} {y}",
                "session_count": monthly[key]["session_count"],
                "total_chickens": monthly[key]["total_chickens"],
            })
        return result

    def get_yearly_summary(self) -> list[dict]:
        """Group daily summaries into yearly totals."""
        daily = self.get_summary_by_date()
        from collections import defaultdict
        yearly: dict = defaultdict(lambda: {"session_count": 0, "total_chickens": 0})
        for d in daily:
            try:
                y = d["date"].split("-")[0]
                yearly[y]["session_count"] += d["session_count"]
                yearly[y]["total_chickens"] += d["total_chickens"]
            except Exception:
                continue
        return [
            {"year": int(y), "session_count": yearly[y]["session_count"], "total_chickens": yearly[y]["total_chickens"]}
            for y in sorted(yearly.keys(), reverse=True)
        ]

    def get_summary_by_date(self) -> list[dict]:
        """
        Return daily summary: total chickens counted per date across all valid sessions.
        Sessions with status 'error' or 'dibatalkan' are excluded from the total.
        """
        if not firebase_service.is_ready:
            return []

        try:
            raw_all = firebase_service.get_chicken_history()
            summaries = []
            for date_str, date_data in raw_all.items():
                if not isinstance(date_data, dict):
                    continue
                all_sessions = _parse_sessions(date_data, date_str)
                valid = [
                    s for s in all_sessions
                    if (s.get("status") or "").lower() not in self._EXCLUDED_STATUSES
                ]
                total = sum(s.get("chicken_total", 0) for s in valid)
                summaries.append({
                    "date": date_str,
                    "session_count": len(all_sessions),
                    "total_chickens": total,
                })
            summaries.sort(key=lambda x: x["date"], reverse=True)
            return summaries
        except Exception as e:
            logger.error(f"Error building daily summary: {e}")
            return []

    def cancel_session(self, date: str, session_id: str) -> bool:
        """Mark a session as dibatalkan in Firebase."""
        return firebase_service.update_session_status(date, session_id, "dibatalkan")


# Singleton instance
chicken_service = ChickenService()
