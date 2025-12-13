# scripts/run_pipeline.py
import sys
import os

# Add project root folder to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.database import (
    create_book,
    update_book_status,
    create_summary,
    get_user_by_email,
)
from datetime import datetime
import time

# -----------------------------
# Fake AI Summary generator
# -----------------------------
def generate_ai_summary(text, length="short", style="paragraphs"):
    if not text:
        return "No text found."

    base_summary = f"This is a {length} summary generated in {style} format."
    return base_summary


# -----------------------------
# Chunk text into small parts
# -----------------------------
def chunk_text(raw_text, chunk_size=300):
    words = raw_text.split()
    chunks = []
    for i in range(0, len(words), chunk_size):
        chunk_str = " ".join(words[i:i + chunk_size])
        chunks.append(chunk_str)
    return chunks


# -----------------------------
# MAIN PIPELINE
# -----------------------------
def run_pipeline(user_email, title, raw_text):
    print("\n--- Starting Summarization Pipeline ---\n")

    # 1. find user
    user = get_user_by_email(user_email)
    if not user:
        raise ValueError("User not found. Please create a user first.")

    user_id = user["_id"]

    # 2. create book entry
    print("📌 Creating book record...")
    book_id = create_book(user_id=user_id, title=title, raw_text=raw_text)
    print("✔ Book created:", book_id)

    update_book_status(book_id, "processing")

    # 3. chunk text
    print("📌 Splitting text into chunks...")
    chunks = chunk_text(raw_text)
    print("✔ Total chunks:", len(chunks))

    # 4. generate chunk summaries
    chunk_summaries = []
    start_time = time.time()

    for i, ch in enumerate(chunks, start=1):
        s = generate_ai_summary(ch, length="short", style="paragraphs")
        chunk_summaries.append({"chunk": i, "text": s})

    # 5. combine final summary
    full_summary = " ".join([c["text"] for c in chunk_summaries])

    end_time = time.time()
    total_time = round(end_time - start_time, 2)

    # 6. save summary in DB
    print("📌 Saving final summary...")
    summary_id = create_summary(
        book_id=book_id,
        user_id=user_id,
        summary_text=full_summary,
        summary_length="short",
        summary_style="paragraphs",
        chunk_summaries=chunk_summaries,
        processing_time=total_time
    )

    update_book_status(book_id, "completed")

    print("\n✔ Pipeline completed!")
    print("📚 Book ID:", book_id)
    print("📝 Summary ID:", summary_id)
    print("⏱ Total processing time:", total_time, "seconds")

    return summary_id



if __name__ == "__main__":
    # DEMO RUN
    run_pipeline(
        user_email="test@example.com",
        title="My Test Book",
        raw_text="This is sample text that will be summarized."
    )
