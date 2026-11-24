"""Creates the database, tables, starter data and the admin account.

Run:   python setup_db.py            (safe to run again)
Reset: python setup_db.py --reset    (DELETES everything, then rebuilds)
"""
import os
import sys

import mysql.connector
from werkzeug.security import generate_password_hash

from config import BASE_DIR, Config


def read_statements(filename):
    with open(os.path.join(BASE_DIR, filename), encoding="utf-8") as f:
        lines = [ln for ln in f.read().splitlines() if not ln.strip().startswith("--")]
    return [s.strip() for s in "\n".join(lines).split(";") if s.strip()]


def main():
    reset = "--reset" in sys.argv
    db_name = Config.DB_NAME
    try:
        conn = mysql.connector.connect(
            host=Config.DB_HOST, port=Config.DB_PORT,
            user=Config.DB_USER, password=Config.DB_PASSWORD,
        )
    except mysql.connector.Error as err:
        print("\nCould not connect to MySQL:", err)
        print("Check DB_HOST / DB_USER / DB_PASSWORD in your .env file and that MySQL is running.")
        sys.exit(1)

    cur = conn.cursor()
    if reset:
        print(f"Dropping database '{db_name}' ...")
        cur.execute(f"DROP DATABASE IF EXISTS `{db_name}`")
    cur.execute(
        f"CREATE DATABASE IF NOT EXISTS `{db_name}` "
        "CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
    )
    cur.execute(f"USE `{db_name}`")

    for filename in ("schema.sql", "seed.sql"):
        statements = read_statements(filename)
        for stmt in statements:
            cur.execute(stmt)
        conn.commit()
        print(f"Ran {filename} ({len(statements)} statements)")

    name = os.getenv("ADMIN_NAME", "Foodie Admin")
    email = os.getenv("ADMIN_EMAIL", "admin@foodie.com").lower()
    password = os.getenv("ADMIN_PASSWORD", "Admin@12345")
    cur.execute("SELECT id FROM users WHERE email=%s", (email,))
    if cur.fetchone():
        print(f"Admin '{email}' already exists, not changed.")
    else:
        cur.execute(
            "INSERT INTO users (name, email, phone, password_hash, role) VALUES (%s,%s,%s,%s,'admin')",
            (name, email, "9999999999", generate_password_hash(password)),
        )
        conn.commit()
        print(f"Admin created -> email: {email}  password: {password}")

    cur.close()
    conn.close()
    print("\nDatabase is ready. Now run:  python app.py")


if __name__ == "__main__":
    main()
