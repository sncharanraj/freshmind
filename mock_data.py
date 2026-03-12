from datetime import date, timedelta

MOCK_ITEMS = [
    {
        "id": 1,
        "name": "Milk",
        "quantity": "1L",
        "category": "Dairy",
        "purchase_date": date.today() - timedelta(days=5),
        "expiry_date": date.today() + timedelta(days=2),
    },
    {
        "id": 2,
        "name": "Eggs",
        "quantity": "12 pcs",
        "category": "Dairy",
        "purchase_date": date.today() - timedelta(days=2),
        "expiry_date": date.today() + timedelta(days=5),
    },
    {
        "id": 3,
        "name": "Spinach",
        "quantity": "200g",
        "category": "Vegetables",
        "purchase_date": date.today() - timedelta(days=1),
        "expiry_date": date.today() + timedelta(days=1),
    },
    {
        "id": 4,
        "name": "Chicken Breast",
        "quantity": "500g",
        "category": "Meat",
        "purchase_date": date.today(),
        "expiry_date": date.today() + timedelta(days=10),
    },
    {
        "id": 5,
        "name": "Apple Juice",
        "quantity": "2L",
        "category": "Beverages",
        "purchase_date": date.today() - timedelta(days=3),
        "expiry_date": date.today() + timedelta(days=20),
    },
]

def get_all_items():
    return MOCK_ITEMS

def get_expiring_items(days=7):
    today = date.today()
    return [
        item for item in MOCK_ITEMS
        if (item["expiry_date"] - today).days <= days
    ]
