"""Text chunking utilities for document ingestion."""
import re
from typing import List, Tuple

try:
    import tiktoken
    TOKENIZER = tiktoken.get_encoding("cl100k_base")
    USE_TIKTOKEN = True
except ImportError:
    TOKENIZER = None
    USE_TIKTOKEN = False


def count_tokens(text: str) -> int:
    """Count tokens in text using tiktoken or word approximation."""
    if USE_TIKTOKEN and TOKENIZER:
        return len(TOKENIZER.encode(text))
    # Approximate: ~0.75 words per token
    return int(len(text.split()) / 0.75)


def chunk_text(
    text: str,
    chunk_size: int = 600,
    chunk_overlap: int = 100,
) -> List[Tuple[str, int, int]]:
    """
    Split text into overlapping chunks.

    Args:
        text: Text to split
        chunk_size: Target chunk size in tokens (500-800 range)
        chunk_overlap: Overlap between chunks in tokens

    Returns:
        List of tuples: (chunk_text, start_char, end_char)
    """
    # Clean text
    text = text.strip()
    if not text:
        return []

    # Split into sentences for cleaner breaks
    sentences = re.split(r'(?<=[.!?])\s+', text)

    chunks = []
    current_chunk = []
    current_tokens = 0
    chunk_start = 0
    char_pos = 0

    for sentence in sentences:
        sentence_tokens = count_tokens(sentence)

        # If single sentence exceeds chunk size, force split it
        if sentence_tokens > chunk_size:
            # Flush current chunk
            if current_chunk:
                chunk_text = ' '.join(current_chunk)
                chunks.append((chunk_text, chunk_start, char_pos))
                current_chunk = []
                current_tokens = 0

            # Split long sentence by words
            words = sentence.split()
            word_chunk = []
            word_tokens = 0
            word_start = char_pos

            for word in words:
                word_tok = count_tokens(word)
                if word_tokens + word_tok > chunk_size and word_chunk:
                    chunk_text = ' '.join(word_chunk)
                    chunks.append((chunk_text, word_start, char_pos + len(' '.join(word_chunk))))
                    # Keep overlap words
                    overlap_words = []
                    overlap_tokens = 0
                    for w in reversed(word_chunk):
                        wt = count_tokens(w)
                        if overlap_tokens + wt <= chunk_overlap:
                            overlap_words.insert(0, w)
                            overlap_tokens += wt
                        else:
                            break
                    word_chunk = overlap_words + [word]
                    word_tokens = overlap_tokens + word_tok
                    word_start = char_pos + len(' '.join(word_chunk)) - len(' '.join(overlap_words + [word]))
                else:
                    word_chunk.append(word)
                    word_tokens += word_tok

            if word_chunk:
                chunk_text = ' '.join(word_chunk)
                chunks.append((chunk_text, word_start, char_pos + len(sentence)))

            char_pos += len(sentence) + 1
            chunk_start = char_pos
            continue

        # Check if adding this sentence exceeds chunk size
        if current_tokens + sentence_tokens > chunk_size and current_chunk:
            # Save current chunk
            chunk_text = ' '.join(current_chunk)
            chunks.append((chunk_text, chunk_start, char_pos))

            # Start new chunk with overlap
            overlap_sentences = []
            overlap_tokens = 0
            for s in reversed(current_chunk):
                st = count_tokens(s)
                if overlap_tokens + st <= chunk_overlap:
                    overlap_sentences.insert(0, s)
                    overlap_tokens += st
                else:
                    break

            current_chunk = overlap_sentences + [sentence]
            current_tokens = overlap_tokens + sentence_tokens
            chunk_start = char_pos - sum(len(s) + 1 for s in overlap_sentences)
        else:
            current_chunk.append(sentence)
            current_tokens += sentence_tokens

        char_pos += len(sentence) + 1

    # Don't forget the last chunk
    if current_chunk:
        chunk_text = ' '.join(current_chunk)
        chunks.append((chunk_text, chunk_start, char_pos))

    return chunks


def extract_page_from_position(
    char_position: int,
    page_breaks: List[int],
) -> int | None:
    """
    Determine page number from character position.

    Args:
        char_position: Character position in text
        page_breaks: List of character positions where pages start

    Returns:
        Page number (1-indexed) or None if not available
    """
    if not page_breaks:
        return None

    for i, break_pos in enumerate(page_breaks):
        if char_position < break_pos:
            return i + 1

    return len(page_breaks) + 1
