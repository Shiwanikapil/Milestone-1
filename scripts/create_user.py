from utils.database import create_user, get_user_by_email

if __name__ == "__main__":
    email = "test@example.com"
    name = "Test User"
    password = "test123"   # temporary password

    # Check if user already exists
    if get_user_by_email(email):
        print("User already exists!")
    else:
        user_id = create_user(name=name, email=email, password=password)
        print("User created successfully!")
        print("User ID:", user_id)
