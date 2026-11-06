'''
reader.py - provides dataset traversal and webpage document reading functionality
'''

import json
from collections.abc import Iterator
from pathlib import Path

from search_engine.indexer.document import Document

JSON_FILE_PATTERN = "*.json"


def discover_documents(data_dir: Path) -> list[Path]:
    """
    Recursively discovers JSON files within the data directory.

    Args:
        data_dir (Path): root directory with domain subdirectories

    Returns:
        list[Path]: a sorted list of JSON file paths
    
    Raises:
        FileNotFoundError: indicates that the data directory does not exist
        NotADirectoryError: indicates that the given path is not a directory
    """
    
    # the data directory must exist or we cannot index
    if not data_dir.exists():
        raise FileNotFoundError(f"Data directory does not exist: {data_dir}")
    # the data directory must also be a directory
    if not data_dir.is_dir():
        raise NotADirectoryError(f"Dataset path is not a directory: {data_dir}")
    
    # using Path's recursive glob (rglob) to recursively search for JSON files;
    # sorting list output to ensure determinism of ID assignment
    return sorted(data_dir.rglob(JSON_FILE_PATTERN))


def read_document(doc_id: int, file_path: Path) -> Document:
    """
    Reads a JSON file and constructs a Document instance from its data.

    Args:
        doc_id (int): sequentially-assigned document ID number
        file_path (Path): path to the JSON file

    Returns:
        Document: document populated with processed JSON data
    """
    


def iter_documents(data_dir: Path) -> Iterator[Document]:
    """
    Iterates through all webpage documents in the data directory.

    Args:
        data_dir (Path): root directory with domain subdirectories

    Yields:
        Document: processed Document instance representations of JSON data
    """