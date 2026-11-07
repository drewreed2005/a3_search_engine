# CS121 Assignment 3 - Search Engine

Group Member: Andrew Reed
NetID: reedas1@uci.edu
Student ID: 94006807


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