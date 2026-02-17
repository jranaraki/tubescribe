class ProgressTracker:
    def __init__(self, video_id, socketio):
        self.video_id = video_id
        self.socketio = socketio
        self.progress = {
            "video_id": video_id,
            "status": "queued",
            "current_step": "Initializing...",
            "progress": 0,
        }

    def emit_update(self):
        # Emit to all clients (no room specified = broadcast)
        try:
            self.socketio.emit(
                "all_updates", {"video_id": self.video_id, "data": self.progress}
            )
            self.socketio.emit("video_progress", self.progress)
        except Exception as e:
            print(f"Error emitting WebSocket update: {e}")

    def set_status(self, status, step=None, progress=None):
        self.progress["status"] = status
        if step:
            self.progress["current_step"] = step
        if progress is not None:
            self.progress["progress"] = progress
        self.emit_update()
