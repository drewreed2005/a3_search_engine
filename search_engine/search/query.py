'''
query.py - functions to normalize, tokenize, and stem user queries
'''

from search_engine.indexer.tokenizer import tokenize

# TODO:
# i feel like i should have done this previously
# but i would definitely like to handle stop word stuff at query time
# so make sure to go and do that


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