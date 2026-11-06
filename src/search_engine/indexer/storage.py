'''
storage.py - handles serialization and merging of inverted index data
'''

import heapq
import json
from collections.abc import Iterator
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
    # reading one line (a term's worth of information due to our formatting)
    line = file.readline()
    
    # returning None if the file is exhausted/empty
    if not line:
        return None
    
    # otherwise, returning the data interpreted as a standard Python dict
    return json.loads(line)


def _initialize_merge_heap(partial_files: list[TextIO]) -> list[HeapEntry]:
    """
    Initializes the merge heap with the first record from each file.

    Args:
        partial_files (list[TextIO]): open partial index files

    Returns:
        list[HeapEntry]: min-heap containing the first records from each file
    """
    # heap is represented here as a list of HeapEntry;
    # python heapq is used to enforce actual behavior
    heap: list[HeapEntry] = []
    
    for file_index, file in enumerate(partial_files):
        # reading the first record from each of the partial files into the heap
        record = _read_next_record(file)
        
        # if None, it means the file is empty (not even a first term exists)
        if record is not None:
            # using Python standard library heapq for min-heap algorithm
            heapq.heappush(
                heap, (record[TERM_KEY], file_index, record[POSTINGS_KEY])
            )
    
    # returning initialized heap
    return heap


def _advance_merge_heap(heap: list[HeapEntry], partial_files: list[TextIO],
        file_index: int) -> None:
    """
    Reads the next record from a consumed partial index into the heap.

    Args:
        heap (list[HeapEntry]): the active merge heap
        partial_files (list[TextIO]): open partial index files
        file_index (int): Index of the file whose record was consumed.
    """
    # reading the next term record from the partial index at the given index
    record = _read_next_record(partial_files[file_index])
    
    # pushing to the heap if the file is not exhausted
    if record is not None:
        heapq.heappush(
            heap, (record[TERM_KEY], file_index), record[POSTINGS_KEY]
        )


def _iter_merged_postings(
    partial_files: list[TextIO],
    heap: list[HeapEntry]
) -> Iterator[tuple[str, Posting]]:
    """
    Yields individual postings in term and document ID order, grouped naturally
    by the heap structure.

    Args:
        partial_files (list[TextIO]): open partial index files
        heap (list[HeapEntry]): an (initialized) merge heap

    Yields:
        tuple[str, Posting]: a term and one associated posting each iteration
    """
    # merging while the heap is not empty
    while heap:
        # getting all relevant information from the "smallest" item in the heap
        term, file_index, postings = heapq.heappop(heap)
        
        # streaming postings individually for memory efficiency
        # (especially important for frequently recurring terms)
        for posting in postings:
            yield term, tuple(posting)

        # advancing this file after its current record is consumed
        # (moving on to its next line of term info)
        _advance_merge_heap(heap, partial_files, file_index)


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
        # initializing the heap with the first terms from the partial indexes
        heap = _initialize_merge_heap(partial_files)
        
        # merging postings from each of the partial index files
        merged_postings = _iter_merged_postings(partial_files, heap)
    
    finally:
        for file in partial_files:
            file.close()