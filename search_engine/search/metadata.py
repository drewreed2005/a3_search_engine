'''
metadata.py - loads document metadata for resolving document IDs to URLs
'''

import json
from pathlib import Path

READ_MODE = "r"
METADATA_ENCODING = "utf-8"

from search_engine.indexer.storage import DOCUMENT_ID_KEY, URL_KEY


def load_document_urls(metadata_path: Path) -> dict[int, str]:
    """
    Loads the document ID-to-URL mapping from JSONL metadata file, which is
    read once at search startup so that retrieved document IDs can be resolved
    without repeated file scanning.

    Args:
        metadata_path (Path): path to the documents.jsonl file

    Returns:
        dict[int, str]: a dictionary mapping each document ID to its URL
    
    Raises:
        FileNotFoundError: if the metadata file does not exist
        ValueError: if a document record is malformed
    """
    document_urls: dict[int, str] = {}
    
    with metadata_path.open(READ_MODE,
            encoding = METADATA_ENCODING) as metadata_file:
        # iterating each line of JSON data and numbering for error printing
        for line_number, line in enumerate(metadata_file, start = 1):
            # ignoring any empty lines
            if not line.strip():
                continue
            
            # attempting to get the record data and handling error
            try:
                record = json.loads(line)
            except json.JSONDecodeError as error:
                # "from error" = this error is the consequence of "error"
                raise ValueError(
                    f"Invalid JSON on line {line_number} of {metadata_path}"
                ) from error
            
            if not isinstance(record, dict):
                raise ValueError(  # noqa: TRY004
                    f"Expected a JSON obejct on line {line_number}"
                )
            
            doc_id = record.get(DOCUMENT_ID_KEY)
            url = record.get(URL_KEY)
            
            # validating document ID (bool is a subclass of int in Python)
            if not isinstance(doc_id, int) or isinstance(doc_id, bool):
                raise ValueError(f"Invalid document ID on line {line_number}")  # noqa: TRY004
            if doc_id in document_urls:
                raise ValueError(
                    f"Duplicate document ID {doc_id} on line {line_number}"
                )
            # validating URL
            if not isinstance(url, str) or not url:
                raise ValueError(f"Invalid URL on line {line_number}")
            
            # we finally know for sure that it's valid
            document_urls[doc_id] = url
    
    return document_urls