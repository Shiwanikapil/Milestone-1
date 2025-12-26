# utils/post_processing.py
import re
from collections import Counter

def clean_text(text):
    text = re.sub(r'\s+', ' ', text)   # extra spaces
    text = text.strip()
    return text


def remove_duplicate_sentences(text):
    sentences = re.split(r'(?<=[.!?])\s+', text)
    seen = set()
    result = []

    for s in sentences:
        s_clean = s.lower()
        if s_clean not in seen:
            seen.add(s_clean)
            result.append(s)

    return " ".join(result)


def limit_length(text, level="medium"):
    words = text.split()

    if level == "short":
        return " ".join(words[:80])
    elif level == "long":
        return " ".join(words[:250])
    return " ".join(words[:150])  # medium default


def extract_keywords(text, top_n=5):
    words = re.findall(r'\b[a-zA-Z]{4,}\b', text.lower())
    common = Counter(words).most_common(top_n)
    return [w for w, _ in common]


def post_process_summary(text, level="medium"):
    text = clean_text(text)
    text = remove_duplicate_sentences(text)
    text = limit_length(text, level)

    keywords = extract_keywords(text)

    return text, keywords
