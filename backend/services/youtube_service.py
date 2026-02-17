import yt_dlp
from pathlib import Path
import hashlib
import json
import os
import subprocess
from ..config import DOWNLOAD_DIR, TRANSCRIPTIONS_DIR


def validate_audio_file(audio_path):
    """Validate that the audio file is not corrupted and can be processed."""
    if not audio_path.exists():
        return False, "Audio file does not exist"

    # Check file size
    file_size = audio_path.stat().st_size
    if file_size < 1024:  # Less than 1KB
        return (
            False,
            f"Audio file too small ({file_size} bytes) - video may be silent or have no audio track",
        )

    # Validate audio file with ffprobe - check if it actually has audio
    try:
        # Check duration
        duration_result = subprocess.run(
            [
                "ffprobe",
                "-v",
                "error",
                "-show_entries",
                "format=duration",
                "-of",
                "default=noprint_wrappers=1:nokey=1",
                str(audio_path),
            ],
            capture_output=True,
            text=True,
            timeout=10,
        )

        if duration_result.returncode != 0:
            return False, f"Invalid audio file (ffprobe failed)"

        duration_str = duration_result.stdout.strip()
        if not duration_str:
            return False, "Unable to read audio duration"

        duration = float(duration_str)
        if duration < 1.0:
            return (
                False,
                f"Audio too short for transcription ({duration:.1f}s) - minimum: 1 second",
            )
        if duration > 7200:
            return (
                False,
                f"Audio too long for efficient processing ({duration / 60:.1f} minutes) - maximum: 2 hours",
            )

        # Check if audio actually has content (stream info)
        stream_result = subprocess.run(
            [
                "ffprobe",
                "-v",
                "error",
                "-show_entries",
                "stream=codec_type,duration,nb_samples,codec_name",
                "-select_streams",
                "a:0",
                "-of",
                "default=noprint_wrappers=1=nokey=1",
                "-of",
                "json",
                str(audio_path),
            ],
            capture_output=True,
            text=True,
            timeout=10,
        )

        if stream_result.returncode == 0:
            stream_info = stream_result.stdout.strip()
            return True, f"Audio file valid, duration: {duration:.1f}s"
        else:
            return False, "Invalid audio stream - may be corrupted or silent"

    except subprocess.TimeoutExpired:
        return False, "Audio validation timeout"
    except ValueError:
        return False, "Invalid audio duration format"
    except Exception as e:
        print(f"Error validating audio: {e}")
        return False, f"Audio validation failed: {str(e)}"


def convert_to_mono_if_needed(audio_path):
    """Convert stereo audio to mono for better Whisper compatibility."""
    try:
        print(f"🔄 Checking if mono conversion needed: {audio_path}")

        # Check stream first to see if conversion is needed
        result = subprocess.run(
            [
                "ffprobe",
                "-v",
                "error",
                "-show_entries",
                "stream=channels,duration",
                "-select_streams",
                "a:0",
                "-of",
                "default=noprint_wrappers=1:nokey=1",
                str(audio_path),
            ],
            capture_output=True,
            text=True,
            timeout=10,
        )

        if result.returncode != 0:
            print(f"   ⚠️  Could not check audio channels")
            return False

        stream_info = result.stdout.strip().split("\n")
        if not stream_info or not stream_info[0]:
            print(f"   ⚠️  No audio stream info available")
            return False

        # Parse the stream info (format: channels\nduration)
        parts = (
            stream_info[0].split("|")
            if "|" in stream_info[0]
            else stream_info[0].split()
        )
        if len(parts) >= 2:
            channels = parts[0].strip()
            duration_val = parts[1].strip()

            # Convert to mono if not already mono
            if (
                channels
                and channels != "1"
                and channels != "unknown"
                and channels != "0"
            ):
                print(f"   Converting from {channels} channels to mono...")
                result = subprocess.run(
                    [
                        "ffmpeg",
                        "-i",
                        str(audio_path),
                        "-ac",
                        "1",
                        "-y",
                        str(audio_path),
                    ],
                    capture_output=True,
                    timeout=60,
                )
                if result.returncode == 0:
                    print(f"   ✓ Mono conversion successful")
                    return True
                else:
                    print(f"   ⚠️  Mono conversion failed: {result.stderr.strip()}")
                    return False
            else:
                print(f"   Audio is already mono or channel info unavailable")
                return True
        else:
            print(f"   Stream format unclear, attempting conversion anyway")
            result = subprocess.run(
                ["ffmpeg", "-i", str(audio_path), "-ac", "1", "-y", str(audio_path)],
                capture_output=True,
                timeout=60,
            )
            if result.returncode == 0:
                print(f"   ✓ Mono conversion attempted")
                return True
            else:
                print(f"   ⚠️  Mono conversion failed: {result.stderr.strip()}")
                return False

    except Exception as e:
        print(f"⚠️  Mono conversion error: {e}")
        return False

        # Check current audio properties
        result = subprocess.run(
            [
                "ffprobe",
                "-v",
                "error",
                "-show_entries",
                "stream=channels",
                "-select_streams",
                "a:0",
                "-of",
                "default=noprint_wrappers=1:nokey=1",
                str(audio_path),
            ],
            capture_output=True,
            text=True,
            timeout=10,
        )

        channels = result.stdout.strip()
        if channels and channels != "1" and channels != "0":
            print(f"🔄 Converting from {channels} channels to mono: {audio_path}")
            result = subprocess.run(
                ["ffmpeg", "-i", str(audio_path), "-ac", "1", "-y", str(audio_path)],
                capture_output=True,
                timeout=60,
            )
            if result.returncode == 0:
                print(f"✓ Mono conversion successful: {audio_path}")
                return True
            else:
                print(f"⚠️  Mono conversion failed: {result.stderr}")
                return False

        return True
    except Exception as e:
        print(f"⚠️  Mono conversion error: {e}")
        return False


def extract_video_id(url):
    if "youtube.com" in url or "youtu.be" in url:
        if "youtu.be" in url:
            return url.split("/")[-1]
        elif "v=" in url:
            return url.split("v=")[1].split("&")[0]
    return None


def download_audio(url, video_id=None):
    video_id = video_id or extract_video_id(url)
    if not video_id:
        raise ValueError("Invalid YouTube URL")

    audio_path = DOWNLOAD_DIR / f"{video_id}.mp3"
    metadata_path = DOWNLOAD_DIR / f"{video_id}_metadata.json"

    if audio_path.exists() and metadata_path.exists():
        with open(metadata_path, "r") as f:
            metadata = json.load(f)
        return audio_path, metadata

    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": str(DOWNLOAD_DIR / f"{video_id}.%(ext)s"),
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            },
            {
                "key": "FFmpegMetadata",
                "add_metadata": True,
            },
        ],
        "keepvideo": False,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)

    metadata = {
        "title": info.get("title", "Untitled"),
        "thumbnail": info.get("thumbnail", ""),
        "duration": info.get("duration", 0),
        "description": info.get("description", ""),
    }

    metadata_path = DOWNLOAD_DIR / f"{video_id}_metadata.json"
    with open(metadata_path, "w") as f:
        json.dump(metadata, f)

    return audio_path, metadata


def get_video_metadata(url):
    video_id = extract_video_id(url)
    if not video_id:
        return None

    metadata_path = DOWNLOAD_DIR / f"{video_id}_metadata.json"
    if metadata_path.exists():
        with open(metadata_path, "r") as f:
            return json.load(f)

    try:
        ydl_opts = {
            "quiet": True,
            "no_warnings": True,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)

            metadata = {
                "title": info.get("title", "Untitled"),
                "thumbnail": info.get("thumbnail", ""),
                "duration": info.get("duration", 0),
                "description": info.get("description", ""),
            }

            with open(metadata_path, "w") as f:
                json.dump(metadata, f)

            return metadata
    except Exception as e:
        print(f"Error fetching metadata: {e}")
        return None
