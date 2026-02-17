from flask import Blueprint, request, jsonify
from ..models.database import db, Video, Category
from ..services.youtube_service import (
    extract_video_id,
    download_audio,
    get_video_metadata,
)
from ..services.transcribe_service import transcribe_audio
from ..services.summarize_service import summarize_transcript
from ..services.categorize_service import auto_categorize_video
from ..utils.progress_tracker import ProgressTracker
from .. import socketio, get_app
from ..config import DOWNLOAD_DIR
import threading
import traceback
import os

api_bp = Blueprint("api", __name__)
processing_tasks = {}


def _process_video_thread(video_id, video_url):
    app = get_app()
    if app is None:
        print("Error: Flask app not initialized")
        video = Video.query.get(video_id)
        if video:
            video.status = "error"
            video.current_step = "Error"
            video.error_message = "Flask app not initialized"
            db.session.commit()
        return

    with app.app_context():
        try:
            print(f"🎬 Starting video processing: {video_id}")
            tracker = processing_tasks[video_id]

            tracker.set_status("processing", "Downloading audio...", 5)

            try:
                audio_path, metadata = download_audio(video_url)
                video = Video.query.get(video_id)
                video.title = metadata.get("title", "Untitled")
                video.thumbnail_url = metadata.get("thumbnail", "")
                video.status = "processing"
                video.current_step = "Downloading audio..."
                video.progress = 15
                db.session.commit()
                print(f"✓ Download complete for video {video_id}")
            except Exception as e:
                raise Exception(f"Download failed: {str(e)}")

            tracker.set_status("processing", "Transcribing audio...", 35)

            video = Video.query.get(video_id)
            video.current_step = "Transcribing audio..."
            video.progress = 35
            db.session.commit()

            try:
                transcript, _ = transcribe_audio(
                    audio_path, extract_video_id(video_url)
                )
            except Exception as e:
                error_msg = str(e)
                # If transcription fails due to corrupted audio, delete and mark for retry
                if (
                    "corrupted" in error_msg.lower()
                    or "validation failed" in error_msg.lower()
                ):
                    try:
                        if audio_path.exists():
                            os.remove(audio_path)
                        metadata_path = (
                            DOWNLOAD_DIR
                            / f"{extract_video_id(video_url)}_metadata.json"
                        )
                        if metadata_path.exists():
                            os.remove(metadata_path)
                        print(f"Deleted corrupted audio file: {audio_path}")
                    except Exception as cleanup_error:
                        print(f"Cleanup error: {cleanup_error}")

                raise Exception(f"Transcription failed: {error_msg}")

            tracker.set_status("processing", "Generating summary...", 65)

            try:
                video = Video.query.get(video_id)
                video.current_step = "Generating summary..."
                video.progress = 65
                db.session.commit()

                summary = summarize_transcript(transcript, video.title)
                video.summary = summary
                video.progress = 75
                db.session.commit()
                print(f"✓ Summary generated for video {video_id}")
            except Exception as e:
                raise Exception(f"Summary generation failed: {str(e)}")

            tracker.set_status("processing", "Categorizing video...", 85)

            video = Video.query.get(video_id)
            video.current_step = "Categorizing video..."
            video.progress = 85
            db.session.commit()

            try:
                category = auto_categorize_video(video.title, video.summary)
                if category:
                    video.category_id = category.id
                    print(f"✓ Category assigned: {category.name} for video {video_id}")
            except Exception as e:
                print(f"Categorization warning: {e}")

            tracker.set_status("completed", "Complete!", 100)

            video = Video.query.get(video_id)
            video.status = "completed"
            video.current_step = "Complete"
            video.progress = 100
            db.session.commit()
            print(f"✓ Video processing complete for video {video_id}")

        except Exception as e:
            print(f"Error processing video {video_id}: {str(e)}")
            traceback.print_exc()

            if video_id in processing_tasks:
                tracker = processing_tasks[video_id]
                tracker.set_status("error", f"Error: {str(e)}", 0)

            video = Video.query.get(video_id)
            if video:
                video.status = "error"
                video.current_step = "Error"
                video.error_message = str(e)
                db.session.commit()

        finally:
            if video_id in processing_tasks:
                del processing_tasks[video_id]


@api_bp.route("/videos", methods=["GET"])
def get_videos():
    category_id = request.args.get("category_id", type=int)

    query = Video.query.order_by(Video.created_at.desc())

    if category_id:
        query = query.filter_by(category_id=category_id)

    videos = query.all()
    return jsonify([v.to_dict() for v in videos])


@api_bp.route("/videos/<int:video_id>", methods=["GET"])
def get_video(video_id):
    video = Video.query.get_or_404(video_id)
    return jsonify(video.to_dict())


@api_bp.route("/videos", methods=["POST"])
def add_videos():
    data = request.get_json()
    urls = data.get("urls", [])

    if not urls:
        return jsonify({"error": "No URLs provided"}), 400

    created_videos = []

    for url in urls:
        url = url.strip()
        if not url:
            continue

        if not extract_video_id(url):
            continue

        existing = Video.query.filter_by(youtube_url=url).first()
        if existing:
            created_videos.append(existing.to_dict())
            continue

        metadata = get_video_metadata(url)
        title = metadata.get("title", "Untitled") if metadata else "Processing..."
        thumbnail_url = metadata.get("thumbnail", "") if metadata else ""

        video = Video(
            youtube_url=url,
            title=title,
            thumbnail_url=thumbnail_url,
            status="queued",
            current_step="Waiting to start...",
            progress=0,
        )

        db.session.add(video)
        db.session.commit()

        # Emit video status to WebSocket immediately
        progress = processing_tasks[video.id] = ProgressTracker(video.id, socketio)
        progress.set_status("queued", "Waiting to start...", 0)

        thread = threading.Thread(target=_process_video_thread, args=(video.id, url))
        thread.daemon = True
        thread.start()

        created_videos.append(video.to_dict())

    return jsonify({"videos": created_videos}), 201


@api_bp.route("/videos/<int:video_id>", methods=["DELETE"])
def delete_video(video_id):
    video = Video.query.get_or_404(video_id)
    db.session.delete(video)
    db.session.commit()
    return jsonify({"message": "Video deleted successfully"})


@api_bp.route("/categories", methods=["GET"])
def get_categories():
    categories = Category.query.all()
    return jsonify([c.to_dict() for c in categories])


@api_bp.route("/categories", methods=["POST"])
def create_category():
    data = request.get_json()
    name = data.get("name")

    if not name:
        return jsonify({"error": "Category name is required"}), 400

    existing = Category.query.filter_by(name=name).first()
    if existing:
        return jsonify(existing.to_dict()), 200

    category = Category(
        name=name,
        description=data.get("description", ""),
        color=data.get("color", "#3B82F6"),
    )

    db.session.add(category)
    db.session.commit()

    return jsonify(category.to_dict()), 201


@api_bp.route("/stats", methods=["GET"])
def get_stats():
    total_videos = Video.query.count()
    completed_videos = Video.query.filter_by(status="completed").count()
    processing_videos = Video.query.filter_by(status="processing").count()
    error_videos = Video.query.filter_by(status="error").count()
    total_categories = Category.query.count()

    return jsonify(
        {
            "total_videos": total_videos,
            "completed_videos": completed_videos,
            "processing_videos": processing_videos,
            "error_videos": error_videos,
            "total_categories": total_categories,
        }
    )
