import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from utils.billing import compute

CFG = {"DELIVERY_FEE": 40, "FREE_DELIVERY_ABOVE": 500, "TAX_PERCENT": 5}


def line(orig, unit, addon, qty):
    return {"original_price": orig, "unit_price": unit, "addon_each": addon, "qty": qty}


def test_empty_cart_is_zero():
    b = compute([], CFG)
    assert b["grand_total"] == 0 and b["delivery_fee"] == 0 and b["item_count"] == 0


def test_basic_bill():
    b = compute([line(180, 149, 40, 2)], CFG)
    assert b["mrp_total"] == 360
    assert b["discount"] == 62
    assert b["addon_total"] == 80
    assert b["delivery_fee"] == 40
    assert b["tax"] == 18.9
    assert b["grand_total"] == 436.9


def test_free_delivery_above_limit():
    b = compute([line(300, 250, 0, 2)], CFG)   # 500 after discount
    assert b["delivery_fee"] == 0
    assert b["grand_total"] == 525


def test_total_matches_parts():
    b = compute([line(250, 199, 130, 1), line(90, 70, 10, 3)], CFG)
    parts = b["mrp_total"] - b["discount"] + b["addon_total"] + b["delivery_fee"] + b["tax"]
    assert abs(parts - b["grand_total"]) < 0.02
