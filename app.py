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
from image_fetcher import get_food_image, get_emoji


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
    "logged_in":    False,
    "username":     "",
    "dark_mode":    False,
    "chat_history": [],
    "edit_item_id": None,
    "current_page": "🏠 Home"
}
for key, val in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = val

# ─────────────────────────────────────────
# THEME
# ─────────────────────────────────────────

def get_theme():
    if st.session_state.dark_mode:
        return {
            "bg":       "#0f0f1a",
            "card":     "#1a1a2e",
            "card2":    "#16213e",
            "text":     "#ffffff",
            "subtext":  "#a0a0b0",
            "border":   "#2a2a4a",
            "primary":  "#667eea",
            "success":  "#43e97b",
            "warning":  "#fa709a",
            "danger":   "#f44336",
            "gradient": "linear-gradient(135deg, #0f0f1a, #1a1a2e)",
            "hero":     "linear-gradient(135deg, #1a1a2e, #16213e)",
        }
    else:
        return {
            "bg":       "#f0f4f8",
            "card":     "#ffffff",
            "card2":    "#f8fffe",
            "text":     "#1a1a2e",
            "subtext":  "#666680",
            "border":   "#e0e8f0",
            "primary":  "#667eea",
            "success":  "#2e7d32",
            "warning":  "#e65100",
            "danger":   "#c62828",
            "gradient": "linear-gradient(135deg, #f0f4f8, #e8f5e9)",
            "hero":     "linear-gradient(135deg, #2e7d32, #66bb6a)",
        }

# ─────────────────────────────────────────
# GLOBAL CSS
# ─────────────────────────────────────────

def inject_css():
    t = get_theme()
    st.markdown(f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');

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

        /* ── Sidebar Nav Buttons ── */
        .nav-btn {{
            display: flex;
            align-items: center;
            gap: 12px;
            width: 100%;
            padding: 12px 16px;
            border-radius: 12px;
            border: none;
            background: transparent;
            color: {t['text']};
            font-size: 0.95rem;
            font-weight: 500;
            cursor: pointer;
            transition: all 0.2s;
            margin-bottom: 6px;
            text-align: left;
        }}
        .nav-btn:hover {{
            background: linear-gradient(135deg,#667eea22,#43e97b22);
            transform: translateX(4px);
            color: {t['primary']};
        }}
        .nav-btn.active {{
            background: linear-gradient(135deg,#667eea,#43e97b);
            color: white !important;
            box-shadow: 0 4px 15px rgba(102,126,234,0.4);
            transform: translateX(4px);
        }}
        .nav-btn .icon {{
            font-size: 1.2rem;
            min-width: 24px;
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

        /* ── Badges ── */
        .badge {{
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 11px;
            font-weight: 600;
            display: inline-block;
        }}
        .badge-red    {{ background:#ffe0e0; color:#c62828; }}
        .badge-orange {{ background:#fff3e0; color:#e65100; }}
        .badge-green  {{ background:#e0f2e9; color:#1b5e20; }}
        .badge-gray   {{ background:#f0f0f0; color:#555;    }}

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
        .item-card-red    {{ border-left-color: #f44336 !important; }}
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
            top: -50%; right: -10%;
            width: 300px; height: 300px;
            background: rgba(255,255,255,0.05);
            border-radius: 50%;
        }}
        .hero-banner h1,
        .hero-banner h2,
        .hero-banner p {{
            color: white !important;
            position: relative;
            z-index: 1;
        }}

        /* ── Chat ── */
        .chat-user {{
            background: linear-gradient(135deg,#667eea,#764ba2);
            color: white !important;
            padding: 12px 18px;
            border-radius: 18px 18px 4px 18px;
            margin: 8px 0 8px auto;
            max-width: 75%;
            display: table;
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
            from {{ opacity:0; transform:translateY(20px); }}
            to   {{ opacity:1; transform:translateY(0);    }}
        }}
        .fade-in {{ animation: fadeInUp 0.5s ease forwards; }}

        /* ── Cooking Tips Slider ── */
        .tips-container {{
            background: {t['card']};
            border-radius: 16px;
            padding: 24px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.08);
            border: 1px solid {t['border']};
            margin: 16px 0;
            min-height: 100px;
            position: relative;
            overflow: hidden;
        }}
        .tip-slide {{
            display: none;
            animation: fadeInUp 0.6s ease;
        }}
        .tip-slide.active {{ display: block; }}
        .tip-dots {{
            display: flex;
            gap: 6px;
            justify-content: center;
            margin-top: 16px;
        }}
        .dot {{
            width: 8px; height: 8px;
            border-radius: 50%;
            background: {t['border']};
            cursor: pointer;
            transition: all 0.3s;
        }}
        .dot.active {{
            background: {t['primary']};
            width: 20px;
            border-radius: 4px;
        }}

        /* ── Quick Action Cards ── */
        .action-card {{
            background: {t['card']};
            border-radius: 16px;
            padding: 24px 20px;
            text-align: center;
            box-shadow: 0 4px 20px rgba(0,0,0,0.08);
            border: 1px solid {t['border']};
            cursor: pointer;
            transition: all 0.25s;
        }}
        .action-card:hover {{
            transform: translateY(-6px);
            box-shadow: 0 12px 30px rgba(102,126,234,0.2);
            border-color: {t['primary']};
        }}
        .action-icon {{ font-size: 2.5rem; margin-bottom: 10px; }}
        .action-title {{
            font-size: 0.95rem;
            font-weight: 600;
            color: {t['text']};
        }}
        .action-desc {{
            font-size: 0.75rem;
            color: {t['subtext']};
            margin-top: 4px;
        }}

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

    components.html("""
        <style>
            body { margin:0; overflow:hidden; }
            canvas { display:block; }
        </style>
        <canvas id="bg"></canvas>
        <script>
            const canvas = document.getElementById('bg');
            const ctx = canvas.getContext('2d');
            canvas.width = window.innerWidth;
            canvas.height = 200;
            const particles = Array.from({length:40}, () => ({
                x: Math.random()*canvas.width,
                y: Math.random()*canvas.height,
                r: Math.random()*3+1,
                dx: (Math.random()-0.5)*1.5,
                dy: (Math.random()-0.5)*1.5,
                color: `hsla(${Math.random()*60+120},70%,50%,0.6)`
            }));
            function animate() {
                ctx.clearRect(0,0,canvas.width,canvas.height);
                particles.forEach(p => {
                    ctx.beginPath();
                    ctx.arc(p.x,p.y,p.r,0,Math.PI*2);
                    ctx.fillStyle = p.color;
                    ctx.fill();
                    p.x+=p.dx; p.y+=p.dy;
                    if(p.x<0||p.x>canvas.width)  p.dx*=-1;
                    if(p.y<0||p.y>canvas.height) p.dy*=-1;
                });
                requestAnimationFrame(animate);
            }
            animate();
        </script>
    """, height=200)

    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.markdown(f"""
            <div class='fade-in' style='text-align:center; padding:20px 0;'>
                <div style='font-size:4rem;'>🥗</div>
                <h1 style='font-size:2.5rem; font-weight:700;
                           background:linear-gradient(135deg,#667eea,#43e97b);
                           -webkit-background-clip:text;
                           -webkit-text-fill-color:transparent;'>
                    FreshMind
                </h1>
                <p style='color:{t["subtext"]}; font-size:1rem;'>
                    Your AI-Powered Smart Pantry Assistant
                </p>
            </div>
        """, unsafe_allow_html=True)

        with st.form("login_form"):
            st.markdown("### 👋 Welcome Back!")
            username = st.text_input(
                "👤 Username", placeholder="Enter username"
            )
            password = st.text_input(
                "🔒 Password", type="password",
                placeholder="Enter password"
            )
            c1, c2 = st.columns(2)
            with c1:
                submitted = st.form_submit_button(
                    "🔐 Login", use_container_width=True
                )
            with c2:
                dark = st.form_submit_button(
                    "🌙 Dark" if not st.session_state.dark_mode
                    else "☀️ Light",
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
                    st.session_state.username  = username
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
                particleCount: 120, spread: 80,
                origin: {y:0.6},
                colors: ['#667eea','#43e97b','#f093fb','#4facfe','#fa709a']
            });
        </script>
    """, height=0)

# ─────────────────────────────────────────
# SIDEBAR — BUTTON NAVIGATION
# ─────────────────────────────────────────

def render_sidebar():
    t = get_theme()

    with st.sidebar:
        # Logo & Title
        st.markdown(f"""
            <div style='text-align:center; padding:16px 0 20px;'>
                <div style='font-size:3rem;'>🥗</div>
                <h2 style='margin:4px 0; color:{t["primary"]};
                           font-size:1.4rem;'>FreshMind</h2>
                <p style='color:{t["subtext"]}; font-size:0.75rem;
                           margin:0;'>Smart Pantry Assistant</p>
            </div>
        """, unsafe_allow_html=True)

        # User Card
        st.markdown(f"""
            <div style='background:{t["card2"]};
                        border:1px solid {t["border"]};
                        border-radius:12px; padding:10px 14px;
                        margin-bottom:16px;'>
                <b style='color:{t["text"]};'>
                    👤 {st.session_state.username}
                </b><br>
                <small style='color:{t["subtext"]};'>
                    ● Online
                </small>
            </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
            <p style='color:{t["subtext"]}; font-size:0.72rem;
                      margin:0 0 8px 4px; font-weight:600;
                      text-transform:uppercase; letter-spacing:1px;'>
                Navigation
            </p>
        """, unsafe_allow_html=True)

        # Nav buttons
        pages = [
            ("🏠", "Home",        "🏠 Home"),
            ("📦", "My Pantry",   "📦 My Pantry"),
            ("➕", "Add Item",    "➕ Add Item"),
            ("🤖", "AI Recipes",  "🤖 AI Recipes"),
            ("📊", "Dashboard",   "📊 Dashboard"),
        ]

        for icon, label, key in pages:
            is_active = st.session_state.current_page == key
            active_cls = "active" if is_active else ""

            # Use a styled button
            btn_style = f"""
                background: {'linear-gradient(135deg,#667eea,#43e97b)'
                             if is_active else 'transparent'};
                color: {'white' if is_active else t['text']};
                border: {'none' if is_active
                         else f'1px solid {t["border"]}'};
                box-shadow: {'0 4px 15px rgba(102,126,234,0.35)'
                             if is_active else 'none'};
                display: flex;
                align-items: center;
                gap: 10px;
                width: 100%;
                padding: 11px 14px;
                border-radius: 12px;
                font-size: 0.92rem;
                font-weight: {'600' if is_active else '500'};
                cursor: pointer;
                margin-bottom: 6px;
                transition: all 0.2s;
                font-family: 'Poppins', sans-serif;
            """

            if st.button(
                f"{icon}  {label}",
                key=f"nav_{key}",
                use_container_width=True
            ):
                st.session_state.current_page = key
                st.rerun()

            # Inject active style per button
            if is_active:
                st.markdown(f"""
                    <style>
                        div[data-testid="stButton"]
                        button[kind="secondary"]:has(
                            div:contains("{icon}  {label}")
                        ) {{
                            background: linear-gradient(
                                135deg,#667eea,#43e97b
                            ) !important;
                            color: white !important;
                        }}
                    </style>
                """, unsafe_allow_html=True)

        st.markdown("---")

        # Utility buttons
        c1, c2 = st.columns(2)
        with c1:
            if st.button(
                "🌙" if not st.session_state.dark_mode else "☀️",
                use_container_width=True,
                help="Toggle Dark/Light Mode"
            ):
                st.session_state.dark_mode = \
                    not st.session_state.dark_mode
                st.rerun()
        with c2:
            if st.button(
                "🔔", use_container_width=True,
                help="Check Expiry Alerts"
            ):
                check_and_notify()
                st.toast("✅ Expiry check done!")

        st.markdown("")

        if st.button(
            "🚪 Logout", use_container_width=True
        ):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

        st.markdown(f"""
            <p style='text-align:center; color:{t["subtext"]};
                      font-size:0.68rem; margin-top:20px;'>
                Built with ❤️ using Python & Streamlit
            </p>
        """, unsafe_allow_html=True)

    return st.session_state.current_page

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
            <p style='font-size:1.05rem; opacity:0.85; margin:8px 0 0;'>
                {date.today().strftime("%A, %B %d %Y")} —
                Here's your pantry overview
            </p>
        </div>
    """, unsafe_allow_html=True)

    # Data
    all_items      = get_all_items()
    expiring_items = get_expiring_items(7)
    critical_items = get_expiring_items(3)
    history        = get_usage_history()
    saved          = sum(1 for h in history if not h['was_wasted'])
    wasted         = sum(1 for h in history if h['was_wasted'])

    # ── Animated Metric Cards ──
    components.html(f"""
        <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700&display=swap" rel="stylesheet">
        <style>
            * {{ font-family:'Poppins',sans-serif; box-sizing:border-box; }}
            .grid {{
                display:grid;
                grid-template-columns:repeat(4,1fr);
                gap:16px; padding:4px 0 16px;
            }}
            .card {{
                background:{'#1a1a2e' if st.session_state.dark_mode else 'white'};
                border-radius:16px; padding:22px;
                text-align:center;
                box-shadow:0 4px 20px rgba(0,0,0,0.08);
                transition:transform 0.2s;
                cursor:default;
            }}
            .card:hover {{ transform:translateY(-5px); }}
            .icon  {{ font-size:2rem; margin-bottom:6px; }}
            .num   {{ font-size:2.2rem; font-weight:700; margin:4px 0; }}
            .lbl   {{
                font-size:0.75rem;
                color:{'#a0a0b0' if st.session_state.dark_mode else '#888'};
            }}
        </style>
        <div class="grid">
            <div class="card">
                <div class="icon">📦</div>
                <div class="num" style="color:#667eea" id="c1">0</div>
                <div class="lbl">Total Items</div>
            </div>
            <div class="card">
                <div class="icon">⚠️</div>
                <div class="num" style="color:#fa709a" id="c2">0</div>
                <div class="lbl">Expiring This Week</div>
            </div>
            <div class="card">
                <div class="icon">✅</div>
                <div class="num" style="color:#43e97b" id="c3">0</div>
                <div class="lbl">Items Saved</div>
            </div>
            <div class="card">
                <div class="icon">🗑️</div>
                <div class="num" style="color:#f44336" id="c4">0</div>
                <div class="lbl">Items Wasted</div>
            </div>
        </div>
        <script>
            function countUp(id, target, duration=1500) {{
                const el = document.getElementById(id);
                if(target === 0) {{ el.textContent = 0; return; }}
                let start = 0;
                const step = target / (duration/16);
                const timer = setInterval(() => {{
                    start += step;
                    if(start >= target) {{
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
    """, height=150)

    # ── Alerts ──
    if critical_items:
        st.error("🚨 Critical — Use these items immediately!")
        for item in critical_items:
            _, days, _, _ = get_expiry_info(item['expiry_date'])
            msg = f"EXPIRED {abs(days)} days ago!" \
                  if days < 0 else f"expires in {days} day(s)!"
            st.warning(
                f"⚠️ **{item['name']}** "
                f"({item['category']}) — {msg}"
            )
    elif expiring_items:
        st.warning(
            f"⚠️ {len(expiring_items)} items expiring "
            f"this week — check your pantry!"
        )
    else:
        st.success("✅ Everything is fresh! No urgent alerts.")

    st.markdown("---")

    # ── Auto Sliding Cooking Tips ──
    st.markdown(f"""
        <h3 style='color:{t["text"]}; margin-bottom:8px;'>
            🍳 Cooking Tips of the Day
        </h3>
    """, unsafe_allow_html=True)

    components.html(f"""
        <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600&display=swap" rel="stylesheet">
        <style>
            * {{ font-family:'Poppins',sans-serif; box-sizing:border-box; }}
            .slider-wrap {{
                background:{'#1a1a2e' if st.session_state.dark_mode else 'white'};
                border-radius:16px;
                padding:24px 28px;
                box-shadow:0 4px 20px rgba(0,0,0,0.08);
                border:1px solid {'#2a2a4a' if st.session_state.dark_mode else '#e0e8f0'};
                min-height:110px;
                position:relative;
            }}
            .tip {{
                display:none;
                animation:fadeIn 0.6s ease;
            }}
            .tip.active {{ display:block; }}
            @keyframes fadeIn {{
                from {{ opacity:0; transform:translateX(20px); }}
                to   {{ opacity:1; transform:translateX(0); }}
            }}
            .tip-icon {{
                font-size:2rem;
                margin-bottom:8px;
            }}
            .tip-title {{
                font-size:1rem;
                font-weight:600;
                color:{'#ffffff' if st.session_state.dark_mode else '#1a1a2e'};
                margin-bottom:6px;
            }}
            .tip-text {{
                font-size:0.85rem;
                color:{'#a0a0b0' if st.session_state.dark_mode else '#555'};
                line-height:1.6;
            }}
            .dots {{
                display:flex;
                gap:6px;
                justify-content:center;
                margin-top:16px;
            }}
            .dot {{
                width:8px; height:8px;
                border-radius:50%;
                background:{'#2a2a4a' if st.session_state.dark_mode else '#ddd'};
                cursor:pointer;
                transition:all 0.3s;
                border:none;
            }}
            .dot.active {{
                background:#667eea;
                width:20px;
                border-radius:4px;
            }}
            .nav-arrows {{
                display:flex;
                justify-content:space-between;
                margin-top:12px;
            }}
            .arrow {{
                background:{'#2a2a4a' if st.session_state.dark_mode else '#f0f4f8'};
                border:none;
                border-radius:8px;
                padding:6px 14px;
                cursor:pointer;
                font-size:1rem;
                color:{'#ffffff' if st.session_state.dark_mode else '#333'};
                transition:all 0.2s;
            }}
            .arrow:hover {{
                background:#667eea;
                color:white;
                transform:scale(1.05);
            }}
            .progress-bar {{
                height:3px;
                background:#667eea;
                border-radius:2px;
                margin-top:14px;
                transition:width 0.1s linear;
            }}
        </style>

        <div class="slider-wrap">
            <div id="tips-container"></div>
            <div class="progress-bar" id="progress"></div>
            <div class="nav-arrows">
                <button class="arrow" onclick="prevTip()">← Prev</button>
                <div class="dots" id="dots"></div>
                <button class="arrow" onclick="nextTip()">Next →</button>
            </div>
        </div>

        <script>
            const tips = [
                {{
                    icon: "🥦",
                    title: "Store Vegetables Right",
                    text: "Keep leafy greens wrapped in damp paper towels inside a bag in the fridge. They'll stay fresh 2x longer!"
                }},
                {{
                    icon: "🧅",
                    title: "Onion & Potato Rule",
                    text: "Never store onions and potatoes together! Onions release gases that make potatoes sprout faster."
                }},
                {{
                    icon: "🍋",
                    title: "Citrus Juice Hack",
                    text: "Microwave lemons/limes for 15 seconds before squeezing to get 2x more juice out of them!"
                }},
                {{
                    icon: "🥛",
                    title: "Milk Storage Tip",
                    text: "Store milk on the middle shelf of your fridge, not the door. The door is warmer and milk will spoil faster."
                }},
                {{
                    icon: "🍌",
                    title: "Banana Ripening Trick",
                    text: "To slow banana ripening, wrap the stem in plastic wrap. To speed it up, place them in a paper bag overnight."
                }},
                {{
                    icon: "🧄",
                    title: "Garlic Freshness",
                    text: "Store garlic at room temperature in a mesh bag or open container. It can last up to 6 months this way!"
                }},
                {{
                    icon: "🍞",
                    title: "Bread Freshness",
                    text: "Freeze bread slices you won't use within 3 days. Toast them straight from the freezer — tastes fresh!"
                }},
                {{
                    icon: "🥚",
                    title: "Egg Freshness Test",
                    text: "Drop an egg in water — if it sinks it's fresh, if it floats it's gone bad. Never eat a floating egg!"
                }},
                {{
                    icon: "🌿",
                    title: "Fresh Herbs Trick",
                    text: "Treat fresh herbs like flowers — trim the stems and store them in a glass of water in the fridge!"
                }},
                {{
                    icon: "🍎",
                    title: "Apple Storage",
                    text: "Apples release ethylene gas that ripens nearby produce faster. Store them separately or in a sealed bag!"
                }}
            ];

            let current = 0;
            let timer;
            let progressTimer;
            let progressWidth = 0;
            const INTERVAL = 4000;

            const container = document.getElementById('tips-container');
            const dotsEl    = document.getElementById('dots');
            const progressEl = document.getElementById('progress');

            // Build tips
            tips.forEach((tip, i) => {{
                const div = document.createElement('div');
                div.className = 'tip' + (i===0 ? ' active' : '');
                div.id = 'tip-' + i;
                div.innerHTML = `
                    <div class="tip-icon">${{tip.icon}}</div>
                    <div class="tip-title">${{tip.title}}</div>
                    <div class="tip-text">${{tip.text}}</div>
                `;
                container.appendChild(div);

                const dot = document.createElement('button');
                dot.className = 'dot' + (i===0 ? ' active' : '');
                dot.id = 'dot-' + i;
                dot.onclick = () => goTo(i);
                dotsEl.appendChild(dot);
            }});

            function goTo(n) {{
                document.getElementById('tip-' + current)
                    .classList.remove('active');
                document.getElementById('dot-' + current)
                    .classList.remove('active');
                current = (n + tips.length) % tips.length;
                document.getElementById('tip-' + current)
                    .classList.add('active');
                document.getElementById('dot-' + current)
                    .classList.add('active');
                resetProgress();
            }}

            function nextTip() {{ goTo(current + 1); }}
            function prevTip() {{ goTo(current - 1); }}

            function resetProgress() {{
                progressWidth = 0;
                progressEl.style.width = '0%';
                clearInterval(progressTimer);
                progressTimer = setInterval(() => {{
                    progressWidth += 100 / (INTERVAL / 100);
                    progressEl.style.width = progressWidth + '%';
                    if(progressWidth >= 100) clearInterval(progressTimer);
                }}, 100);
            }}

            // Auto slide
            function startAuto() {{
                timer = setInterval(() => nextTip(), INTERVAL);
            }}

            resetProgress();
            startAuto();
        </script>
    """, height=260)

    st.markdown("---")

    # ── Interactive Quick Actions ──
    st.markdown(f"""
        <h3 style='color:{t["text"]}; margin-bottom:16px;'>
            ⚡ Quick Actions
        </h3>
    """, unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)

    actions = [
        (col1, "➕", "Add Item",
         "Add new pantry item", "➕ Add Item"),
        (col2, "📦", "My Pantry",
         "View & manage items", "📦 My Pantry"),
        (col3, "🤖", "AI Recipes",
         "Get smart recipes",   "🤖 AI Recipes"),
        (col4, "📊", "Dashboard",
         "View analytics",      "📊 Dashboard"),
    ]

    for col, icon, title, desc, page_key in actions:
        with col:
            st.markdown(f"""
                <div class='action-card fade-in'>
                    <div class='action-icon'>{icon}</div>
                    <div class='action-title'>{title}</div>
                    <div class='action-desc'>{desc}</div>
                </div>
            """, unsafe_allow_html=True)
            if st.button(
                f"Go to {title}",
                key=f"home_btn_{page_key}",
                use_container_width=True
            ):
                st.session_state.current_page = page_key
                st.rerun()

    # ── Recent Activity ──
    st.markdown("---")
    st.markdown(f"""
        <h3 style='color:{t["text"]}; margin-bottom:12px;'>
            🕐 Recent Activity
        </h3>
    """, unsafe_allow_html=True)

    history = get_usage_history()
    if not history:
        st.info("No activity yet — start using your pantry!")
    else:
        recent = list(history)[:5]
        for h in recent:
            icon  = "✅" if not h['was_wasted'] else "🗑️"
            color = "#43e97b" if not h['was_wasted'] else "#f44336"
            action = "Used" if not h['was_wasted'] else "Wasted"
            st.markdown(f"""
                <div style='background:{t["card"]};
                            border-radius:10px;
                            padding:10px 16px;
                            margin-bottom:6px;
                            border-left:4px solid {color};
                            display:flex;
                            align-items:center;
                            gap:10px;'>
                    <span style='font-size:1.2rem;'>{icon}</span>
                    <span style='color:{t["text"]};font-size:0.88rem;'>
                        <b>{h['item_name']}</b> — {action}
                        on {h['used_date']}
                    </span>
                </div>
            """, unsafe_allow_html=True)

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

    # ── Search & Filter ──
    col1, col2, col3 = st.columns([3, 1, 1])
    with col1:
        search = st.text_input(
            "🔍 Search", placeholder="Search items..."
        )
    with col2:
        filter_cat = st.selectbox("Category", [
            "All","Dairy","Vegetables","Fruits",
            "Meat & Seafood","Grains & Cereals",
            "Snacks","Beverages","Condiments","Other"
        ])
    with col3:
        filter_expiry = st.selectbox("Expiry Filter", [
            "All","Critical (≤3d)","Expiring (≤7d)","Fresh (>7d)"
        ])

    # ── Filter Logic ──
    filtered = []
    for item in all_items:
        _, days, _, _ = get_expiry_info(item['expiry_date'])
        ms = search.lower() in item['name'].lower() if search else True
        mc = item['category'] == filter_cat if filter_cat != "All" else True
        me = True
        if   filter_expiry == "Critical (≤3d)":  me = days <= 3
        elif filter_expiry == "Expiring (≤7d)":  me = days <= 7
        elif filter_expiry == "Fresh (>7d)":     me = days > 7
        if ms and mc and me:
            filtered.append(item)

    st.markdown(
        f"Showing **{len(filtered)}** of **{len(all_items)}** items"
    )
    st.markdown("---")

    # ── Display Items ──
    for item in filtered:
        emoji, days_left, badge, card_cls = \
            get_expiry_info(item['expiry_date'])

        # ── EDIT MODE ──
        if st.session_state.edit_item_id == item['id']:
            with st.form(key=f"edit_{item['id']}"):
                st.markdown(f"### ✏️ Editing: **{item['name']}**")
                c1, c2 = st.columns(2)
                with c1:
                    nn = st.text_input("Name",     value=item['name'])
                    nq = st.text_input("Quantity", value=item['quantity'])
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
                            item['id'], name=nn, quantity=nq,
                            expiry_date=str(ne), category=nc
                        )
                        st.session_state.edit_item_id = None
                        st.rerun()
                with s2:
                    if st.form_submit_button(
                        "❌ Cancel", use_container_width=True
                    ):
                        st.session_state.edit_item_id = None
                        st.rerun()

        # ── NORMAL VIEW WITH IMAGE ──
        else:
            # Get image url and emoji for this item
            image_url = item['image_url'] \
                        if 'image_url' in item.keys() \
                        and item['image_url'] else None
            item_emoji = get_emoji(item['name'])

            # Layout: image | details | actions
            img_col, info_col, btn_col = st.columns([1, 5, 2])

            # ── Image Column ──
            with img_col:
                if image_url:
                    st.markdown(f"""
                        <div style='
                            width:70px; height:70px;
                            border-radius:12px;
                            overflow:hidden;
                            box-shadow:0 2px 10px rgba(0,0,0,0.1);
                        '>
                            <img src="{image_url}"
                                 style='width:100%; height:100%;
                                        object-fit:cover;'
                                 onerror="this.style.display='none';
                                          this.nextSibling.style.display='flex';"
                            />
                            <div style='
                                display:none;
                                width:70px; height:70px;
                                background:{t["card2"]};
                                border-radius:12px;
                                align-items:center;
                                justify-content:center;
                                font-size:2rem;
                            '>{item_emoji}</div>
                        </div>
                    """, unsafe_allow_html=True)
                else:
                    # Emoji fallback
                    st.markdown(f"""
                        <div style='
                            width:70px; height:70px;
                            background: linear-gradient(
                                135deg,#667eea22,#43e97b22
                            );
                            border-radius:12px;
                            display:flex;
                            align-items:center;
                            justify-content:center;
                            font-size:2.2rem;
                            border:1px solid {t["border"]};
                        '>{item_emoji}</div>
                    """, unsafe_allow_html=True)

            # ── Info Column ──
            with info_col:
                st.markdown(f"""
                    <div class='item-card {card_cls} fade-in'
                         style='margin-bottom:0; padding:12px 16px;'>
                        <div style='display:flex;
                                    align-items:center;
                                    gap:8px; flex-wrap:wrap;'>
                            <b style='font-size:1rem;
                                      color:{t["text"]};'>
                                {emoji} {item['name']}
                            </b>
                            <span class='badge badge-gray'>
                                {item['category']}
                            </span>
                            <span class='badge {badge}'>
                                {"EXPIRED!" if days_left < 0
                                  else "Expires Today!" if days_left == 0
                                  else f"{days_left}d left"}
                            </span>
                        </div>
                        <div style='margin-top:6px;
                                    color:{t["subtext"]};
                                    font-size:0.82rem;'>
                            📏 <b>{item['quantity']}</b>
                            &nbsp;|&nbsp;
                            📅 Expires: <b>{item['expiry_date']}</b>
                            &nbsp;|&nbsp;
                            🛒 Bought: <b>{item['purchase_date']}</b>
                        </div>
                    </div>
                """, unsafe_allow_html=True)

            # ── Action Buttons Column ──
            with btn_col:
                b1, b2, b3 = st.columns(3)
                with b1:
                    if st.button(
                        "✅",
                        key=f"use_{item['id']}",
                        help="Mark as used"
                    ):
                        log_usage(item['name'], was_wasted=False)
                        delete_item(item['id'])
                        st.toast(
                            f"✅ {item['name']} marked as used!"
                        )
                        st.rerun()
                with b2:
                    if st.button(
                        "✏️",
                        key=f"edit_{item['id']}",
                        help="Edit item"
                    ):
                        st.session_state.edit_item_id = item['id']
                        st.rerun()
                with b3:
                    if st.button(
                        "🗑️",
                        key=f"del_{item['id']}",
                        help="Delete item"
                    ):
                        log_usage(item['name'], was_wasted=True)
                        delete_item(item['id'])
                        st.toast(f"🗑️ {item['name']} removed!")
                        st.rerun()

            st.markdown("<div style='margin-bottom:8px;'></div>",
                        unsafe_allow_html=True)
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

        # ── Live Image Preview ──
        st.markdown("#### 🔍 Item Preview")

        # Item name input OUTSIDE form for live preview
        name = st.text_input(
            "Item Name *",
            placeholder="e.g. Milk, Eggs, Spinach",
            key="item_name_input"
        )

        # Show image preview as user types
        if name and len(name) >= 3:
            with st.spinner("🔍 Fetching image..."):
                image_url, emoji = get_food_image(name)

            preview_col1, preview_col2 = st.columns([1, 2])
            with preview_col1:
                if image_url:
                    st.image(
                        image_url,
                        width=150,
                        caption=f"{emoji} {name}"
                    )
                else:
                    st.markdown(f"""
                        <div style='
                            width:150px; height:150px;
                            background:{t["card2"]};
                            border-radius:12px;
                            display:flex;
                            align-items:center;
                            justify-content:center;
                            font-size:4rem;
                            border:2px dashed {t["border"]};
                        '>{emoji}</div>
                    """, unsafe_allow_html=True)

            with preview_col2:
                if image_url:
                    st.success(f"✅ Image found for **{name}**!")
                else:
                    st.info(
                        f"{emoji} No image found — "
                        f"emoji will be used instead!"
                    )
        else:
            # Placeholder before typing
            st.markdown(f"""
                <div style='
                    width:100%; height:120px;
                    background:{t["card2"]};
                    border-radius:12px;
                    display:flex;
                    align-items:center;
                    justify-content:center;
                    border:2px dashed {t["border"]};
                    color:{t["subtext"]};
                    font-size:0.9rem;
                    margin-bottom:16px;
                '>
                    🖼️ Type item name to see preview
                </div>
            """, unsafe_allow_html=True)

        st.markdown("---")

        # ── Rest of the form ──
        with st.form("add_form", clear_on_submit=True):
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
                    "Expiry Date *", value=date.today()
                )

            submitted = st.form_submit_button(
                "➕ Add to Pantry",
                use_container_width=True
            )

            if submitted:
                item_name = st.session_state.get(
                    "item_name_input", ""
                )
                if not item_name or not quantity:
                    st.error("❌ Fill in all required fields!")
                elif expiry_date < purchase_date:
                    st.error("❌ Expiry before purchase date!")
                elif expiry_date < date.today():
                    st.error("❌ Item is already expired!")
                else:
                    # Fetch image URL to save in DB
                    img_url, _ = get_food_image(item_name)

                    add_item(
                        name=item_name,
                        quantity=quantity,
                        purchase_date=str(purchase_date),
                        expiry_date=str(expiry_date),
                        category=category,
                        image_url=img_url or ""
                    )
                    st.success(f"✅ **{item_name}** added!")
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
        st.info(f"📦 **{len(all_items)}** items available")
    with c2:
        if expiring_items:
            st.warning(
                f"⚠️ **{len(expiring_items)}** expiring soon!"
            )

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
    render_dashboard(
        get_all_items(),
        get_expiring_items(7),
        get_usage_history(),
        st.session_state.dark_mode
    )

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
