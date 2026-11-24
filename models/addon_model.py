from extensions import execute, query


def all():
    return query(
        """SELECT a.*, COUNT(fa.food_id) AS food_count
           FROM addons a LEFT JOIN food_addons fa ON fa.addon_id = a.id
           GROUP BY a.id ORDER BY a.name""")


def get(addon_id):
    return query("SELECT * FROM addons WHERE id=%s", (addon_id,), one=True)


def for_food(food_id):
    """Add-ons a customer may pick for this food."""
    return query(
        """SELECT a.id, a.name, a.price FROM addons a
           JOIN food_addons fa ON fa.addon_id = a.id
           WHERE fa.food_id=%s AND a.is_available=1 ORDER BY a.price""", (food_id,))


def ids_for_food(food_id):
    rows = query("SELECT addon_id FROM food_addons WHERE food_id=%s", (food_id,))
    return {r["addon_id"] for r in rows}


def create(name, price, is_available):
    return execute("INSERT INTO addons (name, price, is_available) VALUES (%s,%s,%s)",
                   (name, price, is_available))


def update(addon_id, name, price, is_available):
    execute("UPDATE addons SET name=%s, price=%s, is_available=%s WHERE id=%s",
            (name, price, is_available, addon_id))


def delete(addon_id):
    execute("DELETE FROM addons WHERE id=%s", (addon_id,))
