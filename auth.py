# auth.py — SQLite-based authentication
# Handles login, register, family mode

import sqlite3
import hashlib
import os
from datetime import datetime

DB_PATH = "freshmind.db"

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def create_auth_tables():
    """Creates users and families tables"""
    conn = get_connection()
    cursor = conn.cursor()

    # Users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            username      TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            email         TEXT,
            full_name     TEXT,
            family_id     INTEGER DEFAULT NULL,
            role          TEXT DEFAULT 'member',
            created_at    TEXT DEFAULT CURRENT_TIMESTAMP,
            last_login    TEXT
        )
    """)

    # Families table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS families (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            name       TEXT NOT NULL,
            created_by INTEGER,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()

    # Create default admin if no users exist
    cursor.execute("SELECT COUNT(*) as cnt FROM users")
    count = cursor.fetchone()["cnt"]
    if count == 0:
        _create_default_users(cursor, conn)

    conn.close()

def _create_default_users(cursor, conn):
    """Creates default users for demo"""
    defaults = [
        ("admin",    "admin123",    "admin@freshmind.com",
         "Admin User", "admin"),
        ("person_a", "persona123",  "a@freshmind.com",
         "Person A",  "member"),
        ("person_b", "personb123",  "b@freshmind.com",
         "Person B",  "member"),
    ]
    for username, password, email, full_name, role in defaults:
        cursor.execute("""
            INSERT OR IGNORE INTO users
            (username, password_hash, email, full_name, role)
            VALUES (?, ?, ?, ?, ?)
        """, (username, hash_password(password),
              email, full_name, role))
    conn.commit()

def hash_password(password):
    """Hashes password using SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()

def login_user(username, password):
    """
    Verifies login credentials.
    Returns user dict if valid, None if invalid.
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM users WHERE username = ?
    """, (username,))
    user = cursor.fetchone()

    if user and user["password_hash"] == hash_password(password):
        # Update last login time
        cursor.execute("""
            UPDATE users SET last_login = ?
            WHERE id = ?
        """, (datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
              user["id"]))
        conn.commit()
        conn.close()
        return dict(user)

    conn.close()
    return None

def register_user(username, password, email, full_name):
    """
    Registers a new user.
    Returns (True, message) or (False, error)
    """
    conn = get_connection()
    cursor = conn.cursor()

    # Check if username exists
    cursor.execute(
        "SELECT id FROM users WHERE username = ?",
        (username,)
    )
    if cursor.fetchone():
        conn.close()
        return False, "❌ Username already exists!"

    # Check if email exists
    if email:
        cursor.execute(
            "SELECT id FROM users WHERE email = ?",
            (email,)
        )
        if cursor.fetchone():
            conn.close()
            return False, "❌ Email already registered!"

    try:
        cursor.execute("""
            INSERT INTO users
            (username, password_hash, email, full_name)
            VALUES (?, ?, ?, ?)
        """, (username, hash_password(password),
              email, full_name))
        conn.commit()
        conn.close()
        return True, "✅ Account created successfully!"
    except Exception as e:
        conn.close()
        return False, f"❌ Error: {str(e)}"

def get_all_users():
    """Returns all users — for family mode"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, username, full_name,
               email, role, family_id,
               created_at, last_login
        FROM users
        ORDER BY created_at DESC
    """)
    users = [dict(u) for u in cursor.fetchall()]
    conn.close()
    return users

def create_family(family_name, created_by_user_id):
    """Creates a new family group"""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO families (name, created_by)
        VALUES (?, ?)
    """, (family_name, created_by_user_id))
    family_id = cursor.lastrowid

    # Add creator to family as admin
    cursor.execute("""
        UPDATE users SET family_id = ?, role = 'family_admin'
        WHERE id = ?
    """, (family_id, created_by_user_id))

    conn.commit()
    conn.close()
    return family_id

def join_family(user_id, family_id):
    """Adds a user to an existing family"""
    conn = get_connection()
    cursor = conn.cursor()

    # Check family exists
    cursor.execute(
        "SELECT id FROM families WHERE id = ?",
        (family_id,)
    )
    if not cursor.fetchone():
        conn.close()
        return False, "❌ Family not found!"

    cursor.execute("""
        UPDATE users SET family_id = ?
        WHERE id = ?
    """, (family_id, user_id))
    conn.commit()
    conn.close()
    return True, "✅ Joined family successfully!"

def get_family_members(family_id):
    """Returns all members of a family"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, username, full_name,
               role, last_login
        FROM users WHERE family_id = ?
    """, (family_id,))
    members = [dict(m) for m in cursor.fetchall()]
    conn.close()
    return members

def update_password(user_id, old_password, new_password):
    """Updates user password"""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT password_hash FROM users WHERE id = ?",
        (user_id,)
    )
    user = cursor.fetchone()

    if not user or \
       user["password_hash"] != hash_password(old_password):
        conn.close()
        return False, "❌ Wrong current password!"

    cursor.execute("""
        UPDATE users SET password_hash = ?
        WHERE id = ?
    """, (hash_password(new_password), user_id))
    conn.commit()
    conn.close()
    return True, "✅ Password updated!"

def delete_user(user_id):
    """Deletes a user account"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "DELETE FROM users WHERE id = ?",
        (user_id,)
    )
    conn.commit()
    conn.close()
