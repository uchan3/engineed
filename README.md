# 🔧 Engineed

**AI-powered Technical News Aggregator for Japanese Tech Sites**

Engineedは日本の主要技術サイト（Qiita、Zenn、はてなブックマーク）から技術記事を自動収集し、AI分析によって整理・分類する技術記事アグリゲーターです。

![Python](https://img.shields.io/badge/Python-3.9+-blue)
![Scrapy](https://img.shields.io/badge/Scrapy-2.11+-green)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-red)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0+-orange)

## ✨ 主な機能

- 🕷️ **マルチサイトスクレイピング**: Qiita、Zenn、はてなブックマークから記事を自動収集
- 🤖 **AI分析**: OpenAI GPTによるキーワード抽出と内容分析
- 🎨 **モダンWebUI**: レスポンシブデザインの記事表示インターフェース
- 📊 **学習管理**: ユーザーの学習進捗と推奨記事機能（設計済み）
- 🔧 **CLI管理**: 簡単なコマンドラインインターフェース

## 🚀 クイックスタート

### 1. インストール

```bash
# リポジトリをクローン
git clone https://github.com/uchan3/engineed.git
cd engineed

# 依存関係をインストール
pip install -r requirements.txt

# パッケージをインストール
pip install -e .
```

### 2. 初期設定

```bash
# データベースを初期化
python -m engineed.cli init-db

# テストデータを作成（オプション）
python create_test_data.py
```

### 3. 記事収集を開始

```bash
# 特定のサイトから記事を収集
python -m engineed.cli crawl -s qiita --test
python -m engineed.cli crawl -s zenn --test
python -m engineed.cli crawl -s hateb --test

# または全サイトから収集
python -m engineed.cli crawl --all --test
```

### 4. Webインターフェースを起動

```bash
# Webサーバーを起動
python -m engineed.cli serve

# ブラウザで http://127.0.0.1:8000 にアクセス
```

## 🏗️ プロジェクト構造

```
engineed/
├── engineed/
│   ├── spiders/          # Scrapyスパイダー
│   │   ├── qiita_spider.py    # Qiita記事収集
│   │   ├── zenn_spider.py     # Zenn記事収集
│   │   └── hateb_spider.py    # はてブ経由記事収集
│   ├── models/           # データベースモデル
│   │   └── database.py        # SQLAlchemyモデル
│   ├── ai/               # AI機能
│   │   └── keyword_extractor.py
│   ├── utils/            # ユーティリティ
│   └── cli.py            # CLIインターフェース
├── web/                  # Webアプリケーション
│   ├── app.py            # FastAPIアプリ
│   ├── templates/        # Jinja2テンプレート
│   └── static/           # CSS/JS/画像
├── tests/                # テストスクリプト
└── docs/                 # ドキュメント
```

## 💻 使用技術

### バックエンド
- **Python 3.9+**: メイン言語
- **Scrapy**: Webスクレイピングフレームワーク
- **FastAPI**: WebAPIフレームワーク
- **SQLAlchemy**: ORMとデータベース管理
- **Pydantic**: データバリデーション

### フロントエンド
- **Jinja2**: テンプレートエンジン
- **HTML5/CSS3**: モダンなWebデザイン
- **Font Awesome**: アイコンライブラリ

### AI・機械学習
- **OpenAI GPT**: 記事分析とキーワード抽出
- **scikit-learn**: 機械学習アルゴリズム
- **transformers**: 自然言語処理

### データベース
- **SQLite**: 開発・テスト用データベース
- **PostgreSQL**: 本番環境（対応予定）

## 🔧 設定

### 環境変数

`.env.example`をコピーして`.env`を作成し、必要なAPIキーを設定してください：

```bash
cp .env.example .env
```

```env
# OpenAI API設定（必須）
OPENAI_API_KEY=your_openai_api_key_here

# データベース設定（オプション）
DATABASE_URL=sqlite:///data/articles.db

# Webサーバー設定（オプション）
HOST=127.0.0.1
PORT=8000
```

## 📚 使用方法

### CLIコマンド

```bash
# スパイダー一覧表示
scrapy list

# 記事収集（テストモード）
python -m engineed.cli crawl -s qiita --test
python -m engineed.cli crawl -s zenn --test
python -m engineed.cli crawl -s hateb --test

# 全スパイダー実行
python -m engineed.cli crawl --all

# Webサーバー起動
python -m engineed.cli serve --host 0.0.0.0 --port 8000

# システム状態確認
python -m engineed.cli status
```

### Scrapyコマンド（直接実行）

```bash
# パイプライン無効でテスト実行
scrapy crawl qiita -s ITEM_PIPELINES="{}" -s CLOSESPIDER_ITEMCOUNT=5

# 本格実行
scrapy crawl qiita
scrapy crawl zenn
scrapy crawl hateb
```

## 🧪 テスト

```bash
# 全スパイダーの機能テスト
python test_all_spiders.py

# 個別スパイダーテスト
python test_spider.py

# Webアプリテスト
python test_minimal.py
```

## 🤝 コントリビューション

1. このリポジトリをフォーク
2. フィーチャーブランチを作成 (`git checkout -b feature/amazing-feature`)
3. 変更をコミット (`git commit -m 'Add amazing feature'`)
4. ブランチにプッシュ (`git push origin feature/amazing-feature`)
5. プルリクエストを作成

## 📋 今後の計画

- [ ] 本格的なテストスイート（pytest）
- [ ] 検索・フィルタ機能の実装
- [ ] ユーザー認証・個人設定
- [ ] AI分析機能の拡張（自動要約、難易度判定）
- [ ] モバイル対応（PWA）
- [ ] Docker化とデプロイメント

詳細は[改善提案](./IMPROVEMENT_PROPOSALS.md)をご覧ください。

## 📄 ライセンス

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙋‍♂️ サポート

質問やバグレポートは[Issues](https://github.com/uchan3/engineed/issues)にお気軽にお書きください。

---

**Built with ❤️ by Claude Code**