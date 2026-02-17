# TubeScribe Quick Start Guide

Get TubeScribe up and running in 5 minutes!

## Prerequisites

- Python 3.9+
- Node.js 18+
- FFmpeg
- Ollama

## One-Command Setup (Linux/macOS)

```bash
./setup.sh
```

This script will:
- Check all prerequisites
- Create virtual environment
- Install all dependencies
- Download Ollama model
- Create configuration files

## Manual Setup

### 1. Install FFmpeg

**Ubuntu/Debian:**
```bash
sudo apt update && sudo apt install ffmpeg
```

**macOS:**
```bash
brew install ffmpeg
```

### 2. Install Ollama

Download from [ollama.ai](https://ollama.ai), then:

```bash
ollama serve
ollama pull llama3
```

### 3. Backend Setup

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

### 4. Frontend Setup

```bash
cd frontend
npm install
cd ..
```

## Running the Application

Open **3 terminals**:

### Terminal 1 - Ollama
```bash
ollama serve
```

### Terminal 2 - Backend
```bash
source venv/bin/activate
python app.py
```

### Terminal 3 - Frontend
```bash
cd frontend
npm run dev
```

## Using TubeScribe

1. Open browser to `http://localhost:5173`
2. Paste YouTube URLs (one per line)
3. Click "Add Videos"
4. Watch real-time processing
5. View AI summaries and categories!

## Quick Test

Try these sample URLs:
```
https://www.youtube.com/watch?v=dQw4w9WgXcQ
https://www.youtube.com/watch?v=jNQXAC9IVRw
```

## Troubleshooting

**Ollama not connected?**
```bash
ollama list  # Check if running
ollama pull llama3  # Download model
```

**FFmpeg not found?**
```bash
ffmpeg -version  # Verify installation
```

**Port in use?**
Edit `.env` and change `FLASK_PORT=5001`

## Next Steps

- Read full [README.md](README.md) for detailed documentation
- Customize models in `.env`
- Adjust Whisper model size for speed/accuracy tradeoff

Enjoy summarizing YouTube videos with AI! 🚀