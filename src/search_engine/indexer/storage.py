'''
storage.py - handles serialization and merging of inverted index data
'''

import json
from pathlib import Path

# (creating type aliases for readability; reasoning mirrors builder.py)
Posting = tuple[int, int, int]
InvertedIndex = dict[str, list[Posting]]


'''
STORAGE STRUCTURE:

index/
├── partials/
│   ├── partial_00000.jsonl
│   ├── partial_00001.jsonl
│   └── ...
├── lexicon.json
├── postings.bin
└── documents.jsonl

• index folder contains all index-related generated files
• partials folder contains sorted intermediate indexes
• lexicon.json maps terms to document frequency and location in postings.bin
    • location represented as offset and length
• postings.bin stores final postings lists
• documents.jsonl maps document IDs to corresponding URLs
'''


def write_partial_index(inverted_index: InvertedIndex,
        output_path: Path) -> None:
    """
    Writes an in-memory inverted index to a sorted partial index file.

    Args:
        inverted_index (InvertedIndex): in-memory inverted index
        output_path (Path): destination path of partial index
    """
    
    # terms are sorted before serialization so that multiple partial indexes
    # can be merged efficiently;
    # postings are already sorted by document ID


def merge_partial_indexes(partial_paths: list[Path], lexicon_path: Path,
    postings_path: Path) -> int:
    """
    Merges sorted partial indexes into a final on-disk index.

    Args:
        partial_paths (list[Path]): partial index files in creation order
        lexicon_path (Path): destination path of final term metadata
        postings_path (Path): destination path of final postings data

    Returns:
        int: number of distinct terms written in the final index
    """