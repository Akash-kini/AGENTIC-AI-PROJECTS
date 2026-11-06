

import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

_PLACEHOLDER_KEYS = {"", "your_gemini_api_key_here", "your_api_key_here"}
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip().strip('"').strip("'")
API_KEY_IS_SET = GEMINI_API_KEY.lower() not in _PLACEHOLDER_KEYS

MODEL_NAME = os.getenv("GEMINI_MODEL", "gemini-3.6-flash").strip()

FALLBACK_MODELS = ["gemini-flash-latest", "gemini-2.5-flash"]

TEMPERATURE = 0.4

MAX_RETRIES = 3
RETRY_BASE_DELAY_SECONDS = 3

OUTPUT_DIR = BASE_DIR / "output"

MAX_NAME_LENGTH = 80
MAX_FIELD_LENGTH = 120
MAX_LIST_ITEMS = 30
