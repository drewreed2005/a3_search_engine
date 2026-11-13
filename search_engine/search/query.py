'''
query.py - functions to normalize, tokenize, and stem user queries
'''

from search_engine.indexer.tokenizer import tokenize


def process_query(query: str) -> list[str]:
    """
    Normalizes a user query into tokenized, stemmed search terms.

    Args:
        query (str): the search query to be processed

    Returns:
        list[str]: a list of normalized query terms
    """
    # reusing the existing indexer tokenizer to ensure the same rules are followed
    return list(tokenize(query))