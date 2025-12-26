import os
from datetime import datetime
from typing import Optional, List, Any, Dict
from bson.objectid import ObjectId
from pymongo import MongoClient, ASCENDING, DESCENDING
from pymongo.collection import Collection
from dotenv import load_dotenv
import bcrypt 

# ---------------- ENV ----------------
load_dotenv()

MONGO_URL = os.getenv("MONGO_URL")
if not MONGO_URL:
    raise RuntimeError("MONGO_URL not set in .env")

client = MongoClient(MONGO_URL)
db = client["ai_project_db"]

# ---------------- COLLECTIONS ----------------
users: Collection = db["users"]
books: Collection = db["books"]
summaries: Collection = db["summaries"]


# ---------------- HELPERS ----------------
def oid(value):
    return ObjectId(value) if not isinstance(value, ObjectId) else value


def serialize(doc):
    if not doc:
        return None
    doc["_id"] = str(doc["_id"])
    if "user_id" in doc:
        doc["user_id"] = str(doc["user_id"])
    if "book_id" in doc:
        doc["book_id"] = str(doc["book_id"])
    return doc


# ==================================================
#                    USER
# ==================================================

def create_user(name, email, password, role="user"):
    if users.find_one({"email": email}):
        raise ValueError("Email already exists")

    password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt())

    user = {
        "name": name,
        "email": email,
        "password_hash": password_hash,
        "role": role,
        "created_at": datetime.utcnow()
    }

    return users.insert_one(user).inserted_id


def get_user_by_email(email):
    return users.find_one({"email": email})


def verify_user_password(email, password):
    user = get_user_by_email(email)
    if not user:
        return False
    return bcrypt.checkpw(password.encode(), user["password_hash"])


# ==================================================
#                    BOOKS
# ==================================================

def create_book(user_id, title, author=None, chapter=None,
                file_path=None, raw_text=None):

    book = {
        "user_id": oid(user_id),
        "title": title,
        "author": author,
        "chapter": chapter,
        "file_path": file_path,
        "raw_text": raw_text,
        "uploaded_at": datetime.utcnow(),
        "status": "uploaded"
    }

    return books.insert_one(book).inserted_id


def update_book_status(book_id, status):
    books.update_one(
        {"_id": oid(book_id)},
        {"$set": {"status": status}}
    )


def get_book_by_id(book_id):
    return books.find_one({"_id": oid(book_id)})


# 🔥 REQUIRED FOR HISTORY PAGE
def get_books_by_user(user_id):
    """
    Returns all books uploaded by a specific user
    """
    return list(
        books.find({"user_id": oid(user_id)})
        .sort("uploaded_at", -1) #DESCENDING
    )


# ==================================================
#                    SUMMARY
# ==================================================

def create_summary(book_id, user_id, summary_text,
                   summary_length="medium",
                   summary_style="simple",
                   chunk_summaries=None,
                   processing_time=0.0):

    summary = {
        "book_id": oid(book_id),
        "user_id": oid(user_id),
        "summary_text": summary_text,
        "summary_length": summary_length,
        "summary_style": summary_style,
        "chunk_summaries": chunk_summaries or [],
        "processing_time": float(processing_time),
        "created_at": datetime.utcnow()
    }

    return summaries.insert_one(summary).inserted_id


# 🔥 REQUIRED FOR HISTORY PAGE
def get_summary_by_book(book_id):
    return summaries.find_one({"book_id": oid(book_id)})

def get_summaries_by_user(user_id):
    cursor = summaries.find({"user_id": oid(user_id)})
    return [serialize(s) for s in cursor]


# ==================================================
#                SEARCH / FILTER (TASK 7)
# ==================================================
def search_books(
    user_id,
    search=None,
    status=None,
    sort_by="uploaded_at",
    order="desc",
    page=1,
    limit=5
):
    query = {"user_id": oid(user_id)}

    # 🔍 Search
    if search:
        query["$or"] = [
            {"title": {"$regex": search, "$options": "i"}},
            {"author": {"$regex": search, "$options": "i"}}
        ]

    # 🔖 Status filter
    if status:
        query["status"] = status

    # 🔃 Sorting
    sort_field = sort_by
    sort_order = DESCENDING if order == "desc" else ASCENDING

    skip = (page - 1) * limit

    cursor = books.find(query)\
                  .sort(sort_field, sort_order)\
                  .skip(skip)\
                  .limit(limit)

    total = books.count_documents(query)

    return list(cursor),total


#================2 auth.py
import streamlit as st
from utils.database import create_user, get_user_by_email, verify_user

def show_auth_page():
    st.title("🔐 AI Book Platform")

    tab1, tab2 = st.tabs(["Login", "Sign Up"])

    # -------- LOGIN --------
    with tab1:
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")

        if st.button("Login", use_container_width=True):
            user = verify_user(email, password)
            if not user:
                st.error("Invalid email or password")
                return

            st.session_state.logged_in = True
            st.session_state.user_id = str(user["_id"])
            st.session_state.user_name = user["name"]
            st.rerun()

    # -------- SIGN UP --------
    with tab2:
        name = st.text_input("Name")
        email = st.text_input("Email ")
        password = st.text_input("Password ", type="password")

        if st.button("Create Account", use_container_width=True):
            if get_user_by_email(email):
                st.error("Email already exists")
                return

            create_user(name, email, password)
            st.success("Account created. Please login.")
#### upload.py


import streamlit as st
from utils.database import create_book, save_summary
from utils.full_summary import summarize_large_text

def show_upload_page(user_id):
    if not user_id:
        st.error("Please login again")
        return

    st.header("📤 Upload Book")

    title = st.text_input("Book Title")
    text = st.text_area("Paste book content", height=300)

    if st.button("Generate Summary 🚀", use_container_width=True):
        if not title or not text:
            st.warning("All fields required")
            return

        with st.spinner("Summarizing..."):
            summary = summarize_large_text(text)

        book_id = create_book(user_id, title, text)
        save_summary(book_id, user_id, summary)

        st.success("Summary generated 🎉")
        st.text_area("Summary", summary, height=250)
 #### upload.py 


 import streamlit as st
import os
from docx import Document
import PyPDF2
from utils.database import create_book, save_summary,update_book_status
from utils.full_summary import summarize_large_text
from utils.database import books   # 👈 add import

update_book_status(book_id, "summarized")


MAX_FILE_SIZE_MB = 10

# ---------- FILE TEXT EXTRACTORS ----------
def extract_text_from_txt(file):
    return file.getvalue().decode("utf-8", errors="ignore")

def extract_text_from_pdf(file):
    reader = PyPDF2.PdfReader(file)
    text = ""
    for page in reader.pages:
        if page.extract_text():
            text += page.extract_text() + "\n"
    return text

def extract_text_from_docx(file):
    doc = Document(file)
    return "\n".join(p.text for p in doc.paragraphs)


# ---------- UPLOAD PAGE ----------
def show_upload_page(user_id):
    if not user_id:
        st.error("Please login again")
        return

    st.header("📤 Upload Book")

    uploaded_file = st.file_uploader(
        "Upload TXT / PDF / DOCX (Max 10MB)",
        type=["txt", "pdf", "docx"]
    )

    title = st.text_input("📘 Book Title")
    author = st.text_input("✍️ Author (optional)")   # ✅ add this
    extracted_text = None

    # ---------- FILE VALIDATION ----------
    if uploaded_file:
        file_size_mb = uploaded_file.size / (1024 * 1024)

        if file_size_mb > MAX_FILE_SIZE_MB:
            st.error("❌ File size exceeds 10 MB limit")
            return

        try:
            if uploaded_file.name.endswith(".txt"):
                extracted_text = extract_text_from_txt(uploaded_file)

            elif uploaded_file.name.endswith(".pdf"):
                extracted_text = extract_text_from_pdf(uploaded_file)

            elif uploaded_file.name.endswith(".docx"):
                extracted_text = extract_text_from_docx(uploaded_file)

            st.success("✅ File uploaded successfully")
            st.text_area("📄 File Preview (first 1000 chars)",
                         extracted_text[:1000],
                         height=200)

        except Exception as e:
            st.error(f"File read error: {e}")
            return

    # ---------- GENERATE SUMMARY ----------
    if st.button("🚀 Generate Summary", use_container_width=True):

        if not uploaded_file or not title or not extracted_text:
            st.warning("Please upload file and enter title")
            return

        with st.spinner("🤖 Generating AI summary..."):
            summary = summarize_large_text(extracted_text)

        # Save to DB
        book_id = create_book(user_id, title, extracted_text)
        save_summary(book_id, user_id, summary)
        # ✅ UPDATE STATUS
    from utils.database import books
books.update_one(
    {"_id": book_id},
    {"$set": {"status": "summarized"}}
)

st.success("🎉 Summary generated successfully")
st.balloons()   # 🎈 CELEBRATION

st.subheader("📑 Summary")
st.text_area("Generated Summary", summary, height=300)

##history.py

import streamlit as st
from utils.database import get_books, get_summary

def show_history_page(user_id):
    st.header("📚 History")

    books = get_books(user_id)
    if not books:
        st.info("No uploads yet")
        return

    for b in books:
        with st.expander(b["title"]):
            s = get_summary(b["_id"])
            if s:
                st.write(s["summary"])
            else:
                st.warning("Summary not found")

