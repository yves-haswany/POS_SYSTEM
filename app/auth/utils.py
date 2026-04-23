from flask import redirect

def redirect_by_role(user):
    role = (user.role or "").strip().lower()

    if role == "admin":
        return redirect("/admin/dashboard")

    if role == "tenant":
        return redirect("/tenant/dashboard")

    if role == "branch":
        return redirect("/branch/pos")

    return redirect("/")