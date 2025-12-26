import streamlit as st
from utils.database import get_books, get_summary,delete_book

def show_history_page(user_id):
    st.header("📚 History")

    books = get_books(user_id)
    if not books:
        st.info("No uploads yet")
        return

    for book in books:

      with st.expander(book["title"]):

        col1, col2 = st.columns([4, 1])

        # LEFT SIDE (BOOK DETAILS)
        with col1:
            st.write(f"**Author:** {book.get('author', 'N/A')}")
            st.write(f"**Status:** {book.get('status', 'uploaded')}")

        # RIGHT SIDE (DELETE BUTTON)
        with col2:
            if st.button("🗑️ Delete", key=f"del_{book['_id']}"):
                delete_book(book["_id"], user_id)
                st.success("Book deleted successfully")
                st.rerun()

        # SUMMARY
        summary = get_summary(book["_id"])
        if summary:
            st.subheader("📝 Summary")
            st.write(summary["summary"])
