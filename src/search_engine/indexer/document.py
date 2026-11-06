'''
document.py - defines the Document data structure used for indexing
'''

from dataclasses import dataclass
from pathlib import Path


# using Python dataclass to automatically generate initializer
# and helpful representation methods
@dataclass
class Document:
    """
    Represents a single webpage loaded from the provided dataset.
    
    Attributes:
        doc_id: sequential identifier assigned during traversal
        url: original webpage URL (defragmented)
        content: the raw HTML content of the webpage
        encoding: the original webpage encoding, as specified in JSON data
        source_path: file system path to JSON file
    """
    
    # reasoning for these attribute types is trivial
    doc_id: int
    url: str
    content: str
    encoding: str
    source_path: Path
