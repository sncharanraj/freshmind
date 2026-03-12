# mock_data.py
# ------------------------------------------------------------
# TEMPORARY fake data for frontend development (Person B only)
# Once Person A completes database.py, we swap imports in app.py
# ------------------------------------------------------------

from datetime import date, timedelta

# Fake pantry items that look exactly like what database.py will return
MOCK_ITEMS = [
    {
        "id": 1,
        "name": "Milk",
        "quantity": "1L",
        "category": "Dairy",
        "purchase_date": date.today() - timedelta(days=5),
        "expiry_date":   date.today() + timedelta(days=2),   # 🔴 expires very soon
    },
    {
        "id": 2,
        "name": "Eggs",
        "quantity": "12 pcs",
        "category": "Dairy",
        "purchase_date": date.today() - timedelta(days=2),
        "expiry_date":   date.today() + timedelta(days=5),   # 🟠 expiring this week
    },
    {
        "id": 3,
        "name": "Spinach",
        "quantity": "200g",
        "category": "Vegetables",
        "purchase_date": date.today() - timedelta(days=1),
        "expiry_date":   date.today() + timedelta(days=1),   # 🔴 critical
    },
    {
        "id": 4,
        "name": "Chicken Breast",
        "quantity": "500g",
        "category": "Meat",
        "purchase_date": date.today(),
        "expiry_date":   date.today() + timedelta(days=10),  # 🟢 safe
    },
    {
        "id": 5,
        "name": "Apple Juice",
        "quantity": "2L",
        "category": "Beverages",
        "purchase_date": date.today() - timedelta(days=3),
        "expiry_date":   date.today() + timedelta(days=20),  # 🟢 safe
    },
    {
        "id": 6,
        "name": "Yogurt",
        "quantity": "400g",
        "category": "Dairy",
        "purchase_date": date.today() - timedelta(days=1),
        "expiry_date":   date.today() + timedelta(days=3),   # 🟠 watch this
    },
    {
        "id": 7,
        "name": "Carrots",
        "quantity": "300g",
        "category": "Vegetables",
        "purchase_date": date.today() - timedelta(days=4),
        "expiry_date":   date.today() + timedelta(days=15),  # 🟢 safe
    },
]

def get_all_items():
    """Returns all pantry items (mock version)"""
    return MOCK_ITEMS

def get_expiring_items(days=7):
    """Returns items expiring within the given number of days (mock version)"""
    today = date.today()
    return [
        item for item in MOCK_ITEMS
        if (item["expiry_date"] - today).days <= days
    ]