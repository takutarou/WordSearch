"""
Metadata Manager Module
Handles loading and retrieving metadata for HTML files.
"""

import os
import json
import logging
import unicodedata

logger = logging.getLogger(__name__)


def load_metadata(metadata_path):
    """
    Load metadata from JSON file.

    Args:
        metadata_path: Path to metadata.json file

    Returns:
        dict: Metadata dictionary with file information
              Returns empty dict if file doesn't exist or is invalid
    """
    if not os.path.exists(metadata_path):
        logger.warning(f"Metadata file not found: {metadata_path}")
        return {}

    try:
        with open(metadata_path, 'r', encoding='utf-8') as f:
            metadata = json.load(f)

        if not isinstance(metadata, dict) or 'files' not in metadata:
            logger.warning(f"Invalid metadata format in {metadata_path}")
            return {}

        return metadata.get('files', {})

    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error in {metadata_path}: {e}")
        return {}
    except Exception as e:
        logger.error(f"Error loading metadata from {metadata_path}: {e}")
        return {}


def get_file_metadata(filename, metadata):
    """
    Get metadata for a specific file.

    Args:
        filename: Name of the file (e.g., "毒薬・劇薬.html")
        metadata: Metadata dictionary loaded from metadata.json

    Returns:
        dict: File metadata if found, None otherwise
    """
    if not metadata or not isinstance(metadata, dict):
        return None

    # Normalize filename to NFC (Normalization Form C) for consistent matching
    normalized_filename = unicodedata.normalize('NFC', filename)

    # Try direct lookup first
    if normalized_filename in metadata:
        return metadata[normalized_filename]

    # Try NFD normalization as fallback
    nfd_filename = unicodedata.normalize('NFD', filename)
    if nfd_filename in metadata:
        return metadata[nfd_filename]

    # Try all keys with both normalizations
    for key in metadata.keys():
        if (unicodedata.normalize('NFC', key) == normalized_filename or
            unicodedata.normalize('NFD', key) == normalized_filename):
            return metadata[key]

    return None


def format_metadata_for_display(file_metadata):
    """
    Format metadata for display in UI.

    Args:
        file_metadata: Metadata dictionary for a single file

    Returns:
        dict: Formatted metadata ready for display
    """
    if not file_metadata:
        return None

    formatted = {
        'official_name': file_metadata.get('official_name', ''),
        'short_name': file_metadata.get('short_name', ''),
        'article': file_metadata.get('article', ''),
        'established_date': file_metadata.get('established_date', ''),
        'type': file_metadata.get('type', ''),
        'number': file_metadata.get('number', ''),
        'latest_revision': file_metadata.get('latest_revision', {})
    }

    return formatted


def validate_metadata_schema(metadata):
    """
    Validate metadata schema.

    Args:
        metadata: Metadata dictionary to validate

    Returns:
        tuple: (is_valid, error_messages)
    """
    errors = []

    if not isinstance(metadata, dict):
        errors.append("Metadata must be a dictionary")
        return False, errors

    if 'files' not in metadata:
        errors.append("Missing 'files' key in metadata")
        return False, errors

    files = metadata['files']
    if not isinstance(files, dict):
        errors.append("'files' must be a dictionary")
        return False, errors

    # Validate each file entry
    for filename, file_meta in files.items():
        if not isinstance(file_meta, dict):
            errors.append(f"Invalid metadata for file: {filename}")
            continue

        # Check for expected fields (optional, just warnings)
        expected_fields = ['official_name', 'short_name', 'article',
                          'established_date', 'type', 'number', 'latest_revision']

        for field in expected_fields:
            if field not in file_meta:
                logger.debug(f"File {filename} missing optional field: {field}")

    if errors:
        return False, errors

    return True, []
