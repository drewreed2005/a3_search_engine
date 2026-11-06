'''
reader.py - provides dataset traversal and webpage document reading functionality
'''

import json
from collections.abc import Iterator
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit, urlunsplit

from search_engine.indexer.document import Document

JSON_FILE_PATTERN = "*.json"

EMPTY = ""

READ_MODE = "r"
# i heard from someone after Assignment 2 that "utf-8-sig" is more reliable encoding
# (unclear whether or not it makes any meaningful difference in this situation)
DOCUMENT_ENCODING = "utf-8-sig"
# we rely on any document we read having this information
URL_FIELD = "url"
CONTENT_FIELD = "content"
ENCODING_FIELD = "encoding"
REQUIRED_DATA_FIELDS = (URL_FIELD, CONTENT_FIELD, ENCODING_FIELD)


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


def normalize_url(url: str) -> str:
    """
    Defragments the given webpage URL to normalize all index URLs.

    Args:
        url (str): original webpage URL beign normalized

    Returns:
        str: defragmented version of the given URL
    """
    
    # recombining the split URL
    return urlunsplit(
        # splitting the URL into its components so that the fragment can be removed
        urlsplit(url)._replace(fragment = EMPTY)
    )


def _validate_json_format(json_data: Any, file_path: Path) -> None:
    """
    Validates the format of the loaded JSON data to ensure it contains
    expected fields for indexing

    Args:
        json_data (Any): the loaded JSON data to be validated
        file_path (Path): the file path from which the data was receievd
    
    Raises:
        TypeError: indicates JSON field contained an invalid type of data
        ValueError: indicates missing required fields
    """
    # validating data
    if not isinstance(json_data, dict):
        raise TypeError(f"Non-JSON data loaded from {file_path}")
    
    # validating the existence/data in each field
    for field in REQUIRED_DATA_FIELDS:
        # ensuring the required field can be found
        if field not in json_data:
            raise ValueError(f"Missing required field \"{field}\" in {file_path}")
        # ensuring the field data is a string
        if not isinstance(json_data[field], str):
            raise TypeError(f"Non-string data from field \"{field}\" in {file_path}")


def read_document(doc_id: int, file_path: Path) -> Document:
    """
    Reads a JSON file and constructs a Document instance from its data.

    Args:
        doc_id (int): sequentially-assigned document ID number
        file_path (Path): path to the JSON file

    Returns:
        Document: document populated with processed JSON data
    
    Raises:
        ValueError: indicates missing required fields
        json.JSONDecodeError: indicates that the file contains invalid JSON
        OSError: indicates that the given file path cannot be accessed
    """
    
    # loading document data
    with file_path.open(READ_MODE, encoding = DOCUMENT_ENCODING) as file:
        data = json.load(file)
    
    # performing multiple validation steps on JSON data format
    # (note: may raise TypeError or ValueError)
    _validate_json_format(data, file_path)
    
    # ensuring the document has a valid found URL
    url = data[URL_FIELD]
    if not url:
        raise ValueError(f"Empty URL in {file_path}")
    
    # document contains defragmented (normalized) URL
    return Document(
        doc_id = doc_id,
        url = normalize_url(url),
        content = data[CONTENT_FIELD],
        encoding = data[ENCODING_FIELD],
        source_path = file_path
    )


def iter_documents(data_dir: Path) -> Iterator[Document]:
    """
    Iterates through all webpage documents in the data directory.

    Args:
        data_dir (Path): root directory with domain subdirectories

    Yields:
        Document: processed Document instance representations of JSON data
    """
    
    # getting the sorted list of document paths with traversal function
    document_paths = discover_documents(data_dir)
    
    # allowing enumeration define unique document IDs
    for doc_id, file_path in enumerate(document_paths):
        yield read_document(doc_id, file_path)
    # (implemented as an iterator to ease memory use)