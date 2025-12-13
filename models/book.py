# models/book.py
from datetime import datetime
from utils.database import create_book, update_book_status, get_book_by_id

class Book:
    def __init__(self, user_id, title, author=None, chapter=None, file_path=None, raw_text=None):
        self.user_id = user_id
        self.title = title
        self.author = author
        self.chapter = chapter
        self.file_path = file_path
        self.raw_text = raw_text
        self.uploaded_at = datetime.utcnow()
        self.status = "uploaded"

    def save(self):
        return create_book(
            self.user_id,
            self.title,
            self.author,
            self.chapter,
            self.file_path,
            self.raw_text
        )

    @staticmethod
    def update_status(book_id, status):
        return update_book_status(book_id, status)

    @staticmethod
    def get(book_id):
        return get_book_by_id(book_id)
