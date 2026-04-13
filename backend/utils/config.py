import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).parent.parent
UPLOAD_DIR = BASE_DIR / "uploads"
OUTPUT_DIR = BASE_DIR / "output"
TEMP_DIR = BASE_DIR / "temp"
DATA_DIR = BASE_DIR / "data"
RAW_JSON_DIR = OUTPUT_DIR / "raw_json"
PROCESSED_JSON_DIR = OUTPUT_DIR / "processed_json"
PPT_DIR = OUTPUT_DIR / "ppt"
SIMILAR_QUESTIONS_DIR = OUTPUT_DIR / "similar_questions"

for dir_path in [UPLOAD_DIR, OUTPUT_DIR, TEMP_DIR, RAW_JSON_DIR, PROCESSED_JSON_DIR, PPT_DIR, SIMILAR_QUESTIONS_DIR]:
    dir_path.mkdir(parents=True, exist_ok=True)

API_URL = os.getenv("API_URL", "https://api.deepseek.com/v1")
API_KEY = os.getenv("API_KEY", "")
TOKEN = os.getenv("token", "")

ALLOWED_EXTENSIONS = {".pdf", ".png", ".jpg", ".jpeg"}
MAX_FILE_SIZE = 50 * 1024 * 1024