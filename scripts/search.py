'''
scripts/search.py - user-facing console search interface
'''

from pathlib import Path
from typing import BinaryIO

from search_engine.search.metadata import load_document_urls
from search_engine.search.query import process_query
from search_engine.search.ranking import RankedDocument
from search_engine.search.retrieval import Lexicon


def search_once(query: str, lexicon: Lexicon, postings_file: BinaryIO,
        document_urls: dict[int, str], document_count: int, 
        result_limit: int) -> list[tuple[RankedDocument, str]]:
    """
    Processes one query and returns as many of the highest-ranked matching
    documents in order as allowed by the results limit and existing data.

    Args:
        query (str): the user's unnormalized search query
        lexicon (Lexicon): loaded term-to-postings metadata
        postings_file (BinaryIO): open postings file in binary mode
        document_urls (dict[int, str]): mapping of document IDs to their URLs
        document_count (int): total number of indexed documents
        result_limit (int): maximum number of results to return

    Returns:
        list[tuple[RankedDocument, str]]: ranked documents paired with their
            corresponding URLs
    """