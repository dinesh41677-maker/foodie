from decimal import Decimal, InvalidOperation

from flask import (Blueprint, abort, flash, g, redirect, render_template, request, url_for)

from models import (addon_model, category_model, food_item_model, order_model, user_model)
from utils.upload import delete_image, save_image
from utils.validators import clean, to_int

bp = Blueprint("admin", __name__, url_prefix="/admin")


@bp.before_request
def guard():
    """Every admin page needs an admin login."""
    if not g.user:
        flash("Please log in as admin.", "info")
        return redirect(url_for("auth.login", next=request.path))
    if g.user["role"] != "admin":
        abort(403)


def _money(value, label, errors, allow_zero=False):
    try:
        d = Decimal(str(value).strip())
    except (InvalidOperation, AttributeError):
        errors.append(f"{label} must be a number.")
        return None
    if d < 0 or (d == 0 and not allow_zero) or d > Decimal("99999"):
        errors.append(f"{label} must be between 1 and 99999.")
        return None
    return d.quantize(Decimal("0.01"))


# ---------- dashboard ----------
@bp.route("/")
def dashboard():
    return render_template("admin/dashboard.html", stats=order_model.stats(),
                           users=user_model.count(), foods=food_item_model.count(),
                           recent=order_model.list_all(limit=8))


# ---------- foods ----------
def _parse_food_form(form):
    errors = []
    d = {
        "name": clean(form.get("name"), 100),
        "description": clean(form.get("description"), 255),
        "food_type": form.get("food_type"),
        "category_id": to_int(form.get("category_id")),
        "is_bestseller": 1 if form.get("is_bestseller") else 0,
        "is_available": 1 if form.get("is_available") else 0,
    }
    if len(d["name"]) < 2:
        errors.append("Food name must be at least 2 characters.")
    if d["food_type"] not in ("veg", "nonveg"):
        errors.append("Choose VEG or NON-VEG.")
    if not d["category_id"] or not category_model.get(d["category_id"]):
        errors.append("Choose a category.")
    d["original_price"] = _money(form.get("original_price"), "Original price", errors)
    d["discounted_price"] = _money(form.get("discounted_price"), "Discounted price", errors)
    if d["original_price"] and d["discounted_price"] and d["discounted_price"] > d["original_price"]:
        errors.append("Discounted price cannot be more than the original price.")
    try:
        rating = Decimal(form.get("rating") or "4.0")
        if not Decimal("0") <= rating <= Decimal("5"):
            raise InvalidOperation
        d["rating"] = rating.quantize(Decimal("0.1"))
    except InvalidOperation:
        errors.append("Rating must be between 0 and 5.")
    valid_addons = {a["id"] for a in addon_model.all()}
    d["addon_ids"] = [a for a in (to_int(x) for x in form.getlist("addon_ids")) if a in valid_addons]
    return d, errors


def _food_form_page(food, form_values=None):
    return render_template("admin/food_form.html", food=food, categories=category_model.all(),
                           addons=addon_model.all(),
                           selected_addons=addon_model.ids_for_food(food["id"]) if food else set(),
                           form=form_values)


@bp.route("/foods")
def foods():
    return render_template("admin/foods.html", foods=food_item_model.search(only_available=False))


@bp.route("/foods/new", methods=["GET", "POST"])
def food_new():
    if request.method == "POST":
        d, errors = _parse_food_form(request.form)
        image, img_err = save_image(request.files.get("image"))
        if img_err:
            errors.append(img_err)
        if errors:
            delete_image(image)
            for e in errors:
                flash(e, "error")
            return _food_form_page(None, request.form)
        d["image"] = image
        food_id = food_item_model.create(d)
        food_item_model.set_addons(food_id, d["addon_ids"])
        flash("Food item added.", "success")
        return redirect(url_for("admin.foods"))
    return _food_form_page(None)


@bp.route("/foods/<int:food_id>/edit", methods=["GET", "POST"])
def food_edit(food_id):
    food = food_item_model.get(food_id)
    if not food:
        abort(404)
    if request.method == "POST":
        d, errors = _parse_food_form(request.form)
        image, img_err = save_image(request.files.get("image"))
        if img_err:
            errors.append(img_err)
        if errors:
            delete_image(image)
            for e in errors:
                flash(e, "error")
            return _food_form_page(food, request.form)
        d["image"] = image or food["image"]
        food_item_model.update(food_id, d)
        food_item_model.set_addons(food_id, d["addon_ids"])
        if image:
            delete_image(food["image"])
        flash("Food item updated.", "success")
        return redirect(url_for("admin.foods"))
    return _food_form_page(food)


@bp.post("/foods/<int:food_id>/delete")
def food_delete(food_id):
    food = food_item_model.get(food_id)
    if food:
        food_item_model.delete(food_id)
        delete_image(food["image"])
        flash(f"'{food['name']}' deleted.", "success")
    return redirect(url_for("admin.foods"))


# ---------- categories ----------
@bp.route("/categories")
def categories():
    return render_template("admin/categories.html", categories=category_model.all())


@bp.post("/categories/add")
def category_add():
    name = clean(request.form.get("name"), 60)
    if len(name) < 2:
        flash("Category name must be at least 2 characters.", "error")
    elif category_model.get_by_name(name):
        flash("That category already exists.", "error")
    else:
        category_model.create(name)
        flash("Category added.", "success")
    return redirect(url_for("admin.categories"))


@bp.post("/categories/<int:category_id>/edit")
def category_edit(category_id):
    name = clean(request.form.get("name"), 60)
    existing = category_model.get_by_name(name)
    if len(name) < 2:
        flash("Category name must be at least 2 characters.", "error")
    elif existing and existing["id"] != category_id:
        flash("That category already exists.", "error")
    else:
        category_model.rename(category_id, name)
        flash("Category updated.", "success")
    return redirect(url_for("admin.categories"))


@bp.post("/categories/<int:category_id>/delete")
def category_delete(category_id):
    cat = next((c for c in category_model.all() if c["id"] == category_id), None)
    if cat and cat["item_count"] > 0:
        flash("Move or delete the foods in this category first.", "error")
    elif cat:
        category_model.delete(category_id)
        flash("Category deleted.", "success")
    return redirect(url_for("admin.categories"))


# ---------- add-ons ----------
@bp.route("/addons")
def addons():
    return render_template("admin/addons.html", addons=addon_model.all())


def _addon_fields():
    errors = []
    name = clean(request.form.get("name"), 80)
    if len(name) < 2:
        errors.append("Add-on name must be at least 2 characters.")
    price = _money(request.form.get("price"), "Price", errors)
    return name, price, (1 if request.form.get("is_available") else 0), errors


@bp.post("/addons/add")
def addon_add():
    name, price, available, errors = _addon_fields()
    if errors:
        for e in errors:
            flash(e, "error")
    else:
        addon_model.create(name, price, available)
        flash("Add-on added. Attach it to foods from the food edit page.", "success")
    return redirect(url_for("admin.addons"))


@bp.post("/addons/<int:addon_id>/edit")
def addon_edit(addon_id):
    name, price, available, errors = _addon_fields()
    if errors:
        for e in errors:
            flash(e, "error")
    else:
        addon_model.update(addon_id, name, price, available)
        flash("Add-on updated.", "success")
    return redirect(url_for("admin.addons"))


@bp.post("/addons/<int:addon_id>/delete")
def addon_delete(addon_id):
    addon_model.delete(addon_id)
    flash("Add-on deleted.", "success")
    return redirect(url_for("admin.addons"))


# ---------- orders ----------
@bp.route("/orders")
def orders():
    status = request.args.get("status")
    return render_template("admin/orders.html", orders=order_model.list_all(status),
                           statuses=order_model.ALL_STATUSES, labels=order_model.LABELS,
                           current=status)


@bp.post("/orders/<int:order_id>/status")
def order_status(order_id):
    status = request.form.get("status")
    if status not in order_model.ALL_STATUSES or not order_model.get(order_id):
        flash("Invalid order or status.", "error")
    else:
        order_model.update_status(order_id, status)
        flash(f"Order #{order_id} is now '{order_model.LABELS[status]}'.", "success")
    return redirect(url_for("admin.orders", status=request.form.get("return_status") or None))


# ---------- users ----------
@bp.route("/users")
def users():
    return render_template("admin/users.html", users=user_model.list_all())


@bp.post("/users/<int:user_id>/toggle")
def user_toggle(user_id):
    user = user_model.get_by_id(user_id)
    if not user:
        abort(404)
    if user["id"] == g.user["id"]:
        flash("You cannot deactivate your own account.", "error")
    else:
        user_model.set_active(user_id, not user["is_active"])
        flash(f"{user['name']} is now {'inactive' if user['is_active'] else 'active'}.", "success")
    return redirect(url_for("admin.users"))
