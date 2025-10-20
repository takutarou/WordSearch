"""
Core search engine module for WordSearch application.
Orchestrates all search operations and module interactions.
"""

import os
import re
import hashlib
from datetime import datetime
from typing import List, Dict, Optional
from bs4 import BeautifulSoup

from modules import file_manager
from modules import highlighter
from modules import certificate
from modules import positive_control
from modules import utils


def normalize_word(word: str) -> str:
    """
    Normalize a word by converting to lowercase and stripping whitespace.

    Args:
        word: The word to normalize

    Returns:
        Normalized word (lowercase, stripped)
    """
    return word.lower().strip()


def search_in_file(filepath: str, word: str) -> List[dict]:
    """
    Search for a word in a file and return all hit positions.

    Args:
        filepath: Path to the file to search
        word: The word to search for (case-insensitive)

    Returns:
        List of dictionaries containing hit information:
        - line: Line number (1-indexed)
        - column: Column number (1-indexed)
        - context: Text context around the hit
    """
    hits = []

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        # Parse HTML with BeautifulSoup
        soup = BeautifulSoup(content, 'html.parser')

        # Remove script, style, and meta tags
        for tag in soup(['script', 'style', 'meta']):
            tag.decompose()

        # Get text content
        text = soup.get_text()

        # Split into lines for line number tracking
        lines = text.split('\n')

        # Search for word (case-insensitive)
        # Use word boundaries only for ASCII words
        if word.isascii() and word.replace('_', '').isalnum():
            pattern = re.compile(r'\b' + re.escape(word) + r'\b', re.IGNORECASE)
        else:
            # For non-ASCII (Japanese, etc.), match without word boundaries
            pattern = re.compile(re.escape(word), re.IGNORECASE)

        for line_num, line in enumerate(lines, 1):
            for match in pattern.finditer(line):
                column = match.start() + 1  # 1-indexed

                # Extract context (50 chars before and after)
                start = max(0, match.start() - 50)
                end = min(len(line), match.end() + 50)
                context = line[start:end].strip()

                hits.append({
                    'line': line_num,
                    'column': column,
                    'context': context
                })

    except Exception as e:
        print(f"Error searching in file {filepath}: {e}")

    return hits


def execute_search(words: List[str]) -> dict:
    """
    Main search function that orchestrates the entire search process.

    Args:
        words: List of words to search for

    Returns:
        Dictionary containing:
        - search_id: Unique identifier for this search
        - timestamp: ISO format timestamp
        - words: List of normalized search words
        - results: Dictionary mapping words to their search results
        - output_directories: Dictionary mapping words to their output directories
    """
    # Generate search ID and timestamp
    search_id = utils.generate_uuid()
    timestamp = datetime.now().isoformat()
    timestamp_str = datetime.now().strftime('%Y%m%d_%H%M%S')

    # Normalize all search words
    normalized_words = [normalize_word(word) for word in words]

    # Get target files using file_manager
    target_files = file_manager.get_target_files()

    if not target_files:
        print("No target files found.")
        return {
            'search_id': search_id,
            'timestamp': timestamp,
            'words': normalized_words,
            'results': {},
            'output_directories': {}
        }

    # Results structure
    results = {}
    output_directories = {}

    # Process each word separately
    for word in normalized_words:
        print(f"\nSearching for word: {word}")
        word_results = []

        # Create output directory for this word
        output_dir = os.path.join('output', word, timestamp_str)
        os.makedirs(output_dir, exist_ok=True)
        output_directories[word] = output_dir

        # Search in each file
        for filepath in target_files:
            print(f"  Searching in: {filepath}")

            try:
                # Read file content
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Calculate SHA256 hash
                file_hash = hashlib.sha256(content.encode('utf-8')).hexdigest()

                # Parse HTML with BeautifulSoup
                soup = BeautifulSoup(content, 'html.parser')

                # Remove script, style, and meta tags for searching
                soup_copy = BeautifulSoup(content, 'html.parser')
                for tag in soup_copy(['script', 'style', 'meta']):
                    tag.decompose()

                text = soup_copy.get_text()

                # Search for word (case-insensitive)
                # Use word boundaries only for ASCII words
                if word.isascii() and word.replace('_', '').isalnum():
                    pattern = re.compile(r'\b' + re.escape(word) + r'\b', re.IGNORECASE)
                else:
                    # For non-ASCII (Japanese, etc.), match without word boundaries
                    pattern = re.compile(re.escape(word), re.IGNORECASE)
                matches = pattern.findall(text)

                if matches:
                    # Get detailed hit positions
                    hits = search_in_file(filepath, word)

                    # Use highlighter to create highlighted HTML
                    highlighted_html = highlighter.highlight_word(content, word)

                    # Save highlighted HTML
                    filename = os.path.basename(filepath)
                    output_filename = f"highlighted_{filename}"
                    output_path = os.path.join(output_dir, output_filename)

                    with open(output_path, 'w', encoding='utf-8') as f:
                        f.write(highlighted_html)

                    # Calculate relative path from output directory
                    relative_path = os.path.join(word, timestamp_str, output_filename)

                    # Store result
                    word_results.append({
                        'file': filepath,
                        'filename': filename,
                        'hash': file_hash,
                        'hits': len(matches),
                        'hit_positions': hits,
                        'highlighted_file': output_path,
                        'highlighted_relative': relative_path
                    })

                    print(f"    Found {len(matches)} hit(s)")
                else:
                    # Store result even when no hits found
                    filename = os.path.basename(filepath)
                    word_results.append({
                        'file': filepath,
                        'filename': filename,
                        'hash': file_hash,
                        'hits': 0,
                        'hit_positions': [],
                        'highlighted_file': None,
                        'highlighted_relative': None
                    })
                    print(f"    No hits found")

            except Exception as e:
                print(f"    Error processing file: {e}")

        # Run positive control
        print(f"\nRunning positive control for word: {word}")
        control_result = positive_control.run_positive_control(word, output_dir)

        # Generate and save certificate for this word
        print(f"Generating certificate for word: {word}")
        cert_data = {
            'search_id': search_id,
            'timestamp': timestamp,
            'search_words': [word],
            'total_files': len(target_files),
            'results': word_results,
            'positive_control': control_result
        }

        cert = certificate.generate_certificate(cert_data)
        cert_path = os.path.join(output_dir, 'certificate.json')
        certificate.save_certificate(cert, cert_path)
        print(f"Certificate saved: {cert_path}")

        # Store results for this word
        results[word] = {
            'hits_found': len(word_results) > 0,
            'files_with_hits': len(word_results),
            'total_hits': sum(r['hits'] for r in word_results),
            'results': word_results,
            'positive_control': control_result,
            'certificate': cert_path
        }

    print(f"\n{'='*60}")
    print("Search completed successfully!")
    print(f"Search ID: {search_id}")
    print(f"Timestamp: {timestamp}")

    return {
        'search_id': search_id,
        'timestamp': timestamp,
        'words': normalized_words,
        'results': results,
        'output_directories': output_directories
    }
