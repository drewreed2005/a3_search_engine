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
• postings.bin stores final postings lists
• documents.jsonl maps document IDs to corresponding URLs
'''


def write_partial_index(inverted_index: InvertedIndex,
        output_path: Path) -> None:
    """
    Writes an in-memory inverted index to a sorted partial index file.

    Args:
        inverted_index (InvertedIndex): _description_
        output_path (Path): _description_
    """
    
    # terms are sorted before serialization so that multiple partial indexes
    # can be merged efficiently;
    # postings are already sorted by document ID


