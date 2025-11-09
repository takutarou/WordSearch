"""
Positive control validation module for WordSearch application.

This module implements positive control tests by extracting test words from files
and validating that the search function can find them.
"""

import re
from typing import List, Callable
from bs4 import BeautifulSoup
from modules import file_manager


def extract_test_word(filepath: str) -> str:
    """
    Extract a test word (5+ alphanumeric chars) from HTML/XML file.

    Args:
        filepath: Path to the file to extract test word from

    Returns:
        str: A word with 5+ alphanumeric characters, or empty string if none found
    """
    try:
        content = file_manager.read_file(filepath)

        # Parse HTML/XML with BeautifulSoup
        soup = BeautifulSoup(content, 'html.parser')

        # Remove script, style, and meta tags
        for tag in soup(['script', 'style', 'meta']):
            tag.decompose()

        # Extract text content
        text = soup.get_text()

        # Find words with 5+ alphanumeric characters
        pattern = r'\b[a-zA-Z0-9]{5,}\b'
        matches = re.findall(pattern, text)

        # Return the first match if found
        if matches:
            return matches[0]

        return ""
    except Exception:
        return ""


def validate_result(expected: bool, actual: bool) -> str:
    """
    Validate test result by comparing expected and actual values.

    Args:
        expected: Expected boolean result
        actual: Actual boolean result

    Returns:
        str: "PASS" if expected == actual, "FAIL" otherwise
    """
    return "PASS" if expected == actual else "FAIL"


def run_positive_control(files: List[str], search_func: Callable) -> dict:
    """
    Execute positive control tests on provided files.

    Args:
        files: List of file paths to test
        search_func: Search function to validate (should accept word and files parameters)

    Returns:
        dict: Results containing:
            - executed (bool): Whether tests were executed
            - test_cases (list): List of test case results
            - all_passed (bool): Whether all tests passed
    """
    test_cases = []

    for filepath in files:
        test_word = extract_test_word(filepath)

        # Skip if no suitable test word found
        if not test_word:
            continue

        # Expected result is True (positive control - word should be found)
        expected = True

        # Execute search function
        try:
            search_result = search_func(test_word, [filepath])
            # Check if the search found the word (result should not be empty)
            actual = len(search_result) > 0
        except Exception:
            actual = False

        # Validate result
        status = validate_result(expected, actual)

        # Add test case
        test_cases.append({
            'filename': filepath,
            'test_word': test_word,
            'expected': expected,
            'actual': actual,
            'status': status
        })

    # Determine if tests were executed
    executed = len(test_cases) > 0

    # Check if all tests passed
    all_passed = all(tc['status'] == 'PASS' for tc in test_cases) if executed else False

    return {
        'executed': executed,
        'test_cases': test_cases,
        'all_passed': all_passed
    }
