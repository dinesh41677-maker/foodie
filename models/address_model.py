from extensions import execute, query


def list_for_user(user_id):
    return query("SELECT * FROM addresses WHERE user_id=%s ORDER BY id DESC", (user_id,))


def get(user_id, address_id):
    return query("SELECT * FROM addresses WHERE id=%s AND user_id=%s",
                 (address_id, user_id), one=True)


def create(user_id, label, address_line, city, pincode):
    return execute(
        "INSERT INTO addresses (user_id, label, address_line, city, pincode) VALUES (%s,%s,%s,%s,%s)",
        (user_id, label, address_line, city, pincode))


def delete(user_id, address_id):
    execute("DELETE FROM addresses WHERE id=%s AND user_id=%s", (address_id, user_id))


def as_text(addr):
    return f"{addr['address_line']}, {addr['city']} - {addr['pincode']}"
