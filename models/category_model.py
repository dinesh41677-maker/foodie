from extensions import execute, query


def all():
    return query(
        """SELECT c.id, c.name, COUNT(f.id) AS item_count
           FROM food_categories c LEFT JOIN food_items f ON f.category_id = c.id
           GROUP BY c.id ORDER BY c.name""")


def get(category_id):
    return query("SELECT * FROM food_categories WHERE id=%s", (category_id,), one=True)


def get_by_name(name):
    return query("SELECT * FROM food_categories WHERE name=%s", (name,), one=True)


def create(name):
    return execute("INSERT INTO food_categories (name) VALUES (%s)", (name,))


def rename(category_id, name):
    execute("UPDATE food_categories SET name=%s WHERE id=%s", (name, category_id))


def delete(category_id):
    execute("DELETE FROM food_categories WHERE id=%s", (category_id,))
