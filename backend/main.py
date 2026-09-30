import base64
import json
import os
import re
import smtplib
import subprocess
import threading
import time
import uuid
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from email.message import EmailMessage
from pathlib import Path
from math import radians, sin, cos, sqrt, atan2
import mimetypes

import cv2
import numpy as np
from fastapi import BackgroundTasks, FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles

from backend.config import (
    ALERT_COOLDOWN_SECONDS,
    ALERT_EMAIL_TO,
    ALLOWED_IMAGE_EXTENSIONS,
    ALLOWED_VIDEO_EXTENSIONS,
    BASE_DIR,
    CONTINUOUS_VIOLATION_SECONDS,
    FIRE_SMOKE_MODEL_PATH,
    INCIDENT_DIR,
    INCIDENT_RETENTION_HOURS,
    MAX_UPLOAD_SIZE_MB,
    SMTP_PASSWORD,
    SMTP_PORT,
    SMTP_SERVER,
    SMTP_USERNAME,
    UPLOAD_DIR,
    SITE_ADDRESS, 
    GOOGLE_MAPS_URL, 
    SITE_LATITUDE, 
    SITE_LONGITUDE,
)
from backend.detection_engine import SafetyComplianceEngine

app = FastAPI(title="SafeScan360 AI Engine", version="2.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.mount("/uploads", StaticFiles(directory=str(UPLOAD_DIR)), name="uploads")

engine = SafetyComplianceEngine()
executor = ThreadPoolExecutor(max_workers=2, thread_name_prefix="safescan-video")
email_executor = ThreadPoolExecutor(max_workers=2, thread_name_prefix="safescan-email")
video_jobs = {}
video_jobs_lock = threading.Lock()

latest_live_stats = {
    "total_workers": 0, "compliant": 0, "violations": 0, "hazards": 0,
    "fire": False, "smoke": False, "fire_count": 0, "smoke_count": 0,
    "compliance_pct": "0%", "fps": 0, "latency_ms": 0, "events": [],
    "model_info": {}, "device": engine.device,
}

INCIDENTS_FILE = UPLOAD_DIR / "incident_log.json"
incident_store = []
active_alerts = {}
alert_lock = threading.Lock()


def load_incidents():
    global incident_store
    try:
        with open(INCIDENTS_FILE, "r", encoding="utf-8") as f:
            incident_store = json.load(f)
    except Exception:
        incident_store = []


def save_incidents():
    with open(INCIDENTS_FILE, "w", encoding="utf-8") as f:
        json.dump(incident_store, f, indent=2)


def cleanup_expired_incidents():
    global incident_store
    cutoff = time.time() - INCIDENT_RETENTION_HOURS * 3600
    kept = []
    for item in incident_store:
        if item.get("created_at_ts", time.time()) >= cutoff:
            kept.append(item)
        else:
            path = item.get("screenshot_path")
            if path and os.path.exists(path):
                try: os.remove(path)
                except OSError: pass
    incident_store = kept
    save_incidents()


def safe_name(name: str, fallback="upload"):
    stem = re.sub(r"[^A-Za-z0-9._-]+", "_", Path(name or fallback).name)
    return stem[:120] or fallback


def save_screenshot(frame, label):
    filename = f"{label}_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}.jpg"
    path = INCIDENT_DIR / filename
    if cv2.imwrite(str(path), frame):
        return str(path)
    return None


def calculate_distance_km(lat1, lon1, lat2, lon2):
    """Calculate the great-circle distance between two points on the earth (in kilometers)."""
    R = 6371.0  # Earth radius in kilometers
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat / 2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return R * c


def send_incident_email(incident):
    """Send a safety alert email with violation details, exact GPS coordinates, distance deviation, and captured evidence image."""
    if not ALERT_EMAIL_TO or not SMTP_USERNAME or not SMTP_PASSWORD:
        return

    try:
        details = incident.get("details") or {}
        missing = details.get("missing") or []
        missing_text = ", ".join(missing) if missing else incident.get("message", "Safety event detected")
        screenshot_path = incident.get("screenshot_path")
        source = incident.get("source", "unknown")
        incident_type = incident.get("type", "Unknown Event")
        severity = incident.get("severity", "UNKNOWN")
        timestamp = incident.get("timestamp", "")
        message_text = incident.get("message", "")

        subject = f"SafeScan360 Alert - {incident_type}"
        if missing:
            subject += f": {missing_text}"

        lat_str = SITE_LATITUDE.strip() if SITE_LATITUDE else ""
        lon_str = SITE_LONGITUDE.strip() if SITE_LONGITUDE else ""
        coordinates_text = f"{lat_str}, {lon_str}" if (lat_str and lon_str) else "Coordinates not configured"

        # Calculate traveling distance deviation if mobile/current lat & lon are provided in details
        current_lat = details.get("latitude")
        current_lon = details.get("longitude")
        distance_text = ""
        if current_lat and current_lon and lat_str and lon_str:
            try:
                dist_km = calculate_distance_km(
                    float(lat_str), float(lon_str),
                    float(current_lat), float(current_lon)
                )
                if dist_km < 1.0:
                    distance_text = f"{int(dist_km * 1000)} meters away from base"
                else:
                    distance_text = f"{dist_km:.2f} km away from base"
            except ValueError:
                pass

        # --- 1. Plain Text Body Fallback ---
        body = (
            "SafeScan360 Safety Alert\n\n"
            f"Event: {incident_type}\n"
            f"Severity: {severity}\n"
            f"Source: {source}\n"
            f"Time: {timestamp}\n"
        )

        if source == "live":
            body += (
                f"\n📍 Construction Site: {SITE_ADDRESS}\n"
                f"🎯 Exact Coordinates: {coordinates_text}\n"
            )
            if distance_text:
                body += f"📏 Distance Deviation: {distance_text}\n"
            body += f"🗺️ Google Maps Location: {GOOGLE_MAPS_URL if GOOGLE_MAPS_URL else 'Coordinates not configured'}\n"

        if details.get("worker_id"):
            body += f"Worker: {details['worker_id']}\n"
        if missing:
            body += f"Missing / not detected with explicit violation evidence: {missing_text}\n"
        if message_text:
            body += f"\nMessage: {message_text}\n"
            
        body += "\nThe attached image is the captured evidence frame."

        # --- 2. Rich HTML Body ---
        html_body = f"""
        <html>
          <body style="font-family: Arial, sans-serif; color: #333;">
            <h2 style="color: #d9534f; margin-bottom: 5px;">SafeScan360 Safety Alert</h2>
            <hr style="border: 0; border-top: 2px solid #d9534f; margin-top: 0;" />
            <p><b>Event:</b> {incident_type}</p>
            <p><b>Severity:</b> <span style="color: #d9534f;">{severity}</span></p>
            <p><b>Source:</b> {source}</p>
            <p><b>Time:</b> {timestamp}</p>
        """

        if source == "live":
            html_body += f"""
            <div style="background-color: #f9f9f9; padding: 12px; border-radius: 6px; margin: 15px 0; border-left: 4px solid #0275d8;">
              <p style="margin: 0 0 8px 0;"><b>📍 Construction Site:</b> {SITE_ADDRESS}</p>
              <p style="margin: 0 0 8px 0;"><b>🎯 Exact Coordinates:</b> <code>{coordinates_text}</code></p>
            """
            if distance_text:
                html_body += f"""<p style="margin: 0 0 8px 0; color: #d9534f;"><b>📏 Distance Deviation:</b> {distance_text}</p>"""
            
            if GOOGLE_MAPS_URL:
                html_body += f"""
              <p style="margin: 10px 0 0 0;">
                <a href="{GOOGLE_MAPS_URL}" target="_blank" style="background-color: #0275d8; color: white; padding: 10px 18px; text-decoration: none; border-radius: 4px; font-weight: bold; display: inline-block;">
                  🗺️ Open Exact Pin in Google Maps
                </a>
              </p>
            """
            html_body += "</div>"

        if details.get("worker_id"):
            html_body += f"<p><b>Worker ID:</b> {details['worker_id']}</p>"
        if missing:
            html_body += f"<p><b>Missing PPE / Violation Evidence:</b> {missing_text}</p>"
        if message_text:
            html_body += f"<p><b>Message:</b> {message_text}</p>"

        html_body += """
            <p style="color: #666; font-size: 0.9em; margin-top: 25px;"><em>The attached image is the captured evidence frame.</em></p>
          </body>
        </html>
        """

        msg = EmailMessage()
        msg["Subject"] = subject
        msg["From"] = SMTP_USERNAME
        msg["To"] = ALERT_EMAIL_TO
        
        msg.set_content(body)
        msg.add_alternative(html_body, subtype="html")

        if screenshot_path:
            image_path = Path(screenshot_path)
            if image_path.is_file():
                image_data = image_path.read_bytes()
                mime_type, _ = mimetypes.guess_type(str(image_path))
                maintype, subtype = (mime_type.split("/") if mime_type else ("image", "jpeg"))
                msg.add_attachment(
                    image_data,
                    maintype=maintype,
                    subtype=subtype,
                    filename=image_path.name,
                )

        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT, timeout=20) as server:
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.send_message(msg)
        print(f"[EMAIL] Alert sent to {ALERT_EMAIL_TO}: {subject}")
    except Exception as exc:
        print(f"[EMAIL ERROR] {exc}")


def register_incident(kind, message, severity, source, frame=None, details=None, debounce=True):
    now = time.time()
    key = f"{source}:{kind}"
    with alert_lock:
        if debounce:
            previous = active_alerts.get(key)
            if previous and now - previous < ALERT_COOLDOWN_SECONDS:
                return None
            active_alerts[key] = now
        screenshot_path = save_screenshot(frame, f"{kind.lower()}_{uuid.uuid4().hex[:8]}") if frame is not None else None
        incident = {
            "id": uuid.uuid4().hex,
            "type": kind,
            "source": source,
            "severity": severity,
            "message": message,
            "details": details or {},
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "created_at_ts": now,
            "screenshot_path": screenshot_path,
            "screenshot_url": f"/uploads/incidents/{Path(screenshot_path).name}" if screenshot_path else None,
        }
        incident_store.insert(0, incident)
        save_incidents()
    email_executor.submit(send_incident_email, incident)
    return incident


load_incidents()


def validate_upload(file: UploadFile, allowed):
    ext = Path(file.filename or "").suffix.lower()
    if ext not in allowed:
        raise HTTPException(status_code=400, detail=f"Unsupported file type: {ext or 'unknown'}")
    return ext


async def read_upload(file: UploadFile):
    data = await file.read(MAX_UPLOAD_SIZE_MB * 1024 * 1024 + 1)
    if len(data) > MAX_UPLOAD_SIZE_MB * 1024 * 1024:
        raise HTTPException(status_code=413, detail=f"File exceeds {MAX_UPLOAD_SIZE_MB} MB limit")
    return data


@app.get("/api/health")
def health():
    return {"status": "ok", "service": "SafeScan360 AI Engine", "device": engine.device}


@app.get("/api/models/status")
@app.get("/api/model-status")
def model_status():
    return {
        "ppe_model": True,
        "fire_smoke_model": Path(FIRE_SMOKE_MODEL_PATH).exists(),
        "device": engine.device,
        "ppe_classes": list(engine.ppe_names.values()),
        "fire_smoke_classes": list(engine.hazard_names.values()),
    }


@app.get("/api/live-stats")
def live_stats():
    return latest_live_stats


@app.get("/api/stats")
def stats():
    return latest_live_stats


@app.get("/api/incidents")
def incidents():
    cleanup_expired_incidents()
    return {"incidents": incident_store}


@app.get("/api/recent-alerts")
def recent_alerts():
    cleanup_expired_incidents()
    return {"incidents": incident_store[:10]}


@app.delete("/api/incidents/{incident_id}")
def delete_incident(incident_id: str):
    global incident_store
    for i, item in enumerate(incident_store):
        if item.get("id") == incident_id:
            path = item.get("screenshot_path")
            if path and os.path.exists(path):
                try: os.remove(path)
                except OSError: pass
            incident_store.pop(i)
            save_incidents()
            return {"status": "deleted", "id": incident_id}
    raise HTTPException(status_code=404, detail="Incident not found")


def apply_alerts(stats, frame, source):
    if stats.get("fire"):
        register_incident("FIRE", "Fire detected", "CRITICAL", source, frame, {"confidence": max([e.get("confidence", 0) for e in stats["events"] if e.get("type") == "FIRE"] or [0])})
    if stats.get("smoke"):
        register_incident("SMOKE", "Smoke detected", "HIGH", source, frame, {"confidence": max([e.get("confidence", 0) for e in stats["events"] if e.get("type") == "SMOKE"] or [0])})
    if stats.get("violations"):
        for event in stats.get("events", []):
            if event.get("type") == "PPE_VIOLATION":
                register_incident("PPE_VIOLATION", event["message"], event.get("severity", "MEDIUM"), source, frame, event)


@app.post("/api/detect-image")
async def detect_image(file: UploadFile = File(...)):
    validate_upload(file, ALLOWED_IMAGE_EXTENSIONS)
    data = await read_upload(file)
    image = cv2.imdecode(np.frombuffer(data, np.uint8), cv2.IMREAD_COLOR)
    if image is None:
        raise HTTPException(status_code=400, detail="Invalid or corrupted image")
    annotated, result = engine.process_frame(image)
    apply_alerts(result, annotated, "image")
    ok, buffer = cv2.imencode(".jpg", annotated, [cv2.IMWRITE_JPEG_QUALITY, 90])
    if not ok:
        raise HTTPException(status_code=500, detail="Could not encode annotated image")
    return {
        "status": "Success",
        "annotated_image": "data:image/jpeg;base64," + base64.b64encode(buffer).decode(),
        "stats": result,
    }


def transcode_to_browser_mp4(input_path: Path, output_path: Path):
    ffmpeg = "ffmpeg"
    command = [ffmpeg, "-y", "-i", str(input_path), "-c:v", "libx264", "-preset", "veryfast", "-crf", "23", "-pix_fmt", "yuv420p", "-movflags", "+faststart", "-an", str(output_path)]
    try:
        proc = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
        return True, proc.stderr[-1000:]
    except (FileNotFoundError, subprocess.CalledProcessError) as exc:
        return False, str(exc)


def process_video_job(job_id: str, raw_path: Path):
    with video_jobs_lock:
        video_jobs[job_id]["status"] = "processing"
    temp_path = UPLOAD_DIR / f"{job_id}_annotated_temp.mp4"
    final_path = UPLOAD_DIR / f"{job_id}_annotated.mp4"
    cap = cv2.VideoCapture(str(raw_path))
    if not cap.isOpened():
        raise RuntimeError("Could not open uploaded video")
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH) or 0)
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT) or 0)
    fps = float(cap.get(cv2.CAP_PROP_FPS) or 25.0)
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
    if width <= 0 or height <= 0:
        cap.release(); raise RuntimeError("Corrupted or unsupported video")
    writer = cv2.VideoWriter(str(temp_path), cv2.VideoWriter_fourcc(*"mp4v"), fps, (width, height))
    if not writer.isOpened():
        cap.release(); raise RuntimeError("Could not create temporary video writer")

    frame_idx = 0
    processed = 0
    total_worker_frames = 0
    total_compliant_frames = 0
    max_hazards = 0
    fire_events = 0
    smoke_events = 0
    timeline = []
    start = time.perf_counter()
    last_stats = {}
    last_annotated = None
    try:
        while True:
            ret, frame = cap.read()
            if not ret: break
            if frame_idx % max(1, __import__('backend.config', fromlist=['FRAME_SKIP']).FRAME_SKIP) != 0:
                writer.write(frame)
                frame_idx += 1
                continue
            annotated, stats = engine.process_frame(frame)
            writer.write(annotated)
            last_stats = stats
            last_annotated = annotated
            processed += 1
            total_worker_frames += stats["total_workers"]
            total_compliant_frames += stats["compliant"]
            max_hazards = max(max_hazards, stats["hazards"])
            fire_events += int(stats["fire"])
            smoke_events += int(stats["smoke"])
            if frame_idx % max(1, int(fps)) == 0:
                timeline.append({
                    "time": round(frame_idx / fps, 2),
                    "timestamp": f"{int(frame_idx / fps // 60):02d}:{int(frame_idx / fps % 60):02d}",
                    "workers": stats["total_workers"], "compliant": stats["compliant"],
                    "violations": stats["violations"], "hazards": stats["hazards"],
                    "fire": stats["fire"], "smoke": stats["smoke"], "events": stats["events"],
                })
            if last_annotated is not None and (stats["fire"] or stats["smoke"] or stats["violations"]):
                apply_alerts(stats, annotated, "video")
            frame_idx += 1
            progress = round((frame_idx / frame_count) * 100, 1) if frame_count else 0
            elapsed = time.perf_counter() - start
            with video_jobs_lock:
                video_jobs[job_id].update({
                    "progress": min(progress, 99.9), "frames_processed": processed,
                    "processing_fps": round(processed / elapsed, 2) if elapsed else 0,
                })
    finally:
        cap.release(); writer.release()

    ok, ffmpeg_info = transcode_to_browser_mp4(temp_path, final_path)
    if not ok:
        os.replace(temp_path, final_path)
        ffmpeg_used = False
    else:
        temp_path.unlink(missing_ok=True)
        ffmpeg_used = True

    elapsed = time.perf_counter() - start
    overall_compliance = (total_compliant_frames / total_worker_frames * 100) if total_worker_frames else 0
    summary = {
        "compliance_pct": round(overall_compliance, 1),
        "active_hazards": max_hazards,
        "fire_events": fire_events,
        "smoke_events": smoke_events,
        "frames_total": frame_idx,
        "frames_processed": processed,
        "original_fps": round(fps, 2),
        "processing_fps": round(processed / elapsed, 2) if elapsed else 0,
        "processing_seconds": round(elapsed, 2),
        "duration_seconds": round(frame_idx / fps, 2) if fps else 0,
        "ffmpeg_used": ffmpeg_used,
        "timeline_events": timeline,
        "last_stats": last_stats,
    }
    with video_jobs_lock:
        video_jobs[job_id].update({"status": "completed", "progress": 100, "result": summary, "video_url": f"/uploads/{final_path.name}"})
    raw_path.unlink(missing_ok=True)


def process_video_wrapper(job_id, raw_path):
    try:
        process_video_job(job_id, raw_path)
    except Exception as exc:
        print(f"[VIDEO ERROR] {exc}")
        with video_jobs_lock:
            video_jobs[job_id].update({"status": "failed", "error": "Video processing failed. Check backend logs for details."})
        try: raw_path.unlink(missing_ok=True)
        except OSError: pass


@app.post("/api/detect/video")
@app.post("/upload_video")
async def upload_video(file: UploadFile = File(...)):
    validate_upload(file, ALLOWED_VIDEO_EXTENSIONS)
    data = await read_upload(file)
    job_id = uuid.uuid4().hex
    raw_path = UPLOAD_DIR / f"{job_id}_raw_{safe_name(file.filename, 'video.mp4')}"
    raw_path.write_bytes(data)
    with video_jobs_lock:
        video_jobs[job_id] = {"job_id": job_id, "status": "queued", "progress": 0, "filename": safe_name(file.filename)}
    executor.submit(process_video_wrapper, job_id, raw_path)
    return {"status": "processing", "job_id": job_id}


@app.get("/api/video/status/{job_id}")
def video_status(job_id: str):
    with video_jobs_lock:
        job = video_jobs.get(job_id)
        if not job: raise HTTPException(status_code=404, detail="Video job not found")
        return job


@app.get("/api/video/result/{job_id}")
def video_result(job_id: str):
    with video_jobs_lock:
        job = video_jobs.get(job_id)
    if not job: raise HTTPException(status_code=404, detail="Video job not found")
    if job["status"] != "completed": return job
    return job


@app.post("/api/detect/live")
async def detect_live(file: UploadFile = File(...)):
    global latest_live_stats
    data = await file.read(4 * 1024 * 1024)
    frame = cv2.imdecode(np.frombuffer(data, np.uint8), cv2.IMREAD_COLOR)
    if frame is None:
        raise HTTPException(status_code=400, detail="Invalid live frame")
    annotated, result = engine.process_frame(frame)
    latest_live_stats = result
    latest_live_stats["latency_ms"] = result["processing_ms"]
    apply_alerts(result, annotated, "live")
    ok, buf = cv2.imencode(".jpg", annotated, [cv2.IMWRITE_JPEG_QUALITY, 80])
    if not ok: raise HTTPException(status_code=500, detail="Could not encode live result")
    return {"image": "data:image/jpeg;base64," + base64.b64encode(buf).decode(), "stats": result}


def legacy_camera_stream():
    global latest_live_stats
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        return
    try:
        while True:
            ok, frame = cap.read()
            if not ok: break
            annotated, result = engine.process_frame(frame)
            latest_live_stats = result
            ok, buf = cv2.imencode(".jpg", annotated)
            if not ok: continue
            yield b"--frame\r\nContent-Type: image/jpeg\r\n\r\n" + buf.tobytes() + b"\r\n"
    finally:
        cap.release()


@app.get("/video_feed")
def video_feed():
    return StreamingResponse(legacy_camera_stream(), media_type="multipart/x-mixed-replace; boundary=frame")
