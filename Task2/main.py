"""
Information Retrieval System - Text-based User Interface
"""

import re
import os
from my_module import (
    load_collection_from_url,
    linear_boolean_search,
    remove_stop_words,
    remove_stop_words_by_frequency,
)
from document import Document

# Global document collection
collection: list[Document] = []


def cmd_load_collection():
    """Prompt the user for collection parameters and load documents from a URL."""
    url = input("Enter URL of the plain text file: ").strip()
    author = input("Author name: ").strip()
    origin = input("Collection title (origin): ").strip()
    try:
        start_line = int(input("Start line (1-based): ").strip())
        end_line = int(input("End line (1-based): ").strip())
    except ValueError:
        print("Invalid line numbers.")
        return

    pattern_str = input("Regex search pattern (leave blank for default Aesop pattern): ").strip()
    if not pattern_str:
        pattern_str = r'([^\n]+)\n\n(.*?)(?=\n{5}(?=[^\n]+\n\n)|$)'
    try:
        search_pattern = re.compile(pattern_str, re.DOTALL)
    except re.error as e:
        print(f"Invalid regex pattern: {e}")
        return

    print(f"Downloading from {url} ...")
    global collection
    collection = load_collection_from_url(url, search_pattern, start_line, end_line, author, origin)
    print(f"Loaded {len(collection)} documents.")


def cmd_search():
    """Search the collection for a single keyword using Boolean retrieval."""
    if not collection:
        print("No documents loaded. Please load a collection first.")
        return

    term = input("Enter search term: ").strip()
    use_filtered = input("Use stop-word-filtered terms? (y/n): ").strip().lower() == "y"

    results = linear_boolean_search(term, collection, stopword_filtered=use_filtered)
    matching = [(score, doc) for score, doc in results if score > 0]

    if not matching:
        print("No documents found.")
    else:
        print(f"Found {len(matching)} document(s):")
        for score, doc in matching:
            print(f"  [{score}] {doc}")


def cmd_apply_stopwords_list():
    """Apply list-based stop word removal to all documents in the collection."""
    if not collection:
        print("No documents loaded.")
        return

    filepath = input("Path to stop word file: ").strip()
    if not os.path.isfile(filepath):
        print("File not found.")
        return

    with open(filepath, "r", encoding="utf-8") as f:
        stopwords = {line.strip().replace(" ", "") for line in f}

    for doc in collection:
        doc._filtered_terms = remove_stop_words(doc.terms, stopwords)

    print(f"Stop word filtering applied to {len(collection)} documents.")


def cmd_apply_stopwords_frequency():
    """Apply frequency-based stop word removal to all documents in the collection."""
    if not collection:
        print("No documents loaded.")
        return

    try:
        common = float(input("Common frequency threshold (e.g. 0.9): ").strip())
        rare = float(input("Rare frequency threshold (e.g. 0.1): ").strip())
    except ValueError:
        print("Invalid frequency value.")
        return

    for doc in collection:
        doc._filtered_terms = remove_stop_words_by_frequency(doc.terms, collection, low_freq=rare, high_freq=common)

    print(f"Frequency-based stop word filtering applied to {len(collection)} documents.")


def print_menu():
    print("\n=== Information Retrieval System ===")
    print("1) Load document collection from URL")
    print("2) Search (Boolean linear search)")
    print("3) Apply stop word removal (list-based)")
    print("4) Apply stop word removal (frequency-based)")
    print("0) Exit")


def main():
    while True:
        print_menu()
        choice = input("Choose an option: ").strip()
        if choice == "1":
            cmd_load_collection()
        elif choice == "2":
            cmd_search()
        elif choice == "3":
            cmd_apply_stopwords_list()
        elif choice == "4":
            cmd_apply_stopwords_frequency()
        elif choice == "0":
            print("Goodbye.")
            break
        else:
            print("Unknown option.")


if __name__ == "__main__":
    main()
