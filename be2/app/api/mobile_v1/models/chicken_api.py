"""
Chicken Counting API
Endpoints for reading chicken counting data from Firebase Realtime Database.
"""
from datetime import date as date_type
from typing import Optional
from fastapi import APIRouter, HTTPException, Query
from app.services.chicken_service import chicken_service
from app.services.chicken_counting_service import counting_session

router = APIRouter()


@router.get("/latest")
async def get_latest_count(date: Optional[str] = Query(None, description="YYYY-MM-DD, defaults to today")):
    """
    Get the latest chicken count for a given date.
    Returns the most recent session's data.
    """
    try:
        return {"success": True, "data": chicken_service.get_latest_count(date)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sessions")
async def get_sessions(date: Optional[str] = Query(None, description="YYYY-MM-DD — omit to get all dates")):
    """
    Get all counting sessions.
    If date is provided, returns sessions for that date only.
    If omitted, returns all sessions across all dates.
    """
    try:
        if date:
            sessions = chicken_service.get_sessions_by_date(date)
        else:
            sessions = chicken_service.get_all_sessions()
        return {"success": True, "data": sessions, "total": len(sessions)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/summary")
async def get_daily_summary():
    """Get daily summary — max chicken count and session count per date."""
    try:
        return {"success": True, "data": chicken_service.get_summary_by_date()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/rekap/bulanan")
async def get_monthly_rekap(year: Optional[int] = Query(None, description="Filter by year, e.g. 2024")):
    """Monthly aggregate: total chickens and session count per month."""
    try:
        return {"success": True, "data": chicken_service.get_monthly_summary(year)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/rekap/tahunan")
async def get_yearly_rekap():
    """Yearly aggregate: total chickens and session count per year."""
    try:
        return {"success": True, "data": chicken_service.get_yearly_summary()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/rekap/live-session")
async def get_live_session_status():
    """Return the active counting session status for real-time rekap overlay."""
    return {
        "success": True,
        "data": counting_session.get_status_dict() if counting_session.running else None,
    }


@router.patch("/sessions/{date}/{session_id}/cancel")
async def cancel_session(date: str, session_id: str):
    """Mark a specific session as dibatalkan."""
    try:
        ok = chicken_service.cancel_session(date, session_id)
        if not ok:
            raise HTTPException(status_code=500, detail="Gagal membatalkan sesi")
        return {"success": True, "message": f"Sesi {session_id} telah dibatalkan"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
