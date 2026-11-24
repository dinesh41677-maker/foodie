from flask import Blueprint, render_template, request

from models import category_model

bp = Blueprint("main", __name__)


@bp.route("/")
def menu():
    """First page of the site: the VEG / NON-VEG menu."""
    start_type = "nonveg" if request.args.get("type") == "nonveg" else "veg"
    return render_template("menu.html", categories=category_model.all(), start_type=start_type)
