from flask import Blueprint, redirect, url_for, abort,request
from flask_login import login_required, current_user

from app.extensions import db
from app.modules.notifications.models import Notification

notifications_bp = Blueprint(
    "notifications",
    __name__,
    url_prefix="/notifications"
)


# =====================================================
# 🔹 MARK SINGLE NOTIFICATION AS READ
# =====================================================
@notifications_bp.route("/<int:id>/read", methods=["POST"])
@login_required
def mark_read(id):

    notification = Notification.query.get_or_404(id)

    if notification.user_id != current_user.id:
        abort(403)

    notification.is_read = True

    db.session.commit()

    return redirect(request.referrer or url_for("dashboard.index"))


# =====================================================
# 🔹 MARK ALL AS READ
# =====================================================
@notifications_bp.route("/read-all", methods=["POST"])
@login_required
def mark_all_read():

    Notification.query.filter_by(
        user_id=current_user.id,
        is_read=False
    ).update({
        "is_read": True
    })

    db.session.commit()

    return redirect(request.referrer or url_for("dashboard.index"))