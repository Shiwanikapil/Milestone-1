# frontend/upload.py
import sys, os
import streamlit as st
from datetime import datetime

from utils.database import create_book, update_book_status
from utils.database import get_book_by_id
from utils.summary import generate_summary   # <-- Your summary function

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# -------- File Reader --------
from docx import Document
import PyPDF2


UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# ------------------------------------------------------------------
#                   FILE TEXT EXTRACTION
# ------------------------------------------------------------------

def extract_text_from_txt(file):
    return file.getvalue().decode("utf-8", errors="ignore")


def extract_text_from_pdf(file):
    pdf_reader = PyPDF2.PdfReader(file)
    text = ""

    for page in pdf_reader.pages:
        text += page.extract_text() + "\n"

    return text


def extract_text_from_docx(file):
    doc = Document(file)
    return "\n".join([para.text for para in doc.paragraphs])


# ------------------------------------------------------------------
#                   MAIN UPLOAD PAGE
# ------------------------------------------------------------------

def show_upload_page(user_id):
    if not st.session_state.get("logged_in", False):
        st.error("You must login first!")
        return

    st.markdown("<h1 style='text-align:center; color:#00BFFF;'>📚 Upload Book for Summarization</h1>", unsafe_allow_html=True)
    st.write("Supported formats: **TXT, PDF, DOCX**")
    st.write("Maximum file size: **10MB**")

    uploaded_file = st.file_uploader("Choose a book file", type=['txt', 'pdf', 'docx'])

    st.subheader("Optional Book Details")
    title = st.text_input("Book Title")
    author = st.text_input("Author Name (optional)")
    chapter = st.text_input("Chapter/Section (optional)")

    extracted_text = None

    if uploaded_file:
        # ---------- Show File Info ----------
        file_details = {
            "Filename": uploaded_file.name,
            "File size (KB)": round(len(uploaded_file.getvalue()) / 1024, 2),
            "Upload date": datetime.now().strftime("%Y-%m-%d %H:%M")
        }

        st.success("File uploaded successfully!")
        st.json(file_details)

        # ---------- Extract Text ----------
        try:
            if uploaded_file.name.endswith(".txt"):
                extracted_text = extract_text_from_txt(uploaded_file)
                st.code(extracted_text[:400])

            elif uploaded_file.name.endswith(".pdf"):
                extracted_text = extract_text_from_pdf(uploaded_file)
                st.code(extracted_text[:400])

            elif uploaded_file.name.endswith(".docx"):
                extracted_text = extract_text_from_docx(uploaded_file)
                st.code(extracted_text[:400])

        except Exception as e:
            st.error(f"Error reading file: {str(e)}")
            return

    # ------------------------------------------------------------------
    #                       UPLOAD & PROCESS BUTTON
    # ------------------------------------------------------------------

    if st.button("Upload & Process"):
        if not uploaded_file:
            st.error("Please upload a file first.")
            return

        if not title:
            st.error("Please enter a book title.")
            return

        # ---------- Save file locally ----------
        file_path = os.path.join(UPLOAD_FOLDER, uploaded_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getvalue())

        # ---------- Save book record ----------
        book_id = create_book(
            user_id=user_id,
            title=title,
            author=author,
            chapter=chapter,
            file_path=file_path,
            raw_text=extracted_text
        )

        update_book_status(book_id, "processing")

        st.success("Book saved! Starting summarization...")

        # ---------- Generate summary ----------
        with st.spinner("Summarizing content..."):
            summary = generate_summary(extracted_text)

        update_book_status(book_id, "summarized")

        st.success("✔ Summarization complete!")

        st.subheader("Summary Preview:")
        st.write(summary)

    st.write("---")
    st.subheader("📜 Upload History (Coming Soon)")
    st.info("Upload history feature will appear here.")
