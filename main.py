import streamlit as st
from frontend.auth import show_auth_page
from frontend.upload import show_upload_page
from frontend.history import show_history_page
from frontend.search import show_search_page
st.set_page_config(
    page_title="AI Book Summarization",
    layout="centered",
    initial_sidebar_state="collapsed"
)

#st.set_page_config("AI Book Platform", layout="wide")

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    show_auth_page()
else:
    st.sidebar.title("📚 Navigation")
    page = st.sidebar.radio(
        "Menu",
        ["Upload", "History", "Search", "Logout"]
    )

    if page == "Upload":
        show_upload_page(st.session_state.user_id)

    elif page == "History":
        show_history_page(st.session_state.user_id)

    elif page == "Search":
        show_search_page(st.session_state.user_id)

    elif page == "Logout":
        st.session_state.clear()
        st.rerun()
