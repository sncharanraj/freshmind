# auth.py
# Handles user authentication for FreshMind
# Owned by Person B (Frontend)

import json
import os
import hashlib

USERS_FILE = "users.json"

def load_users():
    """Load all users from users.json"""
    if not os.path.exists(USERS_FILE):
        return {"users": []}
    with open(USERS_FILE, "r") as f:
        return json.load(f)

def save_users(data):
    """Save users to users.json"""
    with open(USERS_FILE, "w") as f:
        json.dump(data, f, indent=4)

def hash_password(password):
    """Convert password to secure hash"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_user(email, password):
    """
    Check if email and password are correct.
    Returns user dict if correct, None if wrong.
    """
    data = load_users()
    hashed = hash_password(password)
    for user in data["users"]:
        if user["email"] == email and user["password"] == hashed:
            return user
    return None

def create_user(name, email, password):
    """
    Register a new user.
    Returns True if created, False if email already exists.
    """
    data = load_users()
    # Check if email already exists
    for user in data["users"]:
        if user["email"] == email:
            return False
    # Add new user
    data["users"].append({
        "name": name,
        "email": email,
        "password": hash_password(password)
    })
    save_users(data)
    return True

def is_logged_in():
    """Check if user is currently logged in"""
    import streamlit as st
    return st.session_state.get("logged_in", False)

def logout():
    """Log out the current user"""
    import streamlit as st
    st.session_state.logged_in = False
    st.session_state.user = None