'''
scripts/search.py - user-facing console search interface
'''

import sys
from argparse import ArgumentParser, Namespace
from pathlib import Path
from typing import BinaryIO

from search_engine.indexer.pipeline import (
    DOCUMENTS_FILE_NAME,
    LEXICON_FILE_NAME,
    POSTINGS_FILE_NAME,
)
from search_engine.search.metadata import load_document_urls
from search_engine.search.query import process_query
from search_engine.search.ranking import RankedDocument, rank_documents
from search_engine.search.retrieval import Lexicon, load_lexicon, retrieve_documents

SearchResults = list[tuple[RankedDocument, str]]

# going along with the milestone 2 specification's expectation of 5 results
DEFAULT_RESULT_LIMIT = 5
DEFAULT_INDEX_DIRECTORY_NAME = "index"

READ_BYTES_MODE = "rb"
SEARCH_TAG = "Query: "

INDEX_DIRECTORY_ARG = "--index-dir"
RESULTS_LIMIT_ARG = "--results"


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
    
    seen_urls: set[str] = set()
    unique_results: SearchResults = []
    
    # restricting the number of output documents by the result limit
    for ranked_document in ranked_documents:
        doc_id = ranked_document.doc_id
        # basic check for result ID validity (must have a URL)
        if doc_id not in document_urls:
            raise ValueError(
                f"Document ID {doc_id} was found in the index "
                "but not in the document metadata"
            )
        
        # verifying that this is a unique URL
        url = document_urls[doc_id]
        if url not in seen_urls:
            seen_urls.add(url)
            unique_results.append((ranked_document, url))
        
        if len(unique_results) >= result_limit:
            break
    
    return unique_results


def display_results(results: SearchResults) -> None:
    """
    Handles printing the ranked search results to the console.

    Args:
        results (SearchResults): the search results to be displayed
    """
    if not results:
        print("No matching documents found.")
        return
    
    # numeric rank from enumeration, since search result order is meaningful
    for rank, (document, url) in enumerate(results, start = 1):
        print(f"{rank}. {url}")
        print(f"    Score: {document.score:.6f}")


def run_search(index_directory: Path, result_limit: int) -> None:
    """
    Loads the index and runs the search session in the console.

    Args:
        index_directory (Path): path of the directory containing index files
        result_limit (int): maximum search results displayed per search
    
    Raises:
        ValueError: if needed metadata cannot be accessed for some reason
    """
    lexicon_path = index_directory / LEXICON_FILE_NAME
    postings_path = index_directory / POSTINGS_FILE_NAME
    metadata_path = index_directory / DOCUMENTS_FILE_NAME
    
    lexicon = load_lexicon(lexicon_path)
    document_urls = load_document_urls(metadata_path)
    document_count = len(document_urls)
    
    if document_count == 0:
        raise ValueError("The document metadata file contains no data.")
    
    # documenting index stats for transparency and because it's cool
    print(f"Loaded {document_count:,} documents.")
    print(f"Loaded {len(lexicon):,} indexed terms.")
    print("Enter a search query. Use an empty query to quit.")
    
    # opening the postings path as raw byte data to use its content efficiently
    with postings_path.open(READ_BYTES_MODE) as postings_file:
        while True:
            try:
                query = input(f"\n{SEARCH_TAG}")
            # standard end of input/file handling
            # (can be manually inputted with CTRL + D on Mac/Linux)
            except EOFError:
                print()
                break
            
            # detecting an empty query (break out of search engine loop)
            # (just whitespace input is also considered an empty query)
            if not query.strip():
                break
            
            # performing the actual search
            display_results(
                search_once(
                    query,
                    lexicon,
                    postings_file,
                    document_urls,
                    document_count,
                    result_limit
                )
            )


def parse_arguments() -> Namespace:
    """
    Parses command line arguments for the search engine program. The program
    accepts --index-dir (allowing customization of the idnex directory path)
    and --results (customizes the number of search results exposed).

    Returns:
        Namespace: the argument namespace
    """
    # defining the project root relative to this script file
    project_root = Path(__file__).resolve().parents[1]
    
    parser = ArgumentParser(
        description = "Search the indexed collection of webpages"
    )
    parser.add_argument(
        INDEX_DIRECTORY_ARG,
        type = Path,
        default = project_root / DEFAULT_INDEX_DIRECTORY_NAME,
        help = f"Directory containing {LEXICON_FILE_NAME}, "
            f"{POSTINGS_FILE_NAME}, and {DOCUMENTS_FILE_NAME}"
    )
    parser.add_argument(
        RESULTS_LIMIT_ARG,
        type = int,
        default = DEFAULT_RESULT_LIMIT,
        help = "Maximum number of results to display per query"
    )
    
    return parser.parse_args()


def main() -> int:
    """
    Entry point for command line search engine program.

    Returns:
        int: run status code
    """
    args = parse_arguments()
    
    # printing basic invalid argument condition to standard error
    if args.results <= 0:
        print(
            f"Error: {RESULTS_LIMIT_ARG} must be a positive integer "
            f"(got {args.results})", file = sys.stderr
        )
        return 1
    
    try:
        run_search(args.index_dir, args.results)
    
    # catching all anticipated error types that could occur during a run
    except (FileNotFoundError, ValueError) as error:
        print(f"Error: {error}", file = sys.stderr)
        return 1

    return 0

if __name__ == "__main__":
    main()