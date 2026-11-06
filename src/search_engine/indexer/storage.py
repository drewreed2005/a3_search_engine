'''
storage.py - handles serialization and merging of inverted index data
'''

import heapq
import json
from pathlib import Path
from typing import Any, TextIO

READ_MODE = "r"
WRITE_MODE = "w"
PARTIAL_INDEX_ENCODING = "utf-8"
TERM_KEY = "term"
POSTINGS_KEY = "postings"
NEWLINE = "\n"

# (creating type aliases for readability; reasoning mirrors builder.py)
Posting = tuple[int, int, int]
InvertedIndex = dict[str, list[Posting]]
# heap entries in the merge logic contain term, source file index, and postings
HeapEntry = tuple[str, int, list[Posting]]


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

# parial index JSON lines should look like this:
'''
{"term":"token1","postings":[[0,2,1],[4,9,0]]}
{"term":"token2","postings":[[0,3,2],[2,3,1]]}
'''

def _read_next_record(file: TextIO) -> dict[str, Any] | None:
    """
    Reads the next term record from an open partial index file.

    Args:
        file (TextIO): the open file positioned at the next record

    Returns:
        dict[str, Any] | None: parsed record or None if the file is exhausted
    """


def _initialize_merge_heap(partial_files: list[TextIO]) -> list[HeapEntry]:
    """
    Initializes the merge heap with the first record from each file.

    Args:
        partial_files (list[TextIO]): open partial index files

    Returns:
        list[HeapEntry]: min-heap containing the first records from each file
    """
    heap: list[HeapEntry] = []
    
    # reading the first record from each of the partial files into the heap
    for file_index, file in enumerate(partial_files):
        record = _read_next_record(file)
        
        if record is not None:
            # using Python standard library heapq for min-heap algorithm
            heapq.heappush(
                heap, (record[TERM_KEY], file_index, record[POSTINGS_KEY])
            )
    
    # returning initialized heap
    return heap


def merge_partial_indexes(partial_paths: list[Path], lexicon_path: Path,
    postings_path: Path) -> int:
    """
    Merges sorted partial indexes into a final on-disk index. Merge uses a heap
    structure to enforce term ordering and ensure efficiency.

    Args:
        partial_paths (list[Path]): partial index files in creation order
        lexicon_path (Path): destination path of final term metadata
        postings_path (Path): destination path of final postings data

    Returns:
        int: number of distinct terms written in the final index
    """
    # opening files to centralize resource management
    partial_files = [
        path.open(READ_MODE, encoding = PARTIAL_INDEX_ENCODING)
        for path in partial_paths
    ]
    
    # try/finally block ensures partial index files are always closed,
    # even if an error is raised
    try:
        heap = _initialize_merge_heap(partial_files)
    
    finally:
        for file in partial_files:
            file.close()