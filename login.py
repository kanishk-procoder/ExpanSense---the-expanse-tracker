import streamlit as st
from auth import login_user, create_user

def login_page():
    st.title("🔐 Login / Register")

    action = st.radio("Select", ["Login", "Register"])

    if action == "Login":
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            user_id = login_user(username, password)
            if user_id:
                st.session_state.logged_in = True
                st.session_state.user_id = user_id
                st.success("Login successful!")
                st.experimental_rerun()
            else:
                st.error("Invalid credentials")

    else:
        username = st.text_input("New Username")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        if st.button("Register"):
            if create_user(username, email, password):
                st.success("Registered! Now login.")
            else:
                st.warning("Username already taken")
