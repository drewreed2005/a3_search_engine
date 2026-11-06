'''
builder.py - builds in-memory inverted index from webpage documents
'''

from collections import Counter

from search_engine.indexer.document import Document
from search_engine.indexer.parser import parse_html
from search_engine.indexer.tokenizer import count_terms

# (creating type aliases for readability)

# postings per token contain:
# • doc_id (ID of document associated with token)
# • tf (total frequency of that term in the document)
# • important_tf (frequency within important HTML elements in the document)
Posting = tuple[int, int, int]

# inverted index maps token terms to a postings list (needs variable length)
InvertedIndex = dict[str, list[Posting]]


def _get_invalid_frequency_term(term_frequencies: Counter,
        important_frequencies: Counter) -> str | None:
    """
    Verifies that the frequency of each important term is less than or equal to
    its frequency in the general term frequencies, since important frequencies
    are a subset of general frequencies. Returns first invalid frequency term.

    Args:
        term_frequencies (Counter): Counter object associating terms with their
            frequencies
        important_frequencies (Counter): Counter object associating terms found
            in important HTML elements with their frequencies
    
    Returns:
        str | None: first invalid frequency term (or None if none found)
    """
    # validation time required scales with number of important terms
    for term, important_tf in important_frequencies.items():
        total_tf = term_frequencies.get(term, 0)
        if important_tf > total_tf:
            return term
    
    # returning none to indicate no invalid frequencies found
    return None


def add_document_to_index(document: Document,
        inverted_index: InvertedIndex) -> None:
    """
    Processes one webpage document and adds its postings to the inverted index.

    Args:
        document (Document): webpage document to process
        inverted_index (InvertedIndex): in-memory inverted index to update
    
    Raises:
        ValueError: indicates that invalid term frequencies were found in
            parsing (important frequency exceeded general frequency)
    """
    
    # extracting general and important text
    parsed_content = parse_html(document.content)
    
    # counting stemmed terms independently for both collections of text
    term_frequencies = count_terms(parsed_content.text)
    important_frequencies = count_terms(parsed_content.important_text)
    
    # important text must be a subset of general text (not separate)
    invalid = _get_invalid_frequency_term(term_frequencies, important_frequencies)
    if invalid is not None:
        raise ValueError(
            f"Important frequency exceeds total frequency for "
            f"term \"{invalid}\" in document with ID {document.doc_id}"
        )
    
    