from pathlib import Path
import os

from dotenv import load_dotenv

# Project root
PROJECT_ROOT = Path(__file__).resolve().parents[2]

# Load .env from project root
load_dotenv(PROJECT_ROOT / ".env")

# ==========================================================
# Retry
# ==========================================================

MAX_RETRIES = 3
RETRY_DELAY = 5

# ==========================================================
# Validation
# ==========================================================

VALIDATION_DELAY = 10
DOWNLOAD_TIMEOUT = 300

# ==========================================================
# Frontend
# ==========================================================

FRONTEND_URL = "http://103.189.89.49:4300"

FRONTEND_USERNAME = os.getenv("KWALIFY_USERNAME")
FRONTEND_PASSWORD = os.getenv("KWALIFY_PASSWORD")

# ==========================================================
# Download Folder
# ==========================================================

DOWNLOAD_FOLDER = Path("downloads")
DOWNLOAD_FOLDER.mkdir(
    parents=True,
    exist_ok=True,
)