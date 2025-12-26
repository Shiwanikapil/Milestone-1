# utils/database.py
import os
from datetime import datetime
from bson.objectid import ObjectId
from pymongo import MongoClient, DESCENDING
from dotenv import load_dotenv
import bcrypt

load_dotenv()

MONGO_URL = os.getenv("MONGO_URL")
client = MongoClient(MONGO_URL)
db = client["ai_project_db"]

users = db.users
books = db.books
summaries = db.summaries

def oid(x):
    return ObjectId(str(x))

# ---------- USER ----------
def create_user(name, email, password):
    pwd = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    users.insert_one({
        "name": name,
        "email": email,
        "password": pwd,
        "created_at": datetime.utcnow()
    })

def get_user_by_email(email):
    return users.find_one({"email": email})

def verify_user(email, password):
    u = get_user_by_email(email)
    if not u:
        return None
    if bcrypt.checkpw(password.encode(), u["password"]):
        return u
    return None

# ---------- BOOK ----------
def create_book(user_id, title,author, text):
    return books.insert_one({
        "user_id": oid(user_id),
        "title": title,
        "author": author,  
        "text": text,
        "created_at": datetime.utcnow()
    }).inserted_id

def update_book_status(book_id, status):
    books.update_one(
        {"_id": oid(book_id)},
        {"$set": {"status": status}}
    )


def get_books(user_id):
    return list(books.find(
        {"user_id": oid(user_id)}
    ).sort("created_at", DESCENDING))

def delete_book(book_id, user_id):
    summaries.delete_many({
        "book_id": oid(book_id),
        "user_id": oid(user_id)
    })

    books.delete_one({
        "_id": oid(book_id),
        "user_id": oid(user_id)
    })


# ---------- SUMMARY ----------
def save_summary(book_id, user_id, summary):
    summaries.insert_one({
        "book_id": oid(book_id),
        "user_id": oid(user_id),
        "summary": summary,
        "created_at": datetime.utcnow()
    })

def get_summary(book_id):
    return summaries.find_one({"book_id": oid(book_id)})

# ---------- SEARCH ----------
def search_books(user_id, title=None, status=None):
    q = {"user_id": oid(user_id)}

    if title:
        q["title"] = {"$regex": title, "$options": "i"}

    if status:
        q["status"] = status   # uploaded / summarized

    return list(books.find(q))

