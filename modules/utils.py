"""
Utility functions for the WordSearch application.

This module provides common utility functions including UUID generation,
timestamp creation, filename sanitization, and directory management.
"""

import uuid
import datetime
import os
import re


def generate_uuid() -> str:
    """
    Generate a unique identifier using UUID4.

    Returns:
        str: A UUID string in hyphenated format (e.g., '123e4567-e89b-12d3-a456-426614174000')

    Examples:
        >>> uid = generate_uuid()
        >>> len(uid)
        36
        >>> '-' in uid
        True
    """
    return str(uuid.uuid4())


def get_timestamp() -> str:
    """
    Generate an ISO 8601 format timestamp for the current UTC time.

    Returns:
        str: ISO 8601 formatted timestamp (e.g., '2025-10-18T12:34:56.789123')

    Examples:
        >>> timestamp = get_timestamp()
        >>> 'T' in timestamp
        True
    """
    return datetime.datetime.utcnow().isoformat()


def sanitize_filename(filename: str) -> str:
    """
    Sanitize a filename for safe filesystem operations.

    Removes or replaces unsafe characters that could cause issues on various
    filesystems. Handles edge cases like empty strings, special characters,
    and path separators.

    Args:
        filename: The filename to sanitize

    Returns:
        str: A sanitized filename safe for filesystem operations

    Examples:
        >>> sanitize_filename("my/file<name>.txt")
        'my_file_name_.txt'
        >>> sanitize_filename("")
        'unnamed'
        >>> sanitize_filename("   ")
        'unnamed'
        >>> sanitize_filename("file:name*test?.txt")
        'file_name_test_.txt'
    """
    if not filename or not filename.strip():
        return "unnamed"

    # Remove leading/trailing whitespace
    filename = filename.strip()

    # Replace path separators and unsafe characters with underscore
    # Unsafe characters: / \ : * ? " < > | and control characters
    unsafe_chars = r'[/\\:*?"<>|\x00-\x1f\x7f]'
    filename = re.sub(unsafe_chars, '_', filename)

    # Replace multiple consecutive underscores with a single underscore
    filename = re.sub(r'_+', '_', filename)

    # Remove leading/trailing dots and underscores (can cause issues on some systems)
    filename = filename.strip('._')

    # If the result is empty after sanitization, return a default name
    if not filename:
        return "unnamed"

    # Limit filename length to 255 characters (common filesystem limit)
    if len(filename) > 255:
        name, ext = os.path.splitext(filename)
        if ext:
            max_name_length = 255 - len(ext)
            filename = name[:max_name_length] + ext
        else:
            filename = filename[:255]

    return filename


def ensure_directory(directory: str) -> None:
    """
    Create a directory if it doesn't exist.

    Creates the directory and any necessary parent directories. Does nothing
    if the directory already exists. Handles edge cases like empty strings
    and invalid paths.

    Args:
        directory: The directory path to create

    Raises:
        ValueError: If directory path is empty or only whitespace
        OSError: If directory creation fails due to permissions or invalid path

    Examples:
        >>> ensure_directory('/tmp/test_dir')
        >>> os.path.exists('/tmp/test_dir')
        True
    """
    if not directory or not directory.strip():
        raise ValueError("Directory path cannot be empty")

    directory = directory.strip()

    # Create directory if it doesn't exist
    if not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)
