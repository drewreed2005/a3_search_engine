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


def _get_valid_term_frequencies(document: Document) -> tuple[Counter[str], Counter[str]]:
    """
    Parses the given document and validates term frequencies associated with
    its textual data. Returns valid term frequencies and important frequencies.

    Args:
        document (Document): webpage document to process

    Returns:
        Counter[str]: first Counter in tuple is total term frequencies
        Counter[str]: second Counter in tuple is important term frequencies
    
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
    
    # returning validated frequencies
    return term_frequencies, important_frequencies


def add_document_to_index(document: Document,
        inverted_index: InvertedIndex) -> None:
    """
    Processes one webpage document and adds its postings to the inverted index.

    Args:
        document (Document): webpage document to process
        inverted_index (InvertedIndex): in-memory inverted index to update
    
    Raises:
        ValueError: indicates that invalid term frequencies were found or that
            posting document ID order was violated
    """
    # getting and validating term frequencies (raises ValueError if invalid)
    term_frequencies, important_frequencies = \
        _get_valid_term_frequencies(document)
    
    # creating a posting for each term in this document
    for term, total_tf in term_frequencies.items():
        # if there is no important instance of the term, it has frequency 0
        important_tf = important_frequencies.get(term, 0)
        
        # getting existing list of postings, which may be empty
        postings = inverted_index.setdefault(term, [])
        
        # ensuring that sorted postings have been maintained for merging
        if postings and postings[-1][0] >= document.doc_id:
            raise ValueError(
                f"Received document {document.doc_id} after document "
                f"{postings[-1][0]} for term '{term}'. "
                f"(Documents should be added in strictly increasing order of ID)"
            )
        
        postings.append((document.doc_id, total_tf, important_tf))