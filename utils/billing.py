"""One place for all price maths, so cart, checkout and orders always agree.

Each line needs: original_price, unit_price (discounted), addon_each, qty
"""
from flask import current_app


def _r2(x):
    return round(x + 1e-9, 2)


def compute(lines, cfg=None):
    cfg = cfg if cfg is not None else current_app.config

    mrp_total = sum(l["original_price"] * l["qty"] for l in lines)
    food_after_discount = sum(l["unit_price"] * l["qty"] for l in lines)
    addon_total = sum(l["addon_each"] * l["qty"] for l in lines)
    discount = mrp_total - food_after_discount

    before_tax = food_after_discount + addon_total
    if not lines or before_tax >= cfg["FREE_DELIVERY_ABOVE"]:
        delivery_fee = 0
    else:
        delivery_fee = cfg["DELIVERY_FEE"]
    tax = before_tax * cfg["TAX_PERCENT"] / 100
    grand_total = before_tax + delivery_fee + tax

    return {
        "item_count": sum(l["qty"] for l in lines),
        "mrp_total": _r2(mrp_total),
        "discount": _r2(discount),
        "addon_total": _r2(addon_total),
        "delivery_fee": _r2(delivery_fee),
        "tax": _r2(tax),
        "tax_percent": cfg["TAX_PERCENT"],
        "grand_total": _r2(grand_total),
        "free_delivery_above": cfg["FREE_DELIVERY_ABOVE"],
    }
