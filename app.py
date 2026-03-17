# app.py — FreshMind v2.5 FIXED FINAL
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
from auth import (
    create_auth_tables, login_user, register_user,
    get_all_users, update_password
)

# ─────────────────────────────────────────
# APP CONFIG
# ─────────────────────────────────────────

st.set_page_config(
    page_title="FreshMind 🥗",
    page_icon="🥗",
    layout="wide",
    initial_sidebar_state="expanded"  # ✅ Always expanded
)

create_tables()
create_auth_tables()

# ─────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────

defaults = {
    "logged_in":    False,
    "username":     "",
    "user_data":    {},
    "dark_mode":    False,
    "chat_history": [],
    "edit_item_id": None,
    "current_page": "🏠 Home",
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
            "gradient":  "linear-gradient(135deg,#0f0f1a,#1a1a2e)",
            "hero":      "linear-gradient(135deg,#1a1a2e,#16213e)",
            "input_bg":  "#16213e",
            "input_text":"#ffffff",
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
            "gradient":  "linear-gradient(135deg,#f0f4f8,#e8f5e9)",
            "hero":      "linear-gradient(135deg,#2e7d32,#66bb6a)",
            "input_bg":  "#ffffff",
            "input_text":"#1a1a2e",
        }

# ─────────────────────────────────────────
# GLOBAL CSS
# ─────────────────────────────────────────

def inject_css():
    t  = get_theme()
    dm = st.session_state.dark_mode
    st.markdown(f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');

        * {{
            font-family: 'Poppins', sans-serif !important;
            transition: background 0.3s, color 0.3s;
            box-sizing: border-box;
        }}

        /* ── App background ── */
        .stApp {{
            background: {t['gradient']} !important;
            min-height: 100vh;
        }}

        /* ── FORCE sidebar always visible & expanded ── */
        section[data-testid="stSidebar"] {{
            background: {t['card']} !important;
            border-right: 1px solid {t['border']} !important;
            box-shadow: 3px 0 20px rgba(0,0,0,0.08) !important;
            min-width: 260px !important;
            width: 260px !important;
            transform: none !important;
            visibility: visible !important;
            display: block !important;
        }}
        section[data-testid="stSidebar"] > div {{
            overflow-x: hidden !important;
            padding-bottom: 20px;
        }}

        /* ── Hide sidebar collapse button ── */
        button[data-testid="collapsedControl"],
        button[kind="header"] {{
            display: none !important;
        }}
        [data-testid="stSidebarCollapseButton"] {{
            display: none !important;
        }}

        /* ── Fix ALL text colors for theme ── */
        h1, h2, h3, h4, h5, h6 {{
            color: {t['text']} !important;
        }}
        p, label, div, span {{
            color: {t['text']};
        }}
        .stMarkdown p {{
            color: {t['text']} !important;
        }}
        small {{ color: {t['subtext']} !important; }}

        /* ── Input fields ── */
        .stTextInput > div > div > input {{
            background: {t['input_bg']} !important;
            color: {t['input_text']} !important;
            border: 1.5px solid {t['border']} !important;
            border-radius: 10px !important;
        }}
        .stTextInput > div > div > input::placeholder {{
            color: {t['subtext']} !important;
            opacity: 0.8 !important;
        }}
        .stTextInput > div > div > input:focus {{
            border-color: {t['primary']} !important;
            box-shadow: 0 0 0 2px {t['primary']}33 !important;
        }}

        /* ── Hide "press enter" hint ── */
        .stTextInput > div > div + div,
        .stTextInput ~ small {{
            display: none !important;
        }}

        /* ── Selectbox ── */
        .stSelectbox > div > div {{
            background: {t['input_bg']} !important;
            color: {t['input_text']} !important;
            border: 1.5px solid {t['border']} !important;
            border-radius: 10px !important;
        }}

        /* ── Tabs ── */
        .stTabs [data-baseweb="tab"] {{
            color: {t['subtext']} !important;
        }}
        .stTabs [aria-selected="true"] {{
            color: {t['primary']} !important;
        }}
        .stTabs [data-baseweb="tab-panel"] {{
            background: transparent !important;
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
        .fm-card p, .fm-card b, .fm-card span {{
            color: {t['text']} !important;
        }}

        /* ── Badges ── */
        .badge {{
            padding: 3px 10px;
            border-radius: 20px;
            font-size: 11px;
            font-weight: 600;
            display: inline-block;
        }}
        .badge-red    {{ background:#ffe0e0; color:#c62828 !important; }}
        .badge-orange {{ background:#fff3e0; color:#e65100 !important; }}
        .badge-green  {{ background:#e0f2e9; color:#1b5e20 !important; }}
        .badge-gray   {{ background:{"#2a2a4a" if dm else "#f0f0f0"};
                         color:{t['subtext']} !important; }}

        /* ── Item Cards ── */
        .item-card {{
            background: {t['card']};
            border-radius: 12px;
            padding: 14px 18px;
            margin-bottom: 6px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.06);
            border-left: 5px solid {t['success']};
            transition: all 0.2s;
        }}
        .item-card:hover {{
            transform: translateX(4px);
            box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        }}
        .item-card b, .item-card small,
        .item-card div, .item-card span {{
            color: {t['text']} !important;
        }}
        .item-card-red    {{ border-left-color:#f44336 !important; }}
        .item-card-orange {{ border-left-color:#ff9800 !important; }}

        /* ── Quick Action Buttons (styled as cards) ── */
        div[data-testid="stButton"] button.action-btn {{
            height: 130px !important;
            background: {t['card']} !important;
            border: 1px solid {t['border']} !important;
            border-radius: 16px !important;
            display: flex !important;
            flex-direction: column !important;
            align-items: center !important;
            justify-content: center !important;
            transition: all 0.25s !important;
            color: {t['text']} !important;
            box-shadow: 0 4px 20px rgba(0,0,0,0.06) !important;
        }}
        div[data-testid="stButton"] button.action-btn:hover {{
            transform: translateY(-8px) !important;
            box-shadow: 0 16px 40px rgba(102,126,234,0.2) !important;
            border-color: {t['primary']} !important;
            background: linear-gradient(
                135deg,#667eea0d,#43e97b0d
            ) !important;
        }}

        /* ── All Streamlit buttons ── */
        .stButton > button {{
            border-radius: 10px !important;
            font-weight: 500 !important;
            transition: all 0.2s !important;
            color: {t['text']} !important;
            border: 1px solid {t['border']} !important;
            background: {t['card']} !important;
        }}
        .stButton > button:hover {{
            transform: translateY(-2px) !important;
            box-shadow: 0 5px 15px rgba(102,126,234,0.3) !important;
            background: linear-gradient(
                135deg,#667eea,#43e97b
            ) !important;
            color: white !important;
            border-color: transparent !important;
        }}

        /* ── Hero Banner ── */
        .hero-banner {{
            background: {t['hero']};
            padding: 32px 28px;
            border-radius: 20px;
            margin-bottom: 28px;
            position: relative;
            overflow: hidden;
        }}
        .hero-banner::before {{
            content: '';
            position: absolute;
            top: -50%; right: -10%;
            width: 280px; height: 280px;
            background: rgba(255,255,255,0.06);
            border-radius: 50%;
        }}
        .hero-banner h1,
        .hero-banner h2,
        .hero-banner p {{
            color: white !important;
            position: relative; z-index: 1;
        }}

        /* ── Chat bubbles ── */
        .chat-user {{
            background: linear-gradient(135deg,#667eea,#764ba2);
            color: white !important;
            padding: 12px 16px;
            border-radius: 16px 16px 4px 16px;
            margin: 8px 0 8px auto;
            max-width: 75%; display: table;
        }}
        .chat-ai {{
            background: {t['card2']};
            color: {t['text']} !important;
            padding: 12px 16px;
            border-radius: 16px 16px 16px 4px;
            margin: 8px 0; max-width: 75%;
            border: 1px solid {t['border']};
            display: table;
        }}

        /* ── Animations ── */
        @keyframes fadeInUp {{
            from {{ opacity:0; transform:translateY(16px); }}
            to   {{ opacity:1; transform:translateY(0); }}
        }}
        .fade-in {{ animation: fadeInUp 0.45s ease forwards; }}

        /* ── Notification alert box ── */
        .notif-item {{
            background: {t['card']};
            border-left: 3px solid #f44336;
            border-radius: 10px;
            padding: 8px 12px;
            margin-bottom: 6px;
        }}
        .notif-item b {{ color: {t['text']} !important; }}
        .notif-item small {{ color: #f44336 !important; }}

        /* ── Hide Streamlit chrome ── */
        #MainMenu, footer, header {{ visibility: hidden; }}
        .block-container {{ padding-top: 1rem !important; }}
    </style>
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
            confetti({ particleCount:120, spread:80,
                origin:{y:0.6}, colors:['#667eea','#43e97b',
                '#f093fb','#4facfe','#fa709a'] });
        </script>
    """, height=0)

# ─────────────────────────────────────────
# LOGIN PAGE
# ─────────────────────────────────────────

def login_page():
    inject_css()
    t  = get_theme()
    dm = st.session_state.dark_mode

    components.html(f"""
        <style>
            body {{ margin:0; overflow:hidden; }}
            #bg {{ width:100%; display:block; }}
        </style>
        <canvas id="bg" height="160"></canvas>
        <script>
            const c = document.getElementById('bg');
            const x = c.getContext('2d');
            c.width = window.innerWidth;
            const bg = "{"#0f0f1a" if dm else "#eef4ee"}";
            const ps = Array.from({{length:35}}, () => ({{
                x: Math.random()*c.width,
                y: Math.random()*160,
                r: Math.random()*3+1,
                dx: (Math.random()-.5)*1.4,
                dy: (Math.random()-.5)*1.4,
                col:`hsla(${{Math.random()*60+100}},70%,55%,.6)`
            }}));
            function draw() {{
                x.fillStyle = bg;
                x.fillRect(0,0,c.width,160);
                ps.forEach(p=>{{
                    x.beginPath();
                    x.arc(p.x,p.y,p.r,0,Math.PI*2);
                    x.fillStyle=p.col; x.fill();
                    p.x+=p.dx; p.y+=p.dy;
                    if(p.x<0||p.x>c.width) p.dx*=-1;
                    if(p.y<0||p.y>160) p.dy*=-1;
                }});
                requestAnimationFrame(draw);
            }}
            draw();
        </script>
    """, height=160)

    col1, col2, col3 = st.columns([1, 1.4, 1])
    with col2:
        st.markdown(f"""
            <div class='fade-in'
                 style='text-align:center; padding:14px 0 10px;'>
                <div style='font-size:3.2rem;'>🥗</div>
                <h1 style='font-size:2rem; font-weight:700;
                    background:linear-gradient(135deg,#667eea,#43e97b);
                    -webkit-background-clip:text;
                    -webkit-text-fill-color:transparent;
                    margin:4px 0;'>FreshMind</h1>
                <p style='color:{t["subtext"]} !important;
                           font-size:0.9rem; margin:0 0 14px;'>
                    Your AI-Powered Smart Pantry Assistant
                </p>
            </div>
        """, unsafe_allow_html=True)

        tab1, tab2 = st.tabs(["🔐 Login", "📝 Register"])

        with tab1:
            with st.form("login_form"):
                st.markdown(f"""
                    <h3 style='color:{t["text"]} !important;
                               margin-bottom:10px;'>
                        👋 Welcome Back!
                    </h3>
                """, unsafe_allow_html=True)
                username = st.text_input(
                    "👤 Username",
                    placeholder="Enter username"
                )
                password = st.text_input(
                    "🔒 Password", type="password",
                    placeholder="Enter password"
                )
                c1, c2 = st.columns(2)
                with c1:
                    submitted = st.form_submit_button(
                        "🔐 Login",
                        use_container_width=True
                    )
                with c2:
                    dark_btn = st.form_submit_button(
                        "🌙 Dark" if not dm else "☀️ Light",
                        use_container_width=True
                    )
                if dark_btn:
                    st.session_state.dark_mode = not dm
                    st.rerun()
                if submitted:
                    if not username or not password:
                        st.error("❌ Fill in all fields!")
                    else:
                        user = login_user(username, password)
                        if user:
                            st.session_state.logged_in    = True
                            st.session_state.username     = username
                            st.session_state.user_data    = user
                            st.session_state.current_page = "🏠 Home"
                            st.rerun()
                        else:
                            st.error(
                                "❌ Wrong username or password!"
                            )

            st.markdown(f"""
                <p style='text-align:center;
                          color:{t["subtext"]} !important;
                          font-size:0.78rem; margin-top:8px;'>
                    Demo:
                    <b style='color:{t["text"]} !important;'>
                        admin
                    </b> /
                    <b style='color:{t["text"]} !important;'>
                        admin123
                    </b>
                </p>
            """, unsafe_allow_html=True)

        with tab2:
            with st.form("register_form"):
                st.markdown(f"""
                    <h3 style='color:{t["text"]} !important;
                               margin-bottom:10px;'>
                        🆕 Create Account
                    </h3>
                """, unsafe_allow_html=True)
                r_name  = st.text_input(
                    "👤 Full Name *",
                    placeholder="Your full name"
                )
                r_user  = st.text_input(
                    "🆔 Username *",
                    placeholder="Choose a username"
                )
                r_email = st.text_input(
                    "📧 Email",
                    placeholder="your@email.com"
                )
                r_pass  = st.text_input(
                    "🔒 Password *", type="password",
                    placeholder="Min 6 characters"
                )
                r_pass2 = st.text_input(
                    "🔒 Confirm Password *", type="password",
                    placeholder="Repeat password"
                )
                reg = st.form_submit_button(
                    "📝 Create Account",
                    use_container_width=True
                )
                if reg:
                    if not r_name or not r_user or not r_pass:
                        st.error("❌ Fill all required fields!")
                    elif len(r_pass) < 6:
                        st.error("❌ Password min 6 characters!")
                    elif r_pass != r_pass2:
                        st.error("❌ Passwords don't match!")
                    else:
                        ok, msg = register_user(
                            r_user, r_pass, r_email, r_name
                        )
                        if ok:
                            # ✅ Auto-login → home page!
                            user = login_user(r_user, r_pass)
                            if user:
                                st.session_state.logged_in    = True
                                st.session_state.username     = r_user
                                st.session_state.user_data    = user
                                st.session_state.current_page = "🏠 Home"
                                st.rerun()
                        else:
                            st.error(msg)

# ─────────────────────────────────────────
# SIDEBAR — always visible, native Streamlit
# ─────────────────────────────────────────

def render_sidebar():
    t  = get_theme()
    dm = st.session_state.dark_mode

    with st.sidebar:
        # ── Logo ──
        st.markdown(f"""
            <div style='text-align:center; padding:14px 0 16px;'>
                <div style='font-size:2.6rem;'>🥗</div>
                <h2 style='margin:4px 0;
                    color:{t["primary"]} !important;
                    font-size:1.3rem;'>FreshMind</h2>
                <p style='color:{t["subtext"]} !important;
                           font-size:0.7rem; margin:0;'>
                    Smart Pantry Assistant
                </p>
            </div>
        """, unsafe_allow_html=True)

        # ── User card ──
        user = st.session_state.user_data
        fname = user.get("full_name","") or \
                st.session_state.username
        st.markdown(f"""
            <div style='background:{t["card2"]};
                border:1px solid {t["border"]};
                border-radius:12px; padding:9px 13px;
                margin-bottom:12px;'>
                <b style='color:{t["text"]} !important;
                           font-size:0.88rem;'>
                    👤 {fname}
                </b><br>
                <small style='color:{t["subtext"]} !important;
                               font-size:0.72rem;'>
                    @{st.session_state.username} ● Online
                </small>
            </div>
        """, unsafe_allow_html=True)

        # ── Nav label ──
        st.markdown(f"""
            <p style='color:{t["subtext"]} !important;
                      font-size:0.65rem; margin:0 0 5px 2px;
                      font-weight:700; text-transform:uppercase;
                      letter-spacing:1.2px;'>
                Navigation
            </p>
        """, unsafe_allow_html=True)

        # ── Nav buttons ──
        pages = [
            ("🏠", "Home",       "🏠 Home"),
            ("📦", "My Pantry",  "📦 My Pantry"),
            ("➕", "Add Item",   "➕ Add Item"),
            ("🤖", "AI Recipes", "🤖 AI Recipes"),
            ("📊", "Dashboard",  "📊 Dashboard"),
            ("⚙️", "Settings",  "⚙️ Settings"),
        ]

        for icon, label, key in pages:
            is_active = st.session_state.current_page == key
            if st.button(
                f"{icon}  {label}",
                key=f"nav_{key}",
                use_container_width=True
            ):
                st.session_state.current_page = key
                st.rerun()

            # Highlight active page
            if is_active:
                st.markdown(f"""
                    <style>
                    div[data-testid="stSidebar"]
                    div[data-testid="stButton"]
                    button:has(p:contains("{icon}  {label}")) {{
                        background: linear-gradient(
                            135deg,#667eea,#43e97b
                        ) !important;
                        color: white !important;
                        border-color: transparent !important;
                        box-shadow: 0 4px 14px
                            rgba(102,126,234,0.4) !important;
                        transform: translateX(3px) !important;
                    }}
                    </style>
                """, unsafe_allow_html=True)

        st.markdown("---")

        # ── Notification alerts (native — always works!) ──
        expiring = get_expiring_items(7)
        count    = len(expiring)

        if count > 0:
            st.markdown(f"""
                <div style='background:#f4433615;
                    border:1px solid #f4433640;
                    border-radius:12px; padding:10px 12px;
                    margin-bottom:10px;'>
                    <b style='color:#f44336 !important;
                               font-size:0.85rem;'>
                        🔔 {count} Expiry Alert(s)
                    </b>
                </div>
            """, unsafe_allow_html=True)
            for item in expiring:
                _, days, _, _ = get_expiry_info(
                    item['expiry_date']
                )
                if days < 0:
                    label = f"EXPIRED {abs(days)}d ago!"
                    color = "#f44336"
                elif days == 0:
                    label = "Expires TODAY! 🚨"
                    color = "#f44336"
                elif days <= 3:
                    label = f"In {days} day(s) ⚠️"
                    color = "#ff9800"
                else:
                    label = f"{item['expiry_date']}"
                    color = "#ff9800"
                st.markdown(f"""
                    <div style='background:{t["card"]};
                        border-left:3px solid {color};
                        border-radius:8px;
                        padding:7px 10px;
                        margin-bottom:5px;'>
                        <b style='color:{t["text"]} !important;
                                   font-size:0.8rem;'>
                            {item['name']}
                        </b><br>
                        <small style='color:{color} !important;
                                      font-size:0.7rem;'>
                            📅 {label}
                        </small>
                    </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
                <div style='background:#43e97b15;
                    border:1px solid #43e97b40;
                    border-radius:10px; padding:8px 12px;
                    margin-bottom:10px; text-align:center;'>
                    <small style='color:#43e97b !important;
                                  font-size:0.78rem;'>
                        ✅ No expiry alerts!
                    </small>
                </div>
            """, unsafe_allow_html=True)

        st.markdown("---")

        # ── Dark mode toggle ──
        if st.button(
            "🌙 Dark Mode" if not dm else "☀️ Light Mode",
            use_container_width=True,
            key="theme_toggle"
        ):
            st.session_state.dark_mode = not dm
            st.rerun()

        st.markdown("")

        # ── Logout ──
        if st.button(
            "🚪 Logout",
            use_container_width=True,
            key="logout_btn"
        ):
            for k in list(st.session_state.keys()):
                del st.session_state[k]
            st.rerun()

        st.markdown(f"""
            <p style='text-align:center;
                      color:{t["subtext"]} !important;
                      font-size:0.62rem; margin-top:14px;'>
                Built with ❤️ Python & Streamlit
            </p>
        """, unsafe_allow_html=True)

    return st.session_state.current_page

# ─────────────────────────────────────────
# PAGE — HOME
# ─────────────────────────────────────────

def home_page():
    t  = get_theme()
    dm = st.session_state.dark_mode

    user  = st.session_state.user_data
    fname = user.get("full_name","") or \
            st.session_state.username

    st.markdown(f"""
        <div class='hero-banner fade-in'>
            <h1 style='font-size:1.9rem; margin:0;'>
                👋 Hello, {fname}!
            </h1>
            <p style='font-size:1rem; opacity:0.85;
                      margin:7px 0 0;'>
                {date.today().strftime("%A, %B %d %Y")} —
                Here's your pantry overview
            </p>
        </div>
    """, unsafe_allow_html=True)

    all_items      = get_all_items()
    expiring_items = get_expiring_items(7)
    critical_items = get_expiring_items(3)
    history        = get_usage_history()
    saved  = sum(1 for h in history if not h['was_wasted'])
    wasted = sum(1 for h in history if h['was_wasted'])

    # ── Animated metric cards ──
    components.html(f"""
        <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700&display=swap"
              rel="stylesheet">
        <style>
            *{{ font-family:'Poppins',sans-serif;
                box-sizing:border-box; }}
            .g{{ display:grid;
                 grid-template-columns:repeat(4,1fr);
                 gap:14px; padding:2px 0 12px; }}
            .c{{ background:{"#1a1a2e" if dm else "white"};
                 border-radius:14px; padding:20px;
                 text-align:center;
                 box-shadow:0 4px 18px rgba(0,0,0,0.07);
                 transition:transform .2s; cursor:default; }}
            .c:hover{{ transform:translateY(-5px); }}
            .i{{ font-size:1.9rem; margin-bottom:5px; }}
            .n{{ font-size:2rem; font-weight:700; margin:3px 0; }}
            .l{{ font-size:0.72rem;
                 color:{"#a0a0b0" if dm else "#888"}; }}
        </style>
        <div class="g">
            <div class="c">
                <div class="i">📦</div>
                <div class="n" style="color:#667eea" id="c1">0</div>
                <div class="l">Total Items</div>
            </div>
            <div class="c">
                <div class="i">⚠️</div>
                <div class="n" style="color:#fa709a" id="c2">0</div>
                <div class="l">Expiring This Week</div>
            </div>
            <div class="c">
                <div class="i">✅</div>
                <div class="n" style="color:#43e97b" id="c3">0</div>
                <div class="l">Items Saved</div>
            </div>
            <div class="c">
                <div class="i">🗑️</div>
                <div class="n" style="color:#f44336" id="c4">0</div>
                <div class="l">Items Wasted</div>
            </div>
        </div>
        <script>
            function up(id,target,dur=1400){{
                const el=document.getElementById(id);
                if(!el||!target){{if(el)el.textContent=0;return;}}
                let s=0,step=target/(dur/16);
                const t=setInterval(()=>{{
                    s+=step;
                    if(s>=target){{el.textContent=target;clearInterval(t);}}
                    else el.textContent=Math.floor(s);
                }},16);
            }}
            up('c1',{len(all_items)});
            up('c2',{len(expiring_items)});
            up('c3',{saved});
            up('c4',{wasted});
        </script>
    """, height=140)

    # Alerts
    if critical_items:
        st.error("🚨 Critical — Use these items immediately!")
        for item in critical_items:
            _, days, _, _ = get_expiry_info(item['expiry_date'])
            msg = f"EXPIRED {abs(days)}d ago!" \
                  if days < 0 else f"expires in {days} day(s)!"
            st.warning(
                f"⚠️ **{item['name']}** "
                f"({item['category']}) — {msg}"
            )
    elif expiring_items:
        st.warning(
            f"⚠️ {len(expiring_items)} items expiring this week!"
        )
    else:
        st.success("✅ Everything is fresh!")

    st.markdown("---")

    # ── Cooking Tips + AI button ──
    st.markdown(f"""
        <h3 style='color:{t["text"]} !important;
                   margin-bottom:8px;'>
            🍳 Cooking Tips of the Day
        </h3>
    """, unsafe_allow_html=True)

    if st.button(
        "✨ Get AI Tips for My Pantry",
        key="ai_tips_btn"
    ):
        with st.spinner("🤖 Getting personalized tips..."):
            try:
                from groq import Groq
                from dotenv import load_dotenv
                import os
                load_dotenv()
                client = Groq(api_key=os.getenv("GROQ_API_KEY"))
                items_text = ", ".join(
                    [i['name'] for i in all_items[:10]]
                ) if all_items else "empty pantry"
                resp = client.chat.completions.create(
                    model="llama-3.1-8b-instant",
                    max_tokens=300,
                    messages=[{"role":"user","content":(
                        f"Give 3 quick cooking/storage tips for "
                        f"these pantry items: {items_text}. "
                        f"Each tip under 2 sentences. "
                        f"Format: emoji + tip"
                    )}]
                )
                st.info(
                    f"💡 **AI Tips:**\n\n"
                    f"{resp.choices[0].message.content}"
                )
            except Exception as e:
                st.error(f"❌ Error: {e}")

    # Cooking Tips Slider — 5s
    components.html(f"""
        <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600&display=swap"
              rel="stylesheet">
        <style>
            *{{ font-family:'Poppins',sans-serif;
                box-sizing:border-box; }}
            .sw{{ background:{"#1a1a2e" if dm else "white"};
                  border-radius:14px; padding:20px 24px;
                  box-shadow:0 4px 18px rgba(0,0,0,0.07);
                  border:1px solid {"#2a2a4a" if dm else "#e0e8f0"}; }}
            .tip{{ display:none; animation:fi .5s ease; }}
            .tip.active{{ display:block; }}
            @keyframes fi{{
                from{{opacity:0;transform:translateX(18px);}}
                to{{opacity:1;transform:translateX(0);}}
            }}
            .ti{{ font-size:1.7rem; margin-bottom:5px; }}
            .tt{{ font-size:.92rem; font-weight:600;
                  color:{"#fff" if dm else "#1a1a2e"};
                  margin-bottom:3px; }}
            .tx{{ font-size:.8rem; line-height:1.55;
                  color:{"#a0a0b0" if dm else "#555"}; }}
            .dots{{ display:flex; gap:5px;
                    justify-content:center; margin-top:12px; }}
            .dot{{ width:7px; height:7px; border-radius:50%;
                   background:{"#2a2a4a" if dm else "#ddd"};
                   cursor:pointer; border:none; transition:all .3s; }}
            .dot.active{{ background:#667eea; width:17px;
                          border-radius:4px; }}
            .nav{{ display:flex; justify-content:space-between;
                   margin-top:10px; }}
            .arr{{ background:{"#2a2a4a" if dm else "#f0f4f8"};
                   border:none; border-radius:8px;
                   padding:5px 12px; cursor:pointer;
                   font-size:.82rem;
                   color:{"#fff" if dm else "#333"};
                   transition:all .2s; }}
            .arr:hover{{ background:#667eea; color:white; }}
            .pb{{ height:3px; background:#667eea;
                  border-radius:2px; margin-top:10px;
                  transition:width .1s linear; }}
        </style>
        <div class="sw">
            <div id="tc"></div>
            <div class="pb" id="pb"></div>
            <div class="nav">
                <button class="arr" onclick="prev()">← Prev</button>
                <div class="dots" id="de"></div>
                <button class="arr" onclick="next()">Next →</button>
            </div>
        </div>
        <script>
            const tips=[
                {{i:"🥦",t:"Store Vegetables Right",
                  x:"Wrap leafy greens in damp paper towels. Stay fresh 2x longer!"}},
                {{i:"🧅",t:"Onion & Potato Rule",
                  x:"Never store together — onions release gases that sprout potatoes!"}},
                {{i:"🍋",t:"Citrus Juice Hack",
                  x:"Microwave lemons 15s before squeezing — 2x more juice!"}},
                {{i:"🥛",t:"Milk Storage Tip",
                  x:"Store milk on the middle shelf, not the door — stays cooler!"}},
                {{i:"🍌",t:"Banana Trick",
                  x:"Wrap banana stems in plastic wrap to slow ripening!"}},
                {{i:"🧄",t:"Garlic Freshness",
                  x:"Store at room temp in a mesh bag. Lasts 6 months!"}},
                {{i:"🍞",t:"Bread Hack",
                  x:"Freeze bread you won't use in 3 days. Toast from freezer!"}},
                {{i:"🥚",t:"Egg Test",
                  x:"Sink=fresh, float=bad. Never eat a floating egg!"}},
                {{i:"🌿",t:"Fresh Herbs",
                  x:"Store in a glass of water in fridge like flowers!"}},
                {{i:"🍎",t:"Apple Storage",
                  x:"Apples release ethylene — store separately!"}},
            ];
            let cur=0,pw=0,pt,at;
            const INT=5000;
            const tc=document.getElementById('tc');
            const de=document.getElementById('de');
            const pb=document.getElementById('pb');
            tips.forEach((tip,i)=>{{
                const d=document.createElement('div');
                d.className='tip'+(i===0?' active':'');
                d.id='t'+i;
                d.innerHTML=`<div class="ti">${{tip.i}}</div>
                    <div class="tt">${{tip.t}}</div>
                    <div class="tx">${{tip.x}}</div>`;
                tc.appendChild(d);
                const dot=document.createElement('button');
                dot.className='dot'+(i===0?' active':'');
                dot.id='d'+i; dot.onclick=()=>go(i);
                de.appendChild(dot);
            }});
            function go(n){{
                document.getElementById('t'+cur).classList.remove('active');
                document.getElementById('d'+cur).classList.remove('active');
                cur=(n+tips.length)%tips.length;
                document.getElementById('t'+cur).classList.add('active');
                document.getElementById('d'+cur).classList.add('active');
                reset();
            }}
            function next(){{go(cur+1);}}
            function prev(){{go(cur-1);}}
            function reset(){{
                pw=0; pb.style.width='0%';
                clearInterval(pt); clearTimeout(at);
                pt=setInterval(()=>{{
                    pw+=100/(INT/100);
                    pb.style.width=pw+'%';
                    if(pw>=100) clearInterval(pt);
                }},100);
                at=setTimeout(()=>next(),INT);
            }}
            reset();
        </script>
    """, height=230)

    st.markdown("---")

    # ── Quick Actions — pure Streamlit buttons styled as cards ──
    st.markdown(f"""
        <h3 style='color:{t["text"]} !important;
                   margin-bottom:12px;'>
            ⚡ Quick Actions
        </h3>
    """, unsafe_allow_html=True)

    actions = [
        ("➕", "Add Item",    "Add new pantry item",  "➕ Add Item"),
        ("📦", "My Pantry",  "View & manage items",  "📦 My Pantry"),
        ("🤖", "AI Recipes", "Get smart recipes",    "🤖 AI Recipes"),
        ("📊", "Dashboard",  "View analytics",       "📊 Dashboard"),
    ]

    cols = st.columns(4)
    for i, (col, (icon, title, desc, page_key)) in \
            enumerate(zip(cols, actions)):
        with col:
            # Single button styled as a card — NO extra button
            if st.button(
                f"{icon}",
                key=f"qa_{i}",
                use_container_width=True,
                help=f"{title} — {desc}"
            ):
                st.session_state.current_page = page_key
                st.rerun()

            # Style the button to look like a card
            st.markdown(f"""
                <style>
                div[data-testid="stButton"]:has(
                    button[data-testid="baseButton-secondary"][title="{title} — {desc}"]
                ) button {{
                    height: 120px !important;
                    background: {t['card']} !important;
                    border: 1px solid {t['border']} !important;
                    border-radius: 16px !important;
                    font-size: 2.2rem !important;
                    box-shadow: 0 4px 16px rgba(0,0,0,0.06) !important;
                }}
                div[data-testid="stButton"]:has(
                    button[data-testid="baseButton-secondary"][title="{title} — {desc}"]
                ) button:hover {{
                    background: linear-gradient(
                        135deg,#667eea11,#43e97b11
                    ) !important;
                    border-color: #667eea !important;
                    transform: translateY(-8px) !important;
                    box-shadow: 0 16px 36px
                        rgba(102,126,234,0.2) !important;
                }}
                </style>
                <div style='text-align:center; margin-top:-8px;
                            margin-bottom:8px;'>
                    <b style='font-size:0.88rem;
                               color:{t["text"]} !important;'>
                        {title}
                    </b><br>
                    <small style='font-size:0.72rem;
                                  color:{t["subtext"]} !important;'>
                        {desc}
                    </small>
                </div>
            """, unsafe_allow_html=True)

    # ── Recent Activity ──
    st.markdown("---")
    st.markdown(f"""
        <h3 style='color:{t["text"]} !important;
                   margin-bottom:10px;'>
            🕐 Recent Activity
        </h3>
    """, unsafe_allow_html=True)

    history = get_usage_history()
    if not history:
        st.info("No activity yet — start using your pantry!")
    else:
        for h in list(history)[:5]:
            icon   = "✅" if not h['was_wasted'] else "🗑️"
            color  = "#43e97b" if not h['was_wasted'] \
                     else "#f44336"
            action = "Used" if not h['was_wasted'] else "Wasted"
            st.markdown(f"""
                <div style='background:{t["card"]};
                    border-radius:10px; padding:9px 14px;
                    margin-bottom:5px;
                    border-left:4px solid {color};
                    display:flex; align-items:center; gap:9px;'>
                    <span style='font-size:1.1rem;'>{icon}</span>
                    <span style='color:{t["text"]} !important;
                                 font-size:0.84rem;'>
                        <b>{h['item_name']}</b> — {action}
                        on {h['used_date']}
                    </span>
                </div>
            """, unsafe_allow_html=True)

# ─────────────────────────────────────────
# PANTRY PAGE
# ─────────────────────────────────────────

def pantry_page():
    t  = get_theme()
    st.markdown("""
        <div class='hero-banner fade-in'
             style='padding:20px 25px;'>
            <h2 style='margin:0;'>📦 My Pantry</h2>
            <p style='margin:4px 0 0; opacity:0.85;'>
                Manage your food items
            </p>
        </div>
    """, unsafe_allow_html=True)

    all_items = get_all_items()
    if not all_items:
        st.info("🛒 Pantry is empty! Add some items.")
        return

    c1, c2, c3 = st.columns([3, 1, 1])
    with c1:
        search = st.text_input(
            "🔍 Search", placeholder="Search items..."
        )
    with c2:
        filter_cat = st.selectbox("Category", [
            "All","Dairy","Vegetables","Fruits",
            "Meat & Seafood","Grains & Cereals",
            "Snacks","Beverages","Condiments","Other"
        ])
    with c3:
        filter_expiry = st.selectbox("Expiry Filter", [
            "All","Critical (≤3d)",
            "Expiring (≤7d)","Fresh (>7d)"
        ])

    filtered = []
    for item in all_items:
        _, days, _, _ = get_expiry_info(item['expiry_date'])
        ms = search.lower() in item['name'].lower() \
             if search else True
        mc = item['category'] == filter_cat \
             if filter_cat != "All" else True
        me = True
        if   filter_expiry == "Critical (≤3d)": me = days <= 3
        elif filter_expiry == "Expiring (≤7d)": me = days <= 7
        elif filter_expiry == "Fresh (>7d)":    me = days > 7
        if ms and mc and me:
            filtered.append(item)

    st.markdown(
        f"Showing **{len(filtered)}** of "
        f"**{len(all_items)}** items"
    )
    st.markdown("---")

    for item in filtered:
        emoji, days_left, badge, card_cls = \
            get_expiry_info(item['expiry_date'])

        if st.session_state.edit_item_id == item['id']:
            with st.form(key=f"edit_{item['id']}"):
                st.markdown(
                    f"### ✏️ Editing: **{item['name']}**"
                )
                c1, c2 = st.columns(2)
                with c1:
                    nn = st.text_input(
                        "Name", value=item['name']
                    )
                    nq = st.text_input(
                        "Quantity", value=item['quantity']
                    )
                    cats = ["Dairy","Vegetables","Fruits",
                            "Meat & Seafood","Grains & Cereals",
                            "Snacks","Beverages",
                            "Condiments","Other"]
                    nc = st.selectbox(
                        "Category", cats,
                        index=cats.index(item['category'])
                    )
                with c2:
                    ne = st.date_input(
                        "Expiry Date",
                        value=datetime.strptime(
                            item['expiry_date'],"%Y-%m-%d"
                        ).date()
                    )
                s1, s2 = st.columns(2)
                with s1:
                    if st.form_submit_button(
                        "💾 Save",
                        use_container_width=True
                    ):
                        update_item(
                            item['id'], name=nn, quantity=nq,
                            expiry_date=str(ne), category=nc
                        )
                        st.session_state.edit_item_id = None
                        st.rerun()
                with s2:
                    if st.form_submit_button(
                        "❌ Cancel",
                        use_container_width=True
                    ):
                        st.session_state.edit_item_id = None
                        st.rerun()
        else:
            image_url  = item['image_url'] \
                if 'image_url' in item.keys() \
                and item['image_url'] else None
            item_emoji = get_emoji(item['name'])

            img_col, info_col, btn_col = st.columns([1,5,2])

            with img_col:
                if image_url:
                    st.markdown(f"""
                        <div style='width:65px;height:65px;
                            border-radius:11px;overflow:hidden;
                            box-shadow:0 2px 8px rgba(0,0,0,0.1);'>
                            <img src="{image_url}"
                                 style='width:100%;height:100%;
                                        object-fit:cover;'/>
                        </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                        <div style='width:65px;height:65px;
                            background:linear-gradient(135deg,
                                #667eea22,#43e97b22);
                            border-radius:11px;
                            display:flex;align-items:center;
                            justify-content:center;
                            font-size:2rem;
                            border:1px solid {t["border"]};'>
                            {item_emoji}
                        </div>
                    """, unsafe_allow_html=True)

            with info_col:
                st.markdown(f"""
                    <div class='item-card {card_cls} fade-in'
                         style='margin:0; padding:11px 15px;'>
                        <div style='display:flex;
                            align-items:center;
                            gap:7px; flex-wrap:wrap;'>
                            <b style='font-size:.92rem;
                                color:{t["text"]} !important;'>
                                {emoji} {item['name']}
                            </b>
                            <span class='badge badge-gray'>
                                {item['category']}
                            </span>
                            <span class='badge {badge}'>
                                {"EXPIRED!" if days_left<0
                                  else "Today!" if days_left==0
                                  else f"{days_left}d left"}
                            </span>
                        </div>
                        <div style='margin-top:4px;
                            color:{t["subtext"]} !important;
                            font-size:.78rem;'>
                            📏 <b style='color:{t["text"]}
                                !important;'>{item['quantity']}</b>
                            &nbsp;|&nbsp;
                            📅 <b style='color:{t["text"]}
                                !important;'>{item['expiry_date']}</b>
                        </div>
                    </div>
                """, unsafe_allow_html=True)

            with btn_col:
                b1,b2,b3 = st.columns(3)
                with b1:
                    if st.button("✅",
                                 key=f"use_{item['id']}",
                                 help="Mark used"):
                        log_usage(item['name'],was_wasted=False)
                        delete_item(item['id'])
                        st.toast(f"✅ {item['name']} used!")
                        st.rerun()
                with b2:
                    if st.button("✏️",
                                 key=f"edit_{item['id']}",
                                 help="Edit"):
                        st.session_state.edit_item_id=item['id']
                        st.rerun()
                with b3:
                    if st.button("🗑️",
                                 key=f"del_{item['id']}",
                                 help="Delete"):
                        log_usage(item['name'],was_wasted=True)
                        delete_item(item['id'])
                        st.toast(f"🗑️ {item['name']} removed!")
                        st.rerun()

            st.markdown(
                "<div style='margin-bottom:5px'></div>",
                unsafe_allow_html=True
            )

# ─────────────────────────────────────────
# ADD ITEM PAGE
# ─────────────────────────────────────────

def add_item_page():
    t = get_theme()
    st.markdown("""
        <div class='hero-banner fade-in'
             style='padding:20px 25px;'>
            <h2 style='margin:0;'>➕ Add New Item</h2>
            <p style='margin:4px 0 0; opacity:0.85;'>
                Add items to your pantry
            </p>
        </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("#### 🔍 Item Preview")
        name = st.text_input(
            "Item Name *",
            placeholder="e.g. Milk, Eggs, Spinach",
            key="item_name_input"
        )

        if name and len(name) >= 3:
            with st.spinner("🔍 Fetching image..."):
                image_url, emoji = get_food_image(name)
            p1, p2 = st.columns([1, 2])
            with p1:
                if image_url:
                    st.image(image_url, width=140,
                             caption=f"{emoji} {name}")
                else:
                    st.markdown(f"""
                        <div style='width:140px;height:140px;
                            background:{t["card2"]};
                            border-radius:12px;
                            display:flex;align-items:center;
                            justify-content:center;
                            font-size:3.8rem;
                            border:2px dashed {t["border"]};'>
                            {emoji}
                        </div>
                    """, unsafe_allow_html=True)
            with p2:
                if image_url:
                    st.success(f"✅ Image found!")
                else:
                    st.info(f"{emoji} Emoji preview")
        else:
            st.markdown(f"""
                <div style='width:100%;height:100px;
                    background:{t["card2"]};border-radius:12px;
                    display:flex;align-items:center;
                    justify-content:center;
                    border:2px dashed {t["border"]};
                    color:{t["subtext"]};font-size:.85rem;
                    margin-bottom:12px;'>
                    🖼️ Type item name to see preview
                </div>
            """, unsafe_allow_html=True)

        st.markdown("---")

        with st.form("add_form", clear_on_submit=True):
            c1, c2 = st.columns(2)
            with c1:
                quantity = st.text_input(
                    "Quantity *",
                    placeholder="e.g. 1 litre, 500g"
                )
            with c2:
                category = st.selectbox("Category *", [
                    "Dairy","Vegetables","Fruits",
                    "Meat & Seafood","Grains & Cereals",
                    "Snacks","Beverages","Condiments","Other"
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
            if st.form_submit_button(
                "➕ Add to Pantry",
                use_container_width=True
            ):
                item_name = st.session_state.get(
                    "item_name_input", ""
                )
                if not item_name or not quantity:
                    st.error("❌ Fill in all required fields!")
                elif expiry_date < purchase_date:
                    st.error("❌ Expiry before purchase date!")
                elif expiry_date < date.today():
                    st.error("❌ Item already expired!")
                else:
                    img_url, _ = get_food_image(item_name)
                    add_item(
                        name=item_name, quantity=quantity,
                        purchase_date=str(purchase_date),
                        expiry_date=str(expiry_date),
                        category=category,
                        image_url=img_url or ""
                    )
                    st.success(f"✅ **{item_name}** added!")
                    confetti()

# ─────────────────────────────────────────
# AI RECIPES PAGE
# ─────────────────────────────────────────

def ai_recipes_page():
    t = get_theme()
    st.markdown("""
        <div class='hero-banner fade-in'
             style='padding:20px 25px;'>
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
            ["Any","Breakfast","Lunch",
             "Dinner","Snack","Dessert"]
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
                "role":"assistant","content":result
            })

    st.markdown("### 💬 Recipe Chat")
    for msg in st.session_state.chat_history:
        if msg["role"] == "user":
            st.markdown(
                f"<div class='chat-user'>"
                f"{msg['content']}</div>",
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                f"<div class='chat-ai'>"
                f"{msg['content']}</div>",
                unsafe_allow_html=True
            )

    if st.session_state.chat_history:
        if st.button("🗑️ Clear Chat"):
            st.session_state.chat_history = []
            st.rerun()

    user_input = st.chat_input(
        "Ask — 'make it spicy', 'no onions', 'quick meal'"
    )
    if user_input:
        st.session_state.chat_history.append({
            "role":"user","content":user_input
        })
        with st.spinner("🤖 Thinking..."):
            response, st.session_state.chat_history = \
                chat_with_ai(
                    user_input,
                    st.session_state.chat_history
                )
        st.rerun()

# ─────────────────────────────────────────
# DASHBOARD
# ─────────────────────────────────────────

def dashboard_page():
    render_dashboard(
        get_all_items(), get_expiring_items(7),
        get_usage_history(), st.session_state.dark_mode
    )

# ─────────────────────────────────────────
# SETTINGS PAGE
# ─────────────────────────────────────────

def settings_page():
    t = get_theme()
    st.markdown("""
        <div class='hero-banner fade-in'
             style='padding:20px 25px;'>
            <h2 style='margin:0;'>⚙️ Settings</h2>
            <p style='margin:4px 0 0; opacity:0.85;'>
                Manage your account
            </p>
        </div>
    """, unsafe_allow_html=True)

    user = st.session_state.user_data
    tab1, tab2 = st.tabs([
        "👤 My Profile", "🔒 Change Password"
    ])

    with tab1:
        st.markdown(f"""
            <div class='fm-card'>
                <h3 style='color:{t["text"]} !important;
                           margin-bottom:12px;'>
                    👤 Profile Info
                </h3>
                <p style='color:{t["text"]} !important;'>
                    <b>Username:</b>
                    @{user.get('username','')}
                </p>
                <p style='color:{t["text"]} !important;'>
                    <b>Full Name:</b>
                    {user.get('full_name','') or 'Not set'}
                </p>
                <p style='color:{t["text"]} !important;'>
                    <b>Email:</b>
                    {user.get('email','') or 'Not set'}
                </p>
                <p style='color:{t["text"]} !important;'>
                    <b>Role:</b> {user.get('role','member')}
                </p>
                <p style='color:{t["text"]} !important;'>
                    <b>Member since:</b>
                    {str(user.get('created_at',''))[:10]}
                </p>
            </div>
        """, unsafe_allow_html=True)

        if user.get('role') == 'admin':
            st.markdown(f"""
                <h3 style='color:{t["text"]} !important;
                           margin:14px 0 8px;'>
                    👥 All Users
                </h3>
            """, unsafe_allow_html=True)
            for u in get_all_users():
                st.markdown(f"""
                    <div class='fm-card'
                         style='padding:10px 14px;'>
                        <b style='color:{t["text"]} !important;'>
                            👤 {u['username']}
                        </b>
                        <span style='color:{t["subtext"]} !important;
                            font-size:.78rem; margin-left:8px;'>
                            {u['full_name'] or ''} | {u['role']}
                        </span>
                    </div>
                """, unsafe_allow_html=True)

    with tab2:
        with st.form("change_pass"):
            old  = st.text_input(
                "Current Password", type="password"
            )
            new  = st.text_input(
                "New Password", type="password"
            )
            new2 = st.text_input(
                "Confirm New Password", type="password"
            )
            if st.form_submit_button(
                "🔒 Update Password",
                use_container_width=True
            ):
                if new != new2:
                    st.error("❌ Passwords don't match!")
                elif len(new) < 6:
                    st.error("❌ Min 6 characters!")
                else:
                    ok, msg = update_password(
                        user['id'], old, new
                    )
                    st.success(msg) if ok \
                    else st.error(msg)

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
    elif page == "⚙️ Settings":  settings_page()

if __name__ == "__main__":
    main()