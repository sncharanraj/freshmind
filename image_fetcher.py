# image_fetcher.py
# Fetches food images from Wikipedia API
# No API key needed — completely free!

import requests

# ─────────────────────────────────────────
# EMOJI FALLBACK MAP
# ─────────────────────────────────────────
# Used when Wikipedia has no image

EMOJI_MAP = {
    # Dairy
    "milk":        "🥛", "cheese":    "🧀", "butter":   "🧈",
    "yogurt":      "🥛", "cream":     "🥛", "curd":     "🥛",

    # Vegetables
    "tomato":      "🍅", "potato":    "🥔", "onion":    "🧅",
    "garlic":      "🧄", "carrot":    "🥕", "broccoli": "🥦",
    "spinach":     "🥬", "lettuce":   "🥬", "cucumber": "🥒",
    "pepper":      "🫑", "corn":      "🌽", "mushroom": "🍄",
    "eggplant":    "🍆", "pumpkin":   "🎃", "beans":    "🫘",

    # Fruits
    "apple":       "🍎", "banana":    "🍌", "orange":   "🍊",
    "mango":       "🥭", "grapes":    "🍇", "lemon":    "🍋",
    "strawberry":  "🍓", "watermelon":"🍉", "pineapple":"🍍",
    "cherry":      "🍒", "peach":     "🍑", "pear":     "🍐",
    "coconut":     "🥥", "kiwi":      "🥝", "avocado":  "🥑",

    # Meat & Seafood
    "chicken":     "🍗", "meat":      "🥩", "fish":     "🐟",
    "egg":         "🥚", "eggs":      "🥚", "shrimp":   "🍤",
    "beef":        "🥩", "pork":      "🥩", "lamb":     "🥩",

    # Grains
    "rice":        "🍚", "bread":     "🍞", "wheat":    "🌾",
    "pasta":       "🍝", "noodles":   "🍜", "flour":    "🌾",
    "oats":        "🌾", "cereal":    "🥣",

    # Beverages
    "water":       "💧", "juice":     "🧃", "coffee":   "☕",
    "tea":         "🍵", "milk":      "🥛",

    # Condiments
    "salt":        "🧂", "sugar":     "🍬", "oil":      "🫙",
    "sauce":       "🫙", "honey":     "🍯", "vinegar":  "🫙",

    # Snacks
    "chips":       "🍟", "chocolate": "🍫", "biscuit":  "🍪",
    "cookie":      "🍪", "cake":      "🎂", "nuts":     "🥜",
}

def get_emoji(item_name):
    """
    Returns emoji for a food item.
    Checks if any key word matches the item name.
    """
    name_lower = item_name.lower()
    for key, emoji in EMOJI_MAP.items():
        if key in name_lower:
            return emoji
    return "🛒"  # default emoji


def get_food_image(item_name):
    """
    Fetches food image from Wikipedia API.
    No API key needed — completely free!

    Parameters:
        item_name (str): Name of the food item

    Returns:
        tuple: (image_url, emoji)
               image_url → Wikipedia image URL or None
               emoji     → fallback emoji always included
    """
    emoji = get_emoji(item_name)

    try:
        # Clean up item name for Wikipedia search
        search_term = item_name.strip().title()

        # Wikipedia REST API — get page summary + image
        url = (
            f"https://en.wikipedia.org/api/rest_v1/"
            f"page/summary/{search_term}"
        )

        response = requests.get(url, timeout=5)

        if response.status_code == 200:
            data = response.json()

            # Check if Wikipedia returned a thumbnail
            if "thumbnail" in data:
                image_url = data["thumbnail"]["source"]

                # Upgrade to higher resolution image
                # Wikipedia thumbnails are small by default
                image_url = image_url.replace(
                    "/thumb/", "/"
                ).rsplit("/", 1)[0]

                # Fallback to original thumbnail if
                # high-res doesn't work
                image_url = data["thumbnail"]["source"]
                return image_url, emoji

        # If Wikipedia has no image try with "food" appended
        url2 = (
            f"https://en.wikipedia.org/api/rest_v1/"
            f"page/summary/{search_term}_food"
        )
        response2 = requests.get(url2, timeout=5)

        if response2.status_code == 200:
            data2 = response2.json()
            if "thumbnail" in data2:
                return data2["thumbnail"]["source"], emoji

    except Exception as e:
        print(f"Image fetch failed for {item_name}: {e}")

    # Return None if no image found — emoji will be used
    return None, emoji


if __name__ == "__main__":
    # Quick test
    test_items = [
        "Milk", "Apple", "Spinach",
        "Chicken", "Rice", "Banana"
    ]
    print("🧪 Testing Wikipedia Image Fetcher...\n")
    for item in test_items:
        url, emoji = get_food_image(item)
        print(f"{emoji} {item}:")
        print(f"   URL: {url or 'No image found'}\n")