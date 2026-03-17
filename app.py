# app.py — FreshMind v3.0
# Major upgrade: auth, lottie, barcode, family mode

import streamlit as st
from datetime import date, datetime
import streamlit.components.v1 as components
import requests
import json
import base64
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
    get_all_users, create_family, join_family,
    get_family_members, update_password
)

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
    "show_register": False,
    "scan_result":  None,
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
            "hover":     "#2a2a4a",
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
            "hover":     "#f0f4f8",
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

        /* ── App Background ── */
        .stApp {{
            background: {t['gradient']} !important;
            min-height: 100vh;
        }}

        /* ── Sidebar ── */
        section[data-testid="stSidebar"] {{
            background: {t['card']} !important;
            border-right: 1px solid {t['border']} !important;
            box-shadow: 2px 0 15px rgba(0,0,0,0.05);
            overflow-y: hidden !important;
        }}

        /* ── Remove sidebar scroll ── */
        section[data-testid="stSidebar"] > div {{
            overflow-y: auto !important;
            overflow-x: hidden !important;
        }}

        /* ── Remove right arrow on radio ── */
        .stRadio > div {{
            display: none !important;
        }}

        /* ── Remove press enter text ── */
        .stTextInput > div > div > div > small,
        .stTextInput ~ small,
        div[data-baseweb="input"] ~ div > small {{
            display: none !important;
        }}
        input + div[style*="font-size"] {{
            display: none !important;
        }}

        /* ── All Text Colors ── */
        h1, h2, h3, h4, h5, h6 {{
            color: {t['text']} !important;
        }}
        p, span, label, div {{
            color: {t['text']};
        }}
        .stMarkdown p {{
            color: {t['text']} !important;
        }}

        /* ── Input Fields ── */
        .stTextInput > div > div > input {{
            background: {t['input_bg']} !important;
            color: {t['text']} !important;
            border: 1px solid {t['border']} !important;
            border-radius: 10px !important;
        }}
        .stTextInput > div > div > input:focus {{
            border-color: {t['primary']} !important;
            box-shadow: 0 0 0 2px {t['primary']}33 !important;
        }}
        .stSelectbox > div > div {{
            background: {t['input_bg']} !important;
            color: {t['text']} !important;
            border: 1px solid {t['border']} !important;
            border-radius: 10px !important;
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
            box-shadow: 0 8px 30px rgba(0,0,0,0.15);
        }}

        /* ── Badges ── */
        .badge {{
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 11px;
            font-weight: 600;
            display: inline-block;
        }}
        .badge-red    {{ background:#ffe0e0; color:#c62828 !important; }}
        .badge-orange {{ background:#fff3e0; color:#e65100 !important; }}
        .badge-green  {{ background:#e0f2e9; color:#1b5e20 !important; }}
        .badge-gray   {{ background:#f0f0f0; color:#555 !important;    }}

        /* ── Item Cards ── */
        .item-card {{
            background: {t['card']};
            border-radius: 12px;
            padding: 14px 18px;
            margin-bottom: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.06);
            border-left: 5px solid #43e97b;
            transition: all 0.25s;
        }}
        .item-card:hover {{
            transform: translateX(5px);
            box-shadow: 0 6px 20px rgba(0,0,0,0.12);
            border-left-width: 6px;
        }}
        .item-card-red    {{ border-left-color: #f44336 !important; }}
        .item-card-orange {{ border-left-color: #ff9800 !important; }}
        .item-card b, .item-card small {{
            color: {t['text']} !important;
        }}

        /* ── Buttons ── */
        .stButton > button {{
            border-radius: 10px !important;
            font-weight: 600 !important;
            transition: all 0.2s !important;
            color: {t['text']} !important;
        }}
        .stButton > button:hover {{
            transform: translateY(-2px) !important;
            box-shadow: 0 5px 15px rgba(102,126,234,0.4) !important;
            background: linear-gradient(
                135deg,#667eea,#43e97b
            ) !important;
            color: white !important;
        }}

        /* ── Hero Banner ── */
        .hero-banner {{
            background: {t['hero']};
            padding: 30px;
            border-radius: 20px;
            margin-bottom: 24px;
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
            margin: 0;
        }}

        /* ── Chat Bubbles ── */
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

        /* ── Action Cards ── */
        .action-card {{
            background: {t['card']};
            border-radius: 16px;
            padding: 22px 16px;
            text-align: center;
            box-shadow: 0 4px 15px rgba(0,0,0,0.06);
            border: 1px solid {t['border']};
            transition: all 0.25s;
            cursor: pointer;
        }}
        .action-card:hover {{
            transform: translateY(-6px);
            box-shadow: 0 12px 30px rgba(102,126,234,0.2);
            border-color: {t['primary']};
        }}
        .action-card .action-icon {{
            font-size: 2.2rem;
            margin-bottom: 8px;
        }}
        .action-card .action-title {{
            font-size: 0.9rem;
            font-weight: 600;
            color: {t['text']} !important;
        }}
        .action-card .action-desc {{
            font-size: 0.72rem;
            color: {t['subtext']} !important;
            margin-top: 4px;
        }}

        /* ── Notification Bell ── */
        .notif-bell {{
            position: fixed;
            top: 16px;
            right: 20px;
            z-index: 9999;
            cursor: pointer;
        }}
        .notif-badge {{
            position: absolute;
            top: -6px; right: -6px;
            background: #f44336;
            color: white !important;
            font-size: 10px;
            font-weight: 700;
            width: 18px; height: 18px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            border: 2px solid white;
            animation: pulse 1.5s infinite;
        }}
        @keyframes pulse {{
            0%, 100% {{ transform: scale(1); }}
            50%       {{ transform: scale(1.2); }}
        }}

        /* ── Notification Panel ── */
        .notif-panel {{
            position: fixed;
            top: 50px; right: 20px;
            width: 300px;
            background: {t['card']};
            border-radius: 16px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
            border: 1px solid {t['border']};
            z-index: 9998;
            padding: 16px;
            max-height: 400px;
            overflow-y: auto;
        }}
        .notif-item {{
            padding: 10px 12px;
            border-radius: 10px;
            margin-bottom: 8px;
            border-left: 3px solid #f44336;
            background: {'#16213e' if st.session_state.dark_mode
                         else '#fff5f5'};
        }}
        .notif-item-title {{
            font-size: 0.85rem;
            font-weight: 600;
            color: {t['text']} !important;
        }}
        .notif-item-date {{
            font-size: 0.72rem;
            color: {t['subtext']} !important;
            margin-top: 2px;
        }}

        /* ── Animations ── */
        @keyframes fadeInUp {{
            from {{ opacity:0; transform:translateY(20px); }}
            to   {{ opacity:1; transform:translateY(0);    }}
        }}
        .fade-in {{ animation: fadeInUp 0.5s ease forwards; }}

        /* ── Hide Streamlit UI ── */
        #MainMenu, footer, header {{ visibility: hidden; }}
        .block-container {{ padding-top: 1rem !important; }}

        /* ── Metric card text fix ── */
        .metric-num {{
            color: inherit !important;
        }}
    </style>
    """, unsafe_allow_html=True)

# ─────────────────────────────────────────
# NOTIFICATION BELL (top right)
# ─────────────────────────────────────────

def render_notification_bell():
    """Fixed position notification bell top right"""
    t = get_theme()
    expiring = get_expiring_items(7)
    critical = get_expiring_items(3)
    count    = len(expiring)

    if "show_notif" not in st.session_state:
        st.session_state.show_notif = False

    # Build notification items HTML
    notif_items_html = ""
    for item in expiring:
        _, days, _, _ = get_expiry_info(item['expiry_date'])
        if days < 0:
            label = f"EXPIRED {abs(days)} days ago!"
            color = "#f44336"
        elif days == 0:
            label = "Expires TODAY!"
            color = "#f44336"
        elif days <= 3:
            label = f"Expires in {days} day(s)!"
            color = "#ff9800"
        else:
            label = f"Expires on {item['expiry_date']}"
            color = "#ff9800"

        notif_items_html += f"""
            <div style='padding:10px 12px; border-radius:10px;
                        margin-bottom:8px;
                        border-left:3px solid {color};
                        background:{'#16213e' if st.session_state.dark_mode
                                    else '#fff5f5'};'>
                <div style='font-size:0.85rem; font-weight:600;
                            color:{t["text"]};'>
                    {item['name']}
                </div>
                <div style='font-size:0.72rem;
                            color:{t["subtext"]};
                            margin-top:2px;'>
                    📅 {label}
                </div>
            </div>
        """

    empty_html = "" if expiring else f"""
        <div style='text-align:center; padding:20px;
                    color:{t["subtext"]}; font-size:0.85rem;'>
            ✅ No expiry alerts!
        </div>
    """

    components.html(f"""
        <style>
            * {{ font-family:'Poppins',sans-serif;
                 box-sizing:border-box; }}
            .bell-wrap {{
                position: fixed;
                top: 12px; right: 20px;
                z-index: 99999;
            }}
            .bell-btn {{
                background: {'#1a1a2e' if st.session_state.dark_mode
                             else 'white'};
                border: 1px solid {'#2a2a4a' if st.session_state.dark_mode
                                   else '#e0e8f0'};
                border-radius: 50%;
                width: 42px; height: 42px;
                display: flex;
                align-items: center;
                justify-content: center;
                cursor: pointer;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                font-size: 1.2rem;
                position: relative;
                transition: all 0.2s;
            }}
            .bell-btn:hover {{
                transform: scale(1.1);
                box-shadow: 0 4px 20px rgba(0,0,0,0.15);
            }}
            .badge {{
                position: absolute;
                top: -4px; right: -4px;
                background: #f44336;
                color: white;
                font-size: 9px;
                font-weight: 700;
                min-width: 16px; height: 16px;
                border-radius: 8px;
                display: flex;
                align-items: center;
                justify-content: center;
                border: 2px solid white;
                padding: 0 3px;
                animation: pulse 1.5s infinite;
            }}
            @keyframes pulse {{
                0%,100% {{ transform:scale(1); }}
                50%      {{ transform:scale(1.3); }}
            }}
            .panel {{
                display: none;
                position: fixed;
                top: 60px; right: 20px;
                width: 280px;
                background: {'#1a1a2e' if st.session_state.dark_mode
                             else 'white'};
                border-radius: 16px;
                box-shadow: 0 10px 40px rgba(0,0,0,0.2);
                border: 1px solid {'#2a2a4a' if st.session_state.dark_mode
                                   else '#e0e8f0'};
                padding: 16px;
                max-height: 380px;
                overflow-y: auto;
                z-index: 99998;
                animation: fadeIn 0.2s ease;
            }}
            .panel.open {{ display: block; }}
            @keyframes fadeIn {{
                from {{ opacity:0; transform:translateY(-10px); }}
                to   {{ opacity:1; transform:translateY(0); }}
            }}
            .panel-title {{
                font-size: 0.9rem;
                font-weight: 700;
                color: {'#ffffff' if st.session_state.dark_mode
                        else '#1a1a2e'};
                margin-bottom: 12px;
                padding-bottom: 8px;
                border-bottom: 1px solid {'#2a2a4a' if st.session_state.dark_mode
                                          else '#e0e8f0'};
            }}
        </style>

        <div class="bell-wrap">
            <div class="bell-btn" onclick="togglePanel()"
                 title="Expiry Notifications">
                🔔
                {'<div class="badge">' + str(count) + '</div>'
                 if count > 0 else ''}
            </div>
            <div class="panel" id="notif-panel">
                <div class="panel-title">
                    🔔 Expiry Alerts ({count})
                </div>
                {notif_items_html}
                {empty_html}
            </div>
        </div>

        <script>
            function togglePanel() {{
                const panel = document.getElementById('notif-panel');
                panel.classList.toggle('open');
            }}
            // Close when clicking outside
            document.addEventListener('click', function(e) {{
                const wrap = document.querySelector('.bell-wrap');
                if (!wrap.contains(e.target)) {{
                    document.getElementById('notif-panel')
                        .classList.remove('open');
                }}
            }});
        </script>
    """, height=60)

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
                colors:['#667eea','#43e97b','#f093fb',
                        '#4facfe','#fa709a']
            });
        </script>
    """, height=0)

# ─────────────────────────────────────────
# LOGIN PAGE — Lottie Animation
# ─────────────────────────────────────────

def login_page():
    inject_css()
    t = get_theme()

    # ── Lottie Animation Header ──
    components.html("""
        <script src="https://cdnjs.cloudflare.com/ajax/libs/lottie-web/5.12.2/lottie.min.js"></script>
        <style>
            body {{ margin:0; overflow:hidden; }}
            #lottie-bg {{
                width: 100%;
                height: 200px;
                background: linear-gradient(
                    135deg, #2e7d32, #66bb6a
                );
                border-radius: 0 0 30px 30px;
                display: flex;
                align-items: center;
                justify-content: center;
                position: relative;
                overflow: hidden;
            }}
            .food-items {{
                display: flex;
                gap: 20px;
                font-size: 3rem;
                animation: float 3s ease-in-out infinite;
            }}
            .food-items span {{
                animation: bounce 1s ease-in-out infinite;
            }}
            .food-items span:nth-child(2) {{
                animation-delay: 0.2s;
            }}
            .food-items span:nth-child(3) {{
                animation-delay: 0.4s;
            }}
            .food-items span:nth-child(4) {{
                animation-delay: 0.6s;
            }}
            .food-items span:nth-child(5) {{
                animation-delay: 0.8s;
            }}
            @keyframes bounce {{
                0%, 100% {{ transform: translateY(0); }}
                50%       {{ transform: translateY(-20px); }}
            }}
            .tagline {{
                position: absolute;
                bottom: 20px;
                color: white;
                font-family: 'Poppins', sans-serif;
                font-size: 1rem;
                opacity: 0.9;
                letter-spacing: 1px;
            }}
            /* Floating particles */
            .particle {{
                position: absolute;
                border-radius: 50%;
                opacity: 0.3;
                animation: floatUp 4s ease-in-out infinite;
            }}
            @keyframes floatUp {{
                0%   {{ transform: translateY(100px); opacity:0; }}
                50%  {{ opacity: 0.4; }}
                100% {{ transform: translateY(-100px); opacity:0; }}
            }}
        </style>

        <div id="lottie-bg">
            <!-- Floating particles -->
            <div class="particle" style="
                width:20px; height:20px;
                background:#ffffff;
                left:10%; animation-delay:0s;
            "></div>
            <div class="particle" style="
                width:12px; height:12px;
                background:#43e97b;
                left:30%; animation-delay:1s;
            "></div>
            <div class="particle" style="
                width:16px; height:16px;
                background:#ffffff;
                left:60%; animation-delay:2s;
            "></div>
            <div class="particle" style="
                width:10px; height:10px;
                background:#43e97b;
                left:80%; animation-delay:0.5s;
            "></div>

            <!-- Bouncing food emojis -->
            <div>
                <div class="food-items">
                    <span>🥗</span>
                    <span>🍎</span>
                    <span>🥛</span>
                    <span>🥦</span>
                    <span>🍋</span>
                </div>
                <div class="tagline"
                     style="text-align:center; width:100%;">
                    ✨ Reduce waste. Eat smart. Live fresh.
                </div>
            </div>
        </div>
    """, height=210)

    # ── Login / Register Form ──
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.markdown(f"""
            <div style='text-align:center; padding:16px 0 8px;'>
                <h1 style='font-size:2.2rem; font-weight:700;
                           background:linear-gradient(
                               135deg,#667eea,#43e97b
                           );
                           -webkit-background-clip:text;
                           -webkit-text-fill-color:transparent;
                           margin:0;'>
                    FreshMind 🥗
                </h1>
                <p style='color:{t["subtext"]}; font-size:0.9rem;
                           margin:4px 0 16px;'>
                    Your AI-Powered Smart Pantry
                </p>
            </div>
        """, unsafe_allow_html=True)

        # Toggle between login and register
        tab1, tab2 = st.tabs(["🔐 Login", "📝 Register"])

        # ── LOGIN TAB ──
        with tab1:
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
                c1, c2 = st.columns(2)
                with c1:
                    submitted = st.form_submit_button(
                        "🔐 Login",
                        use_container_width=True
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
                    if not username or not password:
                        st.error("❌ Fill in all fields!")
                    else:
                        user = login_user(username, password)
                        if user:
                            st.session_state.logged_in  = True
                            st.session_state.username   = username
                            st.session_state.user_data  = user
                            st.rerun()
                        else:
                            st.error("❌ Wrong username or password!")

            st.markdown(f"""
                <p style='text-align:center;
                          color:{t["subtext"]};
                          font-size:0.78rem; margin-top:8px;'>
                    Demo: <b>admin</b> / <b>admin123</b>
                </p>
            """, unsafe_allow_html=True)

        # ── REGISTER TAB ──
        with tab2:
            with st.form("register_form"):
                r_name = st.text_input(
                    "👤 Full Name *",
                    placeholder="Your full name"
                )
                r_username = st.text_input(
                    "🆔 Username *",
                    placeholder="Choose a username"
                )
                r_email = st.text_input(
                    "📧 Email",
                    placeholder="your@email.com"
                )
                r_pass = st.text_input(
                    "🔒 Password *",
                    type="password",
                    placeholder="Min 6 characters"
                )
                r_pass2 = st.text_input(
                    "🔒 Confirm Password *",
                    type="password",
                    placeholder="Repeat password"
                )

                reg_submitted = st.form_submit_button(
                    "📝 Create Account",
                    use_container_width=True
                )

                if reg_submitted:
                    if not r_name or not r_username or not r_pass:
                        st.error("❌ Fill in all required fields!")
                    elif len(r_pass) < 6:
                        st.error(
                            "❌ Password must be at least 6 chars!"
                        )
                    elif r_pass != r_pass2:
                        st.error("❌ Passwords don't match!")
                    else:
                        success, msg = register_user(
                            r_username, r_pass,
                            r_email, r_name
                        )
                        if success:
                            st.success(msg)
                            st.info("Now login with your credentials!")
                        else:
                            st.error(msg)

# ─────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────

def render_sidebar():
    t = get_theme()
    with st.sidebar:
        # Logo
        st.markdown(f"""
            <div style='text-align:center;
                        padding:16px 0 16px;'>
                <div style='font-size:2.8rem;'>🥗</div>
                <h2 style='margin:4px 0; color:{t["primary"]};
                           font-size:1.3rem;'>FreshMind</h2>
                <p style='color:{t["subtext"]};
                           font-size:0.72rem; margin:0;'>
                    Smart Pantry Assistant
                </p>
            </div>
        """, unsafe_allow_html=True)

        # User card
        user = st.session_state.user_data
        full_name = user.get("full_name", "") or \
                    st.session_state.username
        st.markdown(f"""
            <div style='background:{t["card2"]};
                        border:1px solid {t["border"]};
                        border-radius:12px;
                        padding:10px 14px;
                        margin-bottom:14px;'>
                <b style='color:{t["text"]};
                           font-size:0.9rem;'>
                    👤 {full_name}
                </b><br>
                <small style='color:{t["subtext"]};'>
                    @{st.session_state.username} ● Online
                </small>
            </div>
        """, unsafe_allow_html=True)

        # Nav label
        st.markdown(f"""
            <p style='color:{t["subtext"]};
                      font-size:0.68rem;
                      margin:0 0 6px 4px;
                      font-weight:600;
                      text-transform:uppercase;
                      letter-spacing:1px;'>
                Navigation
            </p>
        """, unsafe_allow_html=True)

        # Nav buttons
        pages = [
            ("🏠", "Home",       "🏠 Home"),
            ("📦", "Pantry",     "📦 My Pantry"),
            ("➕", "Add Item",   "➕ Add Item"),
            ("🤖", "Recipes",    "🤖 AI Recipes"),
            ("📊", "Dashboard",  "📊 Dashboard"),
            ("👨‍👩‍👧", "Family",   "👨‍👩‍👧 Family"),
            ("⚙️", "Settings",  "⚙️ Settings"),
        ]

        for icon, label, key in pages:
            is_active = st.session_state.current_page == key
            btn_label = f"{icon}  {label}"

            # Style active button differently
            if is_active:
                st.markdown(f"""
                    <div style='
                        background:linear-gradient(
                            135deg,#667eea,#43e97b
                        );
                        color:white;
                        padding:11px 14px;
                        border-radius:12px;
                        font-size:0.9rem;
                        font-weight:600;
                        margin-bottom:5px;
                        box-shadow:0 4px 15px
                            rgba(102,126,234,0.35);
                    '>
                        {icon} &nbsp; {label}
                    </div>
                """, unsafe_allow_html=True)
                # Hidden button to maintain click functionality
                if st.button(
                    btn_label,
                    key=f"nav_{key}",
                    use_container_width=True
                ):
                    st.session_state.current_page = key
                    st.rerun()
            else:
                if st.button(
                    btn_label,
                    key=f"nav_{key}",
                    use_container_width=True
                ):
                    st.session_state.current_page = key
                    st.rerun()

        st.markdown("---")

        # Utility buttons
        c1, c2 = st.columns(2)
        with c1:
            if st.button(
                "🌙" if not st.session_state.dark_mode
                else "☀️",
                use_container_width=True,
                help="Toggle Theme"
            ):
                st.session_state.dark_mode = \
                    not st.session_state.dark_mode
                st.rerun()
        with c2:
            if st.button(
                "📷", use_container_width=True,
                help="Scan Barcode"
            ):
                st.session_state.current_page = "➕ Add Item"
                st.session_state.show_scanner = True
                st.rerun()

        st.markdown("")
        if st.button("🚪 Logout", use_container_width=True):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

        st.markdown(f"""
            <p style='text-align:center;
                      color:{t["subtext"]};
                      font-size:0.65rem;
                      margin-top:16px;'>
                Built with ❤️ Python & Streamlit
            </p>
        """, unsafe_allow_html=True)

    return st.session_state.current_page

# ─────────────────────────────────────────
# PAGE — HOME
# ─────────────────────────────────────────

def home_page():
    t = get_theme()

    user = st.session_state.user_data
    full_name = user.get("full_name", "") or \
                st.session_state.username

    st.markdown(f"""
        <div class='hero-banner fade-in'>
            <h1 style='font-size:1.8rem;'>
                👋 Hello, {full_name}!
            </h1>
            <p style='font-size:1rem; opacity:0.85;
                      margin-top:6px;'>
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
        <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700&display=swap"
              rel="stylesheet">
        <style>
            * {{ font-family:'Poppins',sans-serif;
                 box-sizing:border-box; }}
            .grid {{
                display:grid;
                grid-template-columns:repeat(4,1fr);
                gap:14px; padding:4px 0 12px;
            }}
            .card {{
                background:{'#1a1a2e' if st.session_state.dark_mode
                            else 'white'};
                border-radius:14px; padding:20px;
                text-align:center;
                box-shadow:0 4px 16px rgba(0,0,0,0.08);
                transition:transform 0.2s;
            }}
            .card:hover {{ transform:translateY(-5px); }}
            .icon  {{ font-size:1.8rem; margin-bottom:6px; }}
            .num   {{
                font-size:2rem; font-weight:700; margin:4px 0;
            }}
            .lbl   {{
                font-size:0.72rem;
                color:{'#a0a0b0' if st.session_state.dark_mode
                       else '#888'};
                margin-top:2px;
            }}
        </style>
        <div class="grid">
            <div class="card">
                <div class="icon">📦</div>
                <div class="num" style="color:#667eea"
                     id="c1">0</div>
                <div class="lbl">Total Items</div>
            </div>
            <div class="card">
                <div class="icon">⚠️</div>
                <div class="num" style="color:#fa709a"
                     id="c2">0</div>
                <div class="lbl">Expiring This Week</div>
            </div>
            <div class="card">
                <div class="icon">✅</div>
                <div class="num" style="color:#43e97b"
                     id="c3">0</div>
                <div class="lbl">Items Saved</div>
            </div>
            <div class="card">
                <div class="icon">🗑️</div>
                <div class="num" style="color:#f44336"
                     id="c4">0</div>
                <div class="lbl">Items Wasted</div>
            </div>
        </div>
        <script>
            function countUp(id, target, duration=1500) {{
                const el = document.getElementById(id);
                if(!el || target===0) {{
                    if(el) el.textContent = 0;
                    return;
                }}
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
    """, height=145)

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
            f"this week!"
        )
    else:
        st.success("✅ Everything is fresh! No urgent alerts.")

    st.markdown("---")

    # ── Cooking Tips Slider (5s) ──
    st.markdown(f"""
        <h3 style='color:{t["text"]}; margin-bottom:8px;'>
            🍳 Cooking Tips
        </h3>
    """, unsafe_allow_html=True)

    # Daily Pantry Tips button (Groq powered)
    if st.button(
        "✨ Get AI Tips for My Pantry Today",
        use_container_width=False
    ):
        with st.spinner("🤖 Getting personalized tips..."):
            try:
                from groq import Groq
                from dotenv import load_dotenv
                import os
                load_dotenv()
                client = Groq(
                    api_key=os.getenv("GROQ_API_KEY")
                )
                items_text = ", ".join(
                    [i['name'] for i in all_items[:10]]
                ) if all_items else "empty pantry"

                resp = client.chat.completions.create(
                    model="llama-3.1-8b-instant",
                    max_tokens=300,
                    messages=[{
                        "role": "user",
                        "content": f"""Give 3 quick cooking tips 
                        for these pantry items: {items_text}.
                        Keep each tip under 2 sentences.
                        Format: emoji + tip text"""
                    }]
                )
                tips_text = resp.choices[0].message.content
                st.info(f"💡 **AI Tips for Your Pantry:**\n\n"
                        f"{tips_text}")
            except Exception as e:
                st.error(f"❌ Could not get tips: {e}")

    # Auto sliding tips (5s interval)
    components.html(f"""
        <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600&display=swap"
              rel="stylesheet">
        <style>
            * {{ font-family:'Poppins',sans-serif;
                 box-sizing:border-box; }}
            .wrap {{
                background:{'#1a1a2e' if st.session_state.dark_mode
                            else 'white'};
                border-radius:14px; padding:20px 24px;
                box-shadow:0 4px 16px rgba(0,0,0,0.08);
                border:1px solid {'#2a2a4a' if st.session_state.dark_mode
                                  else '#e0e8f0'};
            }}
            .tip {{
                display:none;
                animation:slide 0.5s ease;
            }}
            .tip.active {{ display:block; }}
            @keyframes slide {{
                from {{ opacity:0; transform:translateX(20px); }}
                to   {{ opacity:1; transform:translateX(0); }}
            }}
            .tip-icon {{ font-size:1.8rem; margin-bottom:6px; }}
            .tip-title {{
                font-size:0.95rem; font-weight:600;
                color:{'#fff' if st.session_state.dark_mode
                       else '#1a1a2e'};
                margin-bottom:4px;
            }}
            .tip-text {{
                font-size:0.82rem; line-height:1.6;
                color:{'#a0a0b0' if st.session_state.dark_mode
                       else '#555'};
            }}
            .controls {{
                display:flex;
                justify-content:space-between;
                align-items:center;
                margin-top:12px;
            }}
            .dots {{
                display:flex; gap:5px;
            }}
            .dot {{
                width:7px; height:7px;
                border-radius:50%;
                background:{'#2a2a4a' if st.session_state.dark_mode
                            else '#ddd'};
                cursor:pointer; border:none;
                transition:all 0.3s;
            }}
            .dot.active {{
                background:#667eea; width:18px;
                border-radius:4px;
            }}
            .arrow {{
                background:{'#2a2a4a' if st.session_state.dark_mode
                            else '#f0f4f8'};
                border:none; border-radius:8px;
                padding:5px 12px; cursor:pointer;
                color:{'#fff' if st.session_state.dark_mode
                       else '#333'};
                font-size:0.85rem; transition:all 0.2s;
            }}
            .arrow:hover {{
                background:#667eea; color:white;
            }}
            .progress {{
                height:3px; background:#667eea;
                border-radius:2px; margin-top:10px;
                transition:width 0.1s linear;
            }}
        </style>
        <div class="wrap">
            <div id="tc"></div>
            <div class="progress" id="prog"></div>
            <div class="controls">
                <button class="arrow" onclick="prev()">← Prev</button>
                <div class="dots" id="dots"></div>
                <button class="arrow" onclick="next()">Next →</button>
            </div>
        </div>
        <script>
            const tips = [
                {{icon:"🥦",title:"Store Vegetables Right",
                  text:"Wrap leafy greens in damp paper towels. They stay fresh 2x longer in the fridge!"}},
                {{icon:"🧅",title:"Onion & Potato Rule",
                  text:"Never store onions and potatoes together — onions release gases that sprout potatoes!"}},
                {{icon:"🍋",title:"Citrus Juice Hack",
                  text:"Microwave lemons for 15 seconds before squeezing to get 2x more juice!"}},
                {{icon:"🥛",title:"Milk Storage Tip",
                  text:"Store milk on the middle shelf, not the door — it's cooler and lasts longer!"}},
                {{icon:"🍌",title:"Banana Trick",
                  text:"Wrap banana stems in plastic wrap to slow ripening. Works like magic!"}},
                {{icon:"🧄",title:"Garlic Freshness",
                  text:"Store garlic at room temperature in a mesh bag. Lasts up to 6 months!"}},
                {{icon:"🍞",title:"Bread Hack",
                  text:"Freeze bread you won't use in 3 days. Toast straight from freezer — tastes fresh!"}},
                {{icon:"🥚",title:"Egg Test",
                  text:"Drop an egg in water — sinks = fresh, floats = bad. Never eat a floating egg!"}},
                {{icon:"🌿",title:"Fresh Herbs",
                  text:"Treat herbs like flowers — trim stems and store in a glass of water in the fridge!"}},
                {{icon:"🍎",title:"Apple Storage",
                  text:"Apples release ethylene gas. Store separately or they'll ripen your other produce!"}},
            ];
            let cur=0, progW=0, progTimer, autoTimer;
            const INTERVAL = 5000; // ← 5 seconds!
            const tc   = document.getElementById('tc');
            const dots = document.getElementById('dots');
            const prog = document.getElementById('prog');

            tips.forEach((t,i) => {{
                const d = document.createElement('div');
                d.className = 'tip'+(i===0?' active':'');
                d.id = 'tip-'+i;
                d.innerHTML = `
                    <div class="tip-icon">${{t.icon}}</div>
                    <div class="tip-title">${{t.title}}</div>
                    <div class="tip-text">${{t.text}}</div>
                `;
                tc.appendChild(d);

                const dot = document.createElement('button');
                dot.className='dot'+(i===0?' active':'');
                dot.id='dot-'+i;
                dot.onclick=()=>goTo(i);
                dots.appendChild(dot);
            }});

            function goTo(n) {{
                document.getElementById('tip-'+cur)
                    .classList.remove('active');
                document.getElementById('dot-'+cur)
                    .classList.remove('active');
                cur = (n+tips.length)%tips.length;
                document.getElementById('tip-'+cur)
                    .classList.add('active');
                document.getElementById('dot-'+cur)
                    .classList.add('active');
                resetProg();
            }}
            function next() {{ goTo(cur+1); }}
            function prev() {{ goTo(cur-1); }}

            function resetProg() {{
                progW=0; prog.style.width='0%';
                clearInterval(progTimer);
                clearInterval(autoTimer);
                progTimer = setInterval(() => {{
                    progW += 100/(INTERVAL/100);
                    prog.style.width = progW+'%';
                    if(progW>=100) clearInterval(progTimer);
                }}, 100);
                autoTimer = setTimeout(()=>next(), INTERVAL);
            }}
            resetProg();
        </script>
    """, height=220)

    st.markdown("---")

    # ── Quick Actions ──
    st.markdown(f"""
        <h3 style='color:{t["text"]}; margin-bottom:14px;'>
            ⚡ Quick Actions
        </h3>
    """, unsafe_allow_html=True)

    actions = [
        ("➕", "Add Item",    "Add new item",    "➕ Add Item"),
        ("📦", "My Pantry",  "View items",      "📦 My Pantry"),
        ("🤖", "AI Recipes", "Smart recipes",   "🤖 AI Recipes"),
        ("📊", "Dashboard",  "View analytics",  "📊 Dashboard"),
    ]
    cols = st.columns(4)
    for col, (icon, title, desc, page_key) in \
            zip(cols, actions):
        with col:
            st.markdown(f"""
                <div class='action-card fade-in'>
                    <div class='action-icon'>{icon}</div>
                    <div class='action-title'>{title}</div>
                    <div class='action-desc'>{desc}</div>
                </div>
            """, unsafe_allow_html=True)
            if st.button(
                f"→ {title}",
                key=f"home_{page_key}",
                use_container_width=True
            ):
                st.session_state.current_page = page_key
                st.rerun()

    # ── Recent Activity ──
    st.markdown("---")
    st.markdown(f"""
        <h3 style='color:{t["text"]}; margin-bottom:10px;'>
            🕐 Recent Activity
        </h3>
    """, unsafe_allow_html=True)

    history = get_usage_history()
    if not history:
        st.info("No activity yet!")
    else:
        for h in list(history)[:5]:
            icon   = "✅" if not h['was_wasted'] else "🗑️"
            color  = "#43e97b" if not h['was_wasted'] else "#f44336"
            action = "Used" if not h['was_wasted'] else "Wasted"
            st.markdown(f"""
                <div style='background:{t["card"]};
                            border-radius:10px;
                            padding:10px 14px;
                            margin-bottom:6px;
                            border-left:4px solid {color};'>
                    <span style='font-size:1.1rem;'>{icon}</span>
                    <span style='color:{t["text"]};
                                 font-size:0.85rem;
                                 margin-left:8px;'>
                        <b>{h['item_name']}</b> — {action}
                        on {h['used_date']}
                    </span>
                </div>
            """, unsafe_allow_html=True)

# ─────────────────────────────────────────
# PAGE — PANTRY (unchanged from before)
# ─────────────────────────────────────────

def pantry_page():
    t = get_theme()
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
        st.info("🛒 Pantry is empty!")
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
                            item['id'], name=nn,
                            quantity=nq,
                            expiry_date=str(ne),
                            category=nc
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
            image_url = item['image_url'] \
                if 'image_url' in item.keys() \
                and item['image_url'] else None
            item_emoji = get_emoji(item['name'])

            img_col, info_col, btn_col = \
                st.columns([1, 5, 2])

            with img_col:
                if image_url:
                    st.markdown(f"""
                        <div style='width:65px;height:65px;
                            border-radius:10px;overflow:hidden;
                            box-shadow:0 2px 8px rgba(0,0,0,0.1);'>
                            <img src="{image_url}"
                                 style='width:100%;height:100%;
                                        object-fit:cover;'/>
                        </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                        <div style='width:65px;height:65px;
                            background:linear-gradient(
                                135deg,#667eea22,#43e97b22
                            );
                            border-radius:10px;
                            display:flex;align-items:center;
                            justify-content:center;
                            font-size:2rem;
                            border:1px solid {t["border"]};'>
                            {item_emoji}
                        </div>
                    """, unsafe_allow_html=True)

            with info_col:
                st.markdown(f"""
                    <div class='item-card {card_cls}'>
                        <b style='font-size:0.95rem;'>
                            {emoji} {item['name']}
                        </b>
                        <span class='badge badge-gray'
                              style='margin-left:8px;'>
                            {item['category']}
                        </span>
                        <span class='badge {badge}'
                              style='margin-left:4px;'>
                            {"EXPIRED!" if days_left < 0
                              else f"{days_left}d left"}
                        </span><br>
                        <small>
                            📏 {item['quantity']} &nbsp;|&nbsp;
                            📅 {item['expiry_date']}
                        </small>
                    </div>
                """, unsafe_allow_html=True)

            with btn_col:
                b1, b2, b3 = st.columns(3)
                with b1:
                    if st.button(
                        "✅", key=f"use_{item['id']}",
                        help="Mark as used"
                    ):
                        log_usage(item['name'], was_wasted=False)
                        delete_item(item['id'])
                        st.toast(f"✅ {item['name']} used!")
                        st.rerun()
                with b2:
                    if st.button(
                        "✏️", key=f"edit_{item['id']}",
                        help="Edit"
                    ):
                        st.session_state.edit_item_id = item['id']
                        st.rerun()
                with b3:
                    if st.button(
                        "🗑️", key=f"del_{item['id']}",
                        help="Delete"
                    ):
                        log_usage(item['name'], was_wasted=True)
                        delete_item(item['id'])
                        st.toast(f"🗑️ {item['name']} removed!")
                        st.rerun()

            st.markdown(
                "<div style='margin-bottom:6px;'></div>",
                unsafe_allow_html=True
            )

# ─────────────────────────────────────────
# PAGE — ADD ITEM (with Barcode Scanner)
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

    # ── Barcode Scanner ──
    with st.expander("📷 Scan Barcode (Optional)", expanded=
                     st.session_state.get("show_scanner", False)):
        st.info(
            "📷 Upload a barcode image to auto-fill item details!"
        )
        uploaded = st.file_uploader(
            "Upload barcode image",
            type=["png","jpg","jpeg"],
            key="barcode_upload"
        )
        if uploaded:
            try:
                from PIL import Image
                from pyzbar.pyzbar import decode
                import numpy as np

                img  = Image.open(uploaded)
                st.image(img, width=300, caption="Uploaded image")
                codes = decode(img)

                if codes:
                    barcode_data = codes[0].data.decode("utf-8")
                    st.success(f"✅ Barcode found: `{barcode_data}`")

                    # Try to fetch product info
                    with st.spinner("🔍 Looking up product..."):
                        try:
                            resp = requests.get(
                                f"https://world.openfoodfacts.org"
                                f"/api/v0/product/{barcode_data}.json",
                                timeout=5
                            )
                            data = resp.json()
                            if data.get("status") == 1:
                                prod = data["product"]
                                p_name = prod.get(
                                    "product_name", ""
                                )
                                st.session_state.scan_result = {
                                    "name": p_name,
                                    "barcode": barcode_data
                                }
                                st.success(
                                    f"🎉 Found: **{p_name}**"
                                )
                            else:
                                st.warning(
                                    "⚠️ Product not found in "
                                    "database. Enter details manually."
                                )
                        except Exception:
                            st.warning(
                                "⚠️ Could not fetch product info."
                            )
                else:
                    st.warning(
                        "⚠️ No barcode detected. "
                        "Try a clearer image!"
                    )
            except ImportError:
                st.error(
                    "❌ Install pyzbar: "
                    "`pip install pyzbar pillow`"
                )

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        # Pre-fill from scan result
        scan = st.session_state.get("scan_result") or {}

        st.markdown("#### 🔍 Item Preview")
        name = st.text_input(
            "Item Name *",
            value=scan.get("name", ""),
            placeholder="e.g. Milk, Eggs, Spinach",
            key="item_name_input"
        )

        if name and len(name) >= 3:
            with st.spinner("🔍 Fetching image..."):
                image_url, emoji_icon = get_food_image(name)

            p1, p2 = st.columns([1, 2])
            with p1:
                if image_url:
                    st.image(image_url, width=130,
                             caption=f"{emoji_icon} {name}")
                else:
                    st.markdown(f"""
                        <div style='width:130px;height:130px;
                            background:{t["card2"]};
                            border-radius:12px;
                            display:flex;align-items:center;
                            justify-content:center;
                            font-size:3.5rem;
                            border:2px dashed {t["border"]};'>
                            {emoji_icon}
                        </div>
                    """, unsafe_allow_html=True)
            with p2:
                if image_url:
                    st.success(f"✅ Image found for **{name}**!")
                else:
                    st.info(f"{emoji_icon} Using emoji preview")
        else:
            st.markdown(f"""
                <div style='width:100%;height:100px;
                    background:{t["card2"]};
                    border-radius:12px;
                    display:flex;align-items:center;
                    justify-content:center;
                    border:2px dashed {t["border"]};
                    color:{t["subtext"]};
                    font-size:0.85rem;
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
                    st.session_state.scan_result = None
                    st.session_state.show_scanner = False
                    st.success(f"✅ **{item_name}** added!")
                    confetti()

# ─────────────────────────────────────────
# PAGE — AI RECIPES
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
        st.info("🛒 Add some items first!")
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
                "role": "assistant", "content": result
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
            "role": "user", "content": user_input
        })
        with st.spinner("🤖 Thinking..."):
            response, st.session_state.chat_history = \
                chat_with_ai(
                    user_input,
                    st.session_state.chat_history
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
# PAGE — FAMILY MODE
# ─────────────────────────────────────────

def family_page():
    t = get_theme()
    st.markdown("""
        <div class='hero-banner fade-in'
             style='padding:20px 25px;'>
            <h2 style='margin:0;'>👨‍👩‍👧 Family Mode</h2>
            <p style='margin:4px 0 0; opacity:0.85;'>
                Share pantry with your family
            </p>
        </div>
    """, unsafe_allow_html=True)

    user = st.session_state.user_data
    family_id = user.get("family_id")

    tab1, tab2, tab3 = st.tabs([
        "👥 My Family",
        "➕ Create Family",
        "🔗 Join Family"
    ])

    # ── My Family Tab ──
    with tab1:
        if not family_id:
            st.info(
                "You're not in a family yet! "
                "Create or join one below."
            )
        else:
            members = get_family_members(family_id)
            st.markdown(
                f"### 👨‍👩‍👧 Family ID: `{family_id}`"
            )
            st.markdown(
                f"**{len(members)} member(s)** in your family"
            )
            st.markdown("---")
            for m in members:
                last = m.get('last_login', 'Never') or 'Never'
                role_badge = "👑" if "admin" in \
                             (m.get('role') or '') else "👤"
                st.markdown(f"""
                    <div class='fm-card' style='padding:14px;'>
                        <b style='color:{t["text"]};'>
                            {role_badge} {m['full_name'] or
                                          m['username']}
                        </b>
                        <span style='color:{t["subtext"]};
                                     font-size:0.8rem;
                                     margin-left:8px;'>
                            @{m['username']}
                        </span><br>
                        <small style='color:{t["subtext"]};'>
                            Last active: {last}
                        </small>
                    </div>
                """, unsafe_allow_html=True)

    # ── Create Family Tab ──
    with tab2:
        with st.form("create_family_form"):
            family_name = st.text_input(
                "Family Name *",
                placeholder="e.g. The Sharma Family"
            )
            submitted = st.form_submit_button(
                "🏠 Create Family",
                use_container_width=True
            )
            if submitted:
                if not family_name:
                    st.error("❌ Enter a family name!")
                elif family_id:
                    st.warning(
                        "⚠️ You're already in a family!"
                    )
                else:
                    fid = create_family(
                        family_name, user['id']
                    )
                    st.success(
                        f"✅ Family created! "
                        f"Share ID **{fid}** with family members"
                    )
                    st.balloons()

    # ── Join Family Tab ──
    with tab3:
        with st.form("join_family_form"):
            fid_input = st.number_input(
                "Family ID *",
                min_value=1, step=1
            )
            submitted = st.form_submit_button(
                "🔗 Join Family",
                use_container_width=True
            )
            if submitted:
                if family_id:
                    st.warning(
                        "⚠️ You're already in a family!"
                    )
                else:
                    ok, msg = join_family(
                        user['id'], int(fid_input)
                    )
                    if ok:
                        st.success(msg)
                    else:
                        st.error(msg)

# ─────────────────────────────────────────
# PAGE — SETTINGS
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
                <h3>👤 Profile Info</h3>
                <p><b>Username:</b>
                   @{user.get('username','')}</p>
                <p><b>Full Name:</b>
                   {user.get('full_name','') or 'Not set'}</p>
                <p><b>Email:</b>
                   {user.get('email','') or 'Not set'}</p>
                <p><b>Role:</b>
                   {user.get('role','member')}</p>
                <p><b>Member since:</b>
                   {user.get('created_at','').split(' ')[0]}</p>
            </div>
        """, unsafe_allow_html=True)

        # All users (admin only)
        if user.get('role') == 'admin':
            st.markdown("### 👥 All Users (Admin View)")
            all_users = get_all_users()
            for u in all_users:
                st.markdown(f"""
                    <div class='fm-card'
                         style='padding:12px 16px;'>
                        <b style='color:{t["text"]};'>
                            👤 {u['username']}
                        </b>
                        <span style='color:{t["subtext"]};
                                     font-size:0.8rem;
                                     margin-left:8px;'>
                            {u['full_name'] or ''} |
                            {u['role']}
                        </span>
                    </div>
                """, unsafe_allow_html=True)

    with tab2:
        with st.form("change_pass_form"):
            old_pass = st.text_input(
                "Current Password",
                type="password"
            )
            new_pass = st.text_input(
                "New Password",
                type="password"
            )
            confirm_pass = st.text_input(
                "Confirm New Password",
                type="password"
            )
            submitted = st.form_submit_button(
                "🔒 Update Password",
                use_container_width=True
            )
            if submitted:
                if new_pass != confirm_pass:
                    st.error("❌ Passwords don't match!")
                elif len(new_pass) < 6:
                    st.error(
                        "❌ Password must be 6+ characters!"
                    )
                else:
                    ok, msg = update_password(
                        user['id'], old_pass, new_pass
                    )
                    if ok:
                        st.success(msg)
                    else:
                        st.error(msg)

# ─────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────

def main():
    inject_css()

    if not st.session_state.logged_in:
        login_page()
        return

    # Notification bell (fixed top right)
    render_notification_bell()

    page = render_sidebar()

    if   page == "🏠 Home":       home_page()
    elif page == "📦 My Pantry":  pantry_page()
    elif page == "➕ Add Item":   add_item_page()
    elif page == "🤖 AI Recipes": ai_recipes_page()
    elif page == "📊 Dashboard":  dashboard_page()
    elif page == "👨‍👩‍👧 Family":  family_page()
    elif page == "⚙️ Settings":  settings_page()

if __name__ == "__main__":
    main()
