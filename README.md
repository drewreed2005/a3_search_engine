# CS121 Assignment 3 - Search Engine

Group Member: Andrew Reed
NetID: reedas1@uci.edu
Student ID: 94006807


## Milestone 2

### Implemented Functionality

The current implementation extends the indexer with a console search engine interface. It retrieves and ranks webpage results using the disk-based inverted index.

Implemented components include:

- **Query processing**: Normalizes user queries using the same tokenization and Porter-stemming rules as the indexer.
- **Document retrieval**: Retrieves documents containing all query terms using Boolean AND. Terms are processed in ascending document-frequency order to reduce the number of candidate documents during intersection.
- **Disk-based postings access**: Loads the lexicon into memory and reads individual posting lists from `postings.bin` as needed, rather than loading the entire inverted index.
- **Result ranking**: Calculates TF-IDF scores using term frequency, inverse document frequency, and an additional weight for occurrences in important text. (See formula in `ranking.py` documentation.)
- **URL resolution**: Uses `documents.jsonl` to map retrieved document IDs to their corresponding URLs.
- **Result presentation**: Displays ranked URLs and their scores in the console interface.

The current ranking implementation uses weighted TF-IDF rather than cosine similarity, since we have not been instructed on exactly how to perform this yet. Further ranking improvements, including document-length normalization and handling duplicate URLs during indexing, are deferred to a later milestone.

### Running the Search Interface

Ensure that the index has been generated in `index/` (or some other specified index directory) before running the search interface.

From the project root, run:

```bash
python3 -m scripts.search
```

To specify an alternative index directory, run:

```bash
python3 -m scripts.search --index-dir path/to/index
```

To provide a custom number of search results per query (e.g., 10), run:

```bash
python3 -m scripts.search --results 10
```

Enter a query when prompted. An empty query exits the program.

The interface displays the retrieved results in ranked order, including their URLs and scores.


## Milestone 1

### Report

See the `reports/` folder for the Milestone 1 report PDF.
(File name: "CS121 Assignment 3 Milestone 1 – Indexer Report.pdf".)


### Implemented Functionality

The current implementation builds a disk-based inverted index from the provided webpage corpus.

Implemented components include:
- **Document reading**: Discovers and reads webpage JSON files, assigns sequential document IDs and removes URL fragments.
- **HTML parsing**: Extracts webpage text and important text from titles, headings, bold and strong elements.
- **Tokenization**: Extracts alphanumeric tokens, lowercases and Porter-stems them. Stop words are retained.
- **Index construction**: Builds postings containing document IDs, total term frequencies (`tf`), and important text frequencies (`important_tf`).
- **Index storage**: Periodically writes partial indexes to disk and merges them into a final index. (The number of documents per partial indexing is customizeable.)
- **Document metadata**: Stores document ID-to-URL mappings in `documents.jsonl`.
- **Index statistics**: Reports document counts, unique terms, and final index file sizes.

The final index consists of:
- `documents.jsonl` - Document ID-to-URL mappings.
- `lexicon.json` - Term metadata and posting-list locations.
- `postings.bin` - Serialized posting lists.

At the end of a run, partial indexes remain saved for inspection, but may be deleted without issue.


### Requirements

Python 3 and the dependencies listed in `requirements.txt` are required.

Install dependencies from the project root:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```


### Creating the Index

Place the webpage corpus under `data/raw/` in its domain-directory structure.

From the project root, run:

```bash
python3 -m scripts.build_index
```

To display indexing progress and additional status information throughout execution, use:

```bash
python3 -m scripts.build_index --log
```

The completed index is generated in the `index/` directory. Running the indexer again rebuilds the index from the provided corpus.