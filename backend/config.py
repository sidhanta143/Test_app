import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")
UPLOAD_DIR = BASE_DIR / "uploads"
INCIDENT_DIR = UPLOAD_DIR / "incidents"
UPLOAD_DIR.mkdir(exist_ok=True)
INCIDENT_DIR.mkdir(exist_ok=True)

PPE_MODEL_PATH = BASE_DIR / "best.pt"
FIRE_SMOKE_MODEL_PATH = BASE_DIR / "Fire_smoke.pt"

PPE_CONFIDENCE = float(os.getenv("PPE_CONFIDENCE", "0.25"))
FIRE_CONFIDENCE = float(os.getenv("FIRE_CONFIDENCE", "0.25"))
SMOKE_CONFIDENCE = float(os.getenv("SMOKE_CONFIDENCE", "0.25"))
IMG_SIZE = int(os.getenv("IMG_SIZE", "640"))
FRAME_SKIP = max(1, int(os.getenv("FRAME_SKIP", "1")))
LIVE_FPS = max(1, int(os.getenv("LIVE_FPS", "8")))
LIVE_JPEG_QUALITY = int(os.getenv("LIVE_JPEG_QUALITY", "80"))
MAX_UPLOAD_SIZE_MB = int(os.getenv("MAX_UPLOAD_SIZE_MB", "500"))
DEVICE = os.getenv("DEVICE", "auto").strip().lower()

CONTINUOUS_VIOLATION_SECONDS = float(os.getenv("CONTINUOUS_VIOLATION_SECONDS", "2.0"))
ALERT_COOLDOWN_SECONDS = float(os.getenv("ALERT_COOLDOWN_SECONDS", "10"))
INCIDENT_RETENTION_HOURS = float(os.getenv("INCIDENT_RETENTION_HOURS", "24"))

ALERT_EMAIL_TO = os.getenv("ALERT_EMAIL_TO", "")
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "465"))
SMTP_USERNAME = os.getenv("SMTP_USERNAME", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")

ALLOWED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
ALLOWED_VIDEO_EXTENSIONS = {".mp4", ".avi", ".mov", ".mkv"}

COLOR_SAFE = (0, 210, 80)
COLOR_WARNING = (0, 165, 255)
COLOR_HAZARD = (0, 60, 255)
COLOR_INFO = (255, 180, 0)

