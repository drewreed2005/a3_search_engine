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

from pathlib import Path
from typing import TypedDict


# used for good type annotation, as i've done before
class LexiconEntry(TypedDict):
    offset: int
    length: int
    df: int

Lexicon = dict[str, LexiconEntry]


def load_lexicon(lexicon_path: Path) -> Lexicon:
    """
    Loads the lexicon from its JSON file, kept in memory so that term
    lookups don't require repeated reading and parsing of the metadata file.

    Args:
        lexicon_path (Path): _description_

    Returns:
        Lexicon: _description_
    """