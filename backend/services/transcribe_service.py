import whisper
from pathlib import Path
import json
import os
from .youtube_service import validate_audio_file, convert_to_mono_if_needed
from ..config import TRANSCRIPTIONS_DIR, WHISPER_MODEL

model = None


def load_model():
    global model
    if model is None:
        print(f"Loading Whisper model: {WHISPER_MODEL}")
        model = whisper.load_model(WHISPER_MODEL)
        print("Whisper model loaded successfully")
    return model


def transcribe_audio(audio_path, video_id, retry_count=3):
    """Transcribe audio with validation and retry logic."""
    audio_path = Path(audio_path)

    # Check if transcription already exists
    transcription_path = TRANSCRIPTIONS_DIR / f"{video_id}_transcription.json"
    if transcription_path.exists():
        try:
            with open(transcription_path, "r") as f:
                data = json.load(f)
                if data.get("text"):
                    return data["text"], data
        except Exception as e:
            print(f"Error reading cached transcription, will re-transcribe: {e}")

    model = load_model()

    for attempt in range(retry_count):
        try:
            # Validate audio file
            is_valid, validation_msg = validate_audio_file(audio_path)
            if not is_valid:
                print(f"❌ Audio validation failed: {validation_msg}")
                raise Exception(f"Audio validation failed: {validation_msg}")

            print(
                f"🎙️  Transcribing audio (attempt {attempt + 1}/{retry_count}): {audio_path}"
            )

            # Transcribe with error handling
            result = model.transcribe(
                str(audio_path),
                fp16=False,  # Use float32 for better compatibility
                language=None,  # Auto-detect language
            )

            if not result or not result.get("text"):
                raise Exception("Transcription returned empty result")

            transcribed_text = result["text"]

            if not transcribed_text or len(transcribed_text.strip()) == 0:
                print(f"⚠️  Empty transcribed text detected")
                raise Exception(
                    "Transcription returned empty text - the audio contains no speech content. "
                    "This often happens with: 1) Music videos 2) Silent videos 3) Videos with sound effects but no voice 4) Very short clips (< 5s). "
                    "Try a video with spoken narration."
                )

            transcription_data = {
                "text": transcribed_text,
                "segments": result.get("segments", []),
                "language": result.get("language", "unknown"),
            }

            # Cache the transcription
            with open(transcription_path, "w") as f:
                json.dump(transcription_data, f)

            print(
                f"✓ Transcription successful: {len(transcription_data['text'])} characters, language: {transcription_data['language']}"
            )
            return transcription_data["text"], transcription_data

        except RuntimeError as e:
            error_msg = str(e)
            if (
                "tensor size mismatch" in error_msg.lower()
                or "Expected key.size(1)" in error_msg
                or "Expected key.size(1) == value.size(1)" in error_msg
                or "0 elements" in error_msg
            ):
                print(
                    f"⚠️  Audio format issue detected (attempt {attempt + 1}/{retry_count})"
                )

                if attempt < retry_count - 1:
                    # Try to convert to mono and retry
                    print("🔄 Attempting: Re-encoding audio to mono format...")
                    print(f"   Current file size: {audio_path.stat().st_size} bytes")
                    converted = convert_to_mono_if_needed(audio_path)

                    if not converted:
                        # Conversion failed, give up
                        file_size = audio_path.stat().st_size
                        print(f"   ❌ Re-encoding failed. File size: {file_size} bytes")
                        raise Exception(
                            f"Video cannot be transcribed. The audio appears corrupted or empty (size: {file_size} bytes). "
                            "Common causes: 1) Silent videos with no speech 2) Very short videos (< 1 second) 3) Videos with audio track as music/sound effects but no narration. "
                            "Please try a different video with spoken content and narration."
                        )

                    # If conversion succeeded, validate again
                    print("🔍 Validating re-encoded audio...")
                    is_valid, validation_msg = validate_audio_file(audio_path)
                    print(f"   Re-encoded validation: {validation_msg}")

                    if not is_valid:
                        raise Exception(
                            f"Re-encoded audio still invalid: {validation_msg}"
                        )

                    # Retry with re-encoded audio
                    continue

                file_size = audio_path.stat().st_size
                raise Exception(
                    f"Transcription failed: Video has no detectable speech content "
                    f"(file size: {file_size} bytes). "
                    f"This happens with: silent videos, music videos, very short videos, or videos with no audio track. "
                    f"Please use a video with spoken narration."
                )

            raise Exception(f"Transcription failed: {str(e)}")

        except Exception as e:
            if attempt < retry_count - 1:
                print(f"Transcription attempt {attempt + 1} failed: {e}. Retrying...")
                continue

            raise Exception(
                f"Transcription failed after {retry_count} attempts: {str(e)}"
            )
