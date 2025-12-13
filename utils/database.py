import os
from datetime import datetime
from typing import Optional, List, Any, Dict
from bson.objectid import ObjectId
from pymongo import MongoClient, ASCENDING, DESCENDING
from pymongo.collection import Collection
from dotenv import load_dotenv
import bcrypt

load_dotenv()

MONGO_URL = os.getenv("MONGO_URL")
if not MONGO_URL:
    raise RuntimeError("MONGO_URL not set in .env")

client = MongoClient(MONGO_URL)
db = client["ai_project_db"]

# Collections
users: Collection = db["users"]
books: Collection = db["books"]
summaries: Collection = db["summaries"]


def oid(value):
    return ObjectId(value) if not isinstance(value, ObjectId) else value


# ---------------- USER ----------------

def create_user(name, email, password, role="user"):
    if users.find_one({"email": email}):
        raise ValueError("Email already exists")

    password_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())

    user = {
        "name": name,
        "email": email,
        "password_hash": password_hash,
        "role": role,
        "created_at": datetime.utcnow(),
    }

    return users.insert_one(user).inserted_id


def get_user_by_email(email):
    return users.find_one({"email": email})


def verify_user_password(email, password):
    user = get_user_by_email(email)
    if not user:
        return False
    return bcrypt.checkpw(password.encode("utf-8"), user["password_hash"])


# ---------------- BOOKS ----------------

def create_book(user_id, title, author=None, chapter=None, file_path=None, raw_text=None):

    book = {
        "user_id": oid(user_id),
        "title": title,
        "author": author,
        "chapter": chapter,
        "file_path": file_path,
        "raw_text": raw_text,
        "uploaded_at": datetime.utcnow(),
        "status": "uploaded",
    }

    return books.insert_one(book).inserted_id


def update_book_status(book_id, status):
    books.update_one({"_id": oid(book_id)}, {"$set": {"status": status}})


def get_book_by_id(book_id):
    return books.find_one({"_id": oid(book_id)})


# ---------------- SUMMARY ----------------

def create_summary(book_id, user_id, summary_text,
                   summary_length, summary_style,
                   chunk_summaries, processing_time):

    summary = {
        "book_id": oid(book_id),
        "user_id": oid(user_id),
        "summary_text": summary_text,
        "summary_length": summary_length,
        "summary_style": summary_style,
        "chunk_summaries": chunk_summaries,
        "processing_time": float(processing_time),
        "created_at": datetime.utcnow(),
    }

    return summaries.insert_one(summary).inserted_id


# ---------------- SEARCH ----------------

def search_books(user_id, query=None, filter_by=None,
                 sort_by="date_desc", page=1, limit=10):

    mongo_query = {"user_id": oid(user_id)}

    if query:
        mongo_query["$or"] = [
            {"title": {"$regex": query, "$options": "i"}},
            {"author": {"$regex": query, "$options": "i"}},
        ]

    if filter_by == "summarized":
        mongo_query["status"] = "summarized"
    elif filter_by == "not_summarized":
        mongo_query["status"] = "uploaded"

    sort_options = {
        "date_desc": ("uploaded_at", DESCENDING),
        "date_asc": ("uploaded_at", ASCENDING),
        "title_asc": ("title", ASCENDING),
        "title_desc": ("title", DESCENDING),
    }
    sort_field, sort_order = sort_options.get(sort_by, ("uploaded_at", DESCENDING))

    skip = (page - 1) * limit

    cursor = books.find(mongo_query).sort(sort_field, sort_order).skip(skip).limit(limit)
    results = list(cursor)
    total = books.count_documents(mongo_query)

    return {
        "total": total,
        "page": page,
        "limit": limit,
        "results": results,
    }
