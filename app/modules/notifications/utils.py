from app.extensions import db
from app.modules.notifications.models import Notification

def create_notification(user_id, message, type="transfer"):
    notification = Notification(
        user_id=user_id,
        message=message,
        type=type
    )
    db.session.add(notification)
    db.session.commit()