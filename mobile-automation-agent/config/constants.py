from pathlib import Path

# Timeouts & Retries
DEFAULT_TIMEOUT = 10
MAX_RETRIES = 3
BACKOFF_FACTOR = 2

# Paths
DATA_DIR = Path("data")
LOGS_DIR = Path("logs")
CACHE_DIR = Path("cache")
SCREENSHOTS_DIR = DATA_DIR / "screenshots"
AUDIO_DIR = DATA_DIR / "audio"

# Ensure directories exist
for path in [DATA_DIR, LOGS_DIR, CACHE_DIR, SCREENSHOTS_DIR, AUDIO_DIR]:
    path.mkdir(parents=True, exist_ok=True)

# Audio
TTS_RATE_DEFAULT = 175
STT_TIMEOUT = 10

# Vision
OCR_CONFIDENCE_THRESHOLD = 0.7
FULL_SCREEN_BOUNDS = {"left": 0, "top": 0, "width": 1080, "height": 2400}

# Task Status
STATUS_PENDING = "pending"
STATUS_IN_PROGRESS = "in_progress"
STATUS_COMPLETED = "completed"
STATUS_FAILED = "failed"
