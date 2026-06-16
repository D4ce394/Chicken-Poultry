"""
Chicken Counting Stream API
Model management, video management, and live counting control + MJPEG stream.
"""
import asyncio
import socket
import urllib.request
from pathlib import Path

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse, Response, StreamingResponse

from app.services.chicken_counting_service import (
    CHICKEN_MODELS_DIR,
    CHICKEN_VIDEOS_DIR,
    CHICKEN_OUTPUT_DIR,
    counting_session,
)

router = APIRouter()


# ── Helpers ───────────────────────────────────────────────────────────────────

def _scan_models():
    models = []
    if CHICKEN_MODELS_DIR.exists():
        for f in sorted(CHICKEN_MODELS_DIR.glob("*.pt")):
            models.append(
                {
                    "name": f.stem,
                    "filename": f.name,
                    "size_mb": round(f.stat().st_size / 1024 / 1024, 2),
                    "active": False,
                }
            )
    # Mark first as active
    if models:
        models[0]["active"] = True
    return models


def _scan_videos():
    videos = []
    if CHICKEN_VIDEOS_DIR.exists():
        for pattern in ("*.mp4", "*.avi", "*.mov", "*.mkv"):
            for f in sorted(CHICKEN_VIDEOS_DIR.glob(pattern)):
                videos.append(
                    {
                        "name": f.name,
                        "size_mb": round(f.stat().st_size / 1024 / 1024, 2),
                    }
                )
    return videos


# ── Model Management ──────────────────────────────────────────────────────────

@router.get("/models")
async def list_models():
    return {"success": True, "data": _scan_models()}


@router.post("/models/upload")
async def upload_model(
    file: UploadFile = File(...),
    name: str = Form(""),
    version: str = Form(""),
):
    ext = Path(file.filename or "").suffix.lower()
    if ext not in (".pt", ".onnx", ".bin"):
        raise HTTPException(400, "Format harus .pt, .onnx, atau .bin")

    CHICKEN_MODELS_DIR.mkdir(parents=True, exist_ok=True)
    stem = (name.strip().replace(" ", "_") or Path(file.filename or "model").stem)
    if version.strip():
        stem = f"{stem}_v{version.strip()}"
    save_path = CHICKEN_MODELS_DIR / f"{stem}{ext}"

    content = await file.read()
    with open(save_path, "wb") as f:
        f.write(content)

    return {
        "success": True,
        "message": f"Model '{stem}' berhasil disimpan ({len(content) / 1024 / 1024:.2f} MB)",
        "filename": save_path.name,
    }


@router.delete("/models/{filename}")
async def delete_model(filename: str):
    path = CHICKEN_MODELS_DIR / filename
    if not path.exists():
        raise HTTPException(404, "Model tidak ditemukan")
    path.unlink()
    return {"success": True, "message": f"Model '{filename}' dihapus"}


# ── Video Management ──────────────────────────────────────────────────────────

@router.get("/videos")
async def list_videos():
    return {"success": True, "data": _scan_videos()}


@router.post("/videos/upload")
async def upload_video(file: UploadFile = File(...)):
    ext = Path(file.filename or "").suffix.lower()
    if ext not in (".mp4", ".avi", ".mov", ".mkv", ".webm"):
        raise HTTPException(400, "Format video tidak didukung (.mp4, .avi, .mov, .mkv)")

    CHICKEN_VIDEOS_DIR.mkdir(parents=True, exist_ok=True)
    save_path = CHICKEN_VIDEOS_DIR / (file.filename or "video")

    content = await file.read()
    with open(save_path, "wb") as f:
        f.write(content)

    return {
        "success": True,
        "message": f"Video '{file.filename}' berhasil diupload",
        "filename": file.filename,
        "size_mb": round(len(content) / 1024 / 1024, 2),
    }


@router.delete("/videos/{filename}")
async def delete_video(filename: str):
    path = CHICKEN_VIDEOS_DIR / filename
    if not path.exists():
        raise HTTPException(404, "Video tidak ditemukan")
    path.unlink()
    return {"success": True, "message": f"Video '{filename}' dihapus"}


# ── Stream URL Test (proxy test, avoids browser CORS issues) ─────────────────

@router.post("/process/test-stream")
async def test_stream_url(url: str):
    from urllib.parse import urlparse
    parsed = urlparse(url)

    if url.lower().startswith("rtsp://"):
        host = parsed.hostname or ""
        port = parsed.port or 554
        try:
            s = socket.create_connection((host, port), timeout=5)
            s.close()
            return {"success": True, "message": f"Port RTSP ({port}) pada {host} terbuka"}
        except Exception as e:
            return {"success": False, "message": f"Tidak dapat terhubung ke RTSP: {str(e)}"}
    else:
        try:
            req = urllib.request.Request(url, method="GET")
            resp = urllib.request.urlopen(req, timeout=5)
            ct = resp.headers.get("Content-Type", "unknown")
            resp.close()
            return {"success": True, "message": f"Stream dapat diakses. Content-Type: {ct}"}
        except Exception as e:
            return {"success": False, "message": f"Tidak dapat mengakses URL: {str(e)}"}


# ── Counting Process Control ──────────────────────────────────────────────────

@router.post("/process/start")
async def start_counting(
    source_type: str = Form("video"),
    source_name: str = Form(""),
    model_filename: str = Form(""),
    line_x: int = Form(400),
    buffer_width: int = Form(100),
):
    if counting_session.running:
        raise HTTPException(400, "Sesi counting sudah berjalan. Hentikan dulu.")

    if source_type == "video":
        if not source_name:
            raise HTTPException(400, "Nama file video diperlukan")
        video_path = CHICKEN_VIDEOS_DIR / source_name
        if not video_path.exists():
            raise HTTPException(404, f"File video tidak ditemukan: {source_name}")
        source = str(video_path)
    else:
        if not source_name:
            raise HTTPException(400, "Stream URL diperlukan")
        source = source_name

    if model_filename:
        model_path = CHICKEN_MODELS_DIR / model_filename
    else:
        models = sorted(CHICKEN_MODELS_DIR.glob("*.pt")) if CHICKEN_MODELS_DIR.exists() else []
        if not models:
            raise HTTPException(
                404,
                "Belum ada model tersedia. Upload model .pt dulu di halaman Konfigurasi.",
            )
        model_path = models[0]

    if not Path(model_path).exists():
        raise HTTPException(404, f"File model tidak ditemukan: {model_path}")

    ok = counting_session.start(
        source=source,
        model_path=str(model_path),
        line_x=line_x,
        buffer_width=buffer_width,
    )
    if not ok:
        raise HTTPException(500, "Gagal memulai sesi counting")

    return {
        "success": True,
        "message": "Counting dimulai",
        "status": counting_session.status,
    }


@router.post("/process/pause")
async def pause_counting():
    ok = counting_session.pause()
    if not ok:
        raise HTTPException(400, f"Tidak bisa menjeda. Status saat ini: {counting_session.status}")
    return {"success": True, "message": "Counting dijeda", "status": counting_session.status}


@router.post("/process/resume")
async def resume_counting():
    ok = counting_session.resume()
    if not ok:
        raise HTTPException(400, f"Tidak bisa melanjutkan. Status saat ini: {counting_session.status}")
    return {"success": True, "message": "Counting dilanjutkan", "status": counting_session.status}


@router.post("/process/stop")
async def stop_counting():
    if not counting_session.running:
        return {"success": True, "message": "Tidak ada sesi yang berjalan", "total_count": counting_session.total_count}
    counting_session.stop()
    return {
        "success": True,
        "message": "Counting dihentikan",
        "total_count": counting_session.total_count,
    }


@router.get("/process/status")
async def get_counting_status():
    return {"success": True, "data": counting_session.get_status_dict()}


# ── Live MJPEG stream of currently-processed frames ──────────────────────────

@router.get("/process/live-stream")
async def live_mjpeg_stream():
    """
    MJPEG live stream: returns processed frames with overlays in real-time.
    Attach to <img src="..."> in the browser.
    The stream ends automatically when counting stops.
    """
    async def generate():
        while counting_session.running:
            frame_bytes = counting_session.get_latest_frame()
            if frame_bytes:
                yield (
                    b"--frame\r\n"
                    b"Content-Type: image/jpeg\r\n\r\n" +
                    frame_bytes +
                    b"\r\n"
                )
            await asyncio.sleep(1 / 25)  # cap at ~25fps

        # Send the very last frame once more so the image doesn't go blank
        frame_bytes = counting_session.get_latest_frame()
        if frame_bytes:
            yield (
                b"--frame\r\n"
                b"Content-Type: image/jpeg\r\n\r\n" +
                frame_bytes +
                b"\r\n"
            )

    return StreamingResponse(
        generate(),
        media_type="multipart/x-mixed-replace; boundary=frame",
        headers={"Cache-Control": "no-cache, no-store", "Pragma": "no-cache"},
    )


# ── Processed video file (result MP4) ────────────────────────────────────────

@router.get("/process/video")
async def get_processed_video():
    """
    Serve the processed MP4 result for inline browser playback.
    FileResponse with no filename = Content-Disposition: inline (browser plays, not downloads).
    """
    if not counting_session.output_file:
        raise HTTPException(404, "Belum ada video hasil. Jalankan counting dulu.")
    path = Path(counting_session.output_file)
    if not path.exists():
        raise HTTPException(404, "File video hasil tidak ditemukan di server.")
    # No `filename` param so Starlette sends Content-Disposition: inline
    return FileResponse(path, media_type="video/mp4")


# ── Video preview frame with counting line ────────────────────────────────────

@router.get("/videos/{filename}/preview")
async def video_preview_frame(filename: str, line_x: int = 400, buffer_width: int = 100):
    """
    Return JPEG of first frame with counting line overlay drawn.
    Use in <img src="..."> to preview where the counting line falls.
    """
    from app.services.chicken_counting_service import CV2_AVAILABLE
    if not CV2_AVAILABLE:
        raise HTTPException(503, "cv2 tidak tersedia")
    import cv2 as _cv2
    path = CHICKEN_VIDEOS_DIR / filename
    if not path.exists():
        raise HTTPException(404, "Video tidak ditemukan")
    cap = _cv2.VideoCapture(str(path))
    ok, frame = cap.read()
    cap.release()
    if not ok:
        raise HTTPException(500, "Tidak dapat membaca frame video")
    h, w = frame.shape[:2]
    # Draw counting lines (same colours as counting_ayam.py)
    _cv2.line(frame, (line_x, 0), (line_x, h), (0, 0, 255), 2)
    _cv2.line(frame, (line_x + buffer_width, 0), (line_x + buffer_width, h), (0, 255, 255), 1)
    # Label
    _cv2.putText(frame, f"LINE X={line_x}", (max(line_x - 100, 5), 40),
                 _cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), 2)
    _cv2.putText(frame, f"BUFFER +{buffer_width}", (line_x + 10, 80),
                 _cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
    _, buf = _cv2.imencode(".jpg", frame, [_cv2.IMWRITE_JPEG_QUALITY, 90])
    return Response(buf.tobytes(), media_type="image/jpeg")


@router.get("/videos/{filename}/info")
async def video_info(filename: str):
    """Return video metadata and suggested LINE_X value."""
    from app.services.chicken_counting_service import CV2_AVAILABLE
    if not CV2_AVAILABLE:
        raise HTTPException(503, "cv2 tidak tersedia")
    import cv2 as _cv2
    path = CHICKEN_VIDEOS_DIR / filename
    if not path.exists():
        raise HTTPException(404, "Video tidak ditemukan")
    cap = _cv2.VideoCapture(str(path))
    w = int(cap.get(_cv2.CAP_PROP_FRAME_WIDTH))
    h = int(cap.get(_cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(_cv2.CAP_PROP_FPS)
    total = int(cap.get(_cv2.CAP_PROP_FRAME_COUNT))
    cap.release()
    # Suggest LINE_X: script asli pakai 400 untuk 848px video (~47% dari kiri).
    # Kalau video lebar beda, skala proporsional ke 47%.
    suggested_line_x = int(w * 0.47)
    suggested_buffer = int(w * 0.12)
    return {
        "success": True,
        "data": {
            "width": w, "height": h,
            "fps": round(fps, 2),
            "total_frames": total,
            "duration_seconds": round(total / fps, 1) if fps > 0 else 0,
            "suggested_line_x": suggested_line_x,
            "suggested_buffer_width": suggested_buffer,
        }
    }


@router.get("/process/videos")
async def list_processed_videos():
    """List all processed output videos."""
    videos = []
    if CHICKEN_OUTPUT_DIR.exists():
        for f in sorted(CHICKEN_OUTPUT_DIR.glob("*.mp4"), reverse=True):
            videos.append({
                "name": f.name,
                "size_mb": round(f.stat().st_size / 1024 / 1024, 2),
            })
    return {"success": True, "data": videos}
