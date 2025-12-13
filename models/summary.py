# models/summary.py
from datetime import datetime
from utils.database import create_summary, get_summaries_by_user

class Summary:
    def __init__(self, book_id, user_id, summary_text, length, style, chunk_summaries, processing_time):
        self.book_id = book_id
        self.user_id = user_id
        self.summary_text = summary_text
        self.length = length
        self.style = style
        self.chunk_summaries = chunk_summaries
        self.processing_time = processing_time
        self.created_at = datetime.utcnow()

    def save(self):
        return create_summary(
            self.book_id,
            self.user_id,
            self.summary_text,
            self.length,
            self.style,
            self.chunk_summaries,
            self.processing_time
        )

    @staticmethod
    def get_by_user(user_id):
        return get_summaries_by_user(user_id)
