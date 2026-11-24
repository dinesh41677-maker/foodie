import secrets
import time

from flask import Blueprint, flash, g, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

from models import address_model, cart_model, user_model
from utils.decorators import login_required
from utils.validators import (clean, password_error, safe_next, valid_email, valid_name,
                              valid_phone, valid_pincode)

bp = Blueprint("auth", __name__)

# Very simple brute-force guard (kept in memory, resets when the server restarts)
_FAILS = {}
MAX_FAILS, WINDOW = 5, 600


def _blocked(email):
    now = time.time()
    _FAILS[email] = [t for t in _FAILS.get(email, []) if now - t < WINDOW]
    return len(_FAILS[email]) >= MAX_FAILS


def _log_in(user):
    guest_items = cart_model.raw_items(None)  # session cart, read before we reset the session
    session.clear()
    session["csrf"] = secrets.token_hex(16)
    session["user_id"] = user["id"]
    cart_model.merge_guest_cart(user["id"], guest_items)


@bp.route("/register", methods=["GET", "POST"])
def register():
    if g.user:
        return redirect(url_for("main.menu"))
    form = {}
    if request.method == "POST":
        form = {"name": clean(request.form.get("name"), 80),
                "email": clean(request.form.get("email"), 120).lower(),
                "phone": clean(request.form.get("phone"), 15)}
        password = request.form.get("password", "")
        errors = []
        if not valid_name(form["name"]):
            errors.append("Enter your name (2 to 80 characters).")
        if not valid_email(form["email"]):
            errors.append("Enter a valid email address.")
        if not valid_phone(form["phone"]):
            errors.append("Enter a valid 10 digit mobile number.")
        pw_err = password_error(password)
        if pw_err:
            errors.append(pw_err)
        if password != request.form.get("confirm", ""):
            errors.append("Passwords do not match.")
        if not errors and user_model.get_by_email(form["email"]):
            errors.append("This email is already registered. Please log in.")
        if errors:
            for e in errors:
                flash(e, "error")
        else:
            uid = user_model.create(form["name"], form["email"], form["phone"],
                                    generate_password_hash(password))
            _log_in({"id": uid})
            flash("Welcome to Foodie! Your account is ready.", "success")
            return redirect(url_for("main.menu"))
    return render_template("auth/register.html", form=form)


@bp.route("/login", methods=["GET", "POST"])
def login():
    if g.user:
        return redirect(url_for("main.menu"))
    next_url = safe_next(request.values.get("next"))
    if request.method == "POST":
        email = clean(request.form.get("email"), 120).lower()
        password = request.form.get("password", "")
        if _blocked(email):
            flash("Too many failed attempts. Please try again in 10 minutes.", "error")
        else:
            user = user_model.get_by_email(email)
            if user and check_password_hash(user["password_hash"], password):
                if not user["is_active"]:
                    flash("This account has been deactivated. Please contact support.", "error")
                else:
                    _FAILS.pop(email, None)
                    _log_in(user)
                    flash(f"Welcome back, {user['name'].split()[0]}!", "success")
                    if user["role"] == "admin" and not next_url:
                        return redirect(url_for("admin.dashboard"))
                    return redirect(next_url or url_for("main.menu"))
            else:
                _FAILS.setdefault(email, []).append(time.time())
                flash("Wrong email or password.", "error")
    return render_template("auth/login.html", next_url=next_url)


@bp.post("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("main.menu"))


@bp.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    if request.method == "POST":
        name = clean(request.form.get("name"), 80)
        phone = clean(request.form.get("phone"), 15)
        if not valid_name(name):
            flash("Enter your name (2 to 80 characters).", "error")
        elif not valid_phone(phone):
            flash("Enter a valid 10 digit mobile number.", "error")
        else:
            user_model.update_profile(g.user["id"], name, phone)
            flash("Profile updated.", "success")
            return redirect(url_for("auth.profile"))
    return render_template("auth/profile.html", addresses=address_model.list_for_user(g.user["id"]))


@bp.post("/profile/password")
@login_required
def change_password():
    current = request.form.get("current", "")
    new = request.form.get("new", "")
    if not check_password_hash(user_model.get_password_hash(g.user["id"]), current):
        flash("Current password is wrong.", "error")
    elif password_error(new):
        flash(password_error(new), "error")
    elif new != request.form.get("confirm", ""):
        flash("New passwords do not match.", "error")
    else:
        user_model.update_password(g.user["id"], generate_password_hash(new))
        flash("Password changed.", "success")
    return redirect(url_for("auth.profile"))


@bp.post("/profile/address/add")
@login_required
def add_address():
    label = clean(request.form.get("label"), 30) or "Home"
    line = clean(request.form.get("address_line"), 255)
    city = clean(request.form.get("city"), 60)
    pincode = clean(request.form.get("pincode"), 6)
    if len(line) < 5 or len(city) < 2:
        flash("Enter a full address and city.", "error")
    elif not valid_pincode(pincode):
        flash("Enter a valid 6 digit pincode.", "error")
    else:
        address_model.create(g.user["id"], label, line, city, pincode)
        flash("Address saved.", "success")
    return redirect(url_for("auth.profile"))


@bp.post("/profile/address/<int:address_id>/delete")
@login_required
def delete_address(address_id):
    address_model.delete(g.user["id"], address_id)
    flash("Address removed.", "info")
    return redirect(url_for("auth.profile"))
