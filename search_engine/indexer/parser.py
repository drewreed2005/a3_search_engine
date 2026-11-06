'''
parser.py - extracts normal and important text from webpage HTML
'''

# just like in Assignment 2, we're using BeautifulSoup
from dataclasses import dataclass

from bs4 import BeautifulSoup, Comment, NavigableString

LXML_PARSER = "lxml"
# text within these tags will be considered important
IMPORTANT_TAGS = frozenset(["b", "strong", "title", "h1", "h2", "h3"])
# text within these tags won't be considered at all
NON_TEXT_TAGS = ("script", "style", "meta", "base")


@dataclass
class ParsedContent:
    """
    Stores the text extracted from webpage data.
    
    Attributes:
        text: all extracted webpage text
        important_text: a subset of text contained in impoortant HTML elements
                        (bold, title, and heading tags)
    """
    
    text: str
    important_text: str


def is_important_text(text_node: NavigableString) -> bool:
    """
    Returns true if a given text node belongs to an important HTML element,
    according to IMPORTANT_TAGS.

    Args:
        text_node (str): a BeautifulSoup text node

    Returns:
        bool: True if the node belongs to an important element; False otherwise
    """
    
    # checking all levels of depth within an important element
    for ancestor in text_node.parent.parents:
        if ancestor.name in IMPORTANT_TAGS:
            return True
    
    # also checking the immediate parent
    return text_node.parent.name in IMPORTANT_TAGS


def parse_html(html_content: str) -> ParsedContent:
    """
    Extracts normal and important text from HTML webpage data and returns it in
    the form of a ParsedContent data object.

    Args:
        html_content (str): raw HTML content from a webpage document

    Returns:
        ParsedContent: data object containing normal and important parsed text
    """
    
    # if the content is empty, no need to parse
    if not html_content:
        return ParsedContent(text = "", important_text = "")
    
    # usming lxml to handle malformed HTML like in Assignment 2
    soup = BeautifulSoup(html_content, LXML_PARSER)
    
    # removing content that should not contribute
    for tag in soup.find_all(NON_TEXT_TAGS):
        tag.decompose()
    
    text_segments: list[str] = []
    important_segments: list[str] = []
    
    # parsing all remaining content by traversing text nodes directly
    # (prevents nested important elements from duplicating of normal text collection)
    for text_node in soup.find_all(string = True):
        # skipping HTML comments detected as readable text
        if isinstance(text_node, Comment):
            continue
        # if not a comment, we'll actually read it
        segment = str(text_node).strip()
        
        # ignoring empty/whitespace-only nodes
        if not segment:
            continue
        
        text_segments.append(segment)
        if is_important_text(text_node):
            important_segments.append(segment)
    
    return ParsedContent(
        text = " ".join(text_segments),
        important_text = " ".join(important_segments)
    )