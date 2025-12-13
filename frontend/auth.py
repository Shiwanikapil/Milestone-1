# frontend/auth.py
import sys, os, re, time
import streamlit as st

# make sure project root is on path so "utils" imports work when run from streamlit
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utils.database import create_user, get_user_by_email, verify_user_password

def is_valid_email(email):
    return re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", email)

def is_strong_password(password):
    return (
        len(password) >= 8 and 
        any(c.isupper() for c in password) and
        any(c.islower() for c in password) and
        any(c.isdigit() for c in password) and
        any(c in "!@#$%^&*()-_=+[]{}|;:'\",.<>/?`~" for c in password)
    )

def show_auth_page():
    st.set_page_config(page_title="Auth System", layout="centered")
    # session defaults
    if "page" not in st.session_state:
        st.session_state.page = "register"
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    if "user_name" not in st.session_state:
        st.session_state.user_name = ""

    def go_to_login():
        st.session_state.page = "login"
    def go_to_register():
        st.session_state.page = "register"
    def logout():
        st.session_state.logged_in = False
        st.session_state.user_name = ""
        st.session_state.page = "login"

    # small CSS
    st.markdown("""
    <style>
      .stApp { background: linear-gradient(135deg,#0f2027,#203a43,#2c5364); color: #fff; }
      .form-container{ background: rgba(0,0,0,0.6); padding:30px; border-radius:12px; max-width:520px; margin:auto; margin-top:40px; }
      .stButton>button{ background: linear-gradient(90deg,#4facfe,#00f2fe); color:#fff; border-radius:8px; padding:8px 14px; }
      .header{ text-align:center; font-size:28px; margin-bottom:10px; font-weight:600; }
      .link{ text-align:center; color:#4facfe; cursor:pointer; margin-top:10px; }
    </style>
    """, unsafe_allow_html=True)

    # If already logged in => show welcome & logout
    if st.session_state.logged_in:
        st.markdown(f"<h2 style='text-align:center;'>Welcome, {st.session_state.user_name} 👋</h2>", unsafe_allow_html=True)
        st.write("---")
        if st.button("Logout"):
            logout()
            st.rerun()

        return

    # REGISTER PAGE
    if st.session_state.page == "register":
        st.markdown('<div class="form-container">', unsafe_allow_html=True)
        st.markdown('<div class="header">Create Account</div>', unsafe_allow_html=True)
        with st.form("register_form"):
            name = st.text_input("Full Name")
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            confirm_password = st.text_input("Confirm Password", type="password")
            register_btn = st.form_submit_button("Sign Up")
            if register_btn:
                if len(name) < 2:
                    st.error("Name must be at least 2 characters.")
                elif not is_valid_email(email):
                    st.error("Invalid email format.")
                elif not is_strong_password(password):
                    st.error("Weak password! Must contain uppercase, lowercase, number, special char.")
                elif password != confirm_password:
                    st.error("Passwords do not match!")
                elif get_user_by_email(email):
                    st.error("Email already registered!")
                else:
                    create_user(name=name, email=email, password=password)
                    st.success("Account created successfully! Redirecting to Login...")
                    time.sleep(1.2)
                    st.session_state.page = "login"
                    st.rerun()

        st.markdown('<div class="link">Already have an account? <a href="#" onclick="window.location.reload()">Login</a></div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # LOGIN PAGE
    if st.session_state.page == "login":
        st.markdown('<div class="form-container">', unsafe_allow_html=True)
        st.markdown('<div class="header">Login</div>', unsafe_allow_html=True)
        with st.form("login_form"):
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            login_btn = st.form_submit_button("Login")
            if login_btn:
                user = get_user_by_email(email)
                # security: don't be too specific in messages (but helpful for dev)
                if not user:
                    st.error("Invalid credentials.")
                elif not verify_user_password(email, password):
                    st.error("Invalid credentials.")
                else:
                    st.success("Login successful! Redirecting...")
                    st.session_state.logged_in = True
                    st.session_state.user_name = user.get("name", "")
                    time.sleep(0.8)
                    st.rerun()

        st.markdown('<div class="link">Don\'t have an account? <a href="#" onclick="window.location.reload()">Register</a></div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
