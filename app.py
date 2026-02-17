from backend import create_app, socketio
from backend.config import FLASK_HOST, FLASK_PORT, FLASK_DEBUG

app = create_app()

if __name__ == "__main__":
    print(f"Starting TubeScribe Flask server on {FLASK_HOST}:{FLASK_PORT}")
    socketio.run(
        app,
        host=FLASK_HOST,
        port=FLASK_PORT,
        debug=FLASK_DEBUG,
        allow_unsafe_werkzeug=True,
    )
