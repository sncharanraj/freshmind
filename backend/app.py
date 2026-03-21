# backend/app.py — FreshMind Flask API (user isolation + login history)
from flask import Flask, request, jsonify
from flask_cors import CORS
import jwt, os
import requests as req
from datetime import datetime, timedelta
from functools import wraps
from dotenv import load_dotenv

import sys
sys.path.append(os.path.dirname(__file__))
from database import (
    create_tables, add_item, get_all_items,
    get_expiring_items, delete_item, update_item,
    log_usage, get_usage_history,
    log_login, get_login_history, get_all_login_stats
)
from auth import (
    create_auth_tables, login_user, register_user,
    get_all_users, update_password
)
from ai_recipes import get_recipe_suggestions, chat_with_ai
from image_fetcher import get_food_image

load_dotenv()
app  = Flask(__name__)
CORS(app, origins=["http://localhost:5173","http://localhost:3000"])
SECRET = os.getenv("JWT_SECRET","freshmind_secret_2024")

create_tables()
create_auth_tables()

# ─────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────
def make_token(user_id, username, role="member"):
    return jwt.encode({
        "id": user_id, "username": username, "role": role,
        "exp": datetime.utcnow() + timedelta(days=7)
    }, SECRET, algorithm="HS256")

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.headers.get("Authorization","")
        if not auth.startswith("Bearer "):
            return jsonify({"error":"Token missing"}), 401
        try:
            request.user = jwt.decode(
                auth.split(" ")[1], SECRET, algorithms=["HS256"]
            )
        except jwt.ExpiredSignatureError:
            return jsonify({"error":"Token expired"}), 401
        except Exception:
            return jsonify({"error":"Invalid token"}), 401
        return f(*args, **kwargs)
    return decorated

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.headers.get("Authorization","")
        if not auth.startswith("Bearer "):
            return jsonify({"error":"Token missing"}), 401
        try:
            payload = jwt.decode(
                auth.split(" ")[1], SECRET, algorithms=["HS256"]
            )
            request.user = payload
            if payload.get("role") != "admin":
                return jsonify({"error":"Admin only"}), 403
        except Exception:
            return jsonify({"error":"Invalid token"}), 401
        return f(*args, **kwargs)
    return decorated

def rows(r):   return [dict(x) for x in r]
def uid():     return request.user["id"]
def client_ip(): return request.headers.get("X-Forwarded-For") or request.remote_addr or ""

# ─────────────────────────────────────────
# ROOT
# ─────────────────────────────────────────
@app.route("/")
def index():
    return jsonify({
        "app":"FreshMind API","version":"1.0.0",
        "status":"running ✅",
        "tip":"Open http://localhost:5173 for the app"
    })

# ─────────────────────────────────────────
# AUTH
# ─────────────────────────────────────────
@app.route("/api/auth/login", methods=["POST"])
def login():
    data = request.json or {}
    username = data.get("username","").strip()
    password = data.get("password","")
    if not username or not password:
        return jsonify({"error":"Fill all fields"}), 400
    user = login_user(username, password)
    if not user:
        return jsonify({"error":"Wrong username or password"}), 401
    user  = dict(user)
    token = make_token(user["id"], username, user.get("role","member"))
    log_login(user["id"], username, client_ip())
    return jsonify({"token":token,"user":user})

@app.route("/api/auth/register", methods=["POST"])
def register():
    data = request.json or {}
    username  = data.get("username","").strip()
    password  = data.get("password","")
    email     = data.get("email","")
    full_name = data.get("full_name","").strip()
    if not username or not password or not full_name:
        return jsonify({"error":"Fill all required fields"}), 400
    if len(password) < 6:
        return jsonify({"error":"Password min 6 characters"}), 400
    ok, msg = register_user(username, password, email, full_name)
    if not ok:
        return jsonify({"error":msg}), 400
    user  = dict(login_user(username, password))
    token = make_token(user["id"], username, user.get("role","member"))
    log_login(user["id"], username, client_ip())
    return jsonify({"token":token,"user":user})

@app.route("/api/auth/me", methods=["GET"])
@token_required
def me():
    return jsonify({"user":request.user})

# ─────────────────────────────────────────
# PANTRY — all filtered by uid()
# ─────────────────────────────────────────
@app.route("/api/pantry/items", methods=["GET"])
@token_required
def get_items():
    return jsonify({"items": rows(get_all_items(user_id=uid()))})

@app.route("/api/pantry/expiring/<int:days>", methods=["GET"])
@token_required
def get_expiring(days):
    return jsonify({"items": rows(get_expiring_items(days, user_id=uid()))})

@app.route("/api/pantry/items", methods=["POST"])
@token_required
def create_item():
    d = request.json or {}
    name     = d.get("name","").strip()
    quantity = d.get("quantity","").strip()
    if not name or not quantity:
        return jsonify({"error":"Name and quantity required"}), 400
    add_item(
        name=name, quantity=quantity,
        purchase_date=d.get("purchase_date",""),
        expiry_date=d.get("expiry_date",""),
        category=d.get("category","Other"),
        image_url=d.get("image_url",""),
        user_id=uid()
    )
    return jsonify({"message":f"{name} added!"})

@app.route("/api/pantry/items/<int:item_id>", methods=["PUT"])
@token_required
def edit_item(item_id):
    d = request.json or {}
    update_item(item_id, user_id=uid(),
                name=d.get("name"), quantity=d.get("quantity"),
                expiry_date=d.get("expiry_date"), category=d.get("category"))
    return jsonify({"message":"Updated!"})

@app.route("/api/pantry/items/<int:item_id>", methods=["DELETE"])
@token_required
def remove_item(item_id):
    d      = request.json or {}
    wasted = d.get("wasted", True)
    u      = uid()
    items  = rows(get_all_items(user_id=u))
    item   = next((i for i in items if i["id"]==item_id), None)
    if item:
        log_usage(item["name"], was_wasted=wasted, user_id=u)
    delete_item(item_id, user_id=u)
    return jsonify({"message":"Deleted!"})

@app.route("/api/pantry/items/<int:item_id>/use", methods=["POST"])
@token_required
def mark_used(item_id):
    u     = uid()
    items = rows(get_all_items(user_id=u))
    item  = next((i for i in items if i["id"]==item_id), None)
    if item:
        log_usage(item["name"], was_wasted=False, user_id=u)
        delete_item(item_id, user_id=u)
    return jsonify({"message":"Marked as used!"})

@app.route("/api/pantry/history", methods=["GET"])
@token_required
def get_history():
    return jsonify({"history": rows(get_usage_history(user_id=uid()))})

# ─────────────────────────────────────────
# IMAGE
# ─────────────────────────────────────────
@app.route("/api/image/fetch", methods=["GET"])
@token_required
def fetch_image():
    name = request.args.get("name","")
    if not name: return jsonify({"url":"","emoji":"🛒"})
    url, emoji = get_food_image(name)
    return jsonify({"url":url or "","emoji":emoji})

# ─────────────────────────────────────────
# AI
# ─────────────────────────────────────────
@app.route("/api/ai/recipes", methods=["POST"])
@token_required
def get_recipes():
    d   = request.json or {}
    u   = uid()
    res = get_recipe_suggestions(
        rows(get_all_items(user_id=u)),
        rows(get_expiring_items(7, user_id=u)),
        d.get("preferences","Any")
    )
    return jsonify({"recipes":res})

@app.route("/api/ai/chat", methods=["POST"])
@token_required
def chat():
    d        = request.json or {}
    response, _ = chat_with_ai(d.get("message",""), d.get("history",[]))
    return jsonify({"response":response})

# ─────────────────────────────────────────
# WEATHER
# ─────────────────────────────────────────
@app.route("/api/weather", methods=["GET"])
def get_weather():
    try:
        r = req.get("https://wttr.in/Bengaluru?format=j1", timeout=4)
        d = r.json()["current_condition"][0]
        return jsonify({
            "temp":d["temp_C"],"feels":d["FeelsLikeC"],
            "humidity":d["humidity"],
            "desc":d["weatherDesc"][0]["value"],
            "wind":d["windspeedKmph"]
        })
    except:
        return jsonify({"temp":"30","feels":"33","humidity":"65",
                        "desc":"Partly Cloudy","wind":"10"})

# ─────────────────────────────────────────
# USER
# ─────────────────────────────────────────
@app.route("/api/users/password", methods=["PUT"])
@token_required
def change_password():
    d = request.json or {}
    new_pass = d.get("new_password","")
    if len(new_pass) < 6:
        return jsonify({"error":"Min 6 characters"}), 400
    ok, msg = update_password(uid(), d.get("old_password",""), new_pass)
    if not ok: return jsonify({"error":msg}), 400
    return jsonify({"message":msg})

@app.route("/api/me/login-history", methods=["GET"])
@token_required
def my_login_history():
    return jsonify({"history": rows(get_login_history(user_id=uid(), limit=20))})

# ─────────────────────────────────────────
# ADMIN
# ─────────────────────────────────────────
@app.route("/api/admin/users", methods=["GET"])
@admin_required
def admin_users():
    return jsonify({"users": rows(get_all_users())})

@app.route("/api/admin/login-history", methods=["GET"])
@admin_required
def admin_login_history():
    limit = int(request.args.get("limit",100))
    return jsonify({"history": rows(get_login_history(user_id=None, limit=limit))})

@app.route("/api/admin/login-stats", methods=["GET"])
@admin_required
def admin_login_stats():
    return jsonify({"stats": rows(get_all_login_stats())})

# ─────────────────────────────────────────
# HEALTH
# ─────────────────────────────────────────
@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"status":"ok","app":"FreshMind API","version":"1.0.0"})

if __name__ == "__main__":
    app.run(debug=True, port=5000)