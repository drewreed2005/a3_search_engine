'''
pipeline.py - combines indexer functionality into a single index builder function
'''

from pathlib import Path

from search_engine.indexer.builder import InvertedIndex, add_document_to_index
from search_engine.indexer.reader import iter_documents
from search_engine.indexer.storage import merge_partial_indexes, write_partial_index

# defining the number of documents processed per partial index
DEFAULT_DOCUMENTS_PER_PARTIAL = 10000


def build_index(data_directory: Path, index_directory: Path,
        documents_per_partial: int = DEFAULT_DOCUMENTS_PER_PARTIAL) -> dict[str, int]:
    """
    Builds the complete file system-based inverted index from the corpus.
    Processes documnets sequentually in memory until reaching the set document
    limit, at which point the index is written to a sorted partial index file.
    Partial indexes are merged into final lexicon and postings files once all
    documents have been processed.

    Args:
        data_directory (Path): directory containing the webpage JSON files
        index_directory (Path): directory where index files will be stored
        documents_per_partial (int): maximum number of documents to process
            before flushing the current in-memory index to disk

    Returns:
        dict[str, int]: summary containing the number of documents indexed,
            partial indexes created, and unique terms in the final index
    """