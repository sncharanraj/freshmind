# database.py
# Person A owns this file
# This file handles all database operations for FreshMind

import sqlite3
from datetime import date, timedelta

# ─────────────────────────────────────────
# DATABASE CONNECTION
# ─────────────────────────────────────────

def get_connection():
    """
    Creates and returns a connection to the SQLite database.
    The database file 'freshmind.db' will be auto-created
    if it doesn't already exist.
    """
    conn = sqlite3.connect("freshmind.db")
    conn.row_factory = sqlite3.Row  # lets us access columns by name
    return conn


# ─────────────────────────────────────────
# TABLE SETUP
# ─────────────────────────────────────────

def create_tables():
    """
    Creates the pantry_items and usage_history tables
    if they don't already exist.
    Call this once when the app starts.
    """
    conn = get_connection()
    cursor = conn.cursor()

    # Table 1: stores all pantry items
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS pantry_items (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            name          TEXT NOT NULL,
            quantity      TEXT NOT NULL,
            purchase_date DATE NOT NULL,
            expiry_date   DATE NOT NULL,
            category      TEXT NOT NULL
        )
    """)

    # Table 2: tracks item usage history (used vs wasted)
    cursor.execute("""
            CREATE TABLE IF NOT EXISTS pantry_items (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                name          TEXT NOT NULL,
                quantity      TEXT NOT NULL,
                purchase_date DATE NOT NULL,
                expiry_date   DATE NOT NULL,
                category      TEXT NOT NULL,
                image_url     TEXT DEFAULT ''
            )
        """)

        # Add image_url column if it doesn't exist
        # (for existing databases that were created before)
    try:
        cursor.execute("""
            ALTER TABLE pantry_items
            ADD COLUMN image_url TEXT DEFAULT ''
        """)
        conn.commit()
    except:
        pass  # Column already exists, no problem!

    conn.commit()
    conn.close()
    print("✅ Tables created successfully!")


# ─────────────────────────────────────────
# ADD ITEM
# ─────────────────────────────────────────

def add_item(name, quantity, purchase_date,
             expiry_date, category, image_url=""):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO pantry_items
        (name, quantity, purchase_date, expiry_date, category, image_url)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (name, quantity, purchase_date,
          expiry_date, category, image_url))

    conn.commit()
    conn.close()
    print(f"✅ '{name}' added to pantry!")


# ─────────────────────────────────────────
# GET ALL ITEMS
# ─────────────────────────────────────────

def get_all_items():
    """
    Returns all items currently in the pantry.
    Person B will call this to display the pantry table in the UI.

    Returns:
        List of rows (each row is like a dictionary)
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM pantry_items
        ORDER BY expiry_date ASC
    """)

    items = cursor.fetchall()
    conn.close()
    return items


# ─────────────────────────────────────────
# GET EXPIRING ITEMS
# ─────────────────────────────────────────

def get_expiring_items(days=7):
    """
    Returns items expiring within the next 'days' days.
    Used by notifier.py for alerts and ai_recipes.py for
    priority recipe suggestions.

    Parameters:
        days (int): How many days ahead to check (default: 7)

    Returns:
        List of rows expiring within that window
    """
    conn = get_connection()
    cursor = conn.cursor()

    today = date.today()
    deadline = today + timedelta(days=days)

    cursor.execute("""
        SELECT * FROM pantry_items
        WHERE expiry_date BETWEEN ? AND ?
        ORDER BY expiry_date ASC
    """, (str(today), str(deadline)))

    items = cursor.fetchall()
    conn.close()
    return items


# ─────────────────────────────────────────
# DELETE ITEM
# ─────────────────────────────────────────

def delete_item(item_id):
    """
    Deletes an item from the pantry by its ID.
    Person B will call this when user clicks delete button.

    Parameters:
        item_id (int): The ID of the item to delete
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        DELETE FROM pantry_items WHERE id = ?
    """, (item_id,))

    conn.commit()
    conn.close()
    print(f"✅ Item {item_id} deleted!")


# ─────────────────────────────────────────
# UPDATE ITEM
# ─────────────────────────────────────────

def update_item(item_id, name=None, quantity=None,
                purchase_date=None, expiry_date=None, category=None):
    """
    Updates one or more fields of an existing pantry item.

    Parameters:
        item_id  (int) : ID of item to update
        All other params are optional — only pass what you want to change
    """
    conn = get_connection()
    cursor = conn.cursor()

    # Build update query dynamically based on what's provided
    fields = []
    values = []

    if name:
        fields.append("name = ?")
        values.append(name)
    if quantity:
        fields.append("quantity = ?")
        values.append(quantity)
    if purchase_date:
        fields.append("purchase_date = ?")
        values.append(purchase_date)
    if expiry_date:
        fields.append("expiry_date = ?")
        values.append(expiry_date)
    if category:
        fields.append("category = ?")
        values.append(category)

    # Only run if there's something to update
    if fields:
        values.append(item_id)
        query = f"UPDATE pantry_items SET {', '.join(fields)} WHERE id = ?"
        cursor.execute(query, values)
        conn.commit()
        print(f"✅ Item {item_id} updated!")

    conn.close()


# ─────────────────────────────────────────
# LOG USAGE HISTORY
# ─────────────────────────────────────────

def log_usage(item_name, was_wasted):
    """
    Logs whether an item was used or wasted.
    Person B's dashboard will use this for the savings tracker.

    Parameters:
        item_name  (str)  : Name of the item
        was_wasted (bool) : True if wasted, False if used
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO usage_history (item_name, used_date, was_wasted)
        VALUES (?, ?, ?)
    """, (item_name, str(date.today()), was_wasted))

    conn.commit()
    conn.close()
    print(f"✅ Usage logged for '{item_name}'!")


# ─────────────────────────────────────────
# GET USAGE HISTORY
# ─────────────────────────────────────────

def get_usage_history():
    """
    Returns full usage history.
    Person B will use this for the waste savings dashboard.

    Returns:
        List of all usage history rows
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM usage_history
        ORDER BY used_date DESC
    """)

    history = cursor.fetchall()
    conn.close()
    return history


# ─────────────────────────────────────────
# QUICK TEST — run this file directly to test
# ─────────────────────────────────────────

if __name__ == "__main__":
    # Step 1: Create tables
    create_tables()

    # Step 2: Add a test item
    add_item(
        name="Milk",
        quantity="1 litre",
        purchase_date="2026-03-10",
        expiry_date="2026-03-15",
        category="Dairy"
    )

    # Step 3: View all items
    print("\n📦 All Pantry Items:")
    for item in get_all_items():
        print(dict(item))

    # Step 4: Check expiring items
    print("\n⚠️ Items expiring in 7 days:")
    for item in get_expiring_items():
        print(dict(item))
