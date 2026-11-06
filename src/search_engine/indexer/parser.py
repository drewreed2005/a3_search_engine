'''
parser.py - extracts normal and important text from webpage HTML
'''

# just like in Assignment 2, we're using BeautifulSoup
from dataclasses import dataclass

from bs4 import BeautifulSoup

# text within these tags will be considered important
IMPORTANT_TAGS = frozenset(["b", "strong", "h1", "h2", "h3"])
# text within these tags won't be considered at all
SKIP_TAGS = ("script", "style", "meta", "base")


@dataclass
class ParsedContent:
    """
    Stores the text extracted from webpage data.
    
    Attributes:
        text: all extracted webpage text
        important_text: a subset of text contained in impoortant HTML elements
                        (bold tags or heading tags)
    """
    
    text: str
    important_text: str