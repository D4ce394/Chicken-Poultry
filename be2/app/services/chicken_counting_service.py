"""
Chicken Counting Service
Processes video with YOLO tracking, saves output MP4 with overlays,
and updates Firebase realtime. Mirrors counting_ayam.py logic.
"""
import logging
import os
import threading
from datetime import datetime
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

try:
    import cv2
    CV2_AVAILABLE = True
except Exception as _e:
    logger.warning(f"cv2 not available: {_e}")
    CV2_AVAILABLE = False

try:
    from ultralytics import YOLO
    YOLO_AVAILABLE = True
except Exception as _e:
    logger.warning(f"ultralytics not available: {_e}")
    YOLO_AVAILABLE = False

try:
    import torch
    DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
    if DEVICE == "cuda":
        logger.info(f"GPU detected: {torch.cuda.get_device_name(0)}")
    else:
        logger.info("No GPU found, using CPU")
except Exception:
    DEVICE = "cpu"

try:
    from qtfaststart import processor as _qtfs
    QTFASTSTART_AVAILABLE = True
except Exception:
    QTFASTSTART_AVAILABLE = False

try:
    import imageio_ffmpeg as _iio_ffmpeg
    IMAGEIO_FFMPEG_AVAILABLE = True
except Exception:
    IMAGEIO_FFMPEG_AVAILABLE = False

from app.services.firebase_service import firebase_service

CHICKEN_MODELS_DIR = Path("uploads/models/chicken")
CHICKEN_VIDEOS_DIR = Path("uploads/videos/chicken")
CHICKEN_OUTPUT_DIR = Path("uploads/videos/chicken/processed")

CHICKEN_MODELS_DIR.mkdir(parents=True, exist_ok=True)
CHICKEN_VIDEOS_DIR.mkdir(parents=True, exist_ok=True)
CHICKEN_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


class ChickenCountingSession:
    """
    Thread-based counting session.
    Processes video frame-by-frame, writes output MP4 with detection overlays,
    updates Firebase on each new detection, and tracks progress.
    """

    def __init__(self):
        self.running: bool = False
        self._thread: Optional[threading.Thread] = None

        # Progress & results
        self.total_count: int = 0
        self.total_frames: int = 0
        self.current_frame: int = 0
        self.progress: int = 0           # 0–100
        self.fps: float = 25.0
        self.latest_frame: Optional[bytes] = None  # JPEG bytes of last processed frame

        # Status: idle | running | paused | transcoding | finished | stopped | error
        self.status: str = "idle"
        self.error_message: str = ""
        self.source_name: str = ""
        self.model_name: str = ""
        self.start_time: Optional[str] = None
        self.stop_time: Optional[str] = None
        self.output_file: Optional[str] = None   # absolute path to result MP4
        self._frame_lock = threading.Lock()
        self._pause_event = threading.Event()
        self._pause_event.set()  # not paused initially

    def start(
        self,
        source: str,
        model_path: str,
        line_x: int = 400,
        buffer_width: int = 100,
    ) -> bool:
        if self.running:
            return False
        self.running = True
        self.total_count = 0
        self.total_frames = 0
        self.current_frame = 0
        self.progress = 0
        self.status = "running"
        self.error_message = ""
        self.source_name = os.path.basename(source)
        self.model_name = os.path.basename(model_path)
        self.start_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.stop_time = None
        self.output_file = None
        self.latest_frame = None
        self._pause_event.set()  # ensure unpaused when restarting

        self._thread = threading.Thread(
            target=self._run,
            args=(source, model_path, line_x, buffer_width),
            daemon=True,
        )
        self._thread.start()
        return True

    def pause(self) -> bool:
        if not self.running or self.status not in ("running",):
            return False
        self._pause_event.clear()
        self.status = "paused"
        return True

    def resume(self) -> bool:
        if not self.running or self.status != "paused":
            return False
        self.status = "running"
        self._pause_event.set()
        return True

    def stop(self):
        self._pause_event.set()  # unblock pause so thread can see running=False
        self.running = False
        if self._thread:
            self._thread.join(timeout=15)
        if self.status in ("running", "paused", "transcoding"):
            self.status = "stopped"
        if not self.stop_time:
            self.stop_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def get_latest_frame(self) -> Optional[bytes]:
        with self._frame_lock:
            return self.latest_frame

    def get_status_dict(self) -> dict:
        return {
            "running": self.running,
            "status": self.status,
            "total_count": self.total_count,
            "total_frames": self.total_frames,
            "current_frame": self.current_frame,
            "progress": self.progress,
            "fps": round(self.fps, 1),
            "device": DEVICE,
            "source_name": self.source_name,
            "model_name": self.model_name,
            "start_time": self.start_time,
            "stop_time": self.stop_time,
            "error_message": self.error_message,
            "output_file": os.path.basename(self.output_file) if self.output_file else None,
        }

    # ── Internal processing thread ────────────────────────────────────────────

    def _run(self, source: str, model_path: str, line_x: int, buffer_width: int):
        if not CV2_AVAILABLE or not YOLO_AVAILABLE:
            self.status = "error"
            self.error_message = "cv2 atau ultralytics tidak tersedia di environment ini."
            self.running = False
            return

        cap = None
        out = None
        session_ref = None

        try:
            model = YOLO(model_path)
            cap = cv2.VideoCapture(source)

            if not cap.isOpened():
                self.status = "error"
                self.error_message = f"Tidak dapat membuka sumber: {source}"
                self.running = False
                return

            # Video metadata
            fps = cap.get(cv2.CAP_PROP_FPS) or 25
            total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            self.fps = fps
            self.total_frames = total

            # Output file — same pattern as counting_ayam.py's hasil_deteksi_ayam.mp4
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = CHICKEN_OUTPUT_DIR / f"hasil_{ts}.mp4"
            fourcc = cv2.VideoWriter.fourcc(*"mp4v")
            out = cv2.VideoWriter(str(output_path), fourcc, fps, (width, height))

            # Firebase session
            now = datetime.now()
            date_str = now.strftime("%Y-%m-%d")
            session_id = f"session_{now.strftime('%H%M%S')}"
            try:
                if firebase_service.is_ready:
                    session_ref = firebase_service.get_ref(
                        f"chicken_counter/history/{date_str}/{session_id}"
                    )
                    session_ref.update({
                        "chicken_total": 0,
                        "start_time": self.start_time,
                        "last_update": self.start_time,
                        "status": "Running...",
                    })
            except Exception as e:
                logger.warning(f"Firebase session init failed: {e}")
                session_ref = None

            counted_ids: set = set()
            id_mapping: dict = {}
            frame_num = 0

            while self.running and cap.isOpened():
                self._pause_event.wait()  # blocks here while paused
                if not self.running:
                    break
                success, frame = cap.read()
                if not success:
                    break

                # YOLO tracking — same as counting_ayam.py
                results = None
                try:
                    results = model.track(
                        frame,
                        persist=True,
                        tracker="bytetrack.yaml",
                        device=DEVICE,
                        verbose=False,
                    )
                except Exception as e:
                    logger.debug(f"Tracking error (non-fatal): {e}")

                if (
                    results
                    and results[0].boxes is not None
                    and results[0].boxes.id is not None
                ):
                    try:
                        boxes = results[0].boxes.xyxy.cpu().numpy()
                        ids = results[0].boxes.id.cpu().numpy().astype(int)
                    except AttributeError:
                        boxes = results[0].boxes.xyxy
                        ids = results[0].boxes.id.astype(int)

                    for box, obj_id in zip(boxes, ids):
                        x1, y1, x2, y2 = map(int, box)
                        cx = (x1 + x2) // 2
                        cy = (y1 + y2) // 2

                        if cx > line_x + buffer_width:
                            continue

                        cv2.circle(frame, (cx, cy), 4, (0, 0, 255), -1)

                        if line_x < cx < line_x + buffer_width and obj_id not in counted_ids:
                            counted_ids.add(obj_id)
                            self.total_count += 1
                            id_mapping[obj_id] = self.total_count
                            waktu = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            # Draw highlighted box when crossing the line
                            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 4)
                            if session_ref:
                                try:
                                    session_ref.update({
                                        "chicken_total": self.total_count,
                                        "last_update": waktu,
                                    })
                                except Exception:
                                    pass

                        if obj_id in id_mapping:
                            label = f"Ayam Ke-{id_mapping[obj_id]}"
                            color = (0, 200, 0)
                        else:
                            label = "Scan..."
                            color = (255, 144, 30)

                        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                        cv2.putText(
                            frame, label, (x1, y1 - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2,
                        )

                # Counting lines — same as counting_ayam.py
                h = frame.shape[0]
                cv2.line(frame, (line_x, 0), (line_x, h), (0, 0, 255), 2)
                cv2.line(
                    frame,
                    (line_x + buffer_width, 0),
                    (line_x + buffer_width, h),
                    (0, 255, 255), 1,
                )
                cv2.putText(
                    frame, f"COUNT: {self.total_count}", (50, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 0), 3,
                )

                # Store latest frame for MJPEG live stream
                try:
                    _, jpeg_buf = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 72])
                    with self._frame_lock:
                        self.latest_frame = jpeg_buf.tobytes()
                except Exception:
                    pass

                # Write frame to output video
                out.write(frame)

                frame_num += 1
                self.current_frame = frame_num
                if total > 0:
                    self.progress = min(int(frame_num / total * 100), 99)

            # Finalize (only reached when video ends naturally, not user-stopped)
            cap.release()
            out.release()
            out = None

            self.status = "transcoding"  # brief phase: converting to H.264

            # Transcode mp4v → H.264 (browser-compatible) with faststart atom
            h264_path = output_path.parent / f"h264_{output_path.name}"
            transcoded = False

            if IMAGEIO_FFMPEG_AVAILABLE:
                import subprocess as _sp
                try:
                    _ffmpeg_exe = _iio_ffmpeg.get_ffmpeg_exe()
                    _result = _sp.run(
                        [
                            _ffmpeg_exe, "-y",
                            "-i", str(output_path),
                            "-c:v", "libx264", "-preset", "fast", "-crf", "23",
                            "-movflags", "+faststart",
                            "-an",
                            str(h264_path),
                        ],
                        capture_output=True,
                        timeout=600,
                    )
                    if _result.returncode == 0 and h264_path.exists() and h264_path.stat().st_size > 0:
                        output_path.unlink()
                        h264_path.rename(output_path)
                        transcoded = True
                        logger.info("H.264 transcoding successful")
                    else:
                        logger.warning(f"ffmpeg non-zero exit: {_result.stderr.decode()[-300:]}")
                        if h264_path.exists():
                            h264_path.unlink()
                except Exception as e:
                    logger.warning(f"H.264 transcoding failed: {e}")
                    if h264_path.exists():
                        h264_path.unlink()

            # Fallback: qtfaststart only (video stays mp4v — limited browser support)
            if not transcoded and QTFASTSTART_AVAILABLE:
                try:
                    faststart_path = output_path.parent / f"fs_{output_path.name}"
                    _qtfs.process(str(output_path), str(faststart_path))
                    output_path.unlink()
                    faststart_path.rename(output_path)
                    logger.info("qtfaststart fallback: moov atom relocated")
                except Exception as e:
                    logger.warning(f"qtfaststart failed: {e}")

            self.progress = 100
            self.output_file = str(output_path)
            self.stop_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.status = "finished"

            if session_ref:
                try:
                    session_ref.update({
                        "status": "Offline (System Stopped)",
                        "stop_time": self.stop_time,
                    })
                except Exception:
                    pass

        except Exception as e:
            logger.error(f"Counting session crashed: {e}", exc_info=True)
            self.status = "error"
            self.error_message = str(e)
        finally:
            if cap:
                cap.release()
            if out:
                out.release()
            self.running = False
            # Preserve finished/error; anything still "active" → stopped
            if self.status in ("running", "paused", "transcoding"):
                self.status = "stopped"
            if not self.stop_time:
                self.stop_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")


counting_session = ChickenCountingSession()
