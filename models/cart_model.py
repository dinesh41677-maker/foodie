"""Cart storage.

Guests  -> cart lives in the session (browser cookie).
Members -> cart lives in MySQL (cart_items + cart_item_addons).
When a guest logs in, the session cart is merged into the MySQL cart.

A raw item looks like: {"id", "food_id", "qty", "addon_ids": [..]}
"""
from flask import current_app, g, session

from extensions import execute, get_db, placeholders, query
from models import food_item_model


def _uid(uid=None):
    if uid:
        return uid
    return g.user["id"] if getattr(g, "user", None) else None


def _max_qty():
    return current_app.config["MAX_ITEM_QTY"]


# ---------- read ----------
def raw_items(uid=None):
    uid = _uid(uid)
    if not uid:
        return [dict(i) for i in session.get("cart", [])]
    rows = query("SELECT id, food_id, quantity FROM cart_items WHERE user_id=%s ORDER BY id", (uid,))
    if not rows:
        return []
    ids = [r["id"] for r in rows]
    addon_rows = query(
        f"SELECT cart_item_id, addon_id FROM cart_item_addons WHERE cart_item_id IN ({placeholders(len(ids))})",
        tuple(ids))
    by_item = {}
    for a in addon_rows:
        by_item.setdefault(a["cart_item_id"], []).append(a["addon_id"])
    return [{"id": r["id"], "food_id": r["food_id"], "qty": r["quantity"],
             "addon_ids": by_item.get(r["id"], [])} for r in rows]


# ---------- write ----------
def add_item(food_id, qty, addon_ids, uid=None):
    uid = _uid(uid)
    addon_ids = sorted(set(addon_ids))
    for it in raw_items(uid):
        if it["food_id"] == food_id and sorted(it["addon_ids"]) == addon_ids:
            set_qty(it["id"], min(_max_qty(), it["qty"] + qty), uid)
            return
    qty = min(_max_qty(), qty)
    if uid:
        db = get_db()
        cur = db.cursor()
        try:
            cur.execute("INSERT INTO cart_items (user_id, food_id, quantity) VALUES (%s,%s,%s)",
                        (uid, food_id, qty))
            item_id = cur.lastrowid
            if addon_ids:
                cur.executemany("INSERT INTO cart_item_addons (cart_item_id, addon_id) VALUES (%s,%s)",
                                [(item_id, a) for a in addon_ids])
            db.commit()
        except Exception:
            db.rollback()
            raise
        finally:
            cur.close()
    else:
        cart = session.get("cart", [])
        seq = session.get("cart_seq", 0) + 1
        cart.append({"id": seq, "food_id": food_id, "qty": qty, "addon_ids": addon_ids})
        session["cart"] = cart
        session["cart_seq"] = seq


def set_qty(item_id, qty, uid=None):
    uid = _uid(uid)
    if qty <= 0:
        return remove_item(item_id, uid)
    qty = min(qty, _max_qty())
    if uid:
        execute("UPDATE cart_items SET quantity=%s WHERE id=%s AND user_id=%s", (qty, item_id, uid))
    else:
        cart = session.get("cart", [])
        for it in cart:
            if it["id"] == item_id:
                it["qty"] = qty
        session["cart"] = cart


def remove_item(item_id, uid=None):
    uid = _uid(uid)
    if uid:
        execute("DELETE FROM cart_items WHERE id=%s AND user_id=%s", (item_id, uid))
    else:
        session["cart"] = [i for i in session.get("cart", []) if i["id"] != item_id]


def merge_guest_cart(uid, guest_items):
    """Called right after login."""
    for it in guest_items:
        add_item(it["food_id"], it["qty"], it["addon_ids"], uid=uid)


# ---------- priced view ----------
def detailed_cart(uid=None):
    """Cart lines with fresh prices from MySQL. Unavailable foods are skipped."""
    items = raw_items(uid)
    if not items:
        return []
    food_ids = {i["food_id"] for i in items}
    foods = {f["id"]: f for f in food_item_model.get_many(food_ids)}
    rows = query(
        f"""SELECT fa.food_id, a.id, a.name, a.price
            FROM food_addons fa JOIN addons a ON a.id = fa.addon_id
            WHERE a.is_available = 1 AND fa.food_id IN ({placeholders(len(food_ids))})""",
        tuple(food_ids))
    allowed = {}
    for r in rows:
        allowed.setdefault(r["food_id"], {})[r["id"]] = {"id": r["id"], "name": r["name"], "price": r["price"]}

    lines = []
    for it in items:
        f = foods.get(it["food_id"])
        if not f or not f["is_available"]:
            continue
        ok = allowed.get(f["id"], {})
        addons = [ok[a] for a in it["addon_ids"] if a in ok]
        addon_each = sum(a["price"] for a in addons)
        lines.append({
            "id": it["id"], "food_id": f["id"], "name": f["name"], "food_type": f["food_type"],
            "image": f["image"], "unit_price": f["discounted_price"],
            "original_price": f["original_price"], "qty": it["qty"],
            "addons": addons, "addon_each": addon_each,
            "line_total": (f["discounted_price"] + addon_each) * it["qty"],
        })
    return lines
