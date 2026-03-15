import streamlit as st
import re
from datetime import date, timedelta
from database import get_all_items, get_expiring_items, add_item, delete_item, update_item, log_usage, create_tables
from ai_recipes import get_recipe_suggestions, chat_with_ai

# Initialize database tables when app starts
create_tables()

st.set_page_config(page_title="FreshMind", page_icon="🥬", layout="wide")

# ─────────────────────────────────────────
# SIDEBAR NAVIGATION
# ─────────────────────────────────────────
st.sidebar.title("🥬 FreshMind")
st.sidebar.markdown("*Your Smart Pantry Assistant*")
st.sidebar.markdown("---")
page = st.sidebar.radio("Navigate", ["🏠 Pantry", "➕ Add Item", "🤖 AI Recipes", "📊 Dashboard"])
st.sidebar.markdown("---")
st.sidebar.caption("FreshMind v1.0 | Person B Frontend")


# ─────────────────────────────────────────
# HELPER FUNCTION
# ─────────────────────────────────────────
def parse_quantity(qty_str):
    """Extract number and unit from quantity string like 1L, 200g, 12pcs"""
    numbers = re.findall(r'\d+\.?\d*', str(qty_str))
    units = re.findall(r'[a-zA-Z]+', str(qty_str))
    number = float(numbers[0]) if numbers else 0
    unit = units[0] if units else "pcs"
    return number, unit


# ─────────────────────────────────────────
# PAGE 1 — PANTRY VIEW
# ─────────────────────────────────────────
def show_pantry():
    st.title("🏠 My Pantry")

    # Get real items from database
    items = get_all_items()

    if not items:
        st.warning("Your pantry is empty! Add some items.")
        return

    today = date.today()

    # Convert to list of dicts
    items = [dict(item) for item in items]

    # Summary metrics
    total = len(items)
    expiring_soon = len([i for i in items if (date.fromisoformat(str(i["expiry_date"])) - today).days <= 7])
    critical = len([i for i in items if (date.fromisoformat(str(i["expiry_date"])) - today).days <= 3])

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Items", total)
    with col2:
        st.metric("Expiring This Week", expiring_soon)
    with col3:
        st.metric("Critical (< 3 days)", critical)

    st.markdown("---")
    st.markdown("**Color Guide:** 🔴 Less than 3 days &nbsp;&nbsp; 🟠 Less than 7 days &nbsp;&nbsp; 🟢 Safe")
    st.markdown("---")

    # Display each item
    for item in items:
        expiry = date.fromisoformat(str(item["expiry_date"]))
        days_left = (expiry - today).days

        if days_left <= 3:
            color = "#ffcccc"
            badge = "🔴 URGENT"
        elif days_left <= 7:
            color = "#ffe5cc"
            badge = "🟠 SOON"
        else:
            color = "#ccffcc"
            badge = "🟢 SAFE"

        st.markdown(
            f"""<div style="background-color: {color}; padding: 12px 20px;
            border-radius: 8px; margin-bottom: 8px;">
            <b>{item['name']}</b> | {item['category']} |
            Qty: {item['quantity']} | Expires: {item['expiry_date']} |
            Days left: <b>{days_left}</b> | {badge}
            </div>""",
            unsafe_allow_html=True
        )

        current_num, current_unit = parse_quantity(item["quantity"])
        col_qty, col_used, col_btn, col_del = st.columns([2, 2, 1, 1])

        with col_qty:
            st.markdown(f"**Current:** {item['quantity']}")

        with col_used:
            used = st.number_input(
                f"Amount used ({current_unit})",
                min_value=0.0,
                max_value=float(current_num),
                value=0.0,
                step=1.0,
                key=f"used_{item['id']}"
            )

        with col_btn:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Update", key=f"upd_{item['id']}"):
                remaining = current_num - used
                if remaining <= 0:
                    st.error(f"{item['name']} is finished!")
                    log_usage(item['name'], was_wasted=False)
                else:
                    new_qty = f"{remaining}{current_unit}"
                    update_item(item['id'], quantity=new_qty)
                    st.success(f"Updated! {item['name']} remaining: {new_qty}")
                    st.rerun()

        with col_del:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Delete", key=f"del_{item['id']}"):
                delete_item(item['id'])
                log_usage(item['name'], was_wasted=False)
                st.success(f"{item['name']} removed!")
                st.rerun()

    st.markdown("---")
    expiring = get_expiring_items(days=7)
    if expiring:
        st.error(f"⚠️ {len(expiring)} item(s) expiring within 7 days — use them soon!")


# ─────────────────────────────────────────
# PAGE 2 — ADD ITEM
# ─────────────────────────────────────────
def show_add_item():
    st.title("➕ Add New Item")

    with st.form("add_item_form"):
        st.subheader("Item Details")

        col1, col2 = st.columns(2)

        with col1:
            name = st.text_input("Item Name", placeholder="e.g. Milk")
            quantity_num = st.number_input("Quantity", min_value=0.1, value=1.0, step=0.5)
            quantity_unit = st.selectbox("Unit", ["g", "kg", "L", "ml", "pcs"])
            category = st.selectbox("Category", [
                "Dairy", "Vegetables", "Fruits",
                "Meat", "Seafood", "Grains",
                "Beverages", "Snacks", "Other"
            ])

        with col2:
            purchase_date = st.date_input("Purchase Date", value=date.today())
            expiry_date = st.date_input(
                "Expiry Date",
                value=date.today() + timedelta(days=7)
            )

        submitted = st.form_submit_button("Add to Pantry")

        if submitted:
            if not name:
                st.error("Please enter item name!")
            elif expiry_date <= purchase_date:
                st.error("Expiry date must be after purchase date!")
            else:
                quantity = f"{quantity_num}{quantity_unit}"
                add_item(
                    name=name,
                    quantity=quantity,
                    purchase_date=str(purchase_date),
                    expiry_date=str(expiry_date),
                    category=category
                )
                st.success(f"✅ {name} added to pantry successfully!")
                st.balloons()


# ─────────────────────────────────────────
# PAGE 3 — AI RECIPES
# ─────────────────────────────────────────
def show_ai_recipes():
    st.title("🤖 AI Recipe Suggestions")

    # Initialize chat history
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "recipes_generated" not in st.session_state:
        st.session_state.recipes_generated = False

    # Preference input
    st.subheader("Get Recipe Suggestions")
    preference = st.text_input(
        "Any preference? (optional)",
        placeholder="e.g. vegetarian, quick meal, spicy"
    )

    if st.button("🍽️ Suggest Recipes with Expiring Items"):
        with st.spinner("AI is thinking..."):
            recipes = get_recipe_suggestions(preference=preference if preference else None)
            st.session_state.recipes_generated = True
            st.session_state.last_recipes = recipes

    # Show recipes
    if st.session_state.recipes_generated:
        st.markdown("---")
        st.subheader("Suggested Recipes")
        st.markdown(st.session_state.last_recipes)

        # Chat section
        st.markdown("---")
        st.subheader("Ask Follow-up Questions")

        # Show chat history
        for msg in st.session_state.chat_history:
            if msg["role"] == "user":
                st.chat_message("user").write(msg["content"])
            else:
                st.chat_message("assistant").write(msg["content"])

        # Chat input
        user_input = st.chat_input("Ask anything about recipes...")
        if user_input:
            with st.spinner("AI is responding..."):
                reply, updated_history = chat_with_ai(
                    user_input,
                    st.session_state.chat_history
                )
                st.session_state.chat_history = updated_history
                st.rerun()


# ─────────────────────────────────────────
# PAGE 4 — DASHBOARD
# ─────────────────────────────────────────
def show_dashboard():
    st.title("📊 Dashboard")
    st.info("Charts coming soon — Building on Day 4!")


# ─────────────────────────────────────────
# PAGE ROUTER
# ─────────────────────────────────────────
if page == "🏠 Pantry":
    show_pantry()
elif page == "➕ Add Item":
    show_add_item()
elif page == "🤖 AI Recipes":
    show_ai_recipes()
elif page == "📊 Dashboard":
    show_dashboard()