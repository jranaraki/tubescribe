import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
TRANSCRIPTIONS_DIR = BASE_DIR / "transcriptions"

DATA_DIR.mkdir(exist_ok=True)
TRANSCRIPTIONS_DIR.mkdir(exist_ok=True)

DATABASE_URL = f"sqlite:///{DATA_DIR / 'tubescribe.db'}"

# Ollama needs /v1 prefix for OpenAI-compatible API
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2:1b")
OLLAMA_CATEGORY_MODEL = os.getenv("OLLAMA_CATEGORY_MODEL", "llama3.2:1b")

WHISPER_MODEL = os.getenv("WHISPER_MODEL", "base")

FLASK_PORT = int(os.getenv("FLASK_PORT", 5000))
FLASK_HOST = os.getenv("FLASK_HOST", "0.0.0.0")
FLASK_DEBUG = os.getenv("FLASK_DEBUG", "True").lower() == "true"

CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://localhost:3000")

DOWNLOAD_DIR = DATA_DIR / "downloads"
DOWNLOAD_DIR.mkdir(exist_ok=True)
