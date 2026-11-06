'''
build_index.py - runs the complete corpus indexing process and reports statistics
'''

from pathlib import Path

from search_engine.indexer.pipeline import build_index

# data file path info
DATA_DIRECTORY = "data"
RAW_DIRECTORY = "raw"
INDEX_DIRECTORY = "index"

# handling issues with importing from external package
PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIRECTORY = PROJECT_ROOT / DATA_DIRECTORY / RAW_DIRECTORY
INDEX_DIRECTORY = PROJECT_ROOT / INDEX_DIRECTORY


def main() -> None:
    """Builds the main corpus index and displays associated statistics."""
    
    return