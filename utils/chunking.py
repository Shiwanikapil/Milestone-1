# utils/chunking.py

def chunk_text(text, chunk_size=1000, overlap=150):
    words = text.split()
    chunks = []

    start = 0
    while start < len(words):
        end = start + chunk_size
        chunk = words[start:end]
        chunks.append(" ".join(chunk))
        start = end - overlap   # overlap for context

    return chunks