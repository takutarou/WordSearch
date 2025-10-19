"""
Flask application for WordSearch
Provides web interface for searching words in HTML/XML files.
"""

import os
import logging
from flask import Flask, jsonify, request, render_template, send_from_directory
from flask_cors import CORS

from modules import search_engine
from modules import file_manager
import config


# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Setup logging
os.makedirs(config.LOG_DIR, exist_ok=True)
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(config.APP_LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


@app.route('/')
def index():
    """
    Render the main index page with total file count.

    Returns:
        Rendered index.html template with total_files count
    """
    try:
        target_files = file_manager.get_target_files(config.DATA_DIR)
        total_files = len(target_files)
        logger.info(f"Index page loaded. Total files: {total_files}")
        return render_template('index.html', total_files=total_files)
    except Exception as e:
        logger.error(f"Error loading index page: {e}")
        return render_template('index.html', total_files=0)


@app.route('/api/search', methods=['POST'])
def api_search():
    """
    Execute search for given words.

    Expected JSON input:
        {
            "words": ["word1", "word2", ...]
        }

    Returns:
        JSON response with search results
    """
    try:
        data = request.get_json()

        if not data or 'words' not in data:
            return jsonify({
                'success': False,
                'error': 'Missing "words" field in request'
            }), 400

        words = data['words']

        # Validate input
        if not isinstance(words, list):
            return jsonify({
                'success': False,
                'error': 'Words must be a list'
            }), 400

        if len(words) == 0:
            return jsonify({
                'success': False,
                'error': 'At least one word is required'
            }), 400

        if len(words) > config.MAX_SEARCH_WORDS:
            return jsonify({
                'success': False,
                'error': f'Maximum {config.MAX_SEARCH_WORDS} words allowed'
            }), 400

        # Validate word lengths
        for word in words:
            if not isinstance(word, str):
                return jsonify({
                    'success': False,
                    'error': 'All words must be strings'
                }), 400

            if len(word) > config.MAX_WORD_LENGTH:
                return jsonify({
                    'success': False,
                    'error': f'Maximum word length is {config.MAX_WORD_LENGTH} characters'
                }), 400

            if len(word.strip()) == 0:
                return jsonify({
                    'success': False,
                    'error': 'Empty words are not allowed'
                }), 400

        logger.info(f"Search request received for words: {words}")

        # Execute search
        results = search_engine.execute_search(words)

        logger.info(f"Search completed. Search ID: {results['search_id']}")

        return jsonify({
            'success': True,
            'data': results
        })

    except Exception as e:
        logger.error(f"Error during search: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/files', methods=['GET'])
def api_files():
    """
    Get list of all target files.

    Returns:
        JSON response with total_files count and file list
    """
    try:
        target_files = file_manager.get_target_files(config.DATA_DIR)

        file_list = []
        for filepath in target_files:
            try:
                file_info = file_manager.get_file_info(filepath)
                file_info['path'] = filepath
                file_list.append(file_info)
            except Exception as e:
                logger.warning(f"Error getting info for file {filepath}: {e}")

        logger.info(f"File list request. Total files: {len(file_list)}")

        return jsonify({
            'success': True,
            'total_files': len(file_list),
            'files': file_list
        })

    except Exception as e:
        logger.error(f"Error getting file list: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/view/<path:filename>')
def view_file(filename):
    """
    Serve highlighted HTML files from output directory.

    Args:
        filename: Path to the file relative to output directory

    Returns:
        HTML file content
    """
    try:
        logger.info(f"View request for file: {filename}")
        return send_from_directory(config.OUTPUT_DIR, filename)
    except Exception as e:
        logger.error(f"Error serving file {filename}: {e}")
        return jsonify({
            'success': False,
            'error': 'File not found'
        }), 404


@app.route('/certificate/<word>/<timestamp>')
def get_certificate(word, timestamp):
    """
    Serve certificate.json file for a specific word and timestamp.

    Args:
        word: Search word
        timestamp: Search timestamp

    Returns:
        certificate.json file content
    """
    try:
        cert_path = os.path.join(config.OUTPUT_DIR, word, timestamp, 'certificate.json')
        logger.info(f"Certificate request for word: {word}, timestamp: {timestamp}")

        if not os.path.exists(cert_path):
            return jsonify({
                'success': False,
                'error': 'Certificate not found'
            }), 404

        directory = os.path.dirname(cert_path)
        filename = os.path.basename(cert_path)
        return send_from_directory(directory, filename)

    except Exception as e:
        logger.error(f"Error serving certificate for {word}/{timestamp}: {e}")
        return jsonify({
            'success': False,
            'error': 'Certificate not found'
        }), 404


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({
        'success': False,
        'error': 'Resource not found'
    }), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    logger.error(f"Internal server error: {error}")
    return jsonify({
        'success': False,
        'error': 'Internal server error'
    }), 500


if __name__ == '__main__':
    # Ensure required directories exist
    os.makedirs(config.DATA_DIR, exist_ok=True)
    os.makedirs(config.OUTPUT_DIR, exist_ok=True)
    os.makedirs(config.LOG_DIR, exist_ok=True)

    logger.info(f"Starting WordSearch application on {config.HOST}:{config.PORT}")
    logger.info(f"Debug mode: {config.DEBUG}")
    logger.info(f"Data directory: {config.DATA_DIR}")
    logger.info(f"Output directory: {config.OUTPUT_DIR}")

    app.run(host=config.HOST, port=config.PORT, debug=config.DEBUG)
