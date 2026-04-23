from app import create_app
from app.extensions import db

app = create_app()

    # Create tables at startup (Flask 3 compatible)
with app.app_context():
        db.create_all()

if __name__ == "__main__":
        app.run(
            host="127.0.0.1",
            port=5000,
            debug=True
        )