from flask import Blueprint, request
from flask_socketio import join_room, emit
from .. import socketio

ws_bp = Blueprint("ws", __name__)


@ws_bp.route("/connect")
def ws_connect():
    return "WebSocket endpoint"


@socketio.on("connect")
def handle_connect():
    emit("connected", {"message": "Connected to TubeScribe WebSocket"})


@socketio.on("disconnect")
def handle_disconnect():
    print("Client disconnected")


@socketio.on("join_video")
def handle_join_video(data):
    video_id = data.get("video_id")
    if video_id:
        room = f"video_{video_id}"
        join_room(room)
        emit("joined", {"video_id": video_id, "room": room})


@socketio.on("leave_video")
def handle_leave_video(data):
    video_id = data.get("video_id")
    if video_id:
        room = f"video_{video_id}"
        emit("left", {"video_id": video_id})


@socketio.on("subscribe_all")
def handle_subscribe_all():
    emit("subscribed_all", {"message": "Subscribed to all updates"})
