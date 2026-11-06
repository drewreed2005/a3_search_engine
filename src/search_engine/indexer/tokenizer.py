'''
tokenizer.py - tokenization and stemming functionality for webpage text content
'''

import re

# we are not restricted from using Counter this time, like before, so it's fast to
from collections import Counter
from collections.abc import Iterator

# using Porter stemming as recommended
from nltk.stem import PorterStemmer

# note: tokens are defined as all "alphanumeric sequences" in the dataset, so
#       this is the definition used by this tokenizer

# the token pattern here matches consecutive alphanumeric characters (excluding
# underscores), taking into account non-ASCII letters and digits as well
# (Python "re" module is unicode aware, see
#  https://learnbyexample.github.io/py_regular_expressions/unicode.html)
TOKEN_PATTERN = re.compile(r"[^W_]+")
# each piece:
# • r"..." = raw string indicator to clarify pattern expression
# • [...] = denoting that a pool of characters will be matched
# • ^ = negation operator, meaning characters EXCEPT those specified will match
# • \W = indicates all non-word characters
# • _ = literal underscore (matching itself)
# • + = quantifier applied to the set, instructing to match one or more
#       consecutive characters in this pattern
#
# • (and if there's any suspicion of AI because of these bullet points (•),
#    keep in mind that they're easily typed on Mac with Option + "8")

# reusing one stemmer so that a new one isn't constructed every token
_STEMMER = PorterStemmer()

def tokenize(text: str) -> Iterator[str]:
    """
    Extracts normalized tokens from the given text string.

    Args:
        text (str): text to be tokenized

    Yields:
        str: lowercase, stemmed tokens in sequential order
    """
    


def count_terms(text: str) -> Counter[str]:
    """
    Calculates the frequency of each stemmed term in a text string.

    Args:
        text (str): _description_

    Returns:
        Counter[str]: _description_
    """
    
    # Counter very efficiently aggregates repeated terms
    # so it's definitely the right choice of structure for this purpose
    return Counter(tokenize(text))