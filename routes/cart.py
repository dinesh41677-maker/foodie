from flask import Blueprint, jsonify, render_template, request

from models import addon_model, cart_model, food_item_model
from utils import billing
from utils.upload import image_url
from utils.validators import to_int

bp = Blueprint("cart", __name__)


def _payload():
    lines = cart_model.detailed_cart()
    items = [{**l, "image_url": image_url(l["image"])} for l in lines]
    return {"items": items, "bill": billing.compute(lines)}


@bp.route("/cart")
def cart_page():
    return render_template("cart.html")


@bp.get("/api/cart")
def get_cart():
    return jsonify(_payload())


@bp.post("/api/cart/add")
def add():
    data = request.get_json(silent=True) or {}
    food_id = to_int(data.get("food_id"))
    qty = to_int(data.get("quantity"), 1)
    raw_addons = data.get("addon_ids") or []
    if not food_id or not isinstance(raw_addons, list):
        return jsonify(error="Invalid request."), 400
    food = food_item_model.get(food_id)
    if not food or not food["is_available"]:
        return jsonify(error="This item is not available."), 404
    allowed = {a["id"] for a in addon_model.for_food(food_id)}
    addon_ids = [to_int(a) for a in raw_addons]
    if any(a not in allowed for a in addon_ids):
        return jsonify(error="One of the add-ons is not available for this item."), 400
    cart_model.add_item(food_id, max(1, min(qty, 20)), addon_ids)
    return jsonify(_payload())


@bp.post("/api/cart/update")
def update():
    data = request.get_json(silent=True) or {}
    item_id, qty = to_int(data.get("item_id")), to_int(data.get("quantity"))
    if not item_id or qty is None:
        return jsonify(error="Invalid request."), 400
    cart_model.set_qty(item_id, qty)
    return jsonify(_payload())


@bp.post("/api/cart/remove")
def remove():
    data = request.get_json(silent=True) or {}
    item_id = to_int(data.get("item_id"))
    if not item_id:
        return jsonify(error="Invalid request."), 400
    cart_model.remove_item(item_id)
    return jsonify(_payload())
