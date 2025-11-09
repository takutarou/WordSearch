"""
設定ファイル
アプリケーション全体で使用する定数やパスを定義
"""
import os

# ベースディレクトリ
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# データディレクトリ
DATA_DIR = os.path.join(BASE_DIR, 'data')

# 出力ディレクトリ
OUTPUT_DIR = os.path.join(BASE_DIR, 'output')

# ログディレクトリ
LOG_DIR = os.path.join(BASE_DIR, 'logs')

# 検索対象ファイル拡張子
SUPPORTED_EXTENSIONS = ['.html', '.htm']

# 検索設定
MAX_SEARCH_WORDS = 100  # 最大検索単語数
MAX_WORD_LENGTH = 200   # 単語の最大文字数

# ハイライト設定
HIGHLIGHT_COLOR = '#FFFF00'  # 黄色

# ログ設定
LOG_LEVEL = 'INFO'
ERROR_LOG_FILE = os.path.join(LOG_DIR, 'error.log')
APP_LOG_FILE = os.path.join(LOG_DIR, 'app.log')

# Flask設定
DEBUG = True
HOST = '127.0.0.1'
PORT = 5000
