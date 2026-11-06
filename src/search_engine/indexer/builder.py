'''
builder.py - builds in-memory inverted index from webpage documents
'''

from search_engine.indexer.document import Document
from search_engine.indexer.parser import parse_html
from search_engine.indexer.tokenizer import tokenize, count_terms

# (creating type aliases for readability)

# postings per token contain:
# • doc_id (ID of document associated with token)
# • tf (total text frequency of that term in the document)
# • important_tf (frequency within important HTML elements in the document)
Posting = tuple[int, int, int]

# inverted index maps token terms to a postings list (needs variable length)
InvertedIndex = dict[str, list[Posting]]


def add_document_to_index(document: Document, inverted_index: InvertedIndex) -> None:
    """
    Processes one webpage document and adds its postings to the inverted index.

    Args:
        document (Document): webpage document to process
        inverted_index (InvertedIndex): in-memory inverted index to update
    """