"""
WebページをHTMLファイルとしてダウンロードするスクリプト
"""
import requests
import sys
import os
from bs4 import BeautifulSoup
from urllib.parse import urlparse


def download_html(url, output_filename=None):
    """
    指定されたURLのHTMLをダウンロードして保存する

    Args:
        url: ダウンロードするURL
        output_filename: 保存するファイル名（省略時は自動生成）

    Returns:
        bool: 成功時True、失敗時False
    """
    try:
        print(f"ダウンロード中: {url}")

        # HTTPリクエスト
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()

        # 文字エンコーディングを設定
        response.encoding = response.apparent_encoding

        # 出力ファイル名を決定
        if not output_filename:
            # URLから自動生成
            parsed = urlparse(url)
            params = parsed.query
            if 'dataId=' in params:
                # dataIdパラメータから名前を生成
                data_id = params.split('dataId=')[1].split('&')[0]
                output_filename = f"web_{data_id}.html"
            else:
                # ドメイン名から生成
                domain = parsed.netloc.replace('.', '_')
                output_filename = f"web_{domain}.html"

        # data/ディレクトリに保存
        output_path = os.path.join('data', output_filename)

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(response.text)

        print(f"✓ 保存完了: {output_path}")
        print(f"  ファイルサイズ: {len(response.text):,} 文字")

        # 簡単な統計情報
        soup = BeautifulSoup(response.text, 'html.parser')
        text = soup.get_text()
        word_count = len(text.strip())
        print(f"  テキスト量: {word_count:,} 文字")

        return True

    except requests.exceptions.RequestException as e:
        print(f"✗ エラー: ダウンロードに失敗しました")
        print(f"  {e}")
        return False
    except Exception as e:
        print(f"✗ エラー: {e}")
        return False


def main():
    """メイン処理"""
    print("=" * 60)
    print("HTML ダウンロードツール")
    print("=" * 60)
    print()

    # コマンドライン引数から取得
    if len(sys.argv) < 2:
        print("使い方:")
        print("  python download_html.py <URL> [出力ファイル名]")
        print()
        print("例:")
        print("  python download_html.py https://example.com")
        print("  python download_html.py https://example.com 法令名.html")
        print()
        return

    url = sys.argv[1]
    output_filename = sys.argv[2] if len(sys.argv) > 2 else None

    # ダウンロード実行
    success = download_html(url, output_filename)

    print()
    if success:
        print("完了しました。data/フォルダを確認してください。")
    else:
        print("ダウンロードに失敗しました。")


if __name__ == '__main__':
    main()
