import streamlit as st
from mock_data import get_all_items, get_expiring_items

st.set_page_config(page_title="FreshMind", page_icon="", layout="wide")

st.sidebar.title("FreshMind - Smart Pantry")
st.sidebar.markdown("*Your Smart Pantry Assistant*")
st.sidebar.markdown("---")

page = st.sidebar.radio("Navigate", ["Pantry", "Add Item", "AI Recipes", "Dashboard"])

st.sidebar.markdown("---")
st.sidebar.caption("FreshMind v1.0 | Person B Frontend")

if page == "Pantry":
    st.title("My Pantry")
    st.info("Pantry View - Coming Day 2")
elif page == "Add Item":
    st.title("Add New Item")
    st.info("Add Item Form - Coming Day 3")
elif page == "AI Recipes":
    st.title("AI Recipe Suggestions")
    st.info("AI Recipes - Coming Day 4")
elif page == "Dashboard":
    st.title("Dashboard")
    st.info("Charts - Coming Day 5")
