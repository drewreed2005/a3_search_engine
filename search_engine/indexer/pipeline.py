'''
pipeline.py - combines indexer functionality into a single index builder function
'''

from pathlib import Path

from search_engine.indexer.builder import InvertedIndex, add_document_to_index
from search_engine.indexer.reader import iter_documents
from search_engine.indexer.storage import (
    merge_partial_indexes,
    write_document_metadata_record,
    write_partial_index,
)

# defining the number of documents processed per partial index
DEFAULT_DOCUMENTS_PER_PARTIAL = 10000
MIN_DOCUMENTS_PER_PARTIAL = 1

WRITE_MODE = "w"
DOCUMENTS_FILE_ENCODING = "utf-8"

PARTIAL_INDEX_DIRECTORY_NAME = "partials"
# lambda for path formatting
get_partial_index_path: Path = (
    lambda partial_index_directory, file_number:
        partial_index_directory / f"partial_{file_number:05d}.jsonl"
)
# partial index paths have 5 integers of space for representation
# (like originally conceptualized when designing storage)
LEXICON_FILE_NAME = "lexicon.json"
POSTINGS_FILE_NAME = "postings.bin"
DOCUMENTS_FILE_NAME = "documents.jsonl"

DOCUMENTS_INDEXED_KEY = "documents_indexed"
PARTIAL_INDEXES_KEY = "partial_indexes"
UNIQUE_TERMS_KEY = "unique_terms"


def build_index(data_directory: Path, index_directory: Path,
        documents_per_partial: int = DEFAULT_DOCUMENTS_PER_PARTIAL,
        should_log: bool = False) -> dict[str, int]:
    """
    Builds the complete file system-based inverted index from the corpus.
    Processes documnets sequentually in memory until reaching the set document
    limit, at which point the index is written to a sorted partial index file.
    Partial indexes are merged into final lexicon and postings files once all
    documents have been processed.

    Args:
        data_directory (Path): directory containing the webpage JSON files
        index_directory (Path): directory where index files will be stored
        documents_per_partial (int): maximum number of documents to process
            before flushing the current in-memory index to disk

    Returns:
        dict[str, int]: summary containing the number of documents indexed,
            partial indexes created, and unique terms in the final index
    
    Raises:
        ValueError: documents per partial index limit is not positive or
            document indexing became malformed in some way
        FileNotFoundError: if the data directory does not exist
        NotADirectoryError: if the data path is not a directory
        JSONDecodeError: if a webpage JSON file cannot be decoded
        OSError: if document access was denied
    """
    
    # nonpositive document processing limit prevents progress; invalid
    if documents_per_partial < MIN_DOCUMENTS_PER_PARTIAL:
        raise ValueError(
            f"A limit of least {MIN_DOCUMENTS_PER_PARTIAL} document"
            f"{"s" if MIN_DOCUMENTS_PER_PARTIAL != 1 else ""} per partial index "
            f"flush is required (provided: {documents_per_partial})."
        )
    
    # establishing separate directory for partial indexes
    partial_directory = index_directory / PARTIAL_INDEX_DIRECTORY_NAME
    partial_directory.mkdir(parents = True, exist_ok = True)
    
    # in-memory index limited to one batch of documents
    inverted_index: InvertedIndex = {}
    
    # partial indexes created during this execution are the only ones passed
    # to the merge operation (older leftover files are not included)
    partial_paths: list[Path] = []
    
    documents_indexed = 0
    documents_since_flush = 0
    
    # using iter_documents for sequential document ID order, memory efficiency
    with (index_directory / DOCUMENTS_FILE_NAME).open(WRITE_MODE,
            encoding = DOCUMENTS_FILE_ENCODING, newline="\n") as documents_file:
        for document in iter_documents(data_directory):
            # adding this document to the index
            add_document_to_index(document, inverted_index)
            # mapping document ID to URL
            write_document_metadata_record(document, documents_file)
            
            documents_indexed += 1
            documents_since_flush += 1
            
            # optional print for debugging
            if should_log and documents_indexed % 1000 == 0:
                print(f"{documents_indexed} documents have been indexed.")
            
            # flushing if the limit has been reached
            if documents_since_flush >= documents_per_partial:
                # optional print for debugging
                if should_log:
                    print(f"Starting flush of {documents_per_partial} documents...")
                
                # creating the partial index path from template
                partial_path = get_partial_index_path(
                    partial_directory, len(partial_paths)
                )
                # writing the partial index to the disk
                write_partial_index(inverted_index, partial_path)
                partial_paths.append(partial_path)
                
                # releasing the postings accumulated over time
                if should_log:
                    print(f"Flush complete. (Total flushes: {len(partial_paths)})")
                inverted_index.clear()
                documents_since_flush = 0
    
    # if final documents remain unflushed, flushing them
    if documents_since_flush > 0:
        partial_path = get_partial_index_path(
            partial_directory, len(partial_paths)
        )
        write_partial_index(inverted_index, partial_path)
        partial_paths.append(partial_path)
    
    # merging the sorted partial indexes into the final disk representation
    unique_terms = merge_partial_indexes(
        partial_paths,
        index_directory / LEXICON_FILE_NAME,
        index_directory / POSTINGS_FILE_NAME
    )
    
    return {
        DOCUMENTS_INDEXED_KEY: documents_indexed,
        PARTIAL_INDEXES_KEY: len(partial_paths),
        UNIQUE_TERMS_KEY: unique_terms
    }