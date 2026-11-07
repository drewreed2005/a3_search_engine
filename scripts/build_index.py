'''
build_index.py - runs the complete corpus indexing process and reports statistics
'''

import argparse
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
    
    # completely optional addition for quality of life:
    # allows the user to use "--log" to have increased transparency during indexing
    parser = argparse.ArgumentParser(
        description = "Build the search engine index."
    )
    parser.add_argument(
        "--log",
        action = "store_true",
        help = "Display benchmarks during the indexer process."
    )
    args = parser.parse_args()
    
    # creating paths relative to repository root
    data_directory = Path(f"{DATA_DIRECTORY_NAME}/{RAW_DIRECTORY_NAME}")
    index_directory = Path(INDEX_DIRECTORY_NAME)
    
    # building index with default documents per partial index flush (10,000)
    results_summary = build_index(data_directory, index_directory, should_log = args.log)
    
    # measuring the sizes of final index files
    index_files = {
        "Lexicon": index_directory / LEXICON_FILE_NAME,
        "Postings": index_directory / POSTINGS_FILE_NAME,
        "Document metadata": index_directory / DOCUMENTS_FILE_NAME
    }
    file_sizes_in_bytes = {
        name: path.stat().st_size
        for name, path in index_files.items()
    }
    total_size_bytes = sum(file_sizes_in_bytes.values())
    
    # printing measured metrics
    print("\nIndexing completed.")
    print(f"Documents indexed: {results_summary[DOCUMENTS_INDEXED_KEY]:,}")
    print(f"Partial indexes created: {results_summary[PARTIAL_INDEXES_KEY]:,}")
    print(f"Unique terms: {results_summary[UNIQUE_TERMS_KEY]:,}")
    
    print("\nFinal index file sizes:")
    for name, size_bytes in file_sizes_in_bytes.items():
        size_kb = size_bytes / BYTES_PER_KILOBYTE
        print(f"  {name}: {size_kb:,.2f} KB")
    print(f"Total: {total_size_bytes / BYTES_PER_KILOBYTE:,.2f} KB")


if __name__ == "__main__":
    main()