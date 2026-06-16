"""
Firebase Service
Handles connection to Firebase Realtime Database for chicken counting data.
"""
import os
import json
import base64
import logging
from typing import Optional
import firebase_admin
from firebase_admin import credentials, db

logger = logging.getLogger(__name__)

_DATABASE_URL = os.getenv(
    "FIREBASE_DATABASE_URL",
    "https://rfid-de0fd-default-rtdb.asia-southeast1.firebasedatabase.app"
)


def _load_credentials() -> Optional[credentials.Certificate]:
    """
    Load Firebase credentials from (in order of priority):
    1. FIREBASE_SERVICE_ACCOUNT_BASE64 env var — base64-encoded JSON (for HF Spaces / CI)
    2. FIREBASE_SERVICE_ACCOUNT_PATH env var — path to JSON file
    3. Default JSON file path (local dev)
    """
    # 1. Base64-encoded JSON dari env var (Hugging Face Secrets)
    b64 = os.getenv("FIREBASE_SERVICE_ACCOUNT_BASE64")
    if b64:
        try:
            sa_dict = json.loads(base64.b64decode(b64).decode("utf-8"))
            return credentials.Certificate(sa_dict)
        except Exception as e:
            logger.error(f"Failed to decode FIREBASE_SERVICE_ACCOUNT_BASE64: {e}")

    # 2. Path ke file JSON
    sa_path = os.getenv(
        "FIREBASE_SERVICE_ACCOUNT_PATH",
        os.path.join(os.path.dirname(__file__), "..", "..", "rfid-de0fd-firebase-adminsdk-fbsvc-22ca2974df.json")
    )
    if os.path.exists(sa_path):
        return credentials.Certificate(sa_path)

    logger.warning("Firebase service account not found — Firebase features disabled.")
    return None


class FirebaseService:
    """Singleton Firebase connection manager"""

    _initialized: bool = False

    def __init__(self):
        self._initialize()

    def _initialize(self):
        if FirebaseService._initialized:
            return

        if not _DATABASE_URL:
            logger.warning("FIREBASE_DATABASE_URL is not set.")
            return

        cred = _load_credentials()
        if not cred:
            return

        try:
            firebase_admin.initialize_app(cred, {"databaseURL": _DATABASE_URL})
            FirebaseService._initialized = True
            logger.info("Firebase initialized successfully.")
        except Exception as e:
            logger.error(f"Failed to initialize Firebase: {e}")

    @property
    def is_ready(self) -> bool:
        return FirebaseService._initialized

    def get_ref(self, path: str):
        if not self.is_ready:
            raise RuntimeError("Firebase is not initialized.")
        return db.reference(path)

    def get_chicken_history(self, date: Optional[str] = None) -> dict:
        path = "chicken_counter/history"
        if date:
            path = f"{path}/{date}"
        ref = self.get_ref(path)
        data = ref.get()
        return data or {}

    def update_session_status(self, date: str, session_id: str, new_status: str) -> bool:
        try:
            ref = self.get_ref(f"chicken_counter/history/{date}/{session_id}/status")
            ref.set(new_status)
            return True
        except Exception as e:
            logger.error(f"Error updating session {session_id} status: {e}")
            return False

    def get_latest_session(self, date: str) -> Optional[dict]:
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
