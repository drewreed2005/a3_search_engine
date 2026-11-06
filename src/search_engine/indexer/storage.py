'''
storage.py - handles serialization and merging of inverted index data
'''

import heapq
import json
from collections.abc import Iterator
from pathlib import Path
from typing import Any, TextIO

# start of constants
READ_MODE = "r"
WRITE_MODE = "w"
WRITE_BYTES_MODE = "wb"
PARTIAL_INDEX_ENCODING = "utf-8"
LEXICON_ENCODING = "utf-8"

TERM_KEY = "term"
POSTINGS_KEY = "postings"

NEWLINE = "\n"
START_BRACE = "{"
END_BRACE = "}"
# (postings file is bin; using bytes)
START_BRACKET_BYTE = b"["
END_BRACKET_BYTE = b"]"
COMMA_BYTE = b","

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


def _write_lexicon_entry(lexicon_file: TextIO, term: str, offset: int,
        length: int, document_frequency: int, is_first_entry: bool) -> None:
    """
    Writes one term's metadata to the final lexicon at the open file location.
    
    Args:
        lexicon_file (TextIO): open lexicon output file
        term (str): the indexed term
        offset (int): the starting byte position in the postings file
        length (int): number of bytes occupied by this term's postings list
        document_frequency (int): number of documents containing the term
        is_first_entry (bool): if this is the first lexicon entry (special)
    """


def _iter_merged_postings(partial_files: list[TextIO],
        heap: list[HeapEntry]) -> Iterator[tuple[str, Posting]]:
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


def _write_final_index(merged_postings: Iterator[tuple[str, Posting]],
        lexicon_path: Path, postings_path: Path) -> int:
    """
    Writes sorted merged postings and their metadata to the final index.

    Args:
        merged_postings (Iterator[tuple[str, Posting]]): ordered iterator
            stream of term-posting pairs
        lexicon_path: destination for final term metadata
        postings_path: destination for final postings data

    Returns:
        int: the number of distinct terms written
    """
    
    # making the lexicon and postings destination paths safely, if necessary
    lexicon_path.parent.mkdir(parents = True, exist_ok = True)
    postings_path.parent.mkdir(parents = True, exist_ok = True)
    
    # preparing to iterate terms
    unique_term_count = 0
    current_term: str | None = None
    current_offset = 0              # starting position of the term's postings
    current_df = 0                  # number of postings written for this term
    first_posting = True            # used for comma formatting
    
    # opening the output files to write
    with (
        postings_path.open(WRITE_BYTES_MODE) as postings_file,
        lexicon_path.open(WRITE_MODE, encoding = LEXICON_ENCODING) as lexicon_file
    ):
        lexicon_file.write(START_BRACE)
        
        # iterating each term and associated posting list
        # (note that merged_postings is an iterator; file is written over time)
        for term, posting in merged_postings:
            # if the term is a new term and the current term isn't None (initial),
            # the previous postings list is complete
            if term != current_term:
                # closing the previous posting list and writing to the lexicon
                # if the current term is not None (indicating initial iteration)
                if current_term is not None:
                    postings_file.write(END_BRACKET_BYTE)
            
                # beginning a new postings list at the current byte position
                postings_file.write(START_BRACKET_BYTE)
        
            # writing the current posting (leading with a comma if necessary)
            if not first_posting:
                postings_file.write(COMMA_BYTE)
            
            # posting is encoded as compactly as possible
            
            # noting the additional posting for this term
            first_posting = False
            current_df += 1
        
        # finalizing the last term after the postings iterator is exhausted
        if current_term is not None:
            # writing final bracket for postings
            postings_file.write(END_BRACKET_BYTE)
            
            # noting byte length for final lexicon entry
            
            # writing final entry
        
        # closing with final brace
        lexicon_file.write(END_BRACE)
    
    return unique_term_count


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
        
        # writing the final index at target paths using the merged postings
        return _write_final_index(merged_postings, lexicon_path, postings_path)
    
    finally:
        for file in partial_files:
            file.close()