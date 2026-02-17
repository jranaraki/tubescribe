#!/bin/bash

# TubeScribe Quick Setup Script
# This script helps set up the environment and run the application

set -e

echo "🎬 TubeScribe Setup Script"
echo "========================="
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.9 or higher."
    exit 1
fi

echo "✅ Python found: $(python3 --version)"

# Check Node.js
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 18 or higher."
    exit 1
fi

echo "✅ Node.js found: $(node --version)"

# Check FFmpeg
if ! command -v ffmpeg &> /dev/null; then
    echo "❌ FFmpeg is not installed. Please install FFmpeg."
    echo "   Ubuntu/Debian: sudo apt install ffmpeg"
    echo "   macOS: brew install ffmpeg"
    echo "   Windows: Download from https://ffmpeg.org/download.html"
    exit 1
fi

echo "✅ FFmpeg found: $(ffmpeg -version | head -n 1)"

# Check Ollama
if ! command -v ollama &> /dev/null; then
    echo "⚠️  Ollama is not installed. Please install from https://ollama.ai"
    read -p "Press Enter after installing Ollama to continue..."
fi

echo "✅ Ollama found: $(ollama --version)"

# Create virtual environment
if [ ! -d "venv" ]; then
    echo ""
    echo "📦 Creating Python virtual environment..."
    python3 -m venv venv
    echo "✅ Virtual environment created"
fi

# Activate virtual environment
echo ""
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install Python dependencies
echo ""
echo "📚 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
echo "✅ Python dependencies installed"

# Install frontend dependencies
echo ""
echo "📚 Installing frontend dependencies..."
cd frontend
npm install
cd ..
echo "✅ Frontend dependencies installed"

# Copy .env file
if [ ! -f ".env" ]; then
    echo ""
    echo "📝 Creating .env file..."
    cp .env.example .env
    echo "✅ .env file created"
fi

# Pull Ollama model
echo ""
echo "🤖 Checking Ollama model..."
if ! ollama list | grep -q "llama3"; then
    echo "⬇️  Pulling llama3 model from Ollama..."
    ollama pull llama3
    echo "✅ Model downloaded"
else
    echo "✅ llama3 model already available"
fi

echo ""
echo "========================="
echo "🎉 Setup Complete!"
echo "========================="
echo ""
echo "To run the application:"
echo ""
echo "1. Start the backend (Terminal 1):"
echo "   source venv/bin/activate"
echo "   python app.py"
echo ""
echo "2. Start the frontend (Terminal 2):"
echo "   cd frontend"
echo "   npm run dev"
echo ""
echo "3. Open your browser to: http://localhost:5173"
echo ""
echo "Make sure Ollama is running:"
echo "   ollama serve"
echo ""