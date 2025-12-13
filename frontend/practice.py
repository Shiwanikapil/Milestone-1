import streamlit as st
import re
import time

# --------------------------
# PAGE CONFIG & CUSTOM CSS
# --------------------------
st.set_page_config(page_title="User Authentication", layout="centered")

st.markdown("""
<style>
    /* Gradient background */
    .stApp {
        background: linear-gradient(135deg, #0f2027, #203a43, #2c5364);
        color: #ffffff;
    }

    /* Form container */
    .form-container {
        background-color: blue(0,0,0,0.6);
        padding: 40px;
        border-radius: 15px;
        box-shadow: 0 8px 32px 0 rgba( 31, 38, 135, 0.37 );
        max-width: 450px;
        margin: auto;
        margin-top: 50px;
    }

    /* Inputs */
    .stTextInput>div>div>input {
        border-radius: 10px;
        padding: 10px;
        border: none;
    }

    /* Buttons */
    .stButton>button {
        background: black(to right, #4facfe, #00f2fe);
        color: #fff;
        font-weight: bold;
        border-radius: 10px;
        padding: 10px 20px;
        transition: transform 0.2s ease-in-out, box-shadow 0.2s ease-in-out;
    }
    .stButton>button:hover {
        transform: scale(1.05);
        box-shadow: 0px 0px 15px 0px #00f2fe;
    }

    /* Centered header */
    .header {
        text-align: center;
        font-size: 32px;
        font-weight: bold;
        margin-bottom: 20px;
    }

    </style>
""", unsafe_allow_html=True)

# --------------------------
# REGEX VALIDATION PATTERNS
# --------------------------
email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
password_pattern = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@#$%^&+=!]).{8,}$'

# Choose Page Type
page = st.sidebar.selectbox("Select Page", ["Login", "Register"])


# ==========================================================
#  REGISTER PAGE
# ==========================================================
if page == "Register":
    st.markdown("<p class='title'>Create Account</p>", unsafe_allow_html=True)
    st.markdown("<p class='subtitle'>Please fill the details below</p>", unsafe_allow_html=True)
    
    with st.form("register_form"):
        full_name = st.text_input("Full Name")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        confirm_password = st.text_input("Confirm Password", type="password")

        submitted = st.form_submit_button("Register")

    # --------------------------
    # VALIDATION LOGIC
    # --------------------------
    if submitted:
        errors = False

        # Validate Full Name
        if len(full_name.strip()) < 2 or not full_name.replace(" ", "").isalpha():
            st.markdown("<p class='error-text'>❌ Name must contain only letters & at least 2 characters</p>", unsafe_allow_html=True)
            errors = True

        # Validate Email
        if not re.match(email_pattern, email):
            st.markdown("<p class='error-text'>❌ Invalid email format</p>", unsafe_allow_html=True)
            errors = True

        # Validate Password
        if not re.match(password_pattern, password):
            st.markdown("<p class='error-text'>❌ Password must include 8+ chars, uppercase, lowercase, number, special character</p>", unsafe_allow_html=True)
            errors = True

        # Validate Confirm Password
        if password != confirm_password:
            st.markdown("<p class='error-text'>❌ Passwords do not match</p>", unsafe_allow_html=True)
            errors = True

        # If NO ERRORS → SUCCESS
        if not errors:
            with st.spinner("Creating your account..."):
                time.sleep(1.5)

            st.success("🎉 Registration successful! You can now login.")


# ==========================================================
# LOGIN PAGE
# ==========================================================
if page == "Login":
    st.markdown("<p class='title'>Welcome Back!</p>", unsafe_allow_html=True)
    st.markdown("<p class='subtitle'>Login to continue</p>", unsafe_allow_html=True)

    with st.form("login_form"):
        login_email = st.text_input("Email")
        login_password = st.text_input("Password", type="password")
        remember = st.checkbox("Remember Me")
        login_button = st.form_submit_button("Login")

    if login_button:

        if login_email == "" or login_password == "":
            st.error("❌ Please fill all fields")
        else:
            with st.spinner("Authenticating..."):
                time.sleep(1.5)

            # Dummy check (you will connect to DB in Task 4)
            st.success("✅ Logged in successfully!")


# END OF FILE

            
            