# SafeScan360 — Two-Model Industrial Safety Monitoring

SafeScan360 is the existing React/Vite + FastAPI application modified to use two trained YOLO models together:

- `best.pt` — PPE/safety model
- `Fire_smoke.pt` — Fire + Smoke model

The application supports image analysis, background video auditing, browser-camera live detection, incident alerts, dashboard statistics, and CUDA/CPU fallback.

## Architecture

```text
Image / Video / Browser Camera
          |
          v
  Persistent FastAPI Engine
       /          \
   best.pt      Fire_smoke.pt
      |              |
      +------ + -----+
             |
      Safety decision engine
             |
   annotations / stats / alerts
             |
        React dashboard
```

## Project structure

```text
Update_safescane360/
├── backend/
│   ├── config.py
│   ├── detection_engine.py
│   └── main.py
├── frontend-react/
│   └── src/
├── best.pt
├── Fire_smoke.pt
├── requirements.txt
└── .env.example
```

## Models

The runtime inspects model class dictionaries at startup. The supplied checkpoints contain the PPE classes:

`helmet, gloves, vest, boots, goggles, Person, no_helmet, no_goggle, no_gloves, no_boots`

and the fire/smoke checkpoint contains:

`smoke, fire`

The application does not replace or retrain these models.

## Backend

Recommended Python: **3.11 or 3.12**.

```powershell
cd Update_safescane360
python -m venv .venv
.\.venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

Check:

- `http://127.0.0.1:8000/api/health`
- `http://127.0.0.1:8000/api/models/status`

## Frontend

Recommended Node.js: **20 LTS or newer**.

```powershell
cd frontend-react
npm install
npm run dev
```

Open the Vite URL shown in the terminal, normally `http://127.0.0.1:5173`.

## Configuration

Copy `.env.example` to `.env` if desired.

Important settings:

- `PPE_CONFIDENCE=0.25`
- `FIRE_CONFIDENCE=0.25`
- `SMOKE_CONFIDENCE=0.25`
- `IMG_SIZE=640`
- `FRAME_SKIP=1`
- `LIVE_FPS=8`
- `MAX_UPLOAD_SIZE_MB=500`
- `DEVICE=auto`

The thresholds are configurable. They should be tuned using a validation set rather than lowered just to increase detection counts.

## PPE compliance logic

A worker is not marked as missing helmet, vest, gloves, boots, or goggles merely because a positive gear box is absent.

A PPE violation is generated when the PPE model supplies an explicit `no_*` detection spatially associated with that worker. Positive PPE detections are also associated to workers using bounding-box overlap/center containment so gear from another worker is not automatically assigned.

## Video processing

Video jobs are processed in a background worker.

```text
POST /api/detect/video
        |
      job_id
        |
GET /api/video/status/{job_id}
        |
   completed
        |
GET /api/video/result/{job_id}
```

Supported uploads: MP4, AVI, MOV, MKV.

FFmpeg is used when available to create browser-compatible H.264 MP4 output with `yuv420p` and `faststart`. If FFmpeg is unavailable, the OpenCV MP4V output is retained as a local fallback and the job result reports `ffmpeg_used: false`.

### Windows FFmpeg

Install a Windows x64 FFmpeg build and add its `bin` directory to PATH. Restart the terminal after changing PATH.

Verify:

```powershell
ffmpeg -version
```

## GPU / CPU

`DEVICE=auto` selects CUDA when PyTorch reports an NVIDIA CUDA device; otherwise the application uses CPU.

For NVIDIA GPU support, install a PyTorch build compatible with your CUDA driver and verify:

```powershell
python -c "import torch; print(torch.cuda.is_available()); print(torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'CPU')"
```

To force CPU:

```text
DEVICE=cpu
```

## Live camera

The Live Detection page uses the **browser camera**, not a fake camera stream. Grant camera permission in the browser. Frames are resized and JPEG-compressed before being sent to `/api/detect/live` so stale frame queues are avoided.

## API

- `GET /api/health`
- `GET /api/models/status`
- `POST /api/detect-image`
- `POST /api/detect/video`
- `GET /api/video/status/{job_id}`
- `GET /api/video/result/{job_id}`
- `POST /api/detect/live`
- `GET /api/live-stats`
- `GET /api/stats`
- `GET /api/incidents`
- `DELETE /api/incidents/{incident_id}`

## Alerts

- Fire → CRITICAL
- Smoke → HIGH
- Multiple PPE violations → HIGH
- Single PPE violation → MEDIUM

Repeated events are debounced by source/type and cooldown so a persistent fire does not create an alert on every frame.

## Troubleshooting

### `Video processing failed`
Check the FastAPI terminal. Verify the input codec is readable by OpenCV and run `ffmpeg -version`.

### Processed video does not play
Use a current Chrome/Edge browser. Ensure FFmpeg is installed so the H.264 fallback conversion can run.

### `FFmpeg not found`
Add the Windows x64 FFmpeg `bin` folder to PATH and restart the terminal.

### CUDA unavailable
The application automatically falls back to CPU. Verify PyTorch/CUDA separately before forcing `DEVICE=cuda:0`.

### Model not found
Keep both `best.pt` and `Fire_smoke.pt` in the project root next to `requirements.txt`.

### Camera unavailable
Grant browser camera permission and close other applications that are using the webcam.

### Frontend cannot reach backend
Run FastAPI on port 8000 and Vite on port 5173. The Vite development proxy forwards `/api`, `/uploads`, `/upload_video`, and `/video_feed` to FastAPI.

## Measurement honesty

Dashboard FPS and latency values come from actual processing measurements returned by the backend. No fixed FPS or accuracy number is hardcoded as a model-performance claim.

## Email alerts

Configure `.env` from `.env.example` with the receiver address and Gmail/SMTP credentials. When an explicit PPE violation, fire, or smoke event is detected, SafeScan360 captures the annotated evidence frame and queues an email with the event details and image attachment. Email sending runs in a background worker so live/video inference is not blocked by SMTP. Alerts are debounced with `ALERT_COOLDOWN_SECONDS`.

### Live camera behavior

The Live Detection page uses the browser camera. **Start Camera** requests camera permission, starts the camera, captures frames continuously, and sends controlled JPEG frames to `/api/detect/live` for both-model analysis. Detected violations/fire/smoke create incident evidence and queue email alerts. **Stop** stops the browser media tracks and the frame-analysis timer. No camera recording continues after Stop.

