from flask import Blueprint, jsonify, request

from models import addon_model, food_item_model
from utils.upload import image_url
from utils.validators import clean, to_float, to_int

bp = Blueprint("menu_api", __name__, url_prefix="/api")


def _food_json(f):
    return {
        "id": f["id"], "name": f["name"], "description": f["description"],
        "food_type": f["food_type"], "category": f["category_name"],
        "original_price": f["original_price"], "discounted_price": f["discounted_price"],
        "rating": f["rating"], "is_bestseller": bool(f["is_bestseller"]),
        "image_url": image_url(f["image"]),
    }


@bp.get("/menu")
def menu():
    foods = food_item_model.search(
        food_type=request.args.get("type"),
        q=clean(request.args.get("q"), 60),
        bestseller=request.args.get("bestseller") == "1",
        min_rating=to_float(request.args.get("min_rating")),
        max_price=to_float(request.args.get("max_price")),
        category_id=to_int(request.args.get("category")),
        sort=request.args.get("sort"),
    )
    return jsonify(items=[_food_json(f) for f in foods], count=len(foods))


@bp.get("/foods/<int:food_id>")
def food_detail(food_id):
    f = food_item_model.get(food_id)
    if not f or not f["is_available"]:
        return jsonify(error="This item is not available."), 404
    data = _food_json(f)
    data["addons"] = addon_model.for_food(food_id)
    return jsonify(data)
