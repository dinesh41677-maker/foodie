from extensions import execute, get_db, placeholders, query

FLOW = ["placed", "confirmed", "preparing", "out_for_delivery", "delivered"]
LABELS = {
    "placed": "Order Placed",
    "confirmed": "Confirmed",
    "preparing": "Preparing",
    "out_for_delivery": "Out for Delivery",
    "delivered": "Delivered",
    "cancelled": "Cancelled",
}
ALL_STATUSES = FLOW + ["cancelled"]


def place_order(user_id, name, phone, address_text, payment_method, lines, bill):
    """Saves the order, items, add-ons and first status in ONE transaction."""
    db = get_db()
    cur = db.cursor()
    try:
        cur.execute(
            """INSERT INTO orders (user_id, customer_name, phone, delivery_address, payment_method,
                   mrp_total, discount_total, addon_total, delivery_fee, tax_amount, grand_total)
               VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
            (user_id, name, phone, address_text, payment_method, bill["mrp_total"], bill["discount"],
             bill["addon_total"], bill["delivery_fee"], bill["tax"], bill["grand_total"]))
        order_id = cur.lastrowid
        for l in lines:
            cur.execute(
                """INSERT INTO order_items (order_id, food_id, food_name, food_type, unit_price,
                       original_price, quantity, line_total) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)""",
                (order_id, l["food_id"], l["name"], l["food_type"], l["unit_price"],
                 l["original_price"], l["qty"], l["line_total"]))
            item_id = cur.lastrowid
            for a in l["addons"]:
                cur.execute(
                    "INSERT INTO order_addons (order_item_id, addon_id, addon_name, price) VALUES (%s,%s,%s,%s)",
                    (item_id, a["id"], a["name"], a["price"]))
        cur.execute("INSERT INTO order_status_history (order_id, status) VALUES (%s,'placed')", (order_id,))
        cur.execute("DELETE FROM cart_items WHERE user_id=%s", (user_id,))
        db.commit()
        return order_id
    except Exception:
        db.rollback()
        raise
    finally:
        cur.close()


def _attach_items(orders):
    if not orders:
        return orders
    ids = [o["id"] for o in orders]
    items = query(f"SELECT * FROM order_items WHERE order_id IN ({placeholders(len(ids))}) ORDER BY id", tuple(ids))
    item_ids = [i["id"] for i in items]
    addons = []
    if item_ids:
        addons = query(
            f"SELECT * FROM order_addons WHERE order_item_id IN ({placeholders(len(item_ids))}) ORDER BY id",
            tuple(item_ids))
    for i in items:
        i["addons"] = [a for a in addons if a["order_item_id"] == i["id"]]
    for o in orders:
        o["items"] = [i for i in items if i["order_id"] == o["id"]]
        o["status_label"] = LABELS[o["status"]]
    return orders


def get(order_id):
    row = query("SELECT * FROM orders WHERE id=%s", (order_id,), one=True)
    if not row:
        return None
    order = _attach_items([row])[0]
    order["history"] = history(order_id)
    return order


def history(order_id):
    return query("SELECT status, changed_at FROM order_status_history WHERE order_id=%s ORDER BY id", (order_id,))


def list_for_user(user_id):
    return _attach_items(query("SELECT * FROM orders WHERE user_id=%s ORDER BY id DESC", (user_id,)))


def list_all(status=None, limit=200):
    if status in ALL_STATUSES:
        rows = query("SELECT * FROM orders WHERE status=%s ORDER BY id DESC LIMIT %s", (status, limit))
    else:
        rows = query("SELECT * FROM orders ORDER BY id DESC LIMIT %s", (limit,))
    return _attach_items(rows)


def update_status(order_id, status):
    if status not in ALL_STATUSES:
        raise ValueError("Invalid status")
    db = get_db()
    cur = db.cursor()
    try:
        cur.execute("UPDATE orders SET status=%s WHERE id=%s", (status, order_id))
        cur.execute("INSERT INTO order_status_history (order_id, status) VALUES (%s,%s)", (order_id, status))
        if status == "delivered":
            cur.execute("UPDATE orders SET payment_status='paid' WHERE id=%s", (order_id,))
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        cur.close()


def stats():
    s = query(
        """SELECT COUNT(*) AS total_orders,
                  COALESCE(SUM(CASE WHEN status <> 'cancelled' THEN grand_total END), 0) AS revenue,
                  COALESCE(SUM(status IN ('placed','confirmed','preparing','out_for_delivery')), 0) AS active_orders,
                  COALESCE(SUM(DATE(created_at) = CURDATE()), 0) AS today_orders
           FROM orders""", one=True)
    return {k: (int(v) if k != "revenue" else float(v)) for k, v in s.items()}
