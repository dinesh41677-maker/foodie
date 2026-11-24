"""Foodie - start here.   Run:  python app.py"""
import secrets

import mysql.connector
from flask import Flask, g, jsonify, render_template, request, session, abort

from config import Config
from extensions import close_db


def create_app():
    import os
    from models import user_model
    from utils.upload import image_url

    app = Flask(__name__)
    app.config.from_object(Config)
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
    app.teardown_appcontext(close_db)

    from routes import admin, auth, cart, checkout, main, menu_api, orders
    for module in (main, menu_api, cart, auth, checkout, orders, admin):
        app.register_blueprint(module.bp)

    @app.before_request
    def load_user_and_check_csrf():
        if request.endpoint == "static":
            return
        g.user = None
        user_id = session.get("user_id")
        if user_id:
            user = user_model.get_by_id(user_id)
            if user and user["is_active"]:
                g.user = user
            else:
                session.clear()
        if "csrf" not in session:
            session["csrf"] = secrets.token_hex(16)
        if request.method == "POST":
            token = request.form.get("csrf_token") or request.headers.get("X-CSRF-Token") or ""
            if not secrets.compare_digest(token, session["csrf"]):
                abort(400, "Your session expired. Please refresh the page and try again.")

    @app.context_processor
    def inject_globals():
        return {"csrf_token": session.get("csrf", ""), "current_user": getattr(g, "user", None),
                "image_url": image_url}

    @app.template_filter("inr")
    def inr(value):
        value = float(value or 0)
        return f"₹{int(value):,}" if value == int(value) else f"₹{value:,.2f}"

    def _error(code, title, message):
        if request.path.startswith("/api/"):
            return jsonify(error=message), code
        return render_template("errors/error.html", code=code, title=title, message=message), code

    @app.errorhandler(400)
    def bad_request(e):
        return _error(400, "Request problem", getattr(e, "description", "Bad request."))

    @app.errorhandler(403)
    def forbidden(_e):
        return _error(403, "Not allowed", "You do not have permission to open this page.")

    @app.errorhandler(404)
    def not_found(_e):
        return _error(404, "Page not found", "We could not find what you were looking for.")

    @app.errorhandler(413)
    def too_large(_e):
        return _error(413, "File too large", "The image must be smaller than 2 MB.")

    @app.errorhandler(mysql.connector.Error)
    def db_error(e):
        app.logger.exception("Database error: %s", e)
        return _error(500, "Database problem",
                      "Could not talk to MySQL. Check that MySQL is running and the .env settings are correct.")

    @app.errorhandler(500)
    def server_error(_e):
        return _error(500, "Something went wrong", "Please try again in a moment.")

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
