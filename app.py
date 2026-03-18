import streamlit as st
import streamlit.components.v1 as components
from datetime import date, datetime
import requests
import os
import json
from database import (
    create_tables, add_item, get_all_items,
    get_expiring_items, delete_item, update_item,
    log_usage, get_usage_history
)
from ai_recipes import get_recipe_suggestions, chat_with_ai
from dashboard import render_dashboard
from auth import (
    create_auth_tables, login_user, register_user,
    get_all_users, update_password
)

st.set_page_config(
    page_title="FreshMind 🥗",
    page_icon="🥗",
    layout="wide",
    initial_sidebar_state="expanded"
)
create_tables()
create_auth_tables()

defaults = {
    "logged_in":    False,
    "username":     "",
    "user_data":    {},
    "dark_mode":    False,
    "chat_history": [],
    "edit_item_id": None,
    "current_page": "🏠 Home",
    "show_weather": False,
    "show_alerts":  False,
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

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
            "gradient":  "linear-gradient(135deg,#0f0f1a,#1a1a2e)",
            "hero":      "linear-gradient(135deg,#1b5e20,#2d6a4f)",
            "input_bg":  "#16213e",
            "input_text":"#ffffff",
            "sidebar":   "#1a1a2e",
            "nav_active":"linear-gradient(135deg,#667eea,#43e97b)",
        }
    else:
        return {
            "bg":        "#f0faf4",
            "card":      "#ffffff",
            "card2":     "#f8fffe",
            "text":      "#1a1a2e",
            "subtext":   "#666680",
            "border":    "#e0e8f0",
            "primary":   "#667eea",
            "success":   "#2e7d32",
            "gradient":  "linear-gradient(135deg,#f0faf4,#e8f5e9)",
            "hero":      "linear-gradient(135deg,#1b5e20,#2d6a4f)",
            "input_bg":  "#ffffff",
            "input_text":"#1a1a2e",
            "sidebar":   "#ffffff",
            "nav_active":"linear-gradient(135deg,#667eea,#43e97b)",
        }

FOOD_EMOJIS = {
    "Dairy":"🥛","Vegetables":"🥦","Fruits":"🍎",
    "Meat & Seafood":"🍗","Grains & Cereals":"🌾",
    "Snacks":"🍿","Beverages":"🥤","Condiments":"🧂","Other":"🛒"
}

DAILY_TIPS = [
    {"i":"🥦","t":"Store Vegetables Right","x":"Wrap leafy greens in damp paper towels. Stay fresh 2x longer!"},
    {"i":"🧅","t":"Onion & Potato Rule","x":"Never store together — onions release gases that sprout potatoes!"},
    {"i":"🍋","t":"Citrus Juice Hack","x":"Microwave lemons 15s before squeezing — 2x more juice!"},
    {"i":"🥛","t":"Milk Storage Tip","x":"Store milk on middle shelf, not the door — stays cooler!"},
    {"i":"🍌","t":"Banana Trick","x":"Wrap banana stems in plastic wrap to slow ripening!"},
    {"i":"🧄","t":"Garlic Freshness","x":"Store at room temp in a mesh bag. Lasts 6 months!"},
    {"i":"🍞","t":"Bread Hack","x":"Freeze bread you won't use in 3 days. Toast from freezer!"},
    {"i":"🥚","t":"Egg Test","x":"Sink=fresh, float=bad. Never eat a floating egg!"},
    {"i":"🌿","t":"Fresh Herbs","x":"Store in a glass of water in fridge like flowers!"},
    {"i":"🍎","t":"Apple Storage","x":"Apples release ethylene gas — store separately!"},
]

def get_weather():
    try:
        r = requests.get("https://wttr.in/Bengaluru?format=j1", timeout=5)
        d = r.json()["current_condition"][0]
        return {
            "temp": d["temp_C"], "feels": d["FeelsLikeC"],
            "humidity": d["humidity"],
            "desc": d["weatherDesc"][0]["value"],
            "wind": d["windspeedKmph"],
        }
    except:
        return {"temp":"31","feels":"34","humidity":"65",
                "desc":"Partly Cloudy","wind":"12"}

def get_greeting():
    h = datetime.now().hour
    if h < 12: return "Good Morning"
    if h < 17: return "Good Afternoon"
    return "Good Evening"

def get_expiry_info(expiry_str):
    today  = date.today()
    expiry = datetime.strptime(expiry_str, "%Y-%m-%d").date()
    days   = (expiry - today).days
    if days < 0:    return "⚫", days, "badge-red",    "item-card-red"
    elif days <= 3: return "🔴", days, "badge-red",    "item-card-red"
    elif days <= 7: return "🟠", days, "badge-orange", "item-card-orange"
    else:           return "🟢", days, "badge-green",  ""

def confetti():
    components.html("""
    <script src="https://cdn.jsdelivr.net/npm/canvas-confetti@1.6.0/dist/confetti.browser.min.js"></script>
    <script>confetti({particleCount:120,spread:80,origin:{y:0.6},
        colors:['#667eea','#43e97b','#f093fb','#4facfe','#fa709a']});</script>
    """, height=0)

def inject_css():
    t  = get_theme()
    dm = st.session_state.dark_mode
    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');
    * {{ font-family:'Poppins',sans-serif !important; box-sizing:border-box; }}
    .stApp {{ background:{t['gradient']} !important; }}
    section[data-testid="stSidebar"] {{
        background:{t['sidebar']} !important;
        border-right:1px solid {t['border']} !important;
        box-shadow:3px 0 20px rgba(0,0,0,0.06) !important;
        min-width:260px !important; width:260px !important;
    }}
    [data-testid="stSidebarCollapseButton"] {{ display:none !important; }}
    h1,h2,h3,h4,h5,h6 {{ color:{t['text']} !important; }}
    p,label,div,span {{ color:{t['text']}; }}
    .stMarkdown p {{ color:{t['text']} !important; }}
    small {{ color:{t['subtext']} !important; }}
    .stTextInput > div > div > input {{
        background:{t['input_bg']} !important;
        color:{t['input_text']} !important;
        border:1.5px solid {t['border']} !important;
        border-radius:10px !important;
    }}
    .stSelectbox > div > div {{
        background:{t['input_bg']} !important;
        color:{t['input_text']} !important;
        border:1.5px solid {t['border']} !important;
        border-radius:10px !important;
    }}
    .stButton > button {{
        border-radius:10px !important; font-weight:500 !important;
        color:{t['text']} !important;
        border:1px solid {t['border']} !important;
        background:{t['card']} !important;
        transition:all 0.2s !important;
    }}
    .stButton > button:hover {{
        background:linear-gradient(135deg,#667eea,#43e97b) !important;
        color:white !important; border-color:transparent !important;
        transform:translateY(-2px) !important;
        box-shadow:0 5px 15px rgba(102,126,234,0.3) !important;
    }}
    .fm-card {{
        background:{t['card']}; border-radius:16px; padding:20px;
        box-shadow:0 4px 20px rgba(0,0,0,0.08);
        border:1px solid {t['border']}; margin-bottom:12px;
        transition:transform 0.2s,box-shadow 0.2s;
    }}
    .fm-card:hover {{
        transform:translateY(-3px);
        box-shadow:0 8px 30px rgba(0,0,0,0.12);
    }}
    .hero-banner {{
        background:{t['hero']}; padding:16px 20px;
        border-radius:12px; margin-bottom:10px;
        position:relative; overflow:hidden;
    }}
    .hero-banner h1,.hero-banner h2,.hero-banner p {{
        color:white !important;
    }}
    .item-card {{
        background:{t['card']}; border-radius:12px;
        padding:14px 18px; margin-bottom:6px;
        box-shadow:0 2px 10px rgba(0,0,0,0.06);
        border-left:5px solid {t['success']};
        transition:all 0.2s;
    }}
    .item-card:hover {{ transform:translateX(4px); }}
    .item-card-red    {{ border-left-color:#f44336 !important; }}
    .item-card-orange {{ border-left-color:#ff9800 !important; }}
    .badge {{
        padding:3px 10px; border-radius:20px;
        font-size:11px; font-weight:600; display:inline-block;
    }}
    .badge-red    {{ background:#ffe0e0; color:#c62828 !important; }}
    .badge-orange {{ background:#fff3e0; color:#e65100 !important; }}
    .badge-green  {{ background:#e0f2e9; color:#1b5e20 !important; }}
    .badge-gray   {{
        background:{"#2a2a4a" if dm else "#f0f0f0"};
        color:{t['subtext']} !important;
    }}
    @keyframes fadeInUp {{
        from {{ opacity:0; transform:translateY(16px); }}
        to   {{ opacity:1; transform:translateY(0); }}
    }}
    .fade-in {{ animation:fadeInUp 0.35s ease forwards; }}
    .chat-user {{
        background:linear-gradient(135deg,#667eea,#764ba2);
        color:white !important; padding:12px 16px;
        border-radius:16px 16px 4px 16px;
        margin:8px 0 8px auto; max-width:75%; display:table;
    }}
    .chat-ai {{
        background:{t['card2']}; color:{t['text']} !important;
        padding:12px 16px; border-radius:16px 16px 16px 4px;
        margin:8px 0; max-width:75%;
        border:1px solid {t['border']}; display:table;
    }}
    [data-testid="stMetric"] {{
        background:{t['card']}; border-radius:12px; padding:10px 12px;
        border:1.5px solid {t['border']};
        transition:all 0.3s; cursor:pointer;
    }}
    [data-testid="stMetric"]:hover {{
        transform:translateY(-3px);
        box-shadow:0 8px 20px rgba(102,126,234,0.15);
        border-color:#667eea;
    }}
    .stTabs [data-baseweb="tab"] {{ color:{t['subtext']} !important; }}
    .stTabs [aria-selected="true"] {{ color:{t['primary']} !important; }}
    #MainMenu,footer,header {{ visibility:hidden; }}
    .block-container {{
        padding-top:0 !important;
        padding-left:0.5rem !important;
        padding-right:0.5rem !important;
        padding-bottom:0.5rem !important;
        max-width:100% !important;
    }}
    .stApp > div {{ padding-top:0 !important; }}
    div[data-testid="stAppViewContainer"] {{ padding-top:0 !important; }}
    div[data-testid="stVerticalBlock"] {{ gap:0 !important; padding-top:0 !important; }}
    .element-container {{ margin-bottom:0.2rem !important; }}
    hr {{ margin:6px 0 !important; }}
    section[data-testid="stSidebar"] > div {{
        padding-top:8px !important;
        padding-bottom:8px !important;
    }}
    div[data-testid="stForm"] {{
        background:{t['card']}; border-radius:16px;
        padding:14px; border:1px solid {t['border']};
    }}
    .topbar-info {{
        background:{t['card']};
        border:1px solid {t['border']};
        border-radius:12px;
        padding:12px 16px;
        margin-bottom:8px;
        animation:fadeInUp 0.3s ease;
    }}
    .icon-btn button {{
        background:{t['card']} !important;
        border:1px solid {t['border']} !important;
        box-shadow:none !important;
        padding:4px !important;
        font-size:1.3rem !important;
        min-height:38px !important;
        height:38px !important;
        width:100% !important;
        border-radius:10px !important;
        transition:all 0.2s !important;
    }}
    .icon-btn button p {{
        font-size:1.3rem !important;
        margin:0 !important;
    }}
    .icon-btn button:hover {{
        background:{"#16213e" if dm else "#e8f5e9"} !important;
        transform:scale(1.15) !important;
        border:none !important;
        color:{t["text"]} !important;
    }}
    .icon-btn button p {{ font-size:1.3rem !important; }}
    </style>
    """, unsafe_allow_html=True)

def render_topbar():
    t        = get_theme()
    dm       = st.session_state.dark_mode
    weather  = get_weather()
    expiring = [dict(i) for i in get_expiring_items(7)]
    exp_count = len(expiring)

    desc   = weather['desc'].lower()
    w_icon = "🌧️" if "rain" in desc else \
             "☀️" if "sun" in desc or "clear" in desc else \
             "🌤️" if "partly" in desc else "⛅"

    # 3 working buttons on right side
    _, c1, c2, c3 = st.columns([7, 1, 1, 1])

    with c1:
        if st.button(
            w_icon,
            key=f"wb_{st.session_state.current_page}",
            use_container_width=True,
            help=f"{weather['temp']}°C — {weather['desc']}"
        ):
            st.session_state.show_weather = \
                not st.session_state.show_weather
            st.session_state.show_alerts = False

    with c2:
        bell = f"🔔" if exp_count == 0 else f"🔔"
        if st.button(
            bell,
            key=f"bb_{st.session_state.current_page}",
            use_container_width=True,
            help=f"{exp_count} expiry alert(s)"
        ):
            st.session_state.show_alerts = \
                not st.session_state.show_alerts
            st.session_state.show_weather = False

    with c3:
        if st.button(
            "🌙" if not dm else "☀️",
            key=f"tb_{st.session_state.current_page}",
            use_container_width=True,
            help="Toggle theme"
        ):
            st.session_state.dark_mode = not dm
            st.session_state.show_weather = False
            st.session_state.show_alerts  = False
            st.rerun()

    # Weather card
    if st.session_state.show_weather:
        _, info_col, _ = st.columns([5, 3, 1])
        with info_col:
            st.markdown(f"""
            <div style='background:{t["card"]};
                border:1px solid {t["border"]};
                border-radius:12px;padding:14px;
                margin-bottom:8px;
                box-shadow:0 4px 20px rgba(0,0,0,0.1);'>
                <div style='text-align:center;margin-bottom:8px;'>
                    <div style='font-size:2rem;'>{w_icon}</div>
                    <div style='font-size:20px;font-weight:600;
                        color:#1b5e20;'>{weather['temp']}°C</div>
                    <div style='font-size:11px;color:#555;'>
                        {weather['desc']}
                    </div>
                    <div style='font-size:10px;color:#888;'>
                        Bengaluru, IN
                    </div>
                </div>
                <div style='background:#e8f5e9;border-radius:8px;
                    padding:7px;font-size:11px;color:#2d6a4f;
                    margin-bottom:8px;'>
                    🥗 {"Hot! Use veggies soon."
                        if int(weather['temp']) > 30
                        else "Cool! Produce lasts longer."}
                </div>
                <div style='display:flex;justify-content:space-between;
                    font-size:10px;color:#888;
                    border-top:1px solid #e0f2e9;padding-top:6px;'>
                    <span>💧 {weather['humidity']}%</span>
                    <span>💨 {weather['wind']}km/h</span>
                    <span>🌡️ {weather['feels']}°C</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

    # Alerts card
    if st.session_state.show_alerts:
        _, info_col, _ = st.columns([5, 3, 1])
        with info_col:
            if expiring:
                html = f"""
                <div style='background:{t["card"]};
                    border:1px solid {t["border"]};
                    border-radius:12px;padding:14px;
                    margin-bottom:8px;
                    box-shadow:0 4px 20px rgba(0,0,0,0.1);'>
                    <div style='font-size:13px;font-weight:600;
                        color:#e53935;margin-bottom:8px;'>
                        🔔 {exp_count} Expiry Alert(s)
                    </div>"""
                for item in expiring[:5]:
                    _, days, _, _ = get_expiry_info(item['expiry_date'])
                    label = "TODAY! 🚨" if days==0 else \
                            "EXPIRED!" if days<0 else f"In {days}d"
                    color = "#f44336" if days<=0 else \
                            "#ff9800" if days<=3 else "#fb8c00"
                    emoji = FOOD_EMOJIS.get(
                        item.get('category','Other'),'🛒'
                    )
                    html += f"""
                    <div style='display:flex;align-items:center;
                        gap:6px;padding:5px 0;
                        border-bottom:0.5px solid #f5f5f5;'>
                        <div style='width:6px;height:6px;
                            border-radius:50%;
                            background:{color};'></div>
                        <span style='font-size:12px;flex:1;
                            color:{t["text"]};'>
                            {emoji} {item['name']}
                        </span>
                        <span style='font-size:10px;
                            color:{color};font-weight:600;'>
                            {label}
                        </span>
                    </div>"""
                html += "</div>"
                st.markdown(html, unsafe_allow_html=True)
            else:
                st.success("✅ No expiry alerts!")

    st.markdown(
        f"<hr style='border-color:{t['border']};margin:2px 0 8px;'>",
        unsafe_allow_html=True
    )

# ─────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────
def render_sidebar():
    t  = get_theme()
    dm = st.session_state.dark_mode

    with st.sidebar:
        st.markdown(f"""
        <div style='text-align:center;padding:14px 0 12px;'>
            <div style='font-size:2.8rem;margin-bottom:6px;'>🥗</div>
            <h2 style='margin:0;color:{t["primary"]} !important;
                font-size:1.3rem;font-weight:700;'>FreshMind</h2>
            <p style='color:{t["subtext"]} !important;
                font-size:0.7rem;margin:3px 0 0;'>
                Smart Pantry Assistant
            </p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(
            f"<hr style='border-color:{t['border']};margin:4px 0 10px;'>",
            unsafe_allow_html=True
        )

        user  = st.session_state.user_data
        fname = user.get("full_name","") or st.session_state.username
        init  = fname[0].upper() if fname else "U"
        st.markdown(f"""
        <div style='background:{t["card2"]};border:1px solid {t["border"]};
            border-radius:10px;padding:8px 12px;margin-bottom:10px;'>
            <div style='display:flex;align-items:center;gap:8px;'>
                <div style='width:32px;height:32px;
                    background:linear-gradient(135deg,#667eea,#43e97b);
                    border-radius:50%;display:flex;align-items:center;
                    justify-content:center;color:white;font-size:13px;
                    font-weight:700;flex-shrink:0;'>{init}</div>
                <div>
                    <b style='color:{t["text"]} !important;
                        font-size:0.85rem;'>{fname}</b><br>
                    <small style='color:{t["subtext"]} !important;
                        font-size:0.7rem;'>
                        @{st.session_state.username} • Online
                    </small>
                </div>
            </div>
        </div>
     """, unsafe_allow_html=True)

        st.markdown(
            "<p style='color:#888 !important;font-size:11px;"
            "font-weight:700;text-transform:uppercase;"
            "letter-spacing:1px;margin:0 0 6px 2px;"
            "display:block !important;visibility:visible !important;"
            "opacity:1 !important;'>NAVIGATION</p>",
            unsafe_allow_html=True
        )

        pages = [
            ("🏠","Home",       "🏠 Home"),
            ("📦","My Pantry",  "📦 My Pantry"),
            ("➕","Add Item",   "➕ Add Item"),
            ("🤖","AI Recipes", "🤖 AI Recipes"),
            ("📊","Dashboard",  "📊 Dashboard"),
            ("⚙️","Settings",  "⚙️ Settings"),
        ]
        for icon, label, key in pages:
            is_active = st.session_state.current_page == key
            if st.button(
                f"{icon}  {label}",
                key=f"nav_{key}",
                use_container_width=True
            ):
                st.session_state.current_page = key
                st.session_state.show_weather = False
                st.session_state.show_alerts  = False
                st.rerun()
            if is_active:
                st.markdown(f"""
                <style>
                div[data-testid="stSidebar"]
                div[data-testid="stButton"]
                button:has(p:contains("{icon}  {label}")) {{
                    background:{t["nav_active"]} !important;
                    color:white !important;
                    border-color:transparent !important;
                    box-shadow:0 4px 14px rgba(102,126,234,0.4) !important;
                    transform:translateX(3px) !important;
                }}
                </style>
                """, unsafe_allow_html=True)

        st.markdown(
            f"<hr style='border-color:{t['border']};margin:8px 0 6px;'>",
            unsafe_allow_html=True
        )

        if st.button("🚪  Logout", key="logout_btn",
                     use_container_width=True):
            for k in list(st.session_state.keys()):
                del st.session_state[k]
            st.rerun()

        st.markdown(f"""
        <style>
        div[data-testid="stSidebar"]
        div[data-testid="stButton"]
        button:has(p:contains("🚪  Logout")) {{
            background:{"#2a0a0a" if dm else "#fff5f5"} !important;
            color:#e53935 !important;
            border:1px solid #ffcdd2 !important;
        }}
        </style>
        <p style='text-align:center;color:{t["subtext"]} !important;
            font-size:0.58rem;margin-top:10px;'>
            Built with ❤️ Python & Streamlit
        </p>
        """, unsafe_allow_html=True)

    return st.session_state.current_page

# ─────────────────────────────────────────
# LOGIN PAGE
# ─────────────────────────────────────────
def login_page():
    inject_css()
    t  = get_theme()
    dm = st.session_state.dark_mode

    components.html(f"""
    <canvas id="bg" style="width:100%;display:block;"></canvas>
    <script>
        const c=document.getElementById('bg');
        const x=c.getContext('2d');
        c.width=window.innerWidth; c.height=160;
        const bg="{'#0f0f1a' if dm else '#f0faf4'}";
        const ps=Array.from({{length:30}},()=>({{
            x:Math.random()*c.width,y:Math.random()*160,
            r:Math.random()*3+1,dx:(Math.random()-.5)*1.2,
            dy:(Math.random()-.5)*1.2,
            col:`hsla(${{Math.random()*60+100}},70%,55%,.5)`
        }}));
        function draw(){{
            x.fillStyle=bg; x.fillRect(0,0,c.width,160);
            ps.forEach(p=>{{
                x.beginPath();x.arc(p.x,p.y,p.r,0,Math.PI*2);
                x.fillStyle=p.col;x.fill();
                p.x+=p.dx;p.y+=p.dy;
                if(p.x<0||p.x>c.width)p.dx*=-1;
                if(p.y<0||p.y>160)p.dy*=-1;
            }});
            requestAnimationFrame(draw);
        }}
        draw();
    </script>
    """, height=160)

    col1, col2, col3 = st.columns([1,1.4,1])
    with col2:
        st.markdown(f"""
        <div class='fade-in' style='text-align:center;padding:14px 0 10px;'>
            <div style='font-size:3.2rem;'>🥗</div>
            <h1 style='font-size:2rem;font-weight:700;
                background:linear-gradient(135deg,#667eea,#43e97b);
                -webkit-background-clip:text;
                -webkit-text-fill-color:transparent;margin:4px 0;'>
                FreshMind
            </h1>
            <p style='color:{t["subtext"]} !important;
                font-size:0.9rem;margin:0 0 14px;'>
                Your AI-Powered Smart Pantry Assistant
            </p>
        </div>
        """, unsafe_allow_html=True)

        tab1, tab2 = st.tabs(["🔐 Login","📝 Register"])

        with tab1:
            with st.form("login_form"):
                st.markdown(
                    f"<h3 style='color:{t['text']} !important;'>"
                    f"👋 Welcome Back!</h3>",
                    unsafe_allow_html=True
                )
                username = st.text_input("👤 Username",
                                         placeholder="Enter username")
                password = st.text_input("🔒 Password", type="password",
                                         placeholder="Enter password")
                c1, c2 = st.columns(2)
                with c1:
                    submitted = st.form_submit_button(
                        "🔐 Login", use_container_width=True
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
                            st.error("❌ Wrong username or password!")
            st.markdown(f"""
            <p style='text-align:center;
                color:{t["subtext"]} !important;font-size:0.78rem;'>
                Demo:
                <b style='color:{t["text"]} !important;'>admin</b> /
                <b style='color:{t["text"]} !important;'>admin123</b>
            </p>
            """, unsafe_allow_html=True)

        with tab2:
            with st.form("register_form"):
                st.markdown(
                    f"<h3 style='color:{t['text']} !important;'>"
                    f"🆕 Create Account</h3>",
                    unsafe_allow_html=True
                )
                r_name  = st.text_input("👤 Full Name *",
                                        placeholder="Your full name")
                r_user  = st.text_input("🆔 Username *",
                                        placeholder="Choose a username")
                r_email = st.text_input("📧 Email",
                                        placeholder="your@email.com")
                r_pass  = st.text_input("🔒 Password *", type="password",
                                        placeholder="Min 6 characters")
                r_pass2 = st.text_input("🔒 Confirm *",  type="password",
                                        placeholder="Repeat password")
                reg = st.form_submit_button(
                    "📝 Create Account", use_container_width=True
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
                            user = login_user(r_user, r_pass)
                            if user:
                                st.session_state.logged_in    = True
                                st.session_state.username     = r_user
                                st.session_state.user_data    = user
                                st.session_state.current_page = "🏠 Home"
                                st.rerun()
                        else:
                            st.error(msg)

def home_page():
    t  = get_theme()
    dm = st.session_state.dark_mode
    render_topbar()

    user  = st.session_state.user_data
    fname = user.get("full_name","") or st.session_state.username

    all_items      = [dict(i) for i in get_all_items()]
    expiring_items = [dict(i) for i in get_expiring_items(7)]
    critical_items = [dict(i) for i in get_expiring_items(3)]
    history        = [dict(i) for i in get_usage_history()]
    saved  = sum(1 for h in history if not h['was_wasted'])
    wasted = sum(1 for h in history if h['was_wasted'])
    exp_count = len(expiring_items)
    weather = get_weather()

    # Build alerts HTML BEFORE components.html
    if expiring_items:
        alerts_html = f"<div class='a-title'>🔔 {exp_count} Alert(s)</div>"
        for i in expiring_items[:5]:
            days = (datetime.strptime(
                i['expiry_date'],'%Y-%m-%d'
            ).date() - date.today()).days
            color = "#f44336" if days<=0 else \
                    "#ff9800" if days<=3 else "#fb8c00"
            label = "TODAY!" if days==0 else \
                    "EXPIRED!" if days<0 else f"In {days}d"
            emoji = FOOD_EMOJIS.get(i.get('category','Other'),'🛒')
            alerts_html += (
                f"<div class='a-item'>"
                f"<div class='a-dot' style='background:{color};'></div>"
                f"<span class='a-name'>{emoji} {i['name']}</span>"
                f"<span class='a-days' style='color:{color};'>{label}</span>"
                f"</div>"
            )
    else:
        alerts_html = "<div class='a-empty'>✅ No expiry alerts!</div>"

    # Weather icon
    desc   = weather['desc'].lower()
    w_icon = "🌧️" if "rain" in desc else \
             "☀️" if "sun" in desc or "clear" in desc else \
             "🌤️" if "partly" in desc else "⛅"

    # ── Hero with Food Rain + Circular Icons ──
    components.html(f"""
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        *{{font-family:'Poppins',sans-serif;box-sizing:border-box;margin:0;padding:0;}}
        .hero{{
            background:linear-gradient(135deg,#1b5e20,#2d6a4f);
            padding:22px 22px 20px;border-radius:14px;
            position:relative;overflow:hidden;min-height:100px;
        }}
        .food-drop{{
            position:absolute;font-size:18px;
            animation:foodRain linear infinite;
            top:-30px;pointer-events:none;user-select:none;
        }}
        @keyframes foodRain{{
            0%{{transform:translateY(-30px) rotate(0deg);opacity:0;}}
            10%{{opacity:0.25;}}
            90%{{opacity:0.15;}}
            100%{{transform:translateY(150px) rotate(360deg);opacity:0;}}
        }}
        .hero-content{{position:relative;z-index:2;margin-top:6px;}}
        .greeting{{font-size:10px;color:rgba(255,255,255,0.7);
            text-transform:uppercase;letter-spacing:1.5px;margin-bottom:4px;}}
        .hero-title{{font-size:1.6rem;font-weight:600;
            color:white;margin-bottom:4px;}}
        .hero-sub{{font-size:0.88rem;color:rgba(255,255,255,0.82);}}
        .hero-leaf{{position:absolute;right:130px;top:50%;
            transform:translateY(-50%);font-size:56px;
            opacity:0.1;z-index:1;}}
        .dot-icons{{
            position:absolute;top:12px;right:12px;
            display:flex;gap:6px;z-index:10;
        }}
        .dot-btn{{
            width:34px;height:34px;border-radius:50%;
            background:rgba(255,255,255,0.18);
            border:1.5px solid rgba(255,255,255,0.3);
            display:flex;align-items:center;justify-content:center;
            font-size:15px;cursor:pointer;
            transition:all 0.2s;position:relative;
        }}
        .dot-btn:hover{{
            background:rgba(255,255,255,0.32);
            transform:scale(1.12);
        }}
        .dot-badge{{
            position:absolute;top:-3px;right:-3px;
            width:14px;height:14px;background:#e53935;
            border-radius:50%;font-size:8px;color:white;
            display:flex;align-items:center;justify-content:center;
            font-weight:700;border:1.5px solid #2d6a4f;
        }}
        .drop-card{{
            position:absolute;top:44px;right:0;
            background:white;border-radius:12px;
            border:1px solid #e0f2e9;
            box-shadow:0 8px 24px rgba(0,0,0,0.12);
            z-index:999;display:none;min-width:200px;
        }}
        .drop-card.open{{display:block;animation:sd 0.2s ease;}}
        @keyframes sd{{
            from{{opacity:0;transform:translateY(-8px);}}
            to{{opacity:1;transform:translateY(0);}}
        }}
        .w-inner{{padding:14px;}}
        .w-center{{text-align:center;margin-bottom:10px;}}
        .w-temp{{font-size:20px;font-weight:600;color:#1b5e20;}}
        .w-desc{{font-size:11px;color:#555;}}
        .w-tip{{background:#e8f5e9;border-radius:8px;
            padding:7px;font-size:11px;color:#2d6a4f;margin:8px 0;}}
        .w-row{{display:flex;justify-content:space-between;
            font-size:10px;color:#888;
            border-top:1px solid #e0f2e9;padding-top:6px;}}
        .a-title{{font-size:13px;font-weight:600;
            color:#e53935;padding:10px 14px 6px;}}
        .a-item{{display:flex;align-items:center;gap:6px;
            padding:6px 14px;border-bottom:0.5px solid #f5f5f5;}}
        .a-dot{{width:6px;height:6px;border-radius:50%;flex-shrink:0;}}
        .a-name{{font-size:12px;flex:1;color:#333;}}
        .a-days{{font-size:10px;font-weight:600;}}
        .a-empty{{padding:14px;text-align:center;
            font-size:12px;color:#43a047;}}
    </style>

    <div class="hero">
        <div class="food-drop" style="left:5%;animation-duration:3.0s;">🥦</div>
        <div class="food-drop" style="left:13%;animation-duration:2.5s;animation-delay:0.4s;">🍎</div>
        <div class="food-drop" style="left:22%;animation-duration:3.5s;animation-delay:0.8s;">🥛</div>
        <div class="food-drop" style="left:31%;animation-duration:2.8s;animation-delay:0.2s;">🧅</div>
        <div class="food-drop" style="left:41%;animation-duration:3.2s;animation-delay:1.0s;">🍗</div>
        <div class="food-drop" style="left:50%;animation-duration:2.6s;animation-delay:0.6s;">🥚</div>
        <div class="food-drop" style="left:59%;animation-duration:3.0s;animation-delay:1.2s;">🍞</div>
        <div class="food-drop" style="left:67%;animation-duration:2.4s;animation-delay:0.3s;">🥕</div>
        <div class="food-drop" style="left:74%;animation-duration:3.3s;animation-delay:0.7s;">🧄</div>
        <div class="food-drop" style="left:81%;animation-duration:2.7s;animation-delay:1.1s;">🍋</div>
        <div class="food-drop" style="left:88%;animation-duration:3.1s;animation-delay:0.5s;">🥬</div>
        <div class="food-drop" style="left:94%;animation-duration:2.9s;animation-delay:0.9s;">🍅</div>

        <div class="hero-leaf">🥗</div>

        <div class="dot-icons">
            <div style="position:relative;">
                <div class="dot-btn" onclick="tg('wd')">{w_icon}</div>
                <div class="drop-card" id="wd">
                    <div class="w-inner">
                        <div class="w-center">
                            <div style="font-size:1.8rem;">{w_icon}</div>
                            <div class="w-temp">{weather['temp']}°C</div>
                            <div class="w-desc">{weather['desc']}</div>
                            <div class="w-desc" style="font-size:9px;color:#888;">Bengaluru, IN</div>
                        </div>
                        <div class="w-tip">🥗 {"Hot! Use leafy veggies soon." if int(weather['temp'])>30 else "Cool! Produce lasts longer."}</div>
                        <div class="w-row">
                            <span>💧{weather['humidity']}%</span>
                            <span>💨{weather['wind']}km/h</span>
                            <span>🌡️{weather['feels']}°C</span>
                        </div>
                    </div>
                </div>
            </div>
            <div style="position:relative;">
                <div class="dot-btn" onclick="tg('ad')">
                    🔔{"<div class='dot-badge'>" + str(exp_count) + "</div>" if exp_count > 0 else ""}
                </div>
                <div class="drop-card" id="ad" style="min-width:220px;">
                    {alerts_html}
                </div>
            </div>
            <div class="dot-btn" onclick="tgTheme()">{"🌙" if not dm else "☀️"}</div>
        </div>

        <div class="hero-content">
            <div class="greeting">{get_greeting()}</div>
            <div class="hero-title">👋 Hello, {fname}!</div>
            <div class="hero-sub">
                {date.today().strftime("%A, %B %d %Y")} — Here's your pantry overview
            </div>
        </div>
    </div>

    <script>
        let od = null;
        function tg(id) {{
            const el = document.getElementById(id);
            if (od && od !== id) {{
                const p = document.getElementById(od);
                if (p) p.classList.remove('open');
            }}
            el.classList.toggle('open');
            od = el.classList.contains('open') ? id : null;
        }}
        function tgTheme() {{
            window.parent.postMessage({{type:'streamlit:setComponentValue',value:'theme_toggle'}},'*');
        }}
        document.addEventListener('click', function(e) {{
            if (!e.target.closest('.dot-btn') && !e.target.closest('.drop-card')) {{
                document.querySelectorAll('.drop-card').forEach(d=>d.classList.remove('open'));
                od = null;
            }}
        }});
    </script>
    """, height=150)

    # ── Animated Metrics ──
    components.html(f"""
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700&display=swap" rel="stylesheet">
    <style>
        *{{font-family:'Poppins',sans-serif;box-sizing:border-box;}}
        .g{{display:grid;grid-template-columns:repeat(4,1fr);gap:10px;padding:8px 0 10px;}}
        .c{{background:{"#1a1a2e" if dm else "white"};border-radius:12px;padding:14px;
            text-align:center;box-shadow:0 4px 18px rgba(0,0,0,0.07);
            border:1.5px solid {"#2a2a4a" if dm else "#e0f2e9"};
            transition:all 0.3s;cursor:pointer;}}
        .c:hover{{transform:translateY(-5px);}}
        .c.g1:hover{{box-shadow:0 0 0 2px #667eea,0 8px 24px rgba(102,126,234,0.2);border-color:transparent;}}
        .c.g2:hover{{box-shadow:0 0 0 2px #fa709a,0 8px 24px rgba(250,112,154,0.2);border-color:transparent;}}
        .c.g3:hover{{box-shadow:0 0 0 2px #43e97b,0 8px 24px rgba(67,233,123,0.2);border-color:transparent;}}
        .c.g4:hover{{box-shadow:0 0 0 2px #f44336,0 8px 24px rgba(244,67,54,0.2);border-color:transparent;}}
        .c:hover .i{{animation:pulse 0.5s ease infinite alternate;}}
        @keyframes pulse{{to{{transform:scale(1.25);}}}}
        .i{{font-size:1.6rem;margin-bottom:5px;display:inline-block;}}
        .n{{font-size:1.8rem;font-weight:700;margin:3px 0;}}
        .l{{font-size:0.7rem;color:{"#a0a0b0" if dm else "#888"};}}
    </style>
    <div class="g">
        <div class="c g1"><div class="i">📦</div>
            <div class="n" style="color:#667eea" id="c1">0</div>
            <div class="l">Total Items</div></div>
        <div class="c g2"><div class="i">⚠️</div>
            <div class="n" style="color:#fa709a" id="c2">0</div>
            <div class="l">Expiring This Week</div></div>
        <div class="c g3"><div class="i">✅</div>
            <div class="n" style="color:#43e97b" id="c3">0</div>
            <div class="l">Items Saved</div></div>
        <div class="c g4"><div class="i">🗑️</div>
            <div class="n" style="color:#f44336" id="c4">0</div>
            <div class="l">Items Wasted</div></div>
    </div>
    <script>
        function up(id,target){{
            const el=document.getElementById(id);
            if(!el||!target){{if(el)el.textContent=0;return;}}
            let s=0,step=target/80;
            const t=setInterval(()=>{{
                s+=step;if(s>=target){{el.textContent=target;clearInterval(t);}}
                else el.textContent=Math.floor(s);
            }},16);
        }}
        up('c1',{len(all_items)});up('c2',{len(expiring_items)});
        up('c3',{saved});up('c4',{wasted});
    </script>
    """, height=160)

    if critical_items:
        st.error(f"🚨 {len(critical_items)} item(s) expire in less than 3 days!")
    elif expiring_items:
        st.warning(f"⚠️ {len(expiring_items)} item(s) expiring this week!")
    else:
        st.success("✅ Everything is fresh!")

    st.markdown(
        "<hr style='margin:6px 0;border-color:#e0f2e9;'>",
        unsafe_allow_html=True
    )

    # ── Quick Actions ──
    st.markdown(
        f"<h3 style='color:{t['text']} !important;margin-bottom:10px;'>"
        f"⚡ Quick Actions</h3>",
        unsafe_allow_html=True
    )
    actions = [
        ("➕","Add Item",   "Add new pantry item","➕ Add Item"),
        ("📦","My Pantry", "View & manage items", "📦 My Pantry"),
        ("🤖","AI Recipes","Get smart recipes",   "🤖 AI Recipes"),
        ("📊","Dashboard", "View analytics",      "📊 Dashboard"),
    ]
    cols = st.columns(4)
    for i,(col,(icon,title,desc,page_key)) in \
            enumerate(zip(cols,actions)):
        with col:
            st.markdown(f"""
            <div style='background:{t["card"]};border-radius:14px;
                padding:20px 12px;text-align:center;
                border:1.5px solid {t["border"]};
                box-shadow:0 4px 16px rgba(0,0,0,0.06);
                transition:all 0.25s;margin-bottom:4px;'
                onmouseover="this.style.transform='translateY(-6px)';
                    this.style.borderColor='#667eea';"
                onmouseout="this.style.transform='translateY(0)';
                    this.style.borderColor='{t['border']}';">
                <div style='font-size:2.4rem;margin-bottom:8px;'>{icon}</div>
                <div style='font-size:0.9rem;font-weight:600;
                    color:{t["text"]};margin-bottom:3px;'>{title}</div>
                <div style='font-size:0.75rem;color:{t["subtext"]};'>{desc}</div>
            </div>
            """, unsafe_allow_html=True)
            if st.button(f"Go {title}", key=f"qa_{i}",
                         use_container_width=True):
                st.session_state.current_page = page_key
                st.rerun()
            st.markdown(f"""
            <style>
            div[data-testid="stColumn"]:nth-child({i+1})
            div[data-testid="stButton"] button {{
                opacity:0 !important;
                height:1px !important;
                min-height:0 !important;
                padding:0 !important;
                margin:0 !important;
            }}
            </style>
            """, unsafe_allow_html=True)

    st.markdown(
        "<hr style='margin:6px 0;border-color:#e0f2e9;'>",
        unsafe_allow_html=True
    )

    # ── Recent Activity ──
    st.markdown(
        f"<h3 style='color:{t['text']} !important;margin-bottom:8px;'>"
        f"🕐 Recent Activity</h3>",
        unsafe_allow_html=True
    )
    history_list = [dict(i) for i in get_usage_history()]
    if not history_list:
        st.info("No activity yet — start using your pantry!")
    else:
        for h in history_list[:5]:
            icon   = "✅" if not h['was_wasted'] else "🗑️"
            color  = "#43e97b" if not h['was_wasted'] else "#f44336"
            action = "Used" if not h['was_wasted'] else "Wasted"
            st.markdown(f"""
            <div style='background:{t["card"]};border-radius:8px;
                padding:7px 12px;margin-bottom:4px;
                border-left:4px solid {color};
                display:flex;align-items:center;gap:8px;'>
                <span style='font-size:1rem;'>{icon}</span>
                <span style='color:{t["text"]} !important;font-size:0.82rem;'>
                    <b>{h['item_name']}</b> — {action} on {h['used_date']}
                </span>
            </div>
            """, unsafe_allow_html=True)

    st.markdown(
        "<hr style='margin:6px 0;border-color:#e0f2e9;'>",
        unsafe_allow_html=True
    )

    # ── Cooking Tips ──
    st.markdown(
        f"<h3 style='color:{t['text']} !important;margin-bottom:6px;'>"
        f"🍳 Cooking Tips of the Day</h3>",
        unsafe_allow_html=True
    )
    if st.button("✨ Get AI Tips for My Pantry", key="ai_tips_btn"):
        with st.spinner("🤖 Getting personalized tips..."):
            try:
                from groq import Groq
                from dotenv import load_dotenv
                load_dotenv()
                client = Groq(api_key=os.getenv("GROQ_API_KEY"))
                items_text = ", ".join(
                    [i['name'] for i in all_items[:10]]
                ) if all_items else "empty pantry"
                resp = client.chat.completions.create(
                    model="llama-3.1-8b-instant", max_tokens=300,
                    messages=[{"role":"user","content":(
                        f"Give 3 quick cooking/storage tips for "
                        f"these pantry items: {items_text}. "
                        f"Each tip under 2 sentences. Format: emoji + tip"
                    )}]
                )
                st.info(
                    f"💡 **AI Tips:**\n\n"
                    f"{resp.choices[0].message.content}"
                )
            except Exception as e:
                st.error(f"❌ Error: {e}")

    tips_json = json.dumps(DAILY_TIPS)
    components.html(f"""
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600&display=swap" rel="stylesheet">
    <style>
        *{{font-family:'Poppins',sans-serif;box-sizing:border-box;}}
        .sw{{background:{"#1a1a2e" if dm else "white"};border-radius:12px;
             padding:16px 20px;box-shadow:0 4px 18px rgba(0,0,0,0.07);
             border:1px solid {"#2a2a4a" if dm else "#e0e8f0"};}}
        .tip{{display:none;animation:fi .4s ease;}}
        .tip.active{{display:block;}}
        @keyframes fi{{from{{opacity:0;transform:translateX(14px);}}to{{opacity:1;transform:translateX(0);}}}}
        .ti{{font-size:1.5rem;margin-bottom:4px;}}
        .tt{{font-size:.88rem;font-weight:600;
             color:{"#fff" if dm else "#1a1a2e"};margin-bottom:2px;}}
        .tx{{font-size:.78rem;line-height:1.5;
             color:{"#a0a0b0" if dm else "#555"};}}
        .dots{{display:flex;gap:4px;justify-content:center;margin-top:10px;}}
        .dot{{width:6px;height:6px;border-radius:50%;
              background:{"#2a2a4a" if dm else "#ddd"};
              cursor:pointer;border:none;transition:all .3s;}}
        .dot.active{{background:#667eea;width:14px;border-radius:3px;}}
        .nav{{display:flex;justify-content:space-between;margin-top:8px;}}
        .arr{{background:{"#2a2a4a" if dm else "#f0f4f8"};border:none;
              border-radius:6px;padding:4px 10px;cursor:pointer;
              font-size:.78rem;color:{"#fff" if dm else "#333"};transition:all .2s;}}
        .arr:hover{{background:#667eea;color:white;}}
        .pb{{height:2px;background:#667eea;border-radius:2px;
             margin-top:8px;transition:width .1s linear;}}
    </style>
    <div class="sw">
        <div id="tc"></div>
        <div class="pb" id="pb"></div>
        <div class="nav">
            
            <div class="dots" id="de"></div>
            <button class="arr" onclick="next()"></button>
        </div>
    </div>
    <script>
        const tips={tips_json};
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
            dot.id='d'+i;dot.onclick=()=>go(i);
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
            pw=0;pb.style.width='0%';
            clearInterval(pt);clearTimeout(at);
            pt=setInterval(()=>{{pw+=100/(INT/100);
                pb.style.width=pw+'%';
                if(pw>=100)clearInterval(pt);}},100);
            at=setTimeout(()=>next(),INT);
        }}
        reset();
    </script>
    """, height=210)
# ─────────────────────────────────────────
# PANTRY PAGE
# ─────────────────────────────────────────
def pantry_page():
    t = get_theme()
    render_topbar()
    st.markdown("""
    <div class='hero-banner fade-in' style='padding:16px 20px;'>
        <h2 style='margin:0;'>📦 My Pantry</h2>
        <p style='margin:3px 0 0;opacity:0.85;'>Manage your food items</p>
    </div>
    """, unsafe_allow_html=True)

    all_items = [dict(i) for i in get_all_items()]
    if not all_items:
        st.info("🛒 Pantry is empty! Add some items.")
        return

    c1,c2,c3 = st.columns([3,1,1])
    with c1: search = st.text_input("🔍 Search",
                                     placeholder="Search items...")
    with c2: filter_cat = st.selectbox("Category",[
        "All","Dairy","Vegetables","Fruits",
        "Meat & Seafood","Grains & Cereals",
        "Snacks","Beverages","Condiments","Other"])
    with c3: filter_expiry = st.selectbox("Expiry",[
        "All","Critical (≤3d)","Expiring (≤7d)","Fresh (>7d)"])

    filtered = []
    for item in all_items:
        _,days,_,_ = get_expiry_info(item['expiry_date'])
        ms = search.lower() in item['name'].lower() if search else True
        mc = item['category']==filter_cat if filter_cat!="All" else True
        me = True
        if   filter_expiry=="Critical (≤3d)": me=days<=3
        elif filter_expiry=="Expiring (≤7d)": me=days<=7
        elif filter_expiry=="Fresh (>7d)":    me=days>7
        if ms and mc and me: filtered.append(item)

    st.markdown(
        f"Showing **{len(filtered)}** of **{len(all_items)}** items"
    )
    st.markdown("---")

    for item in filtered:
        emoji,days_left,badge,card_cls = \
            get_expiry_info(item['expiry_date'])
        item_emoji = FOOD_EMOJIS.get(
            item.get('category','Other'),'🛒'
        )

        if st.session_state.edit_item_id == item['id']:
            with st.form(key=f"edit_{item['id']}"):
                st.markdown(f"### ✏️ Editing: **{item['name']}**")
                c1,c2 = st.columns(2)
                with c1:
                    nn = st.text_input("Name", value=item['name'])
                    nq = st.text_input("Quantity", value=item['quantity'])
                    cats = ["Dairy","Vegetables","Fruits",
                            "Meat & Seafood","Grains & Cereals",
                            "Snacks","Beverages","Condiments","Other"]
                    nc = st.selectbox(
                        "Category", cats,
                        index=cats.index(item['category'])
                        if item['category'] in cats else 0
                    )
                with c2:
                    ne = st.date_input(
                        "Expiry Date",
                        value=datetime.strptime(
                            item['expiry_date'],"%Y-%m-%d"
                        ).date()
                    )
                s1,s2 = st.columns(2)
                with s1:
                    if st.form_submit_button(
                        "💾 Save", use_container_width=True
                    ):
                        update_item(
                            item['id'],name=nn,quantity=nq,
                            expiry_date=str(ne),category=nc
                        )
                        st.session_state.edit_item_id=None
                        st.rerun()
                with s2:
                    if st.form_submit_button(
                        "❌ Cancel", use_container_width=True
                    ):
                        st.session_state.edit_item_id=None
                        st.rerun()
        else:
            ic,info,btn = st.columns([1,5,2])
            with ic:
                st.markdown(f"""
                <div style='width:60px;height:60px;
                    background:linear-gradient(135deg,#667eea22,#43e97b22);
                    border-radius:10px;display:flex;align-items:center;
                    justify-content:center;font-size:1.8rem;
                    border:1px solid {t["border"]};'>
                    {item_emoji}
                </div>
                """, unsafe_allow_html=True)
            with info:
                st.markdown(f"""
                <div class='item-card {card_cls} fade-in'
                     style='margin:0;padding:10px 14px;'>
                    <div style='display:flex;align-items:center;
                        gap:6px;flex-wrap:wrap;'>
                        <b style='font-size:.9rem;
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
                    <div style='margin-top:3px;
                        color:{t["subtext"]} !important;
                        font-size:.76rem;'>
                        📏 <b style='color:{t["text"]} !important;'>
                            {item['quantity']}
                        </b> &nbsp;|&nbsp;
                        📅 <b style='color:{t["text"]} !important;'>
                            {item['expiry_date']}
                        </b>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            with btn:
                b1,b2,b3 = st.columns(3)
                with b1:
                    if st.button("✅",key=f"use_{item['id']}",
                                 help="Mark used"):
                        log_usage(item['name'],was_wasted=False)
                        delete_item(item['id'])
                        st.toast(f"✅ {item['name']} used!")
                        st.rerun()
                with b2:
                    if st.button("✏️",key=f"edit_{item['id']}",
                                 help="Edit"):
                        st.session_state.edit_item_id=item['id']
                        st.rerun()
                with b3:
                    if st.button("🗑️",key=f"del_{item['id']}",
                                 help="Delete"):
                        log_usage(item['name'],was_wasted=True)
                        delete_item(item['id'])
                        st.toast(f"🗑️ {item['name']} removed!")
                        st.rerun()

# ─────────────────────────────────────────
# ADD ITEM PAGE
# ─────────────────────────────────────────
def add_item_page():
    t = get_theme()
    render_topbar()
    st.markdown("""
    <div class='hero-banner fade-in' style='padding:16px 20px;'>
        <h2 style='margin:0;'>➕ Add New Item</h2>
        <p style='margin:3px 0 0;opacity:0.85;'>
            Add items to your pantry
        </p>
    </div>
    """, unsafe_allow_html=True)

    col1,col2,col3 = st.columns([1,2,1])
    with col2:
        name = st.text_input(
            "Item Name *",
            placeholder="e.g. Milk, Eggs, Spinach",
            key="item_name_input"
        )
        if name and len(name) >= 2:
            emoji = FOOD_EMOJIS.get("Other","🛒")
            st.markdown(f"""
            <div style='text-align:center;padding:12px;
                background:{t["card2"]};border-radius:10px;
                border:2px dashed {t["border"]};margin-bottom:10px;'>
                <div style='font-size:3rem;'>{emoji}</div>
                <div style='font-size:12px;color:{t["text"]};
                    font-weight:500;'>{name}</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("---")
        with st.form("add_form", clear_on_submit=True):
            c1,c2 = st.columns(2)
            with c1:
                quantity = st.text_input(
                    "Quantity *", placeholder="e.g. 1 litre, 500g"
                )
                category = st.selectbox("Category *",[
                    "Dairy","Vegetables","Fruits",
                    "Meat & Seafood","Grains & Cereals",
                    "Snacks","Beverages","Condiments","Other"
                ])
            with c2:
                purchase_date = st.date_input(
                    "Purchase Date *", value=date.today()
                )
                expiry_date = st.date_input(
                    "Expiry Date *", value=date.today()
                )
            if st.form_submit_button(
                "➕ Add to Pantry", use_container_width=True
            ):
                item_name = st.session_state.get(
                    "item_name_input",""
                )
                if not item_name or not quantity:
                    st.error("❌ Fill in all required fields!")
                elif expiry_date < purchase_date:
                    st.error("❌ Expiry before purchase date!")
                elif expiry_date < date.today():
                    st.error("❌ Item already expired!")
                else:
                    add_item(
                        name=item_name,quantity=quantity,
                        purchase_date=str(purchase_date),
                        expiry_date=str(expiry_date),
                        category=category
                    )
                    st.success(f"✅ **{item_name}** added!")
                    confetti()

# ─────────────────────────────────────────
# AI RECIPES PAGE
# ─────────────────────────────────────────
def ai_recipes_page():
    t = get_theme()
    render_topbar()
    st.markdown("""
    <div class='hero-banner fade-in' style='padding:16px 20px;'>
        <h2 style='margin:0;'>🤖 AI Recipe Suggestions</h2>
        <p style='margin:3px 0 0;opacity:0.85;'>
            Smart recipes from your pantry
        </p>
    </div>
    """, unsafe_allow_html=True)

    all_items      = [dict(i) for i in get_all_items()]
    expiring_items = [dict(i) for i in get_expiring_items(7)]

    if not all_items:
        st.info("🛒 Add some items to your pantry first!")
        return

    c1,c2 = st.columns(2)
    with c1: st.info(f"📦 **{len(all_items)}** items available")
    with c2:
        if expiring_items:
            st.warning(
                f"⚠️ **{len(expiring_items)}** expiring soon!"
            )

    st.markdown("### 🎛️ Preferences")
    c1,c2,c3 = st.columns(3)
    with c1:
        meal = st.selectbox("🍽️ Meal",[
            "Any","Breakfast","Lunch","Dinner","Snack","Dessert"
        ])
    with c2:
        diet = st.selectbox("🥗 Diet",[
            "Any","Vegetarian","Vegan",
            "Non-Vegetarian","Gluten-Free"
        ])
    with c3:
        time_ = st.selectbox("⏱️ Time",[
            "Any","<15 mins","<30 mins","<1 hour"
        ])
    st.markdown("---")

    if st.button(
        "🍳 Generate Recipes From My Pantry",
        use_container_width=True
    ):
        with st.spinner("🤖 AI is cooking up ideas..."):
            prefs  = f"Meal:{meal}, Diet:{diet}, Time:{time_}"
            result = get_recipe_suggestions(
                all_items, expiring_items, prefs
            )
            st.session_state.chat_history.append({
                "role":"assistant","content":result
            })

    st.markdown("### 💬 Recipe Chat")
    for msg in st.session_state.chat_history:
        if msg["role"]=="user":
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
            st.session_state.chat_history=[]
            st.rerun()

    user_input = st.chat_input(
        "Ask — 'make it spicy', 'no onions', 'quick meal'"
    )
    if user_input:
        st.session_state.chat_history.append({
            "role":"user","content":user_input
        })
        with st.spinner("🤖 Thinking..."):
            response,st.session_state.chat_history = \
                chat_with_ai(
                    user_input,st.session_state.chat_history
                )
        st.rerun()

# ─────────────────────────────────────────
# DASHBOARD PAGE
# ─────────────────────────────────────────
def dashboard_page():
    render_topbar()
    render_dashboard(
        get_all_items(),get_expiring_items(7),
        get_usage_history(),st.session_state.dark_mode
    )

# ─────────────────────────────────────────
# SETTINGS PAGE
# ─────────────────────────────────────────
def settings_page():
    t = get_theme()
    render_topbar()
    st.markdown("""
    <div class='hero-banner fade-in' style='padding:16px 20px;'>
        <h2 style='margin:0;'>⚙️ Settings</h2>
        <p style='margin:3px 0 0;opacity:0.85;'>Manage your account</p>
    </div>
    """, unsafe_allow_html=True)

    user = st.session_state.user_data
    tab1,tab2 = st.tabs(["👤 My Profile","🔒 Change Password"])

    with tab1:
        st.markdown(f"""
        <div class='fm-card'>
            <h3 style='color:{t["text"]} !important;margin-bottom:10px;'>
                👤 Profile Info
            </h3>
            <p style='color:{t["text"]} !important;'>
                <b>Username:</b> @{user.get('username','')}
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
        </div>
        """, unsafe_allow_html=True)

        if user.get('role')=='admin':
            st.markdown(
                f"<h3 style='color:{t['text']} !important;'>"
                f"👥 All Users</h3>",
                unsafe_allow_html=True
            )
            for u in get_all_users():
                st.markdown(f"""
                <div class='fm-card' style='padding:8px 12px;'>
                    <b style='color:{t["text"]} !important;'>
                        👤 {u['username']}
                    </b>
                    <span style='color:{t["subtext"]} !important;
                        font-size:.76rem;margin-left:8px;'>
                        {u['full_name'] or ''} | {u['role']}
                    </span>
                </div>
                """, unsafe_allow_html=True)

    with tab2:
        with st.form("change_pass"):
            old  = st.text_input("Current Password",
                                  type="password")
            new  = st.text_input("New Password", type="password")
            new2 = st.text_input("Confirm New Password",
                                  type="password")
            if st.form_submit_button(
                "🔒 Update Password", use_container_width=True
            ):
                if new!=new2:
                    st.error("❌ Passwords don't match!")
                elif len(new)<6:
                    st.error("❌ Min 6 characters!")
                else:
                    ok,msg=update_password(user['id'],old,new)
                    st.success(msg) if ok else st.error(msg)

# ─────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────
def main():
    inject_css()
    if not st.session_state.logged_in:
        login_page()
        return
    page = render_sidebar()
    if   page=="🏠 Home":       home_page()
    elif page=="📦 My Pantry":  pantry_page()
    elif page=="➕ Add Item":   add_item_page()
    elif page=="🤖 AI Recipes": ai_recipes_page()
    elif page=="📊 Dashboard":  dashboard_page()
    elif page=="⚙️ Settings":  settings_page()

if __name__=="__main__":
    main()