from utils.summarizer import generate_summary

def summarize_large_text(text):
    chunks = [text[i:i+1000] for i in range(0, len(text), 1000)]
    summaries = [generate_summary(c) for c in chunks]
    return " ".join(summaries)
