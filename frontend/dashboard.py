import streamlit as st

def dashboard_page():
    st.set_page_config(page_title="Dashboard", layout="wide")

    # Check Login
    if "is_logged_in" not in st.session_state or st.session_state.is_logged_in == False:
        st.error("Please login to access the dashboard.")
        st.stop()

    username = st.session_state.get("username", "User")

    # Sidebar Navigation
    st.sidebar.title("📌 Navigation")
    page = st.sidebar.radio("Go to", ["Dashboard", "Upload Book", "My Books", "Summaries", "Settings"])

    # Header
    st.markdown(f"<h1>Welcome, {username}! 👋</h1>", unsafe_allow_html=True)
    st.write("---")

    # MAIN DASHBOARD PAGE
    if page == "Dashboard":
        st.subheader("📊 Quick Stats")

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Books Uploaded", "0")
        with col2:
            st.metric("Summaries Generated", "0")
        with col3:
            st.metric("Recent Activity", "None")

        st.write("---")
        st.subheader("🕒 Recent Activity")
        st.info("No activity yet. Upload your first book!")

        st.write("---")
        st.subheader("🚀 Quick Actions")

        c1, c2 = st.columns(2)
        with c1:
            if st.button("📘 Upload New Book"):
                st.session_state.current_page = "Upload"
        with c2:
            if st.button("📄 View All Summaries"):
                st.session_state.current_page = "Summaries"

    elif page == "Upload Book":
        from frontend.upload import upload_page
        upload_page()

    elif page == "My Books":
        st.info("My Books page coming soon!")

    elif page == "Summaries":
        st.info("Summaries page coming soon!")

    elif page == "Settings":
        st.info("Settings page coming soon!")
