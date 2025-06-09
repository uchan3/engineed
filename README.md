# プロジェクト構造
"""
tech_feed/
├── scrapy.cfg
├── requirements.txt
├── setup.py
├── tech_feed/
│   ├── __init__.py
│   ├── items.py          # データモデル定義
│   ├── middlewares.py    # カスタムミドルウェア
│   ├── pipelines.py      # データ処理パイプライン
│   ├── settings.py       # Scrapy設定
│   ├── spiders/
│   │   ├── __init__.py
│   │   ├── base_spider.py
│   │   ├── qiita_spider.py
│   │   ├── zenn_spider.py
│   │   └── hateb_spider.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── database.py   # DB接続・モデル
│   │   └── schemas.py    # Pydanticスキーマ
│   ├── ai/
│   │   ├── __init__.py
│   │   ├── keyword_extractor.py
│   │   ├── tech_analyzer.py
│   │   └── recommender.py
│   └── utils/
│       ├── __init__.py
│       ├── text_processor.py
│       └── tech_keywords.py
├── web/
│   ├── app.py           # FastAPI アプリケーション
│   ├── templates/
│   └── static/
└── data/
    ├── articles.db      # SQLite データベース
    └── tech_keywords.json
"""