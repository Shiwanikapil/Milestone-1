# models/user.py
from datetime import datetime
from utils.database import create_user, get_user_by_email, verify_user_password

class User:
    def __init__(self, name, email, password, role="user"):
        self.name = name
        self.email = email
        self.password = password
        self.role = role
        self.created_at = datetime.utcnow()

    def save(self):
        return create_user(self.name, self.email, self.password, self.role)

    @staticmethod
    def find_by_email(email):
        return get_user_by_email(email)

    @staticmethod
    def verify_password(email, password):
        return verify_user_password(email, password)
