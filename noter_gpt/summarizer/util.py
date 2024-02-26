import re
from typing import Iterator


def chunk_text(text: str, chunk_size: int) -> Iterator[str]:
    while text:
        if len(text) <= chunk_size:
            yield text
            break
        else:
            search_start = int(chunk_size * 2 / 3)
            last_paragraph_end = text.rfind("\n\n", search_start, chunk_size)
            if last_paragraph_end != -1:
                # Split at a paragraph boundary if one exists in the final third of the chunk size
                yield text[:last_paragraph_end]
                text = text[last_paragraph_end + 2 :]  # Skip the paragraph break
            else:
                last_word_break = text.rfind(" ", search_start, chunk_size)
                if last_word_break != -1:
                    # Split at a word break if one exists in the final third of the chunk size
                    yield text[:last_word_break]
                    text = text[last_word_break + 1 :]  # Skip the space
                else:
                    # Just split at whatever char ends the chunk
                    yield text[:chunk_size]
                    text = text[chunk_size:]


def chunk_by_tokens(text: str, tokenizer) -> Iterator[str]:
    """
    This method divides the input text into chunks based on how it is tokenized by the passed tokenizer.
    We need to ensure that `len(tokenizer.tokenize(chunk)) < tokenizer.model_max_length`.
    We prefer to end chunks at paragraph > sentence > word boundaries if that would not leave too much empty space.
    """

    min_chunk_size = min(
        tokenizer.model_max_length * 2 / 3, tokenizer.model_max_length - 200
    )

    chunk = ""
    chunk_tokens = 0

    paragraphs = text.split("\n\n")
    for paragraph in paragraphs:
        paragraph_tokens = len(tokenizer.tokenize(paragraph))
        if chunk_tokens + paragraph_tokens < tokenizer.model_max_length:
            chunk += "\n\n" + paragraph.strip()
            chunk_tokens += (
                paragraph_tokens  # TODO: check if this is always equal to retokenizing
            )
            continue

        if chunk_tokens >= min_chunk_size:
            yield chunk
            chunk = paragraph
            chunk_tokens = paragraph_tokens
            continue

        sentences = re.split(r"(?<=[.!?]) +", paragraph.replace(".\n", ". "))
        for sentence in sentences:
            sentence_tokens = len(tokenizer.tokenize(sentence))
            if chunk_tokens + sentence_tokens < tokenizer.model_max_length:
                chunk += ". " + sentence.strip()
                chunk_tokens += sentence_tokens
                continue

            if chunk_tokens >= min_chunk_size:
                yield chunk
                chunk = sentence
                chunk_tokens = sentence_tokens
                continue

            words = sentence.split(" ")
            for word in words:
                word_tokens = len(tokenizer.tokenize(word))
                if chunk_tokens + word_tokens < tokenizer.model_max_length:
                    chunk += " " + word.strip()
                    chunk_tokens += word_tokens
                    continue

                yield chunk
                chunk = word
                chunk_tokens = word_tokens

    if chunk.strip():
        yield chunk.strip()
