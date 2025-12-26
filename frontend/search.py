import streamlit as st
from utils.database import search_books

def show_search_page(user_id):
    st.header("🔍 Search Books")

    col1, col2 = st.columns(2)

    with col1:
        title = st.text_input("📘 Book Name")

    with col2:
        status = st.selectbox(
            "📌 Status",
            ["", "uploaded", "summarized"]
        )

    if st.button("Search", use_container_width=True):
        results = search_books(
            user_id=user_id,
            title=title if title else None,
            status=status if status else None
        )

        if not results:
            st.warning("No books found")
            return

        st.success(f"{len(results)} book(s) found")

        for book in results:
            with st.expander(book["title"]):
                st.write(f"✍️ Author: {book.get('author','N/A')}")
                st.write(f"📌 Status: {book.get('status','uploaded')}")
