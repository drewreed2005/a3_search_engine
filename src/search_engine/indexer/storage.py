'''
storage.py - handles serialization and merging of inverted index data
'''

import json
from pathlib import Path

WRITE_MODE = "w"
PARTIAL_INDEX_ENCODING = "utf-8"
TERM_KEY = "term"
POSTINGS_KEY = "postings"
NEWLINE = "\n"

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
    # creating the enclosing directory safely if it does not yet exist
    output_path.parent.mkdir(parents = True)
    
    # opening the file to write safely with context manager
    with output_path.open(WRITE_MODE, encoding = PARTIAL_INDEX_ENCODING) as file:
        # terms are sorted before serialization for merge efficiency;
        # postings are already sorted by document ID
        for term in sorted(inverted_index):
            # writing JSON compactly (which does actually reduce intermediate disk usage);
            json.dump(
                {TERM_KEY: term, POSTINGS_KEY: inverted_index[term]},
                file,
                ensure_ascii = False,       # preserving unicode terms
                separators=(",", ":")       # overwriting usual whitespaced separators
            )
            file.write(NEWLINE)


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