import bcrypt
from utils.database import get_user_by_email, insert_user  #  DB helpers
from datetime import datetime
import uuid


# ---------------------- VALIDATION HELPERS ---------------------- #
def validate_email(email):
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email)


def validate_password(password):
    import re
    pattern = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$'
    return re.match(pattern, password)


# ---------------------- REGISTER USER --------------------------- #
def register_user(name, email, password):
    try:
        # Backend validation (never trust frontend only)
        if not name or len(name) < 2:
            return False, "Name must be at least 2 characters"

        if not validate_email(email):
            return False, "Invalid email format"

        if not validate_password(password):
            return False, "Password is too weak"

        # Check if user already exists
        existing_user = get_user_by_email(email)
        if existing_user:
            return False, "Email already registered"

        # Hash password
        password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt(12)).decode()

        # Create user record
        user_data = {
            "user_id": str(uuid.uuid4()),
            "name": name,
            "email": email,
            "password_hash": password_hash,
            "role": "user",
            "created_at": datetime.utcnow()
        }

        # Insert into database
        insert_user(user_data)

        return True, "User registered successfully"

    except Exception as e:
        return False, f"Registration failed: {str(e)}"


# ---------------------- LOGIN USER ------------------------------ #
def login_user(email, password):
    try:
        user = get_user_by_email(email)

        # Do not reveal correct reason
        if not user:
            return False, "Invalid email or password"

        stored_hash = user["password_hash"].encode()

        if not bcrypt.checkpw(password.encode(), stored_hash):
            return False, "Invalid email or password"

        return True, {
            "user_id": user["user_id"],
            "name": user["name"],
            "email": user["email"],
            "role": user["role"],
        }

    except Exception as e:
        return False, f"Login error: {str(e)}"


# ---------------------- SESSION HELPERS -------------------------- #
def start_session(st, user_data):
    st.session_state["logged_in"] = True
    st.session_state["user_id"] = user_data["user_id"]
    st.session_state["user_name"] = user_data["name"]
    st.session_state["user_email"] = user_data["email"]
    st.session_state["user_role"] = user_data["role"]


def is_logged_in(st):
    return st.session_state.get("logged_in", False)


def get_current_user(st):
    if not is_logged_in(st):
        return None
    return {
        "user_id": st.session_state["user_id"],
        "name": st.session_state["user_name"],
        "email": st.session_state["user_email"],
        "role": st.session_state["user_role"],
    }


def logout(st):
    st.session_state.clear()
