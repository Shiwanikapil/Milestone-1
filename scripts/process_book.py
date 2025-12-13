# scripts/process_book.py

from utils.database import (
    create_summary,
    update_book_status,
    get_book_by_id
)


def process_book(book_id, user_id):
    """Simple dummy processor function"""

    # 1. Book retrieve
    book = get_book_by_id(book_id)
    if not book:
        print("Book not found")
        return None

    print(f"Processing book: {book['title']}")

    # 2. Update status → processing
    update_book_status(book_id, "processing")

    # 3. Dummy summary (later LLM add karenge)
    raw_text = book.get("raw_text", "")
    summary_text = "This is a generated summary of the book."

    # 4. Create summary in database
    summary_id = create_summary(
        book_id=book_id,
        user_id=user_id,
        summary_text=summary_text,
        summary_length="short",
        summary_style="paragraphs",
        chunk_summaries=[{"chunk": 1, "text": "dummy chunk"}],
        processing_time=0.1
    )

    # 5. Update status → completed
    update_book_status(book_id, "completed")

    print("Summary created:", summary_id)
    return summary_id
