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


def is_important_text(text_node: str) -> bool:
    """
    Returns true if a given text node belongs to an important HTML element,
    according to IMPORTANT_TAGS.

    Args:
        text_node (str): a BeautifulSoup text node

    Returns:
        bool: True if the node belongs to an important element; False otherwise
    """
    


def parse_html(html_content: str) -> ParsedContent:
    """
    Extracts normal and important text from HTML webpage data and returns it in
    the form of a ParsedContent data object.

    Args:
        html_content (str): raw HTML content from a webpage document

    Returns:
        ParsedContent: data object containing normal and important parsed text
    """
    