"""
ファイル管理モジュール
ファイルの検索、読み込み、情報取得などの操作を提供
"""
import os
import glob
import hashlib
from datetime import datetime
from typing import List
import sys

# プロジェクトルートを追加
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import SUPPORTED_EXTENSIONS


def get_target_files(data_dir: str = "data") -> List[str]:
    """
    指定ディレクトリから対象ファイルを再帰的に取得

    Args:
        data_dir: 検索対象のディレクトリパス

    Returns:
        HTML/XMLファイルのパスリスト
    """
    target_files = []

    # 相対パスの場合は絶対パスに変換
    if not os.path.isabs(data_dir):
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        data_dir = os.path.join(base_dir, data_dir)

    # ディレクトリが存在しない場合は空リストを返す
    if not os.path.exists(data_dir):
        return target_files

    # サポートされている拡張子ごとにファイルを検索
    for ext in SUPPORTED_EXTENSIONS:
        pattern = os.path.join(data_dir, '**', f'*{ext}')
        target_files.extend(glob.glob(pattern, recursive=True))

    return sorted(target_files)


def read_file(filepath: str) -> str:
    """
    ファイルの内容を読み込む

    Args:
        filepath: 読み込むファイルのパス

    Returns:
        ファイルの内容（文字列）

    Raises:
        FileNotFoundError: ファイルが見つからない場合
        IOError: ファイル読み込みエラー
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        raise FileNotFoundError(f"ファイルが見つかりません: {filepath}")
    except Exception as e:
        raise IOError(f"ファイル読み込みエラー: {filepath} - {str(e)}")


def calculate_sha256(filepath: str) -> str:
    """
    ファイルのSHA256ハッシュを計算

    Args:
        filepath: ハッシュを計算するファイルのパス

    Returns:
        SHA256ハッシュ値（16進数文字列）

    Raises:
        FileNotFoundError: ファイルが見つからない場合
        IOError: ファイル読み込みエラー
    """
    try:
        sha256_hash = hashlib.sha256()
        with open(filepath, 'rb') as f:
            # 大きなファイルに対応するため、チャンクで読み込む
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    except FileNotFoundError:
        raise FileNotFoundError(f"ファイルが見つかりません: {filepath}")
    except Exception as e:
        raise IOError(f"ハッシュ計算エラー: {filepath} - {str(e)}")


def get_file_info(filepath: str) -> dict:
    """
    ファイルのメタデータを取得

    Args:
        filepath: 情報を取得するファイルのパス

    Returns:
        ファイル情報を含む辞書
        - name: ファイル名
        - size: ファイルサイズ（バイト）
        - modified: 最終更新日時（ISO形式）

    Raises:
        FileNotFoundError: ファイルが見つからない場合
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"ファイルが見つかりません: {filepath}")

    stat = os.stat(filepath)
    modified_time = datetime.fromtimestamp(stat.st_mtime)

    return {
        'name': os.path.basename(filepath),
        'size': stat.st_size,
        'modified': modified_time.isoformat()
    }
