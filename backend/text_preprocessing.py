# backend/text_preprocessing.py
"""
Text preprocessing utilities for summarization pipeline (Task 6).

Features:
- normalize_text: unicode normalization + whitespace normalization
- remove_citations: removes [1], (Smith et al., 2020) style citations (best-effort)
- remove_references_section: drop everything after a "References" / "Bibliography" header
- remove_footnotes: best-effort removal of common footnote markers
- remove_page_numbers: remove lines that look like page numbers
- remove_special_chars: remove/control special characters (with option to keep punctuation)
- detect_language: wrapper around langdetect
- split_into_chunks: split text into word-based chunks with overlap
- clean_text: single entrypoint calling the above with options and returning metadata
"""

import re
import unicodedata
import logging
from typing import List, Tuple, Dict, Any, Optional

# language detection
try:
    from langdetect import detect, detect_langs
except Exception:
    detect = None
    detect_langs = None

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


# -----------------------
# Normalization & cleaning
# -----------------------
def normalize_text(text: str) -> str:
    """Unicode normalize and unify line breaks and whitespace."""
    if not text:
        return ""
    # unicode normalization
    text = unicodedata.normalize("NFKC", text)
    # unify line endings
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    # replace multiple spaces / tabs with single space
    text = re.sub(r"[ \t]+", " ", text)
    # collapse multiple blank lines to max 2
    text = re.sub(r"\n{3,}", "\n\n", text)
    # strip leading/trailing whitespace
    return text.strip()


def remove_references_section(text: str) -> str:
    """
    If there is a References / Bibliography section, drop it and everything after it.
    Uses a case-insensitive search for common headings.
    """
    if not text:
        return text
    pattern = re.compile(
        r"\n\s*(References|REFERENCES|Bibliography|BIBLIOGRAPHY|Works Cited|WORKS CITED)\s*\n",
        flags=re.IGNORECASE,
    )
    m = pattern.search(text)
    if m:
        return text[: m.start()].strip()
    return text


def remove_citations(text: str) -> str:
    """
    Remove common inline citation patterns:
    - [1], [12, 13]
    - (Smith et al., 2020), (Doe, 2019; Roe et al., 2020)
    - numbered superscripts like ^1 or ¹ (best-effort)
    This is a heuristic — keep a backup of raw text if you need exactness.
    """
    if not text:
        return text
    # remove bracketed numeric citations [1], [1,2], [12-15]
    text = re.sub(r"\[\s*\d+(\s*[-,]\s*\d+)*\s*(,\s*\d+)*\s*\]", "", text)
    # remove parenthetical citations containing years e.g., (Smith et al., 2020)
    text = re.sub(r"\([^()]{0,120}?(19|20)\d{2}[^()]{0,120}?\)", "", text)
    # remove numeric superscripts like ^1 or ¹
    text = re.sub(r"(\^|\u00B9|\u00B2|\u00B3|\u2070|\u2071|\u2072|\u2073|\d+)", "", text)
    # remove residual bracketed text like [see Figure 1] but cautious: only short ones
    text = re.sub(r"\[\s*[^\]]{0,80}\s*\]", "", text)
    return text


def remove_footnotes(text: str) -> str:
    """
    Attempt to remove footnote blocks at bottom-of-page or footnote markers.
    Heuristics: lines starting with digits or special markers and short lines at end.
    """
    if not text:
        return text
    # remove lines like '1. This is a footnote...'
    text = re.sub(r"(?m)^\s*\d+\.\s+.+$", "", text)
    # remove common footnote markers e.g., [1], (1) in-line already handled, try trailing short lines
    # remove trailing block of many short lines (candidate footnote block)
    lines = text.splitlines()
    # detect last block of < 4 words lines that may be footnotes
    cutoff = len(lines) - 1
    # go backwards while lines are short (<= 10 words) and not many characters
    while cutoff >= 0 and len(lines[cutoff].split()) <= 10:
        cutoff -= 1
    cleaned = "\n".join(lines[: cutoff + 1])
    return cleaned.strip()


def remove_page_numbers(text: str) -> str:
    """Remove lines that are just page numbers (optionally 'Page 1', 'p. 1', etc)."""
    if not text:
        return text
    # remove lines that only contain digits or 'Page 1' style
    text = re.sub(r"(?m)^\s*(Page|page|p\.?)?\s*\d+\s*$", "", text)
    return text


def remove_special_chars(text: str, keep_punct: bool = True) -> str:
    """
    Remove control characters and optionally non-standard punctuation.
    keep_punct True -> keep standard punctuation .,;:!?()[]{}'"- etc.
    """
    if not text:
        return text
    # remove control characters (except newline and tab)
    text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", text)
    if not keep_punct:
        # remove punctuation except whitespace and letters/numbers
        text = re.sub(r"[^\w\s]", "", text)
    return text


# -----------------------
# High-level cleaning pipeline
# -----------------------
def clean_text(
    text: str,
    remove_refs: bool = True,
    remove_cites: bool = True,
    remove_footnotes_flag: bool = True,
    remove_pages: bool = True,
    keep_punct: bool = True,
) -> Tuple[str, Dict[str, Any]]:
    """
    Run the cleaning pipeline and return cleaned text + metadata dict:
    metadata contains word_count, char_count, language (if detected)
    """
    original = text or ""
    try:
        t = normalize_text(original)
        if remove_refs:
            t = remove_references_section(t)
        if remove_cites:
            t = remove_citations(t)
        if remove_footnotes_flag:
            t = remove_footnotes(t)
        if remove_pages:
            t = remove_page_numbers(t)
        t = remove_special_chars(t, keep_punct=keep_punct)
        t = normalize_text(t)  # normalize again after removals

        # metadata
        word_count = len(t.split())
        char_count = len(t)
        lang = None
        if detect and detect_langs:
            try:
                # detect_langs provides probabilities
                langs = detect_langs(t[:20000]) if t else []
                if langs:
                    lang = str(langs[0])
            except Exception:
                lang = None

        meta = {"word_count": word_count, "char_count": char_count, "language": lang}
        return t, meta
    except Exception as e:
        logger.exception("Error in clean_text: %s", e)
        return original, {"word_count": len(original.split()), "char_count": len(original), "language": None}


# -----------------------
# Chunking
# -----------------------
def split_into_chunks(text: str, words_per_chunk: int = 1200, overlap: int = 200) -> List[str]:
    """
    Split text into chunks of ~words_per_chunk words, with 'overlap' words repeated
    between consecutive chunks to preserve context.
    """
    if not text:
        return []

    words = text.split()
    if words_per_chunk <= 0:
        raise ValueError("words_per_chunk must be > 0")
    if overlap < 0:
        overlap = 0
    if overlap >= words_per_chunk:
        overlap = int(words_per_chunk // 4)

    chunks: List[str] = []
    start = 0
    n = len(words)
    while start < n:
        end = min(start + words_per_chunk, n)
        chunk_words = words[start:end]
        chunks.append(" ".join(chunk_words))
        # move start forward but keep overlap
        start = end - overlap
        if start < 0:
            start = 0
        if start >= n:
            break
    return chunks


# -----------------------
# Convenience wrapper for extracted files
# -----------------------
def prepare_for_summarization(
    text: str,
    chunk_size: int = 1200,
    overlap: int = 200,
    cleaning_options: Optional[Dict[str, bool]] = None,
) -> Dict[str, Any]:
    """
    Full pipeline: clean -> split into chunks -> return dict with metadata.
    Returns:
        {
            "cleaned_text": str,
            "meta": {...},
            "chunks": [str, ...],
            "chunk_count": int
        }
    """
    if cleaning_options is None:
        cleaning_options = {}

    cleaned, meta = clean_text(
        text,
        remove_refs=cleaning_options.get("remove_refs", True),
        remove_cites=cleaning_options.get("remove_cites", True),
        remove_footnotes_flag=cleaning_options.get("remove_footnotes", True),
        remove_pages=cleaning_options.get("remove_pages", True),
        keep_punct=cleaning_options.get("keep_punct", True),
    )

    chunks = split_into_chunks(cleaned, words_per_chunk=chunk_size, overlap=overlap)
    return {"cleaned_text": cleaned, "meta": meta, "chunks": chunks, "chunk_count": len(chunks)}


# -----------------------
# Example / quick test
# -----------------------
if __name__ == "__main__":
    sample = """This is a sample paragraph that cites a paper (Smith et al., 2020) and references [1]. 
    Page 1

    Some more text. Footnote 1. Another sentence.

    References
    [1] Smith, A. (2020). Title...
    """

    print("---- RAW ----")
    print(sample)
    result = prepare_for_summarization(sample, chunk_size=10, overlap=3)
    print("\n---- METADATA ----")
    print(result["meta"])
    print("\n---- CHUNKS ----")
    for i, c in enumerate(result["chunks"], 1):
        print(f"--- chunk {i} ---\n{c}\n")
