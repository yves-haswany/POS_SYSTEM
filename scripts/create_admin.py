from app import create_app, db
from app.modules.users.models import User
from werkzeug.security import generate_password_hash

app = create_app()

with app.app_context():

    username = "admin"
    password = "admin"

    # prevent duplicates
    existing = User.query.filter_by(username=username).first()
    if existing:
        print("Admin already exists")
        exit()

    admin = User(
        username=username,
        password=generate_password_hash(password),
        role="admin",
        tenant_id=1  # or None if your schema allows
    )

    db.session.add(admin)
    db.session.commit()

    print("Admin created successfully")