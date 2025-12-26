import streamlit as st
from utils.database import create_user, verify_user, get_user_by_email

def show_auth_page():
    st.title("🔐 AI Book Platform")

    tab1, tab2 = st.tabs(["Login", "Sign Up"])

    with tab1:
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")

        if st.button("Login", use_container_width=True):
            user = verify_user(email, password)
            if not user:
                st.error("Invalid credentials")
                return

            st.session_state.logged_in = True
            st.session_state.user_id = str(user["_id"])
            st.session_state.user_name = user["name"]
            st.rerun()

    with tab2:
        name = st.text_input("Name")
        email = st.text_input("Email ")
        password = st.text_input("Password ", type="password")

        if st.button("Create Account", use_container_width=True):
            if get_user_by_email(email):
                st.error("Email already exists")
                return

            create_user(name, email, password)
            st.success("Account created. Login now.")
