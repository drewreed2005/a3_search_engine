'''
build_index.py - runs the complete corpus indexing process and reports statistics
'''

from pathlib import Path

from search_engine.indexer.pipeline import (
    DOCUMENTS_FILE_NAME,
    DOCUMENTS_INDEXED_KEY,
    LEXICON_FILE_NAME,
    PARTIAL_INDEXES_KEY,
    POSTINGS_FILE_NAME,
    UNIQUE_TERMS_KEY,
    build_index,
)

BYTES_PER_KILOBYTE = 1024

# data file path info
DATA_DIRECTORY_NAME = "data"
RAW_DIRECTORY_NAME = "raw"
INDEX_DIRECTORY_NAME = "index"

# # handling issues with importing from external package
# PROJECT_ROOT = Path(__file__).resolve().parents[1]
# DATA_DIRECTORY = PROJECT_ROOT / DATA_DIRECTORY_NAME / RAW_DIRECTORY_NAME
# INDEX_DIRECTORY = PROJECT_ROOT / INDEX_DIRECTORY_NAME


def main() -> None:
    """Builds the main corpus index and displays associated statistics."""
    
    # creating paths relative to repository root
    data_directory = Path(f"{DATA_DIRECTORY_NAME}/{RAW_DIRECTORY_NAME}")
    index_directory = Path(INDEX_DIRECTORY_NAME)
    
    # building index with default documents per partial index flush (10,000)
    results_summary = build_index(data_directory, index_directory)
    
    # measuring the sizes of final index files
    final_index_files = [
        index_directory / LEXICON_FILE_NAME,
        index_directory / POSTINGS_FILE_NAME,
        index_directory / DOCUMENTS_FILE_NAME
    ]
    final_index_size_in_kb = (
        sum(path.stat().st_size for path in final_index_files) / BYTES_PER_KILOBYTE
    )
    
    # printing measured metrics
    print("\nIndexing completed.")
    print(f"Documents indexed: {results_summary[DOCUMENTS_INDEXED_KEY]:,}")
    print(f"Partial indexes created: {results_summary[PARTIAL_INDEXES_KEY]:,}")
    print(f"Unique terms: {results_summary[UNIQUE_TERMS_KEY]:,}")
    print(f"Final index size: {final_index_size_in_kb:,.2f} KB")


if __name__ == "__main__":
    main()