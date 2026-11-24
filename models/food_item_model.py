from extensions import execute, get_db, placeholders, query

_SELECT = ("SELECT f.*, c.name AS category_name FROM food_items f "
           "JOIN food_categories c ON c.id = f.category_id")

# Only these ORDER BY values are allowed (never put user text in SQL).
_SORTS = {
    "price_low": "f.discounted_price ASC",
    "price_high": "f.discounted_price DESC",
    "rating": "f.rating DESC, f.name ASC",
}


def search(food_type=None, q=None, bestseller=False, min_rating=None,
           max_price=None, category_id=None, sort=None, only_available=True):
    where, params = [], []
    if only_available:
        where.append("f.is_available = 1")
    if food_type in ("veg", "nonveg"):
        where.append("f.food_type = %s")
        params.append(food_type)
    if q:
        like = "%" + q.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_") + "%"
        where.append("(f.name LIKE %s OR f.description LIKE %s OR c.name LIKE %s)")
        params += [like, like, like]
    if bestseller:
        where.append("f.is_bestseller = 1")
    if min_rating is not None:
        where.append("f.rating >= %s")
        params.append(min_rating)
    if max_price is not None:
        where.append("f.discounted_price <= %s")
        params.append(max_price)
    if category_id:
        where.append("f.category_id = %s")
        params.append(category_id)

    sql = _SELECT
    if where:
        sql += " WHERE " + " AND ".join(where)
    sql += " ORDER BY " + _SORTS.get(sort, "f.is_bestseller DESC, f.rating DESC, f.name ASC")
    return query(sql, tuple(params))


def get(food_id):
    return query(_SELECT + " WHERE f.id = %s", (food_id,), one=True)


def get_many(ids):
    ids = list(ids)
    if not ids:
        return []
    return query(_SELECT + f" WHERE f.id IN ({placeholders(len(ids))})", tuple(ids))


def create(d):
    return execute(
        """INSERT INTO food_items (category_id, name, description, food_type, image,
               original_price, discounted_price, rating, is_bestseller, is_available)
           VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
        (d["category_id"], d["name"], d["description"], d["food_type"], d["image"],
         d["original_price"], d["discounted_price"], d["rating"],
         d["is_bestseller"], d["is_available"]))


def update(food_id, d):
    execute(
        """UPDATE food_items SET category_id=%s, name=%s, description=%s, food_type=%s, image=%s,
               original_price=%s, discounted_price=%s, rating=%s, is_bestseller=%s, is_available=%s
           WHERE id=%s""",
        (d["category_id"], d["name"], d["description"], d["food_type"], d["image"],
         d["original_price"], d["discounted_price"], d["rating"],
         d["is_bestseller"], d["is_available"], food_id))


def delete(food_id):
    execute("DELETE FROM food_items WHERE id=%s", (food_id,))


def set_addons(food_id, addon_ids):
    db = get_db()
    cur = db.cursor()
    try:
        cur.execute("DELETE FROM food_addons WHERE food_id=%s", (food_id,))
        if addon_ids:
            cur.executemany("INSERT INTO food_addons (food_id, addon_id) VALUES (%s,%s)",
                            [(food_id, a) for a in addon_ids])
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        cur.close()


def count():
    return query("SELECT COUNT(*) AS n FROM food_items", one=True)["n"]
