'''
tokenizer.py - tokenization and stemming functionality for webpage text content
'''

# we are not restricted from using Counter this time, like before, so it's fast to
from collections import Counter
from collections.abc import Iterator

# using Porter stemming as recommended
from nltk.stem import PorterStemmer

# note: tokens are defined as all "alphanumeric sequences" in the dataset, so
#       this is the definition used by this tokenizer


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