# frontend/search.py

import streamlit as st
import sys, os

# ensure project root
sys.path.append(os.path.abspath(os.path.dirname(__file__)) + "/..")

from utils.database import search_books


def show_search_page(user_id):
    st.title("🔍 Search & Filter Books")

    # --- Search Inputs ---
    search_query = st.text_input("Search by title or author")

    col1, col2, col3 = st.columns(3)

    with col1:
        sort_by = st.selectbox(
            "Sort By",
            ["uploaded_at", "title"]
        )

    with col2:
        order = st.selectbox(
            "Order",
            ["desc", "asc"]
        )

    with col3:
        status = st.selectbox(
            "Filter by Status",
            ["all", "uploaded", "summarized"]
        )

    # --- Pagination ---
    page = st.number_input("Page Number", value=1, min_value=1)
    per_page = 5

    # --- Search Button ---
    if st.button("Search"):
        with st.spinner("Searching..."):
            books, total = search_books(
                user_id=user_id,
                search=search_query if search_query else None,
                sort_by=sort_by,
                order=order,
                status=status if status != "all" else None,
                page=page,
                limit=per_page
            )

        st.write(f"### Results ({total} books found)")

        # If no results
        if not books:
            st.warning("No books found.")
            return

        # Display results
        for b in books:
            with st.container():
                st.subheader(b.get("title"))
                st.write(f"**Author:** {b.get('author', '--')}")
                st.write(f"**Status:** {b.get('status')}")
                st.write(f"**Uploaded:** {str(b.get('uploaded_at'))[:19]}")

                colA, colB, colC = st.columns(3)

                with colA:
                    if st.button(f"View Details", key=f"view_{b['_id']}"):
                        st.info("Detail Page under development")

                with colB:
                    if st.button(f"Generate Summary", key=f"summary_{b['_id']}"):
                        st.info("Summary Generation Page Coming Soon")

                with colC:
                    if st.button(f"Delete", key=f"delete_{b['_id']}"):
                        st.warning("Delete Feature Coming Soon")

                st.markdown("---")

        # Pagination info
        total_pages = (total + per_page - 1) // per_page
        st.info(f"Page {page} of {total_pages}")
