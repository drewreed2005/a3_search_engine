'''
metadata.py - loads document metadata for resolving document IDs to URLs
'''

import json
from pathlib import Path


def load_document_urls(metadata_path: Path) -> dict[int, str]:
    """
    Loads the document ID-to-URL mapping from JSONL metadata file, which is
    read once at search startup so that retrieved document IDs can be resolved
    without repeated file scanning.

    Args:
        metadata_path (Path): path to the documents.jsonl file

    Returns:
        dict[int, str]: a dictionary mapping each document ID to its URL
    """