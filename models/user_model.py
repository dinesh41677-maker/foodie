from extensions import execute, query


def get_by_id(user_id):
    return query(
        "SELECT id, name, email, phone, role, is_active, created_at FROM users WHERE id=%s",
        (user_id,), one=True)


def get_by_email(email):
    return query("SELECT * FROM users WHERE email=%s", (email,), one=True)


def create(name, email, phone, password_hash):
    return execute(
        "INSERT INTO users (name, email, phone, password_hash) VALUES (%s,%s,%s,%s)",
        (name, email, phone, password_hash))


def update_profile(user_id, name, phone):
    execute("UPDATE users SET name=%s, phone=%s WHERE id=%s", (name, phone, user_id))


def get_password_hash(user_id):
    row = query("SELECT password_hash FROM users WHERE id=%s", (user_id,), one=True)
    return row["password_hash"] if row else None


def update_password(user_id, password_hash):
    execute("UPDATE users SET password_hash=%s WHERE id=%s", (password_hash, user_id))


def list_all():
    return query(
        """SELECT u.id, u.name, u.email, u.phone, u.role, u.is_active, u.created_at,
                  COUNT(o.id) AS order_count
           FROM users u LEFT JOIN orders o ON o.user_id = u.id
           GROUP BY u.id ORDER BY u.id DESC""")


def set_active(user_id, flag):
    execute("UPDATE users SET is_active=%s WHERE id=%s", (1 if flag else 0, user_id))


def count():
    return query("SELECT COUNT(*) AS n FROM users", one=True)["n"]
