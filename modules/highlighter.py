"""
HTML highlighting module for WordSearch application.
Handles word highlighting in HTML content and file output.
"""

import re
import os
from modules.utils import sanitize_filename, ensure_directory


def highlight_word(html_content: str, word: str, color: str = "#FFFF00") -> str:
    """
    Wrap matched words with <mark> tags.

    Args:
        html_content: HTML content to process
        word: Word to highlight
        color: Background color for highlighting (default: #FFFF00)

    Returns:
        HTML content with highlighted words
    """
    # Use word boundaries only for ASCII words
    if word.isascii() and word.replace('_', '').isalnum():
        pattern = re.compile(r'\b' + re.escape(word) + r'\b', re.IGNORECASE)
    else:
        # For non-ASCII (Japanese, etc.), match without word boundaries
        pattern = re.compile(re.escape(word), re.IGNORECASE)

    # Use a replacement function to preserve the matched case
    def replace_match(match):
        return f'<mark style="background-color: {color};">{match.group(0)}</mark>'

    return pattern.sub(replace_match, html_content)


def save_highlighted_html(content: str, output_path: str) -> bool:
    """
    Save highlighted HTML to file.

    Args:
        content: HTML content to save
        output_path: Path to save the file

    Returns:
        True if successful, False otherwise
    """
    try:
        parent_dir = os.path.dirname(output_path)
        if parent_dir:
            ensure_directory(parent_dir)

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)

        return True
    except Exception as e:
        print(f"Error saving highlighted HTML: {e}")
        return False


def generate_highlighted_path(word: str, timestamp: str, original_filename: str) -> str:
    """
    Generate output path for highlighted HTML file.

    Args:
        word: Search word
        timestamp: Timestamp string
        original_filename: Original HTML filename

    Returns:
        Output path like "output/{word}/{timestamp}/highlighted/{filename}_highlighted.html"
    """
    sanitized_word = sanitize_filename(word)

    # Remove .html extension if present
    if original_filename.endswith('.html'):
        base_filename = original_filename[:-5]
    else:
        base_filename = original_filename

    highlighted_filename = f"{base_filename}_highlighted.html"

    output_path = os.path.join(
        "output",
        sanitized_word,
        timestamp,
        "highlighted",
        highlighted_filename
    )

    return output_path
