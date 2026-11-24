from flask import Blueprint, abort, flash, g, redirect, render_template, request, url_for

from models import address_model, cart_model, order_model
from utils import billing
from utils.decorators import login_required
from utils.validators import clean, to_int, valid_name, valid_phone, valid_pincode

bp = Blueprint("checkout", __name__)
PAYMENT_METHODS = {"cod": "Cash on Delivery", "upi": "UPI on Delivery", "card": "Card on Delivery"}


@bp.route("/checkout", methods=["GET", "POST"])
@login_required
def checkout():
    uid = g.user["id"]
    lines = cart_model.detailed_cart()
    if not lines:
        flash("Your cart is empty. Add something tasty first.", "info")
        return redirect(url_for("main.menu"))
    bill = billing.compute(lines)
    addresses = address_model.list_for_user(uid)
    form = {"customer_name": g.user["name"], "phone": g.user["phone"], "payment_method": "cod",
            "address_id": str(addresses[0]["id"]) if addresses else "new"}

    if request.method == "POST":
        form = {k: clean(request.form.get(k), 255) for k in
                ("customer_name", "phone", "payment_method", "address_id",
                 "address_line", "city", "pincode")}
        form["save_address"] = request.form.get("save_address") == "1"
        errors = []
        if not valid_name(form["customer_name"]):
            errors.append("Enter the customer name (2 to 80 characters).")
        if not valid_phone(form["phone"]):
            errors.append("Enter a valid 10 digit contact number.")
        if form["payment_method"] not in PAYMENT_METHODS:
            errors.append("Choose a payment method.")

        address_text = None
        if form["address_id"] == "new":
            if len(form["address_line"]) < 5 or len(form["city"]) < 2:
                errors.append("Enter the full delivery address and city.")
            elif not valid_pincode(form["pincode"]):
                errors.append("Enter a valid 6 digit pincode.")
            else:
                address_text = f"{form['address_line']}, {form['city']} - {form['pincode']}"
        else:
            addr = address_model.get(uid, to_int(form["address_id"], 0))
            if addr:
                address_text = address_model.as_text(addr)
            else:
                errors.append("Choose a delivery address.")

        if errors:
            for e in errors:
                flash(e, "error")
        else:
            if form["address_id"] == "new" and form["save_address"]:
                address_model.create(uid, "Home", form["address_line"], form["city"], form["pincode"])
            order_id = order_model.place_order(uid, form["customer_name"], form["phone"],
                                              address_text, form["payment_method"], lines, bill)
            return redirect(url_for("checkout.success", order_id=order_id))

    return render_template("checkout.html", lines=lines, bill=bill, addresses=addresses,
                           form=form, payment_methods=PAYMENT_METHODS)


@bp.route("/order/success/<int:order_id>")
@login_required
def success(order_id):
    order = order_model.get(order_id)
    if not order or order["user_id"] != g.user["id"]:
        abort(404)
    return render_template("order_success.html", order=order)
