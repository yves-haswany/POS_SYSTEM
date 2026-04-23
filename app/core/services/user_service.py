from werkzeug.security import generate_password_hash
from app.extensions import db
from app.core.models.user import User


def create_user(username, password, role, tenant_id=None, location_id=None):
    user = User(
        username=username,
        password=generate_password_hash(password),
        role=role.strip().lower(),
        tenant_id=tenant_id,
        location_id=location_id
    )

    db.session.add(user)
    db.session.commit()
    return user