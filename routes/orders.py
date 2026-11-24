from flask import Blueprint, abort, g, jsonify, render_template

from models import order_model
from utils.decorators import login_required

bp = Blueprint("orders", __name__)


def _get_allowed(order_id):
    order = order_model.get(order_id)
    if not order or (order["user_id"] != g.user["id"] and g.user["role"] != "admin"):
        return None
    return order


@bp.route("/orders")
@login_required
def my_orders():
    return render_template("my_orders.html", orders=order_model.list_for_user(g.user["id"]))


@bp.route("/orders/<int:order_id>")
@login_required
def track(order_id):
    order = _get_allowed(order_id)
    if not order:
        abort(404)
    return render_template("order_tracking.html", order=order, flow=order_model.FLOW,
                           labels=order_model.LABELS)


@bp.get("/api/orders/<int:order_id>/status")
@login_required
def status(order_id):
    order = _get_allowed(order_id)
    if not order:
        return jsonify(error="Order not found."), 404
    return jsonify(
        status=order["status"], label=order["status_label"],
        reached=[h["status"] for h in order["history"]])
