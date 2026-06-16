"""
Firebase Service
Handles connection to Firebase Realtime Database for chicken counting data.
"""
import os
import logging
from typing import Optional
import firebase_admin
from firebase_admin import credentials, db

logger = logging.getLogger(__name__)

# Path to Firebase service account key
_SERVICE_ACCOUNT_PATH = os.getenv(
    "FIREBASE_SERVICE_ACCOUNT_PATH",
    os.path.join(os.path.dirname(__file__), "..", "..", "rfid-de0fd-firebase-adminsdk-fbsvc-22ca2974df.json")
)

# Firebase Realtime Database URL
_DATABASE_URL = os.getenv(
    "FIREBASE_DATABASE_URL",
    "https://rfid-de0fd-default-rtdb.firebaseio.com"
)


class FirebaseService:
    """Singleton Firebase connection manager"""

    _initialized: bool = False

    def __init__(self):
        self._initialize()

    def _initialize(self):
        if FirebaseService._initialized:
            return

        if not _DATABASE_URL:
            logger.warning(
                "FIREBASE_DATABASE_URL is not set. Firebase features will not work."
            )
            return

        if not os.path.exists(_SERVICE_ACCOUNT_PATH):
            logger.warning(
                f"Firebase service account key not found at: {_SERVICE_ACCOUNT_PATH}. "
                "Firebase features will not work."
            )
            return

        try:
            cred = credentials.Certificate(_SERVICE_ACCOUNT_PATH)
            firebase_admin.initialize_app(cred, {"databaseURL": _DATABASE_URL})
            FirebaseService._initialized = True
            logger.info("Firebase initialized successfully.")
        except Exception as e:
            logger.error(f"Failed to initialize Firebase: {e}")

    @property
    def is_ready(self) -> bool:
        return FirebaseService._initialized

    def get_ref(self, path: str):
        """Return a Firebase database reference for the given path."""
        if not self.is_ready:
            raise RuntimeError(
                "Firebase is not initialized. Check FIREBASE_DATABASE_URL and "
                "firebase-service-account.json placement."
            )
        return db.reference(path)

    def get_chicken_history(self, date: Optional[str] = None) -> dict:
        """
        Read chicken counting history from Firebase.

        Structure:
          chicken_counter/history/{date}/{session_id}/
            chicken_total, last_update, start_time, status, stop_time

        Args:
            date: target date string "YYYY-MM-DD". If None, reads all dates.

        Returns:
            Raw dict from Firebase.
        """
        path = "chicken_counter/history"
        if date:
            path = f"{path}/{date}"

        ref = self.get_ref(path)
        data = ref.get()
        return data or {}

    def update_session_status(self, date: str, session_id: str, new_status: str) -> bool:
        """Update the status field of a specific session in Firebase."""
        try:
            ref = self.get_ref(f"chicken_counter/history/{date}/{session_id}/status")
            ref.set(new_status)
            return True
        except Exception as e:
            logger.error(f"Error updating session {session_id} status: {e}")
            return False

    def get_latest_session(self, date: str) -> Optional[dict]:
        """
        Return the most recent session for a given date based on start_time.

        Args:
            date: "YYYY-MM-DD"

        Returns:
            dict with session data including session_id, or None if no data.
        """
        history = self.get_chicken_history(date)
        if not history:
            return None

        latest = None
        latest_time = ""
        for session_id, session_data in history.items():
            start_time = session_data.get("start_time", "")
            if start_time > latest_time:
                latest_time = start_time
                latest = {"session_id": session_id, **session_data}

        return latest


# Singleton instance
firebase_service = FirebaseService()
