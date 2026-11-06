'''
reader.py - provides dataset traversal and webpage document reading functionality
'''

import json
from collections.abc import Iterator
from pathlib import Path

from search_engine.indexer.document import Document


def discover_documents(data_directory: Path) -> list[Path]:
    """
    

    Args:
        data_directory (Path): root directory with domain subdirectories

    Returns:
        list[Path]: a sorted list of JSON file paths
    """
    


def read_document(doc_id: int, file_path: Path) -> Document:
    """
    Reads a JSON file and constructs a Document instance from its data.

    Args:
        doc_id (int): sequentially-assigned document ID number
        file_path (Path): path to the JSON file

    Returns:
        Document: document populated with processed JSON data
    """
    


def iter_documents(data_directory: Path) -> Iterator[Document]:
    """
    Iterates through all webpage documents in the dataset.

    Args:
        data_directory (Path): root directory with domain subdirectories

    Yields:
        Document: processed Document instance representations of JSON data
    """