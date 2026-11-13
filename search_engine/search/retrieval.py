'''
retrieval.py - functions to read postings from disk and perform Boolean AND
'''

# retrieval should involve the following operations:
#   1. look up each term in lexicon.json
#       - find each term's offset, length, df
#   2. retrieve its postings from postings.bin
#       - open the file in binary mode, seek to the offset,
#         and the recorded number of bytes
#   3. identify matching document IDs
#       - identified from the postings data for *each term*
#   4. intersect document IDs between matches for terms
# this document should not handle TF-IDF scores or resolve document IDs to URLs

# question remains if stopwords should be filtered out here (maybe?)

import json
from pathlib import Path
from typing import BinaryIO, TypedDict, cast

from search_engine.indexer.builder import Posting

READ_MODE = "r"
LEXICON_ENCODING = "utf-8"

# number of values in each serialized posting
# (document ID, term frequency, and important term frequency)
POSTING_FIELD_COUNT = 3

OFFSET_KEY = "offset"
LENGTH_KEY = "length"
DF_KEY = "df"

# used for good type annotation, as i've done before
class LexiconEntry(TypedDict):
    """Metadata identifying a term's postings record in the index"""
    offset: int
    length: int
    df: int

Lexicon = dict[str, LexiconEntry]

# maps matching document IDs to postings for each query term
DocumentMatches = dict[int, dict[str, Posting]]


def load_lexicon(lexicon_path: Path) -> Lexicon:
    """
    Loads the lexicon from its JSON file, kept in memory so that term
    lookups don't require repeated reading and parsing of the metadata file.

    Args:
        lexicon_path (Path): the path to lexicon.json

    Returns:
        Lexicon: a mapping of terms to their psotings file metadata
    """
    with lexicon_path.open(READ_MODE, encoding = LEXICON_ENCODING) as file:
        # stored JSON structure already matches Lexicon type
        # but cast() gets my type checker to stop bothering me
        return cast(Lexicon, json.load(file))


def _decode_postings(raw_postings: bytes, term: str) -> list[Posting]:
    """
    Decodes and validates a serialized postings list.

    Args:
        raw_postings (bytes): JSON-encoded postings data
        term (str): the term associated with the postings

    Returns:
        list[Posting]: decoded posting data (as tuples)
    
    Raises:
        ValueError: if serialized postings data are malformed
    """
    # parsing the JSON data from the binary data
    parsed_postings = json.loads(raw_postings)
    
    # the postings list must take the form of a list when decoded
    # or something is wrong with the format of the data
    if not isinstance(parsed_postings, list):
        raise ValueError(f"Invalid postings list for term: {term}")  # noqa: TRY004
    
    # preparing to retrieve all postting records
    postings: list[Posting] = []
    
    for record in parsed_postings:
        # validating the posting record data retrieved
        if (
            not isinstance(record, list)
            or len(record) != POSTING_FIELD_COUNT
            or not all(type(value) is int for value in record)
        ):
            raise ValueError(f"Invalid posting record for term: {term}")
        
        # copy of data from the record
        doc_id, tf, important_tf = record
        postings.append((doc_id, tf, important_tf))
    
    return postings


def read_term_postings(term: str, lexicon: Lexicon,
        postings_file: BinaryIO) -> list[Posting]:
    """
    Reads the postings list associated with one term from the disk.

    Args:
        term (str): normalized, stemmed search term
        lexicon (Lexicon): loaded term metadata mapping
        postings_file (BinaryIO): the open postings file (in binary mode)

    Returns:
        list[Posting]: postings for the given term, or an empty list if the
            the term does not exist in the lexicon
    
    Raises:
        OSError: if requested byte range cannot be read
        ValueError: if serialized postings data are malformed
    """
    # getting the current entry
    entry = lexicon.get(term)
    
    if entry is None:
        return []
    
    offset = entry[OFFSET_KEY]
    length = entry[LENGTH_KEY]
    
    # offsets represent byte positions, so we must seek in binary mode data
    postings_file.seek(offset)
    raw_postings = postings_file.read(length)
    
    if len(raw_postings) != length:
        raise OSError(f"Incomplete postings data for term: {term}")
    
    # decoding the found postings to return in proper form
    return _decode_postings(raw_postings, term)


def _get_query_terms_in_retrieval_order(query_terms: list[str],
        lexicon: Lexicon) -> list[str]:
    """
    Removes duplicate terms and prioritizes terms with fewer postings.

    Args:
        query_terms (list[str]): normalized query terms
        lexicon (Lexicon): loaded term metadata

    Returns:
        list[str]: distinct query terms ordered by document frequency
    """
    # removing duplicate terms
    unique_terms = list(dict.fromkeys(query_terms))
    
    # returning in order of term rarity; fewer matches = less intersection work
    return sorted(unique_terms, key = lambda term: lexicon[term][DF_KEY])


def _index_postings_by_document(postings: list[Posting]) -> dict[int, Posting]:
    """
    Creates a document ID lookup for one term's postings.

    Args:
        postings (list[Posting]): posting tuples associated with a single term

    Returns:
        dict[int, Posting]: mapping of document IDs to postings
    """
    return {
        doc_id: posting
        for posting in postings
        for doc_id in [posting[0]]
    }


def retrieve_documents(query_terms: list[str], lexicon: Lexicon,
        postings_file: BinaryIO) -> DocumentMatches:
    """
    Retrieves documents containing every distinct query term (Boolean AND).
    Postings are read from the disk one at a time.

    Args:
        query_terms (list[str]): normalized query terms
        lexicon (Lexicon): loaded term metadata
        postings_file (BinaryIO): open postings file in binary mode

    Returns:
        DocumentMatches: matching documents to query-term postings in ID order
    """
    # if no terms are in the query, no pages to return
    if not query_terms:
        return {}
    
    # missing term guarantees that an AND query cannot generate results
    if any(term not in lexicon for term in query_terms):
        return {}
    
    # using helper to remove duplicate terms and order by fewest postings
    # (makes intersection work afterward less expensive; less to match)
    ordered_terms = _get_query_terms_in_retrieval_order(query_terms, lexicon)
    
    # initializing candidates with rarest query term
    first_term = ordered_terms[0]
    first_postings = read_term_postings(first_term, lexicon, postings_file)
    if not first_postings:
        return {}
    
    matches: DocumentMatches = {
        doc_id: {first_term: posting}
        for doc_id, posting in _index_postings_by_document(
            first_postings
        ).items()
    }