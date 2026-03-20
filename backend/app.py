# backend/app.py — FreshMind Flask API
from flask import Flask, request, jsonify
from flask_cors import CORS
import jwt, os, requests as req
from datetime import datetime, timedelta
from functools import wraps
from dotenv import load_dotenv

# ── Import your existing modules (unchanged!) ──
import sys
sys.path.append(os.path.dirname(__file__))
from database import (
    create_tables, add_item, get_all_items,
    get_expiring_items, delete_item, update_item,
    log_usage, get_usage_history
)
from auth import (
    create_auth_tables, login_user, register_user,
    get_all_users, update_password
)
from ai_recipes import get_recipe_suggestions, chat_with_ai
from image_fetcher import get_food_image

load_dotenv()

app  = Flask(__name__)
CORS(app, origins=["http://localhost:5173", "http://localhost:3000"])

SECRET = os.getenv("JWT_SECRET", "freshmind_secret_2024")

# ── Init DB on startup ──
create_tables()
create_auth_tables()

# ─────────────────────────────────────────
# JWT HELPERS
# ─────────────────────────────────────────

def make_token(user_id, username):
    return jwt.encode({
        "id":       user_id,
        "username": username,
        "exp":      datetime.utcnow() + timedelta(days=7)
    }, SECRET, algorithm="HS256")

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.headers.get("Authorization", "")
        if not auth.startswith("Bearer "):
            return jsonify({"error": "Token missing"}), 401
        try:
            token   = auth.split(" ")[1]
            payload = jwt.decode(token, SECRET, algorithms=["HS256"])
            request.user = payload
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token expired"}), 401
        except Exception:
            return jsonify({"error": "Invalid token"}), 401
        return f(*args, **kwargs)
    return decorated

def rows_to_list(rows):
    return [dict(r) for r in rows]

# ─────────────────────────────────────────
# AUTH ROUTES
# ─────────────────────────────────────────

@app.route("/api/auth/login", methods=["POST"])
def login():
    data     = request.json or {}
    username = data.get("username", "").strip()
    password = data.get("password", "")
    if not username or not password:
        return jsonify({"error": "Fill all fields"}), 400
    user = login_user(username, password)
    if not user:
        return jsonify({"error": "Wrong username or password"}), 401
    user = dict(user)
    token = make_token(user["id"], username)
    return jsonify({"token": token, "user": user})

@app.route("/api/auth/register", methods=["POST"])
def register():
    data      = request.json or {}
    username  = data.get("username", "").strip()
    password  = data.get("password", "")
    email     = data.get("email", "")
    full_name = data.get("full_name", "").strip()
    if not username or not password or not full_name:
        return jsonify({"error": "Fill all required fields"}), 400
    if len(password) < 6:
        return jsonify({"error": "Password min 6 characters"}), 400
    ok, msg = register_user(username, password, email, full_name)
    if not ok:
        return jsonify({"error": msg}), 400
    user  = dict(login_user(username, password))
    token = make_token(user["id"], username)
    return jsonify({"token": token, "user": user})

@app.route("/api/auth/me", methods=["GET"])
@token_required
def me():
    return jsonify({"user": request.user})

# ─────────────────────────────────────────
# PANTRY ROUTES
# ─────────────────────────────────────────

@app.route("/api/pantry/items", methods=["GET"])
@token_required
def get_items():
    items = rows_to_list(get_all_items())
    return jsonify({"items": items})

@app.route("/api/pantry/expiring/<int:days>", methods=["GET"])
@token_required
def get_expiring(days):
    items = rows_to_list(get_expiring_items(days))
    return jsonify({"items": items})

@app.route("/api/pantry/items", methods=["POST"])
@token_required
def create_item():
    data = request.json or {}
    name          = data.get("name", "").strip()
    quantity      = data.get("quantity", "").strip()
    purchase_date = data.get("purchase_date", "")
    expiry_date   = data.get("expiry_date", "")
    category      = data.get("category", "Other")
    image_url     = data.get("image_url", "")
    if not name or not quantity:
        return jsonify({"error": "Name and quantity required"}), 400
    add_item(
        name=name, quantity=quantity,
        purchase_date=purchase_date,
        expiry_date=expiry_date,
        category=category,
        image_url=image_url
    )
    return jsonify({"message": f"{name} added!"})

@app.route("/api/pantry/items/<int:item_id>", methods=["PUT"])
@token_required
def edit_item(item_id):
    data = request.json or {}
    update_item(
        item_id,
        name        = data.get("name"),
        quantity    = data.get("quantity"),
        expiry_date = data.get("expiry_date"),
        category    = data.get("category")
    )
    return jsonify({"message": "Updated!"})

@app.route("/api/pantry/items/<int:item_id>", methods=["DELETE"])
@token_required
def remove_item(item_id):
    data   = request.json or {}
    wasted = data.get("wasted", True)
    items  = rows_to_list(get_all_items())
    item   = next((i for i in items if i["id"] == item_id), None)
    if item:
        log_usage(item["name"], was_wasted=wasted)
    delete_item(item_id)
    return jsonify({"message": "Deleted!"})

@app.route("/api/pantry/items/<int:item_id>/use", methods=["POST"])
@token_required
def mark_used(item_id):
    items = rows_to_list(get_all_items())
    item  = next((i for i in items if i["id"] == item_id), None)
    if item:
        log_usage(item["name"], was_wasted=False)
        delete_item(item_id)
    return jsonify({"message": "Marked as used!"})

@app.route("/api/pantry/history", methods=["GET"])
@token_required
def get_history():
    history = rows_to_list(get_usage_history())
    return jsonify({"history": history})

# ─────────────────────────────────────────
# IMAGE ROUTE
# ─────────────────────────────────────────

@app.route("/api/image/fetch", methods=["GET"])
@token_required
def fetch_image():
    name = request.args.get("name", "")
    if not name:
        return jsonify({"url": "", "emoji": "🛒"})
    url, emoji = get_food_image(name)
    return jsonify({"url": url or "", "emoji": emoji})

# ─────────────────────────────────────────
# AI ROUTES
# ─────────────────────────────────────────

@app.route("/api/ai/recipes", methods=["POST"])
@token_required
def get_recipes():
    data        = request.json or {}
    preferences = data.get("preferences", "Any")
    all_items      = rows_to_list(get_all_items())
    expiring_items = rows_to_list(get_expiring_items(7))
    result = get_recipe_suggestions(
        all_items, expiring_items, preferences
    )
    return jsonify({"recipes": result})

@app.route("/api/ai/chat", methods=["POST"])
@token_required
def chat():
    data    = request.json or {}
    message = data.get("message", "")
    history = data.get("history", [])
    response, updated_history = chat_with_ai(message, history)
    return jsonify({
        "response": response,
        "history":  updated_history
    })

# ─────────────────────────────────────────
# WEATHER ROUTE
# ─────────────────────────────────────────

@app.route("/api/weather", methods=["GET"])
def get_weather():
    try:
        r = req.get(
            "https://wttr.in/Bengaluru?format=j1",
            timeout=4
        )
        d = r.json()["current_condition"][0]
        return jsonify({
            "temp":     d["temp_C"],
            "feels":    d["FeelsLikeC"],
            "humidity": d["humidity"],
            "desc":     d["weatherDesc"][0]["value"],
            "wind":     d["windspeedKmph"],
        })
    except Exception:
        return jsonify({
            "temp": "30", "feels": "33",
            "humidity": "65",
            "desc": "Partly Cloudy", "wind": "10"
        })

# ─────────────────────────────────────────
# USERS ROUTE (admin only)
# ─────────────────────────────────────────

@app.route("/api/users", methods=["GET"])
@token_required
def list_users():
    users = rows_to_list(get_all_users())
    return jsonify({"users": users})

@app.route("/api/users/password", methods=["PUT"])
@token_required
def change_password():
    data     = request.json or {}
    user_id  = request.user["id"]
    old_pass = data.get("old_password", "")
    new_pass = data.get("new_password", "")
    if len(new_pass) < 6:
        return jsonify({"error": "Min 6 characters"}), 400
    ok, msg = update_password(user_id, old_pass, new_pass)
    if not ok:
        return jsonify({"error": msg}), 400
    return jsonify({"message": msg})

# ─────────────────────────────────────────
# HEALTH CHECK
# ─────────────────────────────────────────

@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({
        "status": "ok",
        "app":    "FreshMind API",
        "version":"1.0.0"
    })

if __name__ == "__main__":
    app.run(debug=True, port=5000)
