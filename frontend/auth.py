import streamlit as st
from utils.database import create_user, get_user_by_email, verify_user

# ---------- UI STYLE ----------
st.markdown("""
<style>
.auth-box {
    max-width: 420px;
    margin: auto;
    padding: 30px;
    background-color: #161B22;
    border-radius: 14px;
    box-shadow: 0px 0px 25px rgba(0,0,0,0.6);
}
.title {
    text-align: center;
    font-size: 28px;
    font-weight: 700;
}
.sub {
    text-align: center;
    color: #9BA3AF;
    margin-bottom: 20px;
}
.link-btn {
    background: none;
    border: none;
    color: #4CAF50;
    cursor: pointer;
    font-size: 14px;
}
</style>
""", unsafe_allow_html=True)


# ---------- AUTH PAGE ----------
def show_auth_page():

    if "auth_mode" not in st.session_state:
        st.session_state.auth_mode = "signup"   # default signup

    st.markdown("<div class='auth-box'>", unsafe_allow_html=True)

    if st.session_state.auth_mode == "signup":
        show_signup()
    else:
        show_login()

    st.markdown("</div>", unsafe_allow_html=True)


# ---------- SIGN UP ----------
def show_signup():
    st.markdown("<div class='title'>Create Account ✨</div>", unsafe_allow_html=True)
    st.markdown("<div class='sub'>Join Intelligent Book Summarization</div>", unsafe_allow_html=True)

    name = st.text_input("Full Name")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("🚀 Sign Up", use_container_width=True):
        if not name or not email or not password:
            st.warning("All fields are required")
            return

        if get_user_by_email(email):
            st.error("Account already exists. Please login.")
            return

        create_user(name, email, password)
        st.success("Account created successfully 🎉 Redirecting to login...")

        st.session_state.auth_mode = "login"
        st.rerun()

    st.write("")
    if st.button("Already have an account? Login"):
        st.session_state.auth_mode = "login"
        st.rerun()


# ---------- LOGIN ----------
def show_login():
    st.markdown("<div class='title'>Welcome Back 👋</div>", unsafe_allow_html=True)
    st.markdown("<div class='sub'>Login to continue</div>", unsafe_allow_html=True)

    email = st.text_input("Email", key="login_email")
    password = st.text_input("Password", type="password", key="login_pass")

    if st.button("🔓 Login", use_container_width=True):
        user = verify_user(email, password)
        if not user:
            st.error("Invalid email or password")
            return

        st.session_state.logged_in = True
        st.session_state.user_id = str(user["_id"])
        st.session_state.user_name = user["name"]

        st.success("Login successful 🎉")
        st.rerun()

    st.write("")
    if st.button("New user? Create account"):
        st.session_state.auth_mode = "signup"
        st.rerun()
