# database.py — FreshMind with per-user data isolation
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "freshmind.db")

def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def create_tables():
    conn = get_conn()
    c = conn.cursor()

    # ── pantry_items — now has user_id ──
    c.execute("""
        CREATE TABLE IF NOT EXISTS pantry_items (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id       INTEGER NOT NULL DEFAULT 0,
            name          TEXT    NOT NULL,
            quantity      TEXT    NOT NULL,
            purchase_date TEXT    NOT NULL,
            expiry_date   TEXT    NOT NULL,
            category      TEXT    NOT NULL DEFAULT 'Other',
            image_url     TEXT    DEFAULT ''
        )
    """)

    # ── usage_history — now has user_id ──
    c.execute("""
        CREATE TABLE IF NOT EXISTS usage_history (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id    INTEGER NOT NULL DEFAULT 0,
            item_name  TEXT    NOT NULL,
            used_date  TEXT    NOT NULL,
            was_wasted INTEGER NOT NULL DEFAULT 0
        )
    """)

    # ── login_history — new table ──
    c.execute("""
        CREATE TABLE IF NOT EXISTS login_history (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id    INTEGER NOT NULL,
            username   TEXT    NOT NULL,
            login_time TEXT    NOT NULL,
            ip_address TEXT    DEFAULT ''
        )
    """)

    # ── Migration: add user_id column if old DB exists ──
    try:
        c.execute("ALTER TABLE pantry_items ADD COLUMN user_id INTEGER NOT NULL DEFAULT 0")
    except Exception:
        pass  # Column already exists

    try:
        c.execute("ALTER TABLE usage_history ADD COLUMN user_id INTEGER NOT NULL DEFAULT 0")
    except Exception:
        pass

    conn.commit()
    conn.close()

# ─────────────────────────────────────────
# PANTRY — all filtered by user_id
# ─────────────────────────────────────────

def add_item(name, quantity, purchase_date, expiry_date,
             category="Other", image_url="", user_id=0):
    conn = get_conn()
    conn.execute("""
        INSERT INTO pantry_items
            (user_id, name, quantity, purchase_date,
             expiry_date, category, image_url)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (user_id, name, quantity, purchase_date,
          expiry_date, category, image_url))
    conn.commit()
    conn.close()

def get_all_items(user_id=0):
    conn = get_conn()
    rows = conn.execute("""
        SELECT * FROM pantry_items
        WHERE user_id = ?
        ORDER BY expiry_date ASC
    """, (user_id,)).fetchall()
    conn.close()
    return rows

def get_expiring_items(days=7, user_id=0):
    conn = get_conn()
    rows = conn.execute("""
        SELECT * FROM pantry_items
        WHERE user_id = ?
          AND date(expiry_date) <= date('now', ? || ' days')
        ORDER BY expiry_date ASC
    """, (user_id, str(days))).fetchall()
    conn.close()
    return rows

def delete_item(item_id, user_id=0):
    conn = get_conn()
    conn.execute("""
        DELETE FROM pantry_items
        WHERE id = ? AND user_id = ?
    """, (item_id, user_id))
    conn.commit()
    conn.close()

def update_item(item_id, user_id=0, name=None,
                quantity=None, expiry_date=None, category=None):
    conn = get_conn()
    fields, vals = [], []
    if name:        fields.append("name = ?");        vals.append(name)
    if quantity:    fields.append("quantity = ?");    vals.append(quantity)
    if expiry_date: fields.append("expiry_date = ?"); vals.append(expiry_date)
    if category:    fields.append("category = ?");    vals.append(category)
    if not fields:
        conn.close(); return
    vals += [item_id, user_id]
    conn.execute(f"""
        UPDATE pantry_items
        SET {', '.join(fields)}
        WHERE id = ? AND user_id = ?
    """, vals)
    conn.commit()
    conn.close()

# ─────────────────────────────────────────
# USAGE HISTORY — filtered by user_id
# ─────────────────────────────────────────

def log_usage(item_name, was_wasted=False, user_id=0):
    conn = get_conn()
    from datetime import date
    conn.execute("""
        INSERT INTO usage_history
            (user_id, item_name, used_date, was_wasted)
        VALUES (?, ?, ?, ?)
    """, (user_id, item_name, str(date.today()), int(was_wasted)))
    conn.commit()
    conn.close()

def get_usage_history(user_id=0):
    conn = get_conn()
    rows = conn.execute("""
        SELECT * FROM usage_history
        WHERE user_id = ?
        ORDER BY used_date DESC, id DESC
        LIMIT 100
    """, (user_id,)).fetchall()
    conn.close()
    return rows

# ─────────────────────────────────────────
# LOGIN HISTORY
# ─────────────────────────────────────────

def log_login(user_id, username, ip_address=""):
    conn = get_conn()
    from datetime import datetime
    conn.execute("""
        INSERT INTO login_history
            (user_id, username, login_time, ip_address)
        VALUES (?, ?, ?, ?)
    """, (user_id, username,
          datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
          ip_address))
    conn.commit()
    conn.close()

def get_login_history(user_id=None, limit=50):
    """
    If user_id given → return that user's history only.
    If user_id=None  → return ALL users (admin view).
    """
    conn = get_conn()
    if user_id is not None:
        rows = conn.execute("""
            SELECT lh.*, u.full_name
            FROM login_history lh
            LEFT JOIN users u ON lh.user_id = u.id
            WHERE lh.user_id = ?
            ORDER BY lh.login_time DESC
            LIMIT ?
        """, (user_id, limit)).fetchall()
    else:
        rows = conn.execute("""
            SELECT lh.*, u.full_name
            FROM login_history lh
            LEFT JOIN users u ON lh.user_id = u.id
            ORDER BY lh.login_time DESC
            LIMIT ?
        """, (limit,)).fetchall()
    conn.close()
    return rows

def get_all_login_stats():
    """Admin: total logins per user."""
    conn = get_conn()
    rows = conn.execute("""
        SELECT
            lh.username,
            u.full_name,
            COUNT(*) as total_logins,
            MAX(lh.login_time) as last_login,
            MIN(lh.login_time) as first_login
        FROM login_history lh
        LEFT JOIN users u ON lh.user_id = u.id
        GROUP BY lh.username
        ORDER BY total_logins DESC
    """).fetchall()
    conn.close()
    return rows