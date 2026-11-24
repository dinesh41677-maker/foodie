"""Login / admin protection for routes."""
from functools import wraps

from flask import abort, flash, g, jsonify, redirect, request, url_for


def login_required(view):
    @wraps(view)
    def wrapper(*args, **kwargs):
        if not g.user:
            if request.path.startswith("/api/"):
                return jsonify(error="Please log in first."), 401
            flash("Please log in to continue.", "info")
            return redirect(url_for("auth.login", next=request.full_path.rstrip("?")))
        return view(*args, **kwargs)

    return wrapper


def admin_required(view):
    @wraps(view)
    @login_required
    def wrapper(*args, **kwargs):
        if g.user["role"] != "admin":
            abort(403)
        return view(*args, **kwargs)

    return wrapper
