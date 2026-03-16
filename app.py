import streamlit as st
import re
import requests
import datetime
from datetime import date, timedelta
from database import (get_all_items, get_expiring_items, add_item,
                      delete_item, update_item, log_usage,
                      create_tables, get_usage_history)
from ai_recipes import get_recipe_suggestions, chat_with_ai
from auth import verify_user, create_user, logout

# Initialize database
create_tables()

# Session state init
for key, val in {
    "logged_in": False,
    "user": None,
    "nav": "🏠 Home",
    "chat_history": [],
    "recipes_generated": False,
    "sidebar_collapsed": False,
}.items():
    if key not in st.session_state:
        st.session_state[key] = val

st.set_page_config(page_title="FreshMind", page_icon="🥬", layout="wide")

# ─────────────────────────────────────────
# GLOBAL CSS
# ─────────────────────────────────────────
st.markdown("""
<style>
  .stApp { background-color: #f0faf4; }
  [data-testid="stSidebar"] {
      background-color: #ffffff;
      border-right: 1px solid #e0f2e9;
  }
  .stButton > button {
      background-color: #2d6a4f !important;
      color: white !important;
      border: none !important;
      border-radius: 8px !important;
      transition: all 0.2s !important;
  }
  .stButton > button:hover {
      background-color: #1b5e20 !important;
      transform: translateY(-1px) !important;
  }
  [data-testid="stMetric"] {
      background: white;
      border-radius: 12px;
      padding: 16px;
      border: 1px solid #e0f2e9;
      transition: all 0.2s;
  }
  [data-testid="stMetric"]:hover {
      transform: translateY(-2px);
      box-shadow: 0 8px 20px rgba(45,106,79,0.1);
  }
  .stTextInput > div > div > input {
      border-radius: 8px !important;
      border: 1px solid #c8e6c9 !important;
  }
  div[data-testid="stForm"] {
      background: white;
      border-radius: 16px;
      padding: 24px;
      border: 1px solid #e0f2e9;
  }

  /* Cards */
  .hero-card {
      background: linear-gradient(135deg, #1b5e20 0%, #2d6a4f 50%, #388e3c 100%);
      border-radius: 16px;
      padding: 32px 36px;
      color: white;
      position: relative;
      overflow: hidden;
      margin-bottom: 20px;
  }
  .hero-bg1 {
      position: absolute;
      width: 200px; height: 200px;
      border-radius: 50%;
      background: rgba(255,255,255,0.05);
      top: -60px; right: -40px;
  }
  .hero-bg2 {
      position: absolute;
      width: 120px; height: 120px;
      border-radius: 50%;
      background: rgba(255,255,255,0.04);
      bottom: -30px; right: 80px;
  }
  .hero-leaf {
      position: absolute;
      right: 24px; top: 50%;
      transform: translateY(-50%);
      font-size: 80px;
      opacity: 0.15;
  }
  .notif-red {
      background: #ffebee;
      border-left: 4px solid #e53935;
      border-radius: 8px;
      padding: 12px 16px;
      color: #c62828;
      font-size: 14px;
      margin-bottom: 12px;
      animation: slideIn 0.3s ease;
  }
  .notif-orange {
      background: #fff8e1;
      border-left: 4px solid #fb8c00;
      border-radius: 8px;
      padding: 12px 16px;
      color: #e65100;
      font-size: 14px;
      margin-bottom: 12px;
  }
  .notif-green {
      background: #e8f5e9;
      border-left: 4px solid #43a047;
      border-radius: 8px;
      padding: 12px 16px;
      color: #1b5e20;
      font-size: 14px;
      margin-bottom: 12px;
  }
  @keyframes slideIn {
      from { opacity:0; transform:translateY(-8px); }
      to   { opacity:1; transform:translateY(0); }
  }
  .info-card {
      background: white;
      border-radius: 12px;
      padding: 16px;
      border: 1px solid #e0f2e9;
      height: 100%;
  }
  .card-title {
      font-size: 14px;
      font-weight: 600;
      color: #1b5e20;
      margin-bottom: 12px;
  }
  .activity-item {
      display: flex;
      align-items: flex-start;
      gap: 10px;
      padding: 8px 0;
      border-bottom: 1px solid #f5f5f5;
      font-size: 13px;
  }
  .activity-item:last-child { border-bottom: none; }
  .act-dot {
      width: 28px; height: 28px;
      border-radius: 8px;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 14px;
      flex-shrink: 0;
      margin-top: 1px;
  }
  .stock-item {
      display: flex;
      align-items: center;
      gap: 10px;
      padding: 8px 0;
      border-bottom: 1px solid #f5f5f5;
  }
  .stock-item:last-child { border-bottom: none; }
  .stock-prog {
      height: 4px;
      background: #f0f0f0;
      border-radius: 4px;
      margin-top: 4px;
  }
  .quick-action {
      background: white;
      border: 1px solid #e0f2e9;
      border-radius: 12px;
      padding: 16px 8px;
      text-align: center;
      cursor: pointer;
      transition: all 0.25s;
  }
  .quick-action:hover {
      transform: translateY(-3px);
      box-shadow: 0 8px 20px rgba(45,106,79,0.12);
      border-color: #2d6a4f;
  }
  .pantry-row-red {
      background: #fff3f3;
      border: 1px solid #ffcdd2;
      border-radius: 8px;
      padding: 12px 16px;
      margin-bottom: 8px;
  }
  .pantry-row-orange {
      background: #fff8e1;
      border: 1px solid #ffe082;
      border-radius: 8px;
      padding: 12px 16px;
      margin-bottom: 8px;
  }
  .pantry-row-green {
      background: #f1f8e9;
      border: 1px solid #c5e1a5;
      border-radius: 8px;
      padding: 12px 16px;
      margin-bottom: 8px;
  }
  .weather-card {
      background: linear-gradient(135deg, #e3f2fd, #e8f5e9);
      border-radius: 12px;
      padding: 16px;
      border: 1px solid #c8e6c9;
  }
  .tip-card {
      background: linear-gradient(135deg, #fff8e1, #e8f5e9);
      border-radius: 12px;
      padding: 16px;
      border: 1px solid #c8e6c9;
  }
  .savings-card {
      background: linear-gradient(135deg, #e8f5e9, #f1f8e9);
      border-radius: 12px;
      padding: 20px;
      border: 1px solid #c8e6c9;
      text-align: center;
  }

  /* Confetti */
  .confetti-piece {
      position: fixed;
      width: 8px; height: 8px;
      border-radius: 2px;
      animation: confetti-fall linear forwards;
      z-index: 9999;
      pointer-events: none;
  }
  @keyframes confetti-fall {
      0%   { transform: translateY(-20px) rotate(0deg); opacity: 1; }
      100% { transform: translateY(100vh) rotate(720deg); opacity: 0; }
  }
</style>
""", unsafe_allow_html=True)

# Confetti JS
st.markdown("""
<script>
function triggerConfetti() {
    const colors = ['#2d6a4f','#43a047','#fb8c00','#1565c0','#e53935','#ffd600','#00bcd4'];
    for (let i = 0; i < 80; i++) {
        const p = document.createElement('div');
        p.className = 'confetti-piece';
        p.style.cssText = `
            left: ${Math.random()*100}vw;
            top: 0;
            background: ${colors[Math.floor(Math.random()*colors.length)]};
            animation-duration: ${0.8+Math.random()*1.5}s;
            animation-delay: ${Math.random()*0.5}s;
            width: ${4+Math.random()*8}px;
            height: ${4+Math.random()*8}px;
        `;
        document.body.appendChild(p);
        setTimeout(() => p.remove(), 2500);
    }
}
</script>
""", unsafe_allow_html=True)
# ─────────────────────────────────────────
# BACK BUTTON & BREADCRUMB HELPER
# ─────────────────────────────────────────
def show_back_button(current_page, back_to="🏠 Home"):
    """Shows breadcrumb and back button at top of every page"""
    col1, col2 = st.columns([1, 8])
    with col1:
        if st.button("← Back"):
            st.session_state.nav = back_to
            st.rerun()
    with col2:
        # Breadcrumb
        st.markdown(f"""
        <div style='padding:6px 0; font-size:13px; color:#888;'>
            <span style='color:#2d6a4f; cursor:pointer;'>🏠 Home</span>
            <span style='margin:0 6px;'>›</span>
            <span style='color:#333; font-weight:500;'>{current_page}</span>
        </div>
        """, unsafe_allow_html=True)
    st.markdown("---")


# ─────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────
def parse_quantity(qty_str):
    numbers = re.findall(r'\d+\.?\d*', str(qty_str))
    units   = re.findall(r'[a-zA-Z]+',  str(qty_str))
    return (float(numbers[0]) if numbers else 0,
            units[0] if units else "pcs")

DAILY_TIPS = [
    "Store herbs in water in the fridge — they last 2x longer!",
    "Keep bananas separate — they ripen other fruits faster.",
    "Freeze bread before expiry — stays fresh for 3 months!",
    "Store onions and potatoes separately to prevent spoilage.",
    "Use airtight containers — leftovers last 3x longer!",
    "Check your pantry before shopping to avoid duplicates.",
    "The freezer is your best friend for extending shelf life!",
]

FOOD_EMOJIS = {
    "Dairy": "🥛", "Vegetables": "🥦", "Fruits": "🍎",
    "Meat": "🍗", "Seafood": "🐟", "Grains": "🌾",
    "Beverages": "🥤", "Snacks": "🍿", "Other": "🛒"
}

def get_weather():
    """Fetch real weather for Bengaluru"""
    try:
        url = "https://wttr.in/Bengaluru?format=j1"
        r = requests.get(url, timeout=5)
        data = r.json()
        current = data["current_condition"][0]
        return {
            "temp": current["temp_C"],
            "feels": current["FeelsLikeC"],
            "humidity": current["humidity"],
            "desc": current["weatherDesc"][0]["value"],
            "wind": current["windspeedKmph"],
        }
    except:
        return {
            "temp": "31", "feels": "34",
            "humidity": "65", "desc": "Partly Cloudy",
            "wind": "12"
        }

def get_greeting():
    h = datetime.datetime.now().hour
    if h < 12:   return "Good Morning"
    if h < 17:   return "Good Afternoon"
    return "Good Evening"

def get_low_stock_items(items, threshold=3):
    """Find items with quantity <= threshold"""
    low = []
    for item in items:
        num, unit = parse_quantity(item["quantity"])
        if num <= threshold:
            low.append(item)
    return low


# ─────────────────────────────────────────
# PAGE 0 — LOGIN
# ─────────────────────────────────────────
def show_login():
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        st.markdown("""
        <div style='text-align:center; margin-bottom:28px;'>
            <div style='font-size:3rem;'>🥬</div>
            <h1 style='color:#2d6a4f; font-size:2rem; margin:8px 0 4px;'>FreshMind</h1>
            <p style='color:#52b788;'>Your AI-Powered Smart Pantry Assistant</p>
        </div>
        """, unsafe_allow_html=True)

        tab1, tab2 = st.tabs(["🔑 Login", "📝 Register"])

        with tab1:
            st.markdown("#### Welcome Back!")
            email    = st.text_input("Email", placeholder="admin@freshmind.com", key="li_email")
            password = st.text_input("Password", type="password", placeholder="••••••••", key="li_pass")
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Login to FreshMind", use_container_width=True):
                if not email or not password:
                    st.error("Please fill in all fields!")
                else:
                    user = verify_user(email, password)
                    if user:
                        st.session_state.logged_in = True
                        st.session_state.user = user
                        st.success(f"Welcome, {user['name']}!")
                        st.rerun()
                    else:
                        st.error("Wrong email or password!")
            st.markdown("---")
            st.markdown("""
            <div style='background:#e8f5e9; border-radius:8px;
            padding:10px 14px; font-size:13px; color:#2d6a4f;'>
                Demo: admin@freshmind.com / freshmind123
            </div>
            """, unsafe_allow_html=True)

        with tab2:
            st.markdown("#### Create Account")
            name     = st.text_input("Full Name", placeholder="Your name", key="re_name")
            email2   = st.text_input("Email", placeholder="you@email.com", key="re_email")
            pass1    = st.text_input("Password", type="password", key="re_pass1")
            pass2    = st.text_input("Confirm Password", type="password", key="re_pass2")
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Create Account", use_container_width=True):
                if not name or not email2 or not pass1:
                    st.error("Please fill all fields!")
                elif pass1 != pass2:
                    st.error("Passwords do not match!")
                elif len(pass1) < 6:
                    st.error("Password must be at least 6 characters!")
                elif "@" not in email2:
                    st.error("Enter a valid email!")
                else:
                    if create_user(name, email2, pass1):
                        st.success("Account created! Please login.")
                    else:
                        st.error("Email already exists!")


# ─────────────────────────────────────────
# PAGE 1 — HOME
# ─────────────────────────────────────────
def show_home():
    items   = [dict(i) for i in get_all_items()]
    today   = date.today()
    total   = len(items)
    expiring = [i for i in items
                if (date.fromisoformat(str(i["expiry_date"])) - today).days <= 7]
    critical = [i for i in items
                if (date.fromisoformat(str(i["expiry_date"])) - today).days <= 3]
    history  = [dict(h) for h in get_usage_history()]
    saved    = len([h for h in history if not h["was_wasted"]])
    low_stock = get_low_stock_items(items)

    # ── Notification Banner ──
    if critical:
        names = ", ".join([i["name"] for i in critical[:3]])
        st.markdown(f"""
        <div class='notif-red'>
            🔴 <b>Urgent!</b> {len(critical)} item(s) expiring
            in less than 3 days — <b>{names}</b>
        </div>
        """, unsafe_allow_html=True)
    elif expiring:
        st.markdown(f"""
        <div class='notif-orange'>
            🟠 <b>Heads up!</b> {len(expiring)} item(s) expiring
            this week. Check your pantry!
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class='notif-green'>
            ✅ <b>All good!</b> All pantry items are fresh!
        </div>
        """, unsafe_allow_html=True)

    # ── Hero Section ──
    st.markdown(f"""
    <div class='hero-card'>
        <div class='hero-bg1'></div>
        <div class='hero-bg2'></div>
        <div class='hero-leaf'>🥬</div>
        <div style='font-size:11px; color:#a5d6a7;
        text-transform:uppercase; letter-spacing:1.5px;
        margin-bottom:8px;'>{get_greeting()}</div>
        <h1 style='font-size:2rem; margin-bottom:6px; color:white;'>
            Welcome back, {st.session_state.user['name']}! 👋
        </h1>
        <p style='color:#c8e6c9; margin-bottom:20px; font-size:1rem;'>
            You have <b>{total}</b> items in your pantry.
            {f"<b>{len(critical)}</b> need urgent attention today."
             if critical else "Everything looks fresh today!"}
        </p>
    </div>
    """, unsafe_allow_html=True)

    # ── Hero Stats with Animation ──
    st.markdown("""
    <div style='display:grid; grid-template-columns:repeat(4,1fr);
    gap:12px; margin-bottom:20px;'>
    """, unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("🥦 Total Items", total, "+2 this week")
    with col2:
        st.metric("⏰ Expiring Soon", len(expiring), "This week")
    with col3:
        st.metric("🚨 Critical", len(critical), "< 3 days")
    with col4:
        st.metric("🏆 Items Saved", saved, "Great job!")

    st.markdown("---")

    # ── Quick Actions ──
    st.markdown("### ⚡ Quick Actions")
    qa1, qa2, qa3, qa4 = st.columns(4)
    actions = [
        ("➕", "Add Item",   "➕ Add Item"),
        ("🤖", "AI Recipes", "🤖 AI Recipes"),
        ("🛒", "Shopping",   "🛒 Shopping"),
        ("📅", "Meal Plan",  "📅 Meal Planner"),
    ]
    for col, (icon, label, nav) in zip([qa1,qa2,qa3,qa4], actions):
        with col:
            st.markdown(f"""
            <div class='quick-action'>
                <div style='font-size:28px;'>{icon}</div>
                <div style='font-size:13px; color:#2d6a4f;
                font-weight:500; margin-top:6px;'>{label}</div>
            </div>
            """, unsafe_allow_html=True)
            if st.button(label, key=f"qa_{label}", use_container_width=True):
                st.session_state.nav = nav
                st.rerun()

    st.markdown("---")

    # ── Weather + Activity + Low Stock ──
    w_col, a_col, s_col = st.columns(3)

    # Weather
    with w_col:
        weather = get_weather()
        desc = weather['desc']
        temp = weather['temp']
        icon = "⛅" if "cloud" in desc.lower() else \
               "🌧️" if "rain"  in desc.lower() else \
               "☀️" if "sun"   in desc.lower() or "clear" in desc.lower() else "🌤️"
        tip = "Hot day! Use leafy veggies soon — heat speeds spoilage." \
              if int(temp) > 30 else \
              "Cool weather! Your produce will last longer today."
        st.markdown(f"""
        <div class='weather-card'>
            <div class='card-title'>🌤️ Weather — Bengaluru</div>
            <div style='display:flex; align-items:center; gap:14px; margin-bottom:10px;'>
                <div style='font-size:40px;'>{icon}</div>
                <div>
                    <div style='font-size:28px; font-weight:600;
                    color:#1b5e20;'>{temp}°C</div>
                    <div style='font-size:12px; color:#555;'>{desc}</div>
                </div>
            </div>
            <div style='background:rgba(45,106,79,0.1); border-radius:8px;
            padding:8px 12px; font-size:12px; color:#2d6a4f;
            margin-bottom:10px;'>🥗 {tip}</div>
            <div style='display:flex; justify-content:space-between;
            font-size:11px; color:#888; border-top:1px solid #e0f2e9;
            padding-top:8px;'>
                <span>💧 {weather['humidity']}%</span>
                <span>💨 {weather['wind']}km/h</span>
                <span>🌡️ Feels {weather['feels']}°C</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Recent Activity
    with a_col:
        acts = [dict(h) for h in get_usage_history()][:4]
        activity_html = "<div class='info-card'><div class='card-title'>📋 Recent Activity</div>"
        if acts:
            for a in acts:
                bg  = "#e8f5e9" if not a["was_wasted"] else "#ffebee"
                ico = "✅" if not a["was_wasted"] else "🗑️"
                activity_html += f"""
                <div class='activity-item'>
                    <div class='act-dot' style='background:{bg};'>{ico}</div>
                    <div style='flex:1;'>
                        <div style='color:#333;'>
                            <b>{a['item_name']}</b>
                            {'used' if not a['was_wasted'] else 'wasted'}
                        </div>
                        <div style='font-size:11px; color:#aaa;'>
                            {a['used_date']}
                        </div>
                    </div>
                </div>"""
        else:
            activity_html += """
            <div style='text-align:center; color:#aaa;
            font-size:13px; padding:20px 0;'>
                No activity yet.<br>Start adding items!
            </div>"""
        activity_html += "</div>"
        st.markdown(activity_html, unsafe_allow_html=True)

    # Low Stock Alerts
    with s_col:
        stock_html = "<div class='info-card'><div class='card-title'>⚠️ Low Stock Alerts</div>"
        if low_stock:
            for item in low_stock[:4]:
                num, unit = parse_quantity(item["quantity"])
                pct = min(int((num / 5) * 100), 100)
                color = "#e53935" if pct < 30 else "#fb8c00"
                emoji = FOOD_EMOJIS.get(item["category"], "🛒")
                stock_html += f"""
                <div class='stock-item'>
                    <div style='width:32px; height:32px; background:#f5f5f5;
                    border-radius:8px; display:flex; align-items:center;
                    justify-content:center; font-size:16px;'>{emoji}</div>
                    <div style='flex:1;'>
                        <div style='display:flex; justify-content:space-between;'>
                            <span style='font-size:13px; font-weight:500;
                            color:#333;'>{item['name']}</span>
                            <span style='font-size:11px; color:{color};
                            font-weight:500;'>{item['quantity']}</span>
                        </div>
                        <div class='stock-prog'>
                            <div style='width:{pct}%; height:100%;
                            background:{color}; border-radius:4px;'></div>
                        </div>
                    </div>
                </div>"""
        else:
            stock_html += """
            <div style='text-align:center; color:#aaa;
            font-size:13px; padding:20px 0;'>
                ✅ All items well stocked!
            </div>"""
        stock_html += "</div>"
        st.markdown(stock_html, unsafe_allow_html=True)

    st.markdown("---")

    # ── Daily Tip + Savings + Get Started ──
    t_col, s_col2, b_col = st.columns([2, 1, 1])

    with t_col:
        tip = DAILY_TIPS[today.day % len(DAILY_TIPS)]
        st.markdown(f"""
        <div class='tip-card'>
            <div class='card-title'>💡 Daily Tip</div>
            <div style='font-size:14px; color:#37474f;
            line-height:1.7;'>{tip}</div>
        </div>
        """, unsafe_allow_html=True)

    with s_col2:
        st.markdown(f"""
        <div class='savings-card'>
            <div style='font-size:11px; color:#2d6a4f;
            text-transform:uppercase; letter-spacing:1px;
            margin-bottom:6px;'>This Month</div>
            <div style='font-size:2.5rem; font-weight:700;
            color:#1b5e20;'>{saved}</div>
            <div style='font-size:13px; color:#2d6a4f;
            margin-bottom:8px;'>items saved!</div>
            <div style='font-size:11px; background:#c8e6c9;
            color:#1b5e20; padding:4px 10px;
            border-radius:20px; display:inline-block;'>
                🏆 Eco Hero!
            </div>
        </div>
        """, unsafe_allow_html=True)

    with b_col:
        st.markdown("<br><br>", unsafe_allow_html=True)
        if st.button("🚀 View My Pantry", use_container_width=True):
            st.session_state.nav = "🥦 Pantry"
            st.rerun()
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🤖 Get AI Recipes", use_container_width=True):
            st.session_state.nav = "🤖 AI Recipes"
            st.rerun()

    # ── Confetti trigger ──
    if saved > 0:
        if st.button(f"🎉 Celebrate {saved} Items Saved!", use_container_width=True):
            st.balloons()
            st.success("Amazing! You're reducing food waste! 🌱")


# ─────────────────────────────────────────
# PAGE 2 — PANTRY VIEW
# ─────────────────────────────────────────
def show_pantry():
    st.title("🥦 My Pantry")
    items = get_all_items()
    if not items:
        st.warning("Your pantry is empty! Add some items.")
        return
    today = date.today()
    items = [dict(i) for i in items]
    total = len(items)
    expiring_soon = len([i for i in items
                         if (date.fromisoformat(str(i["expiry_date"])) - today).days <= 7])
    critical = len([i for i in items
                    if (date.fromisoformat(str(i["expiry_date"])) - today).days <= 3])

    col1, col2, col3 = st.columns(3)
    with col1: st.metric("Total Items", total)
    with col2: st.metric("Expiring This Week", expiring_soon)
    with col3: st.metric("Critical (< 3 days)", critical)

    st.markdown("---")
    st.markdown("**Color Guide:** 🔴 < 3 days &nbsp;&nbsp; 🟠 < 7 days &nbsp;&nbsp; 🟢 Safe")
    st.markdown("---")

    for item in items:
        expiry    = date.fromisoformat(str(item["expiry_date"]))
        days_left = (expiry - today).days
        emoji     = FOOD_EMOJIS.get(item["category"], "🛒")

        if days_left <= 3:
            css = "pantry-row-red";   badge = "🔴 URGENT"
        elif days_left <= 7:
            css = "pantry-row-orange"; badge = "🟠 SOON"
        else:
            css = "pantry-row-green";  badge = "🟢 SAFE"

        st.markdown(f"""
        <div class='{css}'>
            {emoji} <b>{item['name']}</b> | {item['category']} |
            Qty: {item['quantity']} | Expires: {item['expiry_date']} |
            Days left: <b>{days_left}</b> | {badge}
        </div>""", unsafe_allow_html=True)

        cur_num, cur_unit = parse_quantity(item["quantity"])
        c1, c2, c3, c4 = st.columns([2, 2, 1, 1])
        with c1: st.markdown(f"**Current:** {item['quantity']}")
        with c2:
            used = st.number_input(
                f"Used ({cur_unit})", min_value=0.0,
                max_value=float(cur_num), value=0.0,
                step=1.0, key=f"used_{item['id']}"
            )
        with c3:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Update", key=f"upd_{item['id']}"):
                remaining = cur_num - used
                if remaining <= 0:
                    st.error(f"{item['name']} finished!")
                    log_usage(item['name'], was_wasted=False)
                else:
                    update_item(item['id'], quantity=f"{remaining}{cur_unit}")
                    st.success(f"Updated! Remaining: {remaining}{cur_unit}")
                    st.rerun()
        with c4:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Delete", key=f"del_{item['id']}"):
                delete_item(item['id'])
                log_usage(item['name'], was_wasted=False)
                st.success(f"{item['name']} removed!")
                st.rerun()

    st.markdown("---")
    expiring = get_expiring_items(days=7)
    if expiring:
        st.error(f"⚠️ {len(expiring)} item(s) expiring within 7 days!")


# ─────────────────────────────────────────
# PAGE 3 — ADD ITEM
# ─────────────────────────────────────────
def show_add_item():
    st.title("➕ Add New Item")
    with st.form("add_form"):
        c1, c2 = st.columns(2)
        with c1:
            name     = st.text_input("Item Name", placeholder="e.g. Milk")
            qty_num  = st.number_input("Quantity", min_value=0.1, value=1.0, step=0.5)
            qty_unit = st.selectbox("Unit", ["g","kg","L","ml","pcs"])
            category = st.selectbox("Category", [
                "Dairy","Vegetables","Fruits","Meat",
                "Seafood","Grains","Beverages","Snacks","Other"
            ])
        with c2:
            purchase_date = st.date_input("Purchase Date", value=date.today())
            expiry_date   = st.date_input("Expiry Date",
                                          value=date.today()+timedelta(days=7))

        if st.form_submit_button("➕ Add to Pantry", use_container_width=True):
            if not name:
                st.error("Please enter item name!")
            elif expiry_date <= purchase_date:
                st.error("Expiry date must be after purchase date!")
            else:
                add_item(name, f"{qty_num}{qty_unit}",
                         str(purchase_date), str(expiry_date), category)
                st.success(f"✅ {name} added to pantry!")
                st.balloons()


# ─────────────────────────────────────────
# PAGE 4 — AI RECIPES
# ─────────────────────────────────────────
def show_ai_recipes():
    st.title("🤖 AI Recipe Suggestions")
    if "recipes_generated" not in st.session_state:
        st.session_state.recipes_generated = False
    if "last_recipes" not in st.session_state:
        st.session_state.last_recipes = ""

    preference = st.text_input(
        "Any preference? (optional)",
        placeholder="e.g. vegetarian, quick meal, spicy"
    )
    if st.button("🍽️ Suggest Recipes with Expiring Items"):
        with st.spinner("AI is thinking..."):
            recipes = get_recipe_suggestions(
                preference=preference if preference else None
            )
            st.session_state.recipes_generated = True
            st.session_state.last_recipes = recipes

    if st.session_state.recipes_generated:
        st.markdown("---")
        st.subheader("Suggested Recipes")
        st.markdown(st.session_state.last_recipes)
        st.markdown("---")
        st.subheader("💬 Ask Follow-up Questions")
        for msg in st.session_state.chat_history:
            st.chat_message(msg["role"]).write(msg["content"])
        user_input = st.chat_input("Ask anything about recipes...")
        if user_input:
            with st.spinner("AI is responding..."):
                reply, updated = chat_with_ai(
                    user_input, st.session_state.chat_history
                )
                st.session_state.chat_history = updated
                st.rerun()


# ─────────────────────────────────────────
# PAGE 5 — SHOPPING LIST
# ─────────────────────────────────────────
def show_shopping():
    st.title("🛒 Shopping List")
    items     = [dict(i) for i in get_all_items()]
    low_stock = get_low_stock_items(items)

    st.markdown("### Auto-generated from Low Stock Items")
    if low_stock:
        st.success(f"Found {len(low_stock)} low stock items to restock!")
        for item in low_stock:
            emoji = FOOD_EMOJIS.get(item["category"], "🛒")
            col1, col2, col3 = st.columns([1, 3, 1])
            with col1:
                st.checkbox("", key=f"shop_{item['id']}")
            with col2:
                st.markdown(f"{emoji} **{item['name']}** — {item['category']} (Currently: {item['quantity']})")
            with col3:
                st.markdown(f"🔴 Low")
    else:
        st.info("✅ All items are well stocked! Nothing to buy.")

    st.markdown("---")
    st.markdown("### Add Custom Item")
    col1, col2 = st.columns([3, 1])
    with col1:
        custom = st.text_input("Item to buy", placeholder="e.g. Olive Oil")
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Add to List"):
            if custom:
                st.success(f"✅ {custom} added to shopping list!")


# ─────────────────────────────────────────
# PAGE 6 — MEAL PLANNER
# ─────────────────────────────────────────
def show_meal_planner():
    st.title("📅 Meal Planner")
    st.markdown("### 7-Day Meal Plan")

    days = ["Monday","Tuesday","Wednesday",
            "Thursday","Friday","Saturday","Sunday"]
    meals = ["Breakfast","Lunch","Dinner"]

    for day in days:
        with st.expander(f"📅 {day}"):
            cols = st.columns(3)
            for col, meal in zip(cols, meals):
                with col:
                    st.text_input(
                        meal,
                        placeholder=f"e.g. Oats & Fruits",
                        key=f"{day}_{meal}"
                    )

    if st.button("🤖 Generate AI Meal Plan", use_container_width=True):
        with st.spinner("AI is planning your week..."):
            items = [dict(i) for i in get_all_items()]
            if items:
                plan = get_recipe_suggestions(
                    preference="create a 7-day meal plan"
                )
                st.markdown("---")
                st.markdown(plan)
            else:
                st.warning("Add items to pantry first!")


# ─────────────────────────────────────────
# PAGE 7 — DASHBOARD
# ─────────────────────────────────────────
def show_dashboard():
    st.title("📊 Dashboard")
    try:
        import plotly.express as px
        import pandas as pd
        items   = [dict(i) for i in get_all_items()]
        history = [dict(h) for h in get_usage_history()]
        today   = date.today()

        if not items:
            st.warning("Add items to pantry to see charts!")
            return

        col1, col2 = st.columns(2)

        with col1:
            # Pie chart by category
            cats = {}
            for item in items:
                cats[item["category"]] = cats.get(item["category"], 0) + 1
            df_cat = pd.DataFrame({
                "Category": list(cats.keys()),
                "Count": list(cats.values())
            })
            fig1 = px.pie(
                df_cat, values="Count", names="Category",
                title="Pantry by Category",
                color_discrete_sequence=px.colors.sequential.Greens_r
            )
            st.plotly_chart(fig1, use_container_width=True)

        with col2:
            # Bar chart - expiry
            exp_items = [i for i in items
                         if (date.fromisoformat(str(i["expiry_date"])) - today).days <= 14]
            if exp_items:
                df_exp = pd.DataFrame({
                    "Item": [i["name"] for i in exp_items],
                    "Days Left": [
                        (date.fromisoformat(str(i["expiry_date"])) - today).days
                        for i in exp_items
                    ]
                })
                fig2 = px.bar(
                    df_exp, x="Item", y="Days Left",
                    title="Items Expiring (Next 14 Days)",
                    color="Days Left",
                    color_continuous_scale="RdYlGn"
                )
                st.plotly_chart(fig2, use_container_width=True)

        # Waste vs Used
        if history:
            used   = len([h for h in history if not h["was_wasted"]])
            wasted = len([h for h in history if h["was_wasted"]])
            df_w   = pd.DataFrame({
                "Type": ["Used ✅", "Wasted 🗑️"],
                "Count": [used, wasted]
            })
            fig3 = px.bar(
                df_w, x="Type", y="Count",
                title="Used vs Wasted Items",
                color="Type",
                color_discrete_map={
                    "Used ✅": "#2d6a4f",
                    "Wasted 🗑️": "#e53935"
                }
            )
            st.plotly_chart(fig3, use_container_width=True)

    except ImportError:
        st.error("Please run: pip install plotly pandas")


# ─────────────────────────────────────────
# MAIN APP
# ─────────────────────────────────────────
if not st.session_state.logged_in:
    show_login()
else:
    # Sidebar
    name = st.session_state.user["name"]
    initials = "".join([w[0].upper() for w in name.split()[:2]])

    st.sidebar.markdown(f"""
    <div style='text-align:center; padding:16px 0 8px;'>
        <div style='width:40px; height:40px; background:#2d6a4f;
        border-radius:10px; display:flex; align-items:center;
        justify-content:center; font-size:20px; margin:0 auto 8px;'>🥬</div>
        <div style='font-size:1.2rem; font-weight:600;
        color:#2d6a4f;'>FreshMind</div>
    </div>
    """, unsafe_allow_html=True)
    st.sidebar.markdown("---")

    pages = [
        "🏠 Home", "🥦 Pantry", "➕ Add Item",
        "🤖 AI Recipes", "🛒 Shopping",
        "📅 Meal Planner", "📊 Dashboard"
    ]

    current = st.session_state.get("nav", "🏠 Home")
    if current not in pages:
        current = "🏠 Home"

    page = st.sidebar.radio("Navigate", pages,
                             index=pages.index(current))
    st.session_state.nav = page

    st.sidebar.markdown("---")
    st.sidebar.markdown(f"""
    <div style='display:flex; align-items:center; gap:10px;
    padding:10px 12px; background:#f0faf4; border-radius:10px;
    margin-bottom:8px;'>
        <div style='width:32px; height:32px; background:#2d6a4f;
        border-radius:50%; display:flex; align-items:center;
        justify-content:center; color:white; font-size:12px;
        font-weight:600;'>{initials}</div>
        <div>
            <div style='font-size:13px; font-weight:500;
            color:#1b5e20;'>{name}</div>
            <div style='font-size:11px; color:#888;'>Admin</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if st.sidebar.button("🚪 Logout", use_container_width=True):
        logout()
        st.rerun()
    st.sidebar.caption("FreshMind v2.0 | Person B")

    # Router
    if   page == "🏠 Home":         show_home()
    elif page == "🥦 Pantry":       show_pantry()
    elif page == "➕ Add Item":      show_add_item()
    elif page == "🤖 AI Recipes":   show_ai_recipes()
    elif page == "🛒 Shopping":     show_shopping()
    elif page == "📅 Meal Planner": show_meal_planner()
    elif page == "📊 Dashboard":    show_dashboard()