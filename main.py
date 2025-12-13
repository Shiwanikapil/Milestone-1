# main.py
import sys, os
import streamlit as st

# ensure project root in path
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from frontend.auth import show_auth_page
from frontend.upload import show_upload_page
from frontend.search import show_search_page   # <-- NEW (if search.py exists)

st.set_page_config(page_title="AI Project", layout="centered")

# initialize session variables
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "user_id" not in st.session_state:
    st.session_state.user_id = None

if "user_name" not in st.session_state:
    st.session_state.user_name = ""

# Sidebar Navigation
st.sidebar.title("Navigation")

if st.session_state.logged_in:
    page = st.sidebar.radio(
        "Go to", 
        ["Upload", "Search", "Logout"]
    )
else:
    page = st.sidebar.radio(
        "Go to",
        ["Auth (Login/SignUp)"]
    )


# Page Routing
if page == "Auth (Login/SignUp)":
    show_auth_page()

elif page == "Upload":
    if not st.session_state.logged_in:
        st.error("Please login first.")
    else:
        show_upload_page(st.session_state.user_id)

elif page == "Search":
    if not st.session_state.logged_in:
        st.error("Please login first.")
    else:
        show_search_page(st.session_state.user_id)

elif page == "Logout":
    st.session_state.logged_in = False
    st.session_state.user_id = None
    st.session_state.user_name = ""
    st.success("Logged out successfully!")
    st.rerun()
