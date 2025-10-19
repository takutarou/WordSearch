# Document Word Search System

文書内の特定単語を検索し、検索結果の証跡を確実に残すWebアプリケーション

## 📋 概要

HTML/XMLファイル内の特定単語の存在を検索し、検索結果をハイライト表示するとともに、検索証明書を生成してコンプライアンスや監査対応を支援します。

### 主な機能

- ✅ 複数単語の同時検索（OR検索）
- ✅ 大文字小文字を区別しない完全一致検索
- ✅ ヒット箇所の蛍光ペン風ハイライト表示
- ✅ タイムスタンプ付き検索証明書（JSON）の自動生成
- ✅ SHA256ハッシュによるファイル改ざん検知
- ✅ ポジティブコントロールによる検索機能の正常性証明

## 🚀 セットアップ

### 必要な環境

- Python 3.8以上
- Webブラウザ（Chrome, Firefox, Safari等）

### インストール手順

```bash
# 1. リポジトリのディレクトリに移動
cd WordSearch

# 2. 仮想環境を有効化
source .venv/bin/activate  # macOS/Linux
# または
.venv\Scripts\activate  # Windows

# 3. 依存パッケージをインストール
pip install -r requirements.txt

# 4. アプリケーションを起動
python app.py
```

### 初回起動後

ブラウザで以下にアクセス:
```
http://127.0.0.1:5000
```

## 📁 ディレクトリ構成

```
WordSearch/
├── app.py                 # Flaskアプリケーション
├── config.py              # 設定ファイル
├── requirements.txt       # 依存パッケージ
├── data/                  # 検索対象ファイル（HTML/XML）を配置
├── output/                # 検索結果出力
│   └── {検索単語}/
│       └── {タイムスタンプ}/
│           ├── highlighted/     # ハイライト済みHTML
│           └── certificate.json # 検索証明書
├── modules/               # ビジネスロジック
│   ├── search_engine.py
│   ├── file_manager.py
│   ├── highlighter.py
│   ├── certificate.py
│   ├── positive_control.py
│   └── utils.py
├── templates/             # HTMLテンプレート
└── static/                # CSS/JavaScript
```

## 📖 使い方

### 1. 検索対象ファイルの配置

`data/` ディレクトリにHTML/XMLファイルを配置します。

```bash
cp your_files/*.html data/
```

### 2. 検索の実行

1. ブラウザで `http://127.0.0.1:5000` にアクセス
2. 検索したい単語を入力
3. 必要に応じて「検索欄を追加」ボタンで複数の単語を追加
4. 「検索実行」ボタンをクリック

### 3. 結果の確認

- **ヒットした場合**:
  - 画面に結果が表示される
  - ハイライト済みHTMLファイル: `output/{単語}/{タイムスタンプ}/highlighted/`
  - 検索証明書: `output/{単語}/{タイムスタンプ}/certificate.json`

- **非ヒットの場合**:
  - 検索証明書のみが生成される

## 🔍 検索証明書の内容

証明書（JSON）には以下の情報が含まれます:

- 検索実行日時（タイムスタンプ）
- 検索単語リスト
- 各単語の検索結果（ヒット/非ヒット）
- ヒットした場合のファイル名と位置
- 各ファイルのSHA256ハッシュ値（改ざん検知用）
- ポジティブコントロール結果（検索機能の正常性証明）
- システム情報（Python版、アプリ版）
- 証明書自体のハッシュ値

## ⚙️ 設定

`config.py` で以下の設定を変更できます:

```python
# 検索設定
MAX_SEARCH_WORDS = 100      # 最大検索単語数
MAX_WORD_LENGTH = 200       # 単語の最大文字数

# ハイライト設定
HIGHLIGHT_COLOR = '#FFFF00' # 黄色

# Flask設定
DEBUG = True
HOST = '127.0.0.1'
PORT = 5000
```

## 📚 ドキュメント

詳細な設計書は `docs/` ディレクトリに格納されています:

- [01_要件定義書.md](docs/01_要件定義書.md)
- [02_機能仕様書.md](docs/02_機能仕様書.md)
- [03_画面設計書.md](docs/03_画面設計書.md)
- [05_システム構成図.md](docs/05_システム構成図.md)
- [06_ディレクトリ構成とファイル一覧.md](docs/06_ディレクトリ構成とファイル一覧.md)

## 🛠️ 技術スタック

- **バックエンド**: Python 3.8+, Flask 2.3+
- **HTMLパーサー**: BeautifulSoup4 4.12+, lxml 4.9+
- **フロントエンド**: HTML5, CSS3, JavaScript (jQuery 3.6+)
- **データ管理**: ファイルシステムベース（データベース不使用）

## 🔐 セキュリティ

- ローカル環境での利用を想定（ユーザー認証不要）
- ファイルパスのサニタイズ処理実装
- XSS対策（Jinja2の自動エスケープ）
- SHA256ハッシュによるファイル完全性チェック

## 📝 ライセンス

このプロジェクトは内部利用を目的としています。

## 🤝 貢献

バグ報告や機能リクエストは、プロジェクト管理者にお問い合わせください。

---

**Document Word Search System v1.0.0**
🤖 Generated with [Claude Code](https://claude.com/claude-code)
