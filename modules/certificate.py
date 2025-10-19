"""
Certificate generation module for WordSearch application
"""
import json
import hashlib
import sys
from typing import Dict, Any
from modules import __version__


def generate_certificate(search_results: dict) -> dict:
    """
    Create certificate with search_id, timestamp, results, positive_control, system_info, certificate_hash

    Args:
        search_results: Dictionary containing search results with required fields

    Returns:
        dict: Certificate dictionary
    """
    certificate = {
        "search_id": search_results.get("search_id"),
        "timestamp": search_results.get("timestamp"),
        "search_words": search_results.get("search_words", []),
        "total_files": search_results.get("total_files", 0),
        "results": search_results.get("results", []),
        "positive_control": search_results.get("positive_control", {
            "executed": False,
            "test_cases": [],
            "all_passed": False
        }),
        "system_info": {
            "python_version": sys.version.split()[0],
            "app_version": __version__
        }
    }

    # Calculate certificate hash (excluding the hash field itself)
    certificate["certificate_hash"] = calculate_certificate_hash(certificate)

    return certificate


def save_certificate(certificate: dict, output_path: str) -> bool:
    """
    Save certificate as JSON file

    Args:
        certificate: Certificate dictionary to save
        output_path: Path to save the certificate JSON file

    Returns:
        bool: True if save successful, False otherwise
    """
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(certificate, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Error saving certificate: {e}")
        return False


def calculate_certificate_hash(certificate: dict) -> str:
    """
    Calculate SHA256 hash of certificate (excluding the hash field itself)

    Args:
        certificate: Certificate dictionary

    Returns:
        str: SHA256 hash string
    """
    # Create a copy without the certificate_hash field
    cert_copy = certificate.copy()
    cert_copy.pop("certificate_hash", None)

    # Convert to JSON string with sorted keys for consistent hashing
    cert_json = json.dumps(cert_copy, sort_keys=True, ensure_ascii=False)

    # Calculate SHA256 hash
    sha256_hash = hashlib.sha256(cert_json.encode('utf-8')).hexdigest()

    return sha256_hash
