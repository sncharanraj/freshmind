# image_fetcher.py — Fixed with User-Agent header
import requests

# ── Required header for Wikipedia API ──
HEADERS = {
    "User-Agent": "FreshMind/1.0 (food pantry app; "
                  "contact@freshmind.com)"
}

# ─────────────────────────────────────────
# EMOJI MAP
# ─────────────────────────────────────────

EMOJI_MAP = {
    "milk": "🥛", "egg": "🥚", "eggs": "🥚",
    "bread": "🍞", "butter": "🧈", "cheese": "🧀",
    "apple": "🍎", "banana": "🍌", "orange": "🍊",
    "mango": "🥭", "grapes": "🍇", "strawberry": "🍓",
    "tomato": "🍅", "potato": "🥔", "onion": "🧅",
    "garlic": "🧄", "carrot": "🥕", "spinach": "🥬",
    "broccoli": "🥦", "corn": "🌽", "pepper": "🌶️",
    "chicken": "🍗", "meat": "🥩", "fish": "🐟",
    "rice": "🍚", "pasta": "🍝", "flour": "🌾",
    "sugar": "🍬", "salt": "🧂", "oil": "🫙",
    "coffee": "☕", "tea": "🍵", "juice": "🧃",
    "yogurt": "🍶", "paneer": "🧀", "ghee": "🧈",
    "chocolate": "🍫", "lemon": "🍋", "avocado": "🥑",
    "mushroom": "🍄", "cucumber": "🥒", "coconut": "🥥",
    "dal": "🫘", "lentils": "🫘", "roti": "🫓",
    "ginger": "🫚", "turmeric": "🌿", "cumin": "🌿",
    "watermelon": "🍉", "pineapple": "🍍",
}

# ─────────────────────────────────────────
# INDIAN FOOD TRANSLATION MAP
# ─────────────────────────────────────────

INDIAN_FOOD_MAP = {
    "atta": "wheat flour", "maida": "refined flour",
    "besan": "chickpea flour", "sooji": "semolina",
    "poha": "flattened rice", "dal": "lentil",
    "chana": "chickpea", "rajma": "kidney bean",
    "moong": "mung bean", "masoor": "red lentil",
    "urad": "urad bean", "aloo": "potato",
    "pyaaz": "onion", "tamatar": "tomato",
    "palak": "spinach", "gobi": "cauliflower",
    "baingan": "eggplant", "bhindi": "okra",
    "lauki": "bottle gourd", "karela": "bitter gourd",
    "methi": "fenugreek", "doodh": "milk",
    "dahi": "yogurt", "makhan": "butter",
    "haldi": "turmeric", "jeera": "cumin",
    "dhania": "coriander", "mirchi": "chili pepper",
    "adrak": "ginger", "lehsun": "garlic",
    "roti": "roti bread", "chapati": "chapati bread",
    "paratha": "paratha bread", "idli": "idli",
    "dosa": "dosa", "sambar": "sambar",
    "biryani": "biryani", "paneer": "paneer cheese",
    "ghee": "ghee butter",
}

def get_emoji(item_name):
    """Returns best matching emoji for food item"""
    name_lower = item_name.lower().strip()
    for key, emoji in EMOJI_MAP.items():
        if key in name_lower:
            return emoji
    return "🥘"

def translate_for_search(item_name):
    """Translates Indian food names to English"""
    name_lower = item_name.lower().strip()
    if name_lower in INDIAN_FOOD_MAP:
        return INDIAN_FOOD_MAP[name_lower]
    for indian, english in INDIAN_FOOD_MAP.items():
        if indian in name_lower:
            return english
    return item_name

def get_food_image(item_name):
    """
    Fetches food image — tries 3 sources.

    Returns:
        tuple: (image_url or None, emoji)
    """
    emoji       = get_emoji(item_name)
    search_term = translate_for_search(item_name)

    # Try Wikipedia first
    url = _try_wikipedia(search_term)
    if url:
        return url, emoji

    # Try Open Food Facts
    url = _try_open_food_facts(search_term)
    if url:
        return url, emoji

    return None, emoji

def _try_wikipedia(search_term):
    """Fetches image from Wikipedia with proper headers"""
    try:
        # Step 1 — Search for page
        search_resp = requests.get(
            "https://en.wikipedia.org/w/api.php",
            headers=HEADERS,
            params={
                "action":   "query",
                "list":     "search",
                "srsearch": f"{search_term} food",
                "format":   "json",
                "srlimit":  1
            },
            timeout=8
        )

        if search_resp.status_code != 200:
            return None

        results = search_resp.json().get(
            "query", {}
        ).get("search", [])

        if not results:
            return None

        # Step 2 — Get page summary with image
        page_title = results[0]["title"]
        summary_resp = requests.get(
            f"https://en.wikipedia.org/api/rest_v1"
            f"/page/summary/{page_title.replace(' ', '_')}",
            headers=HEADERS,
            timeout=8
        )

        if summary_resp.status_code != 200:
            return None

        data      = summary_resp.json()
        thumbnail = data.get("thumbnail", {})

        if thumbnail:
            img_url = thumbnail.get("source", "")
            # Get better quality image
            img_url = img_url.replace("/320px-", "/400px-")
            return img_url if img_url else None

    except Exception as e:
        print(f"Wikipedia error: {e}")

    return None

def _try_open_food_facts(search_term):
    """Fetches image from Open Food Facts"""
    try:
        resp = requests.get(
            "https://world.openfoodfacts.org/cgi/search.pl",
            headers=HEADERS,
            params={
                "search_terms": search_term,
                "search_simple": 1,
                "action":        "process",
                "json":          1,
                "page_size":     5,
            },
            timeout=8
        )

        if resp.status_code != 200:
            return None

        products = resp.json().get("products", [])
        for product in products:
            img = (
                product.get("image_front_small_url") or
                product.get("image_url") or
                product.get("image_small_url")
            )
            if img and img.startswith("http"):
                return img

    except Exception as e:
        print(f"OpenFoodFacts error: {e}")

    return None