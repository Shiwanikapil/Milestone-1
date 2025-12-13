# utils/init_db.py
from database import db

def init_db():
    # Users: unique index on email
    db.users.create_index([("email", 1)], unique=True)
    # Books: index user_id and status
    db.books.create_index([("user_id", 1)])
    db.books.create_index([("status", 1)])
    # Summaries: index user_id and book_id
    db.summaries.create_index([("user_id", 1)])
    db.summaries.create_index([("book_id", 1)])
    print("Indexes created successfully")

if __name__ == "__main__":
    init_db()

