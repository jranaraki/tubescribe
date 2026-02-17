from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


class Category(db.Model):
    __tablename__ = "categories"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=True)
    color = db.Column(db.String(7), default="#3B82F6")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    videos = db.relationship(
        "Video", backref="category", lazy=True, cascade="all, delete-orphan"
    )

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "color": self.color,
            "created_at": self.created_at.isoformat(),
            "video_count": len(self.videos),
        }


class Video(db.Model):
    __tablename__ = "videos"

    id = db.Column(db.Integer, primary_key=True)
    youtube_url = db.Column(db.String(500), unique=True, nullable=False, index=True)
    title = db.Column(db.String(500), nullable=False)
    thumbnail_url = db.Column(db.String(500), nullable=True)
    transcript_path = db.Column(db.String(500), nullable=True)
    summary = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), default="queued")
    current_step = db.Column(db.String(50), nullable=True)
    progress = db.Column(db.Integer, default=0)
    error_message = db.Column(db.Text, nullable=True)

    category_id = db.Column(db.Integer, db.ForeignKey("categories.id"), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    def to_dict(self):
        return {
            "id": self.id,
            "youtube_url": self.youtube_url,
            "title": self.title,
            "thumbnail_url": self.thumbnail_url,
            "transcript_path": self.transcript_path,
            "summary": self.summary,
            "status": self.status,
            "current_step": self.current_step,
            "progress": self.progress,
            "error_message": self.error_message,
            "category": self.category.to_dict() if self.category else None,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }

    def update_status(
        self, status, current_step=None, progress=None, error_message=None
    ):
        self.status = status
        if current_step:
            self.current_step = current_step
        if progress is not None:
            self.progress = progress
        if error_message:
            self.error_message = error_message
        db.session.commit()
