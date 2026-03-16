# app.py — FreshMind v2.0
# Complete upgrade with dark mode, animations, JS charts

import streamlit as st
from datetime import date, datetime
import hashlib
import streamlit.components.v1 as components
from database import (
    create_tables, add_item, get_all_items,
    get_expiring_items, delete_item, update_item,
    log_usage, get_usage_history
)
from ai_recipes import get_recipe_suggestions, chat_with_ai
from notifier import check_and_notify
from dashboard import render_dashboard

# ─────────────────────────────────────────
# APP CONFIG
# ─────────────────────────────────────────

st.set_page_config(
    page_title="FreshMind 🥗",
    page_icon="🥗",
    layout="wide",
    initial_sidebar_state="expanded"
)

create_tables()

# ─────────────────────────────────────────
# SESSION STATE DEFAULTS
# ─────────────────────────────────────────

defaults = {
    "logged_in": False,
    "username": "",
    "dark_mode": False,
    "chat_history": [],
    "edit_item_id": None,
    "show_confetti": False
}
for key, val in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = val

# ─────────────────────────────────────────
# THEME
# ─────────────────────────────────────────

def get_theme():
    """Returns CSS variables based on dark/light mode"""
    if st.session_state.dark_mode:
        return {
            "bg":        "#0f0f1a",
            "card":      "#1a1a2e",
            "card2":     "#16213e",
            "text":      "#ffffff",
            "subtext":   "#a0a0b0",
            "border":    "#2a2a4a",
            "primary":   "#667eea",
            "success":   "#43e97b",
            "warning":   "#fa709a",
            "danger":    "#f44336",
            "gradient":  "linear-gradient(135deg, #0f0f1a, #1a1a2e)",
            "hero":      "linear-gradient(135deg, #1a1a2e, #16213e)",
            "sidebar":   "#1a1a2e",
        }
    else:
        return {
            "bg":        "#f0f4f8",
            "card":      "#ffffff",
            "card2":     "#f8fffe",
            "text":      "#1a1a2e",
            "subtext":   "#666680",
            "border":    "#e0e8f0",
            "primary":   "#667eea",
            "success":   "#2e7d32",
            "warning":   "#e65100",
            "danger":    "#c62828",
            "gradient":  "linear-gradient(135deg, #f0f4f8, #e8f5e9)",
            "hero":      "linear-gradient(135deg, #2e7d32, #66bb6a)",
            "sidebar":   "#ffffff",
        }

# ─────────────────────────────────────────
# GLOBAL CSS
# ─────────────────────────────────────────

def inject_css():
    t = get_theme()
    st.markdown(f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');

        /* ── Base ── */
        * {{
            font-family: 'Poppins', sans-serif !important;
            transition: background 0.3s, color 0.3s;
        }}

        .stApp {{
            background: {t['gradient']} !important;
            min-height: 100vh;
        }}

        /* ── Sidebar ── */
        section[data-testid="stSidebar"] {{
            background: {t['card']} !important;
            border-right: 1px solid {t['border']};
            box-shadow: 2px 0 15px rgba(0,0,0,0.05);
        }}

        /* ── Text ── */
        h1, h2, h3, h4, h5, p, span, label {{
            color: {t['text']} !important;
        }}

        /* ── Cards ── */
        .fm-card {{
            background: {t['card']};
            border-radius: 16px;
            padding: 20px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.08);
            border: 1px solid {t['border']};
            margin-bottom: 12px;
            transition: transform 0.2s, box-shadow 0.2s;
        }}
        .fm-card:hover {{
            transform: translateY(-3px);
            box-shadow: 0 8px 30px rgba(0,0,0,0.12);
        }}

        /* ── Metric Cards ── */
        .metric-card {{
            background: {t['card']};
            border-radius: 16px;
            padding: 24px;
            text-align: center;
            box-shadow: 0 4px 20px rgba(0,0,0,0.08);
            border: 1px solid {t['border']};
            transition: transform 0.2s;
        }}
        .metric-card:hover {{ transform: translateY(-5px); }}
        .metric-number {{
            font-size: 2.5rem;
            font-weight: 700;
            color: {t['primary']} !important;
        }}
        .metric-label {{
            font-size: 0.85rem;
            color: {t['subtext']} !important;
            margin-top: 5px;
        }}

        /* ── Badges ── */
        .badge {{
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 11px;
            font-weight: 600;
            display: inline-block;
        }}
        .badge-red {{
            background: #ffe0e0;
            color: #c62828;
        }}
        .badge-orange {{
            background: #fff3e0;
            color: #e65100;
        }}
        .badge-green {{
            background: #e0f2e9;
            color: #1b5e20;
        }}
        .badge-gray {{
            background: #f0f0f0;
            color: #555;
        }}

        /* ── Item Cards ── */
        .item-card {{
            background: {t['card']};
            border-radius: 12px;
            padding: 16px 20px;
            margin-bottom: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.06);
            border-left: 5px solid {t['success']};
            transition: all 0.2s;
        }}
        .item-card:hover {{
            transform: translateX(4px);
            box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        }}
        .item-card-red  {{ border-left-color: #f44336 !important; }}
        .item-card-orange {{ border-left-color: #ff9800 !important; }}

        /* ── Buttons ── */
        .stButton > button {{
            border-radius: 10px !important;
            font-weight: 600 !important;
            border: none !important;
            transition: all 0.2s !important;
        }}
        .stButton > button:hover {{
            transform: translateY(-2px) !important;
            box-shadow: 0 5px 15px rgba(102,126,234,0.4) !important;
        }}

        /* ── Forms ── */
        .stTextInput > div > div > input,
        .stSelectbox > div > div {{
            border-radius: 10px !important;
            border: 1px solid {t['border']} !important;
            background: {t['card']} !important;
            color: {t['text']} !important;
        }}

        /* ── Alerts ── */
        .stAlert {{
            border-radius: 12px !important;
        }}

        /* ── Hero Banner ── */
        .hero-banner {{
            background: {t['hero']};
            padding: 35px 30px;
            border-radius: 20px;
            color: white !important;
            margin-bottom: 30px;
            position: relative;
            overflow: hidden;
        }}
        .hero-banner::before {{
            content: '';
            position: absolute;
            top: -50%;
            right: -10%;
            width: 300px;
            height: 300px;
            background: rgba(255,255,255,0.05);
            border-radius: 50%;
        }}
        .hero-banner h1,
        .hero-banner p {{
            color: white !important;
            position: relative;
            z-index: 1;
        }}

        /* ── Chat ── */
        .chat-user {{
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white !important;
            padding: 12px 18px;
            border-radius: 18px 18px 4px 18px;
            margin: 8px 0 8px auto;
            max-width: 75%;
            display: table;
            table-layout: fixed;
        }}
        .chat-ai {{
            background: {t['card2']};
            color: {t['text']} !important;
            padding: 12px 18px;
            border-radius: 18px 18px 18px 4px;
            margin: 8px 0;
            max-width: 75%;
            border: 1px solid {t['border']};
            display: table;
        }}

        /* ── Animations ── */
        @keyframes fadeInUp {{
            from {{ opacity: 0; transform: translateY(20px); }}
            to   {{ opacity: 1; transform: translateY(0); }}
        }}
        @keyframes pulse {{
            0%, 100% {{ transform: scale(1); }}
            50%       {{ transform: scale(1.05); }}
        }}
        .fade-in {{ animation: fadeInUp 0.5s ease forwards; }}
        .pulse   {{ animation: pulse 2s infinite; }}

        /* ── Hide Streamlit UI ── */
        #MainMenu, footer, header {{ visibility: hidden; }}
        .block-container {{ padding-top: 1rem !important; }}
    </style>
    """, unsafe_allow_html=True)

# ─────────────────────────────────────────
# LOGIN SYSTEM
# ─────────────────────────────────────────

USERS = {
    "admin":    hashlib.sha256("admin123".encode()).hexdigest(),
    "person_a": hashlib.sha256("persona123".encode()).hexdigest(),
    "person_b": hashlib.sha256("personb123".encode()).hexdigest(),
}

def hash_password(p):
    return hashlib.sha256(p.encode()).hexdigest()

def login_page():
    inject_css()
    t = get_theme()

    # Animated background
    components.html("""
        <style>
            body { margin: 0; overflow: hidden; }
            canvas { display: block; }
        </style>
        <canvas id="bg"></canvas>
        <script>
            const canvas = document.getElementById('bg');
            const ctx = canvas.getContext('2d');
            canvas.width = window.innerWidth;
            canvas.height = 200;

            const particles = Array.from({length: 40}, () => ({
                x: Math.random() * canvas.width,
                y: Math.random() * canvas.height,
                r: Math.random() * 3 + 1,
                dx: (Math.random() - 0.5) * 1.5,
                dy: (Math.random() - 0.5) * 1.5,
                color: `hsla(${Math.random()*60 + 120}, 70%, 50%, 0.6)`
            }));

            function animate() {{
                ctx.clearRect(0, 0, canvas.width, canvas.height);
                particles.forEach(p => {{
                    ctx.beginPath();
                    ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
                    ctx.fillStyle = p.color;
                    ctx.fill();
                    p.x += p.dx;
                    p.y += p.dy;
                    if (p.x < 0 || p.x > canvas.width)  p.dx *= -1;
                    if (p.y < 0 || p.y > canvas.height) p.dy *= -1;
                }});
                requestAnimationFrame(animate);
            }}
            animate();
        </script>
    """, height=200)

    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.markdown(f"""
            <div class='fade-in' style='text-align:center; padding:20px 0;'>
                <div style='font-size:4rem;'>🥗</div>
                <h1 style='font-size:2.5rem; font-weight:700;
                           background: linear-gradient(135deg,#667eea,#43e97b);
                           -webkit-background-clip:text;
                           -webkit-text-fill-color:transparent;'>
                    FreshMind
                </h1>
                <p style='color:{t["subtext"]}; font-size:1rem;'>
                    Your AI-Powered Smart Pantry Assistant
                </p>
            </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
            <div class='fm-card fade-in'>
                <h3 style='text-align:center; margin-bottom:20px;'>
                    👋 Welcome Back!
                </h3>
            </div>
        """, unsafe_allow_html=True)

        with st.form("login_form"):
            username = st.text_input(
                "👤 Username",
                placeholder="Enter username"
            )
            password = st.text_input(
                "🔒 Password",
                type="password",
                placeholder="Enter password"
            )

            col_a, col_b = st.columns(2)
            with col_a:
                submitted = st.form_submit_button(
                    "🔐 Login",
                    use_container_width=True
                )
            with col_b:
                dark = st.form_submit_button(
                    "🌙 Dark Mode" if not st.session_state.dark_mode
                    else "☀️ Light Mode",
                    use_container_width=True
                )

            if dark:
                st.session_state.dark_mode = \
                    not st.session_state.dark_mode
                st.rerun()

            if submitted:
                if username in USERS and \
                   USERS[username] == hash_password(password):
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    st.rerun()
                else:
                    st.error("❌ Wrong username or password!")

        st.markdown(f"""
            <p style='text-align:center; color:{t["subtext"]};
                      font-size:0.8rem; margin-top:15px;'>
                Demo: <b>admin</b> / <b>admin123</b>
            </p>
        """, unsafe_allow_html=True)

# ─────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────

def get_expiry_info(expiry_str):
    today  = date.today()
    expiry = datetime.strptime(expiry_str, "%Y-%m-%d").date()
    days   = (expiry - today).days
    if days < 0:
        return "⚫", days, "badge-red",    "item-card-red"
    elif days <= 3:
        return "🔴", days, "badge-red",    "item-card-red"
    elif days <= 7:
        return "🟠", days, "badge-orange", "item-card-orange"
    else:
        return "🟢", days, "badge-green",  ""

def confetti():
    components.html("""
        <script src="https://cdn.jsdelivr.net/npm/canvas-confetti@1.6.0/dist/confetti.browser.min.js"></script>
        <script>
            confetti({
                particleCount: 120,
                spread: 80,
                origin: { y: 0.6 },
                colors: ['#667eea','#43e97b','#f093fb','#4facfe','#fa709a']
            });
        </script>
    """, height=0)

# ─────────────────────────────────────────
# PAGE — HOME
# ─────────────────────────────────────────

def home_page():
    t = get_theme()

    # Hero Banner
    st.markdown(f"""
        <div class='hero-banner fade-in'>
            <h1 style='font-size:2rem; margin:0;'>
                👋 Hello, {st.session_state.username}!
            </h1>
            <p style='font-size:1.1rem; opacity:0.85; margin:8px 0 0;'>
                {date.today().strftime("%A, %B %d %Y")} —
                Here's your pantry overview
            </p>
        </div>
    """, unsafe_allow_html=True)

    # Metrics
    all_items      = get_all_items()
    expiring_items = get_expiring_items(7)
    critical_items = get_expiring_items(3)
    history        = get_usage_history()
    saved          = sum(1 for h in history if not h['was_wasted'])
    wasted         = sum(1 for h in history if h['was_wasted'])

    # Animated metric cards via JS
    components.html(f"""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700&display=swap');
            * {{ font-family: 'Poppins', sans-serif; box-sizing: border-box; }}
            .grid {{
                display: grid;
                grid-template-columns: repeat(4, 1fr);
                gap: 16px;
                padding: 8px 0;
            }}
            .card {{
                background: {'#1a1a2e' if st.session_state.dark_mode else 'white'};
                border-radius: 16px;
                padding: 24px;
                text-align: center;
                box-shadow: 0 4px 20px rgba(0,0,0,0.08);
                transition: transform 0.2s;
                cursor: default;
            }}
            .card:hover {{ transform: translateY(-5px); }}
            .icon {{ font-size: 2rem; margin-bottom: 8px; }}
            .number {{
                font-size: 2.2rem;
                font-weight: 700;
                margin: 4px 0;
            }}
            .label {{
                font-size: 0.78rem;
                color: {'#a0a0b0' if st.session_state.dark_mode else '#666'};
            }}
        </style>
        <div class="grid">
            <div class="card">
                <div class="icon">📦</div>
                <div class="number" style="color:#667eea"
                     id="c1">0</div>
                <div class="label">Total Items</div>
            </div>
            <div class="card">
                <div class="icon">⚠️</div>
                <div class="number" style="color:#fa709a"
                     id="c2">0</div>
                <div class="label">Expiring This Week</div>
            </div>
            <div class="card">
                <div class="icon">✅</div>
                <div class="number" style="color:#43e97b"
                     id="c3">0</div>
                <div class="label">Items Saved</div>
            </div>
            <div class="card">
                <div class="icon">🗑️</div>
                <div class="number" style="color:#f44336"
                     id="c4">0</div>
                <div class="label">Items Wasted</div>
            </div>
        </div>
        <script>
            function countUp(id, target, duration=1500) {{
                const el = document.getElementById(id);
                let start = 0;
                const step = target / (duration / 16);
                const timer = setInterval(() => {{
                    start += step;
                    if (start >= target) {{
                        el.textContent = target;
                        clearInterval(timer);
                    }} else {{
                        el.textContent = Math.floor(start);
                    }}
                }}, 16);
            }}
            countUp('c1', {len(all_items)});
            countUp('c2', {len(expiring_items)});
            countUp('c3', {saved});
            countUp('c4', {wasted});
        </script>
    """, height=160)

    st.markdown("---")

    # Alerts
    if critical_items:
        st.error("🚨 Critical — Use these items immediately!")
        for item in critical_items:
            _, days, _, _ = get_expiry_info(item['expiry_date'])
            msg = f"EXPIRED {abs(days)} days ago!" \
                  if days < 0 else f"expires in {days} day(s)!"
            st.warning(f"⚠️ **{item['name']}** ({item['category']}) — {msg}")
    elif expiring_items:
        st.warning(
            f"⚠️ {len(expiring_items)} items expiring "
            f"this week — check your pantry!"
        )
    else:
        st.success("✅ Everything is fresh! No urgent alerts.")

    st.markdown("---")

    # Quick Actions
    st.markdown("### ⚡ Quick Actions")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.button("➕ Add Item",      use_container_width=True)
    with col2:
        st.button("📦 View Pantry",   use_container_width=True)
    with col3:
        st.button("🤖 AI Recipes",    use_container_width=True)
    with col4:
        st.button("📊 Dashboard",     use_container_width=True)

# ─────────────────────────────────────────
# PAGE — PANTRY
# ─────────────────────────────────────────

def pantry_page():
    t = get_theme()
    st.markdown("""
        <div class='hero-banner fade-in' style='padding:20px 25px;'>
            <h2 style='margin:0;'>📦 My Pantry</h2>
            <p style='margin:4px 0 0; opacity:0.85;'>
                Manage your food items
            </p>
        </div>
    """, unsafe_allow_html=True)

    all_items = get_all_items()

    if not all_items:
        st.info("🛒 Pantry is empty! Add some items to get started.")
        return

    # Search & Filter
    col1, col2, col3 = st.columns([3, 1, 1])
    with col1:
        search = st.text_input(
            "🔍 Search",
            placeholder="Search items..."
        )
    with col2:
        filter_cat = st.selectbox("Category", [
            "All", "Dairy", "Vegetables", "Fruits",
            "Meat & Seafood", "Grains & Cereals",
            "Snacks", "Beverages", "Condiments", "Other"
        ])
    with col3:
        filter_expiry = st.selectbox("Expiry Filter", [
            "All", "Critical (≤3d)",
            "Expiring (≤7d)", "Fresh (>7d)"
        ])

    # Filter logic
    filtered = []
    for item in all_items:
        _, days, _, _ = get_expiry_info(item['expiry_date'])
        match_search = search.lower() in item['name'].lower() \
                       if search else True
        match_cat    = item['category'] == filter_cat \
                       if filter_cat != "All" else True
        match_expiry = True
        if filter_expiry == "Critical (≤3d)":
            match_expiry = days <= 3
        elif filter_expiry == "Expiring (≤7d)":
            match_expiry = days <= 7
        elif filter_expiry == "Fresh (>7d)":
            match_expiry = days > 7
        if match_search and match_cat and match_expiry:
            filtered.append(item)

    st.markdown(
        f"Showing **{len(filtered)}** of **{len(all_items)}** items"
    )
    st.markdown("---")

    for item in filtered:
        emoji, days_left, badge, card_cls = \
            get_expiry_info(item['expiry_date'])

        if st.session_state.edit_item_id == item['id']:
            with st.form(key=f"edit_{item['id']}"):
                st.markdown(f"### ✏️ Editing: **{item['name']}**")
                c1, c2 = st.columns(2)
                with c1:
                    nn  = st.text_input("Name",     value=item['name'])
                    nq  = st.text_input("Quantity", value=item['quantity'])
                    cats = ["Dairy","Vegetables","Fruits",
                            "Meat & Seafood","Grains & Cereals",
                            "Snacks","Beverages","Condiments","Other"]
                    nc = st.selectbox(
                        "Category", cats,
                        index=cats.index(item['category'])
                    )
                with c2:
                    ne = st.date_input(
                        "Expiry Date",
                        value=datetime.strptime(
                            item['expiry_date'], "%Y-%m-%d"
                        ).date()
                    )
                s1, s2 = st.columns(2)
                with s1:
                    if st.form_submit_button(
                        "💾 Save", use_container_width=True
                    ):
                        update_item(
                            item['id'], name=nn,
                            quantity=nq, expiry_date=str(ne),
                            category=nc
                        )
                        st.session_state.edit_item_id = None
                        st.rerun()
                with s2:
                    if st.form_submit_button(
                        "❌ Cancel", use_container_width=True
                    ):
                        st.session_state.edit_item_id = None
                        st.rerun()
        else:
            st.markdown(f"""
                <div class='item-card {card_cls} fade-in'>
                    <div style='display:flex;
                                justify-content:space-between;
                                align-items:center;'>
                        <div>
                            <b style='font-size:1rem;'>
                                {emoji} {item['name']}
                            </b>
                            <span class='badge badge-gray'
                                  style='margin-left:8px;'>
                                {item['category']}
                            </span><br>
                            <small style='color:#888;'>
                                📏 {item['quantity']} &nbsp;|&nbsp;
                                📅 Expires: {item['expiry_date']}
                                &nbsp;|&nbsp;
                                <span class='badge {badge}'>
                                    {"EXPIRED" if days_left < 0
                                      else f"{days_left}d left"}
                                </span>
                            </small>
                        </div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

            c1, c2, c3, c4 = st.columns([6, 1, 1, 1])
            with c2:
                if st.button("✅", key=f"use_{item['id']}",
                             help="Mark as used"):
                    log_usage(item['name'], was_wasted=False)
                    delete_item(item['id'])
                    st.rerun()
            with c3:
                if st.button("✏️", key=f"edit_{item['id']}",
                             help="Edit"):
                    st.session_state.edit_item_id = item['id']
                    st.rerun()
            with c4:
                if st.button("🗑️", key=f"del_{item['id']}",
                             help="Delete"):
                    log_usage(item['name'], was_wasted=True)
                    delete_item(item['id'])
                    st.rerun()

# ─────────────────────────────────────────
# PAGE — ADD ITEM
# ─────────────────────────────────────────

def add_item_page():
    t = get_theme()
    st.markdown("""
        <div class='hero-banner fade-in' style='padding:20px 25px;'>
            <h2 style='margin:0;'>➕ Add New Item</h2>
            <p style='margin:4px 0 0; opacity:0.85;'>
                Add items to your pantry
            </p>
        </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.form("add_form", clear_on_submit=True):
            name = st.text_input(
                "Item Name *",
                placeholder="e.g. Milk, Eggs, Spinach"
            )
            c1, c2 = st.columns(2)
            with c1:
                quantity = st.text_input(
                    "Quantity *",
                    placeholder="e.g. 1 litre, 500g"
                )
            with c2:
                category = st.selectbox("Category *", [
                    "Dairy", "Vegetables", "Fruits",
                    "Meat & Seafood", "Grains & Cereals",
                    "Snacks", "Beverages", "Condiments", "Other"
                ])
            c3, c4 = st.columns(2)
            with c3:
                purchase_date = st.date_input(
                    "Purchase Date *", value=date.today()
                )
            with c4:
                expiry_date = st.date_input(
                    "Expiry Date *",   value=date.today()
                )

            submitted = st.form_submit_button(
                "➕ Add to Pantry",
                use_container_width=True
            )

            if submitted:
                if not name or not quantity:
                    st.error("❌ Fill in all required fields!")
                elif expiry_date < purchase_date:
                    st.error("❌ Expiry before purchase date!")
                elif expiry_date < date.today():
                    st.error("❌ Item is already expired!")
                else:
                    add_item(
                        name=name,
                        quantity=quantity,
                        purchase_date=str(purchase_date),
                        expiry_date=str(expiry_date),
                        category=category
                    )
                    st.success(f"✅ **{name}** added!")
                    confetti()

# ─────────────────────────────────────────
# PAGE — AI RECIPES
# ─────────────────────────────────────────

def ai_recipes_page():
    t = get_theme()
    st.markdown("""
        <div class='hero-banner fade-in' style='padding:20px 25px;'>
            <h2 style='margin:0;'>🤖 AI Recipe Suggestions</h2>
            <p style='margin:4px 0 0; opacity:0.85;'>
                Smart recipes from your pantry
            </p>
        </div>
    """, unsafe_allow_html=True)

    all_items      = get_all_items()
    expiring_items = get_expiring_items(7)

    if not all_items:
        st.info("🛒 Add some items to your pantry first!")
        return

    c1, c2 = st.columns(2)
    with c1:
        st.info(
            f"📦 **{len(all_items)}** items available in pantry"
        )
    with c2:
        if expiring_items:
            st.warning(
                f"⚠️ **{len(expiring_items)}** expiring soon "
                f"— AI will prioritize these!"
            )

    # Preferences
    st.markdown("### 🎛️ Preferences")
    c1, c2, c3 = st.columns(3)
    with c1:
        meal = st.selectbox(
            "🍽️ Meal",
            ["Any","Breakfast","Lunch","Dinner","Snack","Dessert"]
        )
    with c2:
        diet = st.selectbox(
            "🥗 Diet",
            ["Any","Vegetarian","Vegan",
             "Non-Vegetarian","Gluten-Free"]
        )
    with c3:
        time_ = st.selectbox(
            "⏱️ Time",
            ["Any","<15 mins","<30 mins","<1 hour"]
        )

    st.markdown("---")

    if st.button(
        "🍳 Generate Recipes From My Pantry",
        use_container_width=True
    ):
        with st.spinner("🤖 AI is cooking up ideas..."):
            prefs = f"Meal:{meal}, Diet:{diet}, Time:{time_}"
            result = get_recipe_suggestions(
                [dict(i) for i in all_items],
                [dict(i) for i in expiring_items],
                prefs
            )
            st.session_state.chat_history.append({
                "role": "assistant", "content": result
            })

    # Chat
    st.markdown("### 💬 Recipe Chat")
    for msg in st.session_state.chat_history:
        if msg["role"] == "user":
            st.markdown(
                f"<div class='chat-user'>{msg['content']}</div>",
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                f"<div class='chat-ai'>{msg['content']}</div>",
                unsafe_allow_html=True
            )

    if st.session_state.chat_history:
        if st.button("🗑️ Clear Chat"):
            st.session_state.chat_history = []
            st.rerun()

    user_input = st.chat_input(
        "Ask anything — 'make it spicy', 'no onions', 'quick meal'"
    )
    if user_input:
        st.session_state.chat_history.append({
            "role": "user", "content": user_input
        })
        with st.spinner("🤖 Thinking..."):
            response, st.session_state.chat_history = chat_with_ai(
                user_input, st.session_state.chat_history
            )
        st.rerun()

# ─────────────────────────────────────────
# PAGE — DASHBOARD
# ─────────────────────────────────────────

def dashboard_page():
    from dashboard import render_dashboard
    render_dashboard(
        get_all_items(),
        get_expiring_items(7),
        get_usage_history(),
        st.session_state.dark_mode
    )

# ─────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────

def render_sidebar():
    t = get_theme()
    with st.sidebar:
        st.markdown(f"""
            <div style='text-align:center; padding:10px 0 20px;'>
                <div style='font-size:3rem;'>🥗</div>
                <h2 style='margin:0; color:{t["primary"]};'>FreshMind</h2>
                <p style='color:{t["subtext"]}; font-size:0.8rem;'>
                    Smart Pantry Assistant
                </p>
            </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
            <div class='fm-card' style='padding:10px 15px;
                                        margin-bottom:15px;'>
                <b>👤 {st.session_state.username}</b><br>
                <small style='color:{t["subtext"]};'>
                    Logged in
                </small>
            </div>
        """, unsafe_allow_html=True)

        page = st.radio("", [
            "🏠 Home", "📦 My Pantry",
            "➕ Add Item", "🤖 AI Recipes", "📊 Dashboard"
        ], label_visibility="collapsed")

        st.markdown("---")

        col1, col2 = st.columns(2)
        with col1:
            if st.button(
                "🌙 Dark" if not st.session_state.dark_mode
                else "☀️ Light",
                use_container_width=True
            ):
                st.session_state.dark_mode = \
                    not st.session_state.dark_mode
                st.rerun()
        with col2:
            if st.button("🔔 Alerts", use_container_width=True):
                check_and_notify()
                st.success("✅ Done!")

        st.markdown("---")

        if st.button("🚪 Logout", use_container_width=True):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

        st.markdown(f"""
            <p style='text-align:center; color:{t["subtext"]};
                      font-size:0.72rem; margin-top:20px;'>
                Built with ❤️ using Python & Streamlit
            </p>
        """, unsafe_allow_html=True)

    return page

# ─────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────

def main():
    inject_css()

    if not st.session_state.logged_in:
        login_page()
        return

    page = render_sidebar()

    if   page == "🏠 Home":       home_page()
    elif page == "📦 My Pantry":  pantry_page()
    elif page == "➕ Add Item":   add_item_page()
    elif page == "🤖 AI Recipes": ai_recipes_page()
    elif page == "📊 Dashboard":  dashboard_page()

if __name__ == "__main__":
    main()