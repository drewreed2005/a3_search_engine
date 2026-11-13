'''
scripts/search.py - user-facing console search interface
'''

from pathlib import Path
from typing import BinaryIO

from search_engine.search.metadata import load_document_urls
from search_engine.search.query import process_query
from search_engine.search.ranking import RankedDocument, rank_documents
from search_engine.search.retrieval import Lexicon, retrieve_documents

SearchResults = list[tuple[RankedDocument, str]]

# going along with the milestone 2 specification's expectation of 5 results
DEFAULT_RESULT_LIMIT = 5


def search_once(query: str, lexicon: Lexicon, postings_file: BinaryIO,
        document_urls: dict[int, str], document_count: int, 
        result_limit: int) -> SearchResults:
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
    
    Raises:
        ValueError: if a retrieved document's ID does not have metadata
    """
    query_terms = process_query(query)
    # basic check for empty/unrecognizeable/invalid query
    if not query_terms:
        return []
    
    matches = retrieve_documents(query_terms, lexicon, postings_file)
    ranked_documents = rank_documents(
        matches, query_terms, lexicon, document_count
    )
    
    results: SearchResults = []
    
    # restricting the number of output documents by the result limit
    for ranked_document in ranked_documents[:result_limit]:
        doc_id = ranked_document.doc_id
        
        # basic check for result ID validity (must have a URL)
        if doc_id not in document_urls:
            raise ValueError(
                f"Document ID {doc_id} was found in the index "
                "but not in the document metadata"
            )
        
        results.append((ranked_document, document_urls[doc_id]))
    
    return results


def display_results(results: SearchResults) -> None:
    """
    Handles printing the ranked search results to the console.

    Args:
        results (SearchResults): the search results to be displayed
    """


def run_search(index_directory: Path, result_limit: int) -> None:
    """
    Loads the index and runs the search session in the console.

    Args:
        index_directory (Path): path of the directory containing index files
        result_limit (int): maximum search results displayed per search
    """


def main() -> int:
    """
    Entry point for command line search engine program.

    Returns:
        int: run status code
    """


if __name__ == "__main__":
    main()