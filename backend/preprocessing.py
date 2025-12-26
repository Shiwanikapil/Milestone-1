# backend/preprocessing.py
import re
from langdetect import detect
from nltk.tokenize import sent_tokenize

# ---------------- CLEAN TEXT ----------------
def clean_text(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r'\n+', '\n', text)
    text = re.sub(r'[ \t]+', ' ', text)
    return text.strip()


# ---------------- LANGUAGE DETECTION ----------------
def detect_language(text: str) -> str:
    try:
        return detect(text)
    except:
        return "unknown"


# ---------------- SENTENCE SEGMENTATION ----------------
def segment_sentences(text: str):
    return sent_tokenize(text)


# ---------------- TEXT STATS ----------------
def calculate_text_stats(text: str):
    words = text.split()
    sentences = segment_sentences(text)

    return {
        "word_count": len(words),
        "char_count": len(text),
        "sentence_count": len(sentences),
        "avg_sentence_length": len(words) / max(len(sentences), 1),
        "estimated_read_time_min": round(len(words) / 200, 2)
    }


# ---------------- CHUNKING ----------------
def chunk_text(text, chunk_size=1000, overlap=150):
    sentences = segment_sentences(text)

    chunks = []
    current_chunk = []
    current_words = 0
    chunk_id = 1

    for sent in sentences:
        sent_words = len(sent.split())

        if current_words + sent_words > chunk_size:
            chunks.append({
                "chunk_id": chunk_id,
                "text": " ".join(current_chunk)
            })
            chunk_id += 1

            # overlap
            overlap_words = []
            count = 0
            for s in reversed(current_chunk):
                overlap_words.insert(0, s)
                count += len(s.split())
                if count >= overlap:
                    break

            current_chunk = overlap_words + [sent]
            current_words = sum(len(s.split()) for s in current_chunk)
        else:
            current_chunk.append(sent)
            current_words += sent_words

    if current_chunk:
        chunks.append({
            "chunk_id": chunk_id,
            "text": " ".join(current_chunk)
        })

    return chunks


# ---------------- PIPELINE ORCHESTRATOR ----------------
def preprocess_for_summarization(text, chunk_size=1000):
    if not text or len(text.split()) < 100:
        raise ValueError("Text too short for summarization")

    cleaned = clean_text(text)
    language = detect_language(cleaned)
    sentences = segment_sentences(cleaned)
    stats = calculate_text_stats(cleaned)
    chunks = chunk_text(cleaned, chunk_size)

    return {
        "cleaned_text": cleaned,
        "language": language,
        "sentences": sentences,
        "stats": stats,
        "chunks": chunks
    }