# 実行コマンド例

## スパイダーの基本実行

### 利用可能なスパイダー
- **qiita**: Qiitaの技術記事を収集
- **zenn**: Zennの技術記事を収集  
- **hateb**: はてなブックマーク（テクノロジー）経由の記事を収集

### 1. Scrapyコマンド直接実行
```bash
# 利用可能なスパイダーを確認
scrapy list

# 各スパイダーを実行（パイプライン有効）
scrapy crawl qiita
scrapy crawl zenn
scrapy crawl hateb

# パイプライン無効でテスト実行
scrapy crawl qiita -s ITEM_PIPELINES="{}"
scrapy crawl zenn -s ITEM_PIPELINES="{}"
scrapy crawl hateb -s ITEM_PIPELINES="{}"

# 記事数制限付きでテスト実行
scrapy crawl qiita -s CLOSESPIDER_ITEMCOUNT=5 -s ITEM_PIPELINES="{}"
scrapy crawl zenn -s CLOSESPIDER_ITEMCOUNT=5 -s ITEM_PIPELINES="{}"
scrapy crawl hateb -s CLOSESPIDER_ITEMCOUNT=5 -s ITEM_PIPELINES="{}"

# ログレベル設定で実行
scrapy crawl qiita -s LOG_LEVEL=INFO
```

### 2. CLIコマンド経由
```bash
# ヘルプ確認
python -m engineed.cli --help

# 特定のスパイダー実行
python -m engineed.cli crawl -s qiita
python -m engineed.cli crawl -s zenn
python -m engineed.cli crawl -s hateb

# テストモードで実行（記事数制限）
python -m engineed.cli crawl -s qiita --test
python -m engineed.cli crawl -s zenn --test
python -m engineed.cli crawl -s hateb --test

# 全スパイダー実行
python -m engineed.cli crawl --all

# 全スパイダーをテストモードで実行
python -m engineed.cli crawl --all --test

# データベース初期化
python -m engineed.cli init-db

# Webサーバー起動
python -m engineed.cli serve

# システム状態確認
python -m engineed.cli status
```

## 注意事項

1. **パイプライン依存関係**: AIパイプラインを使用する場合、以下が必要
   - OpenAI APIキー設定
   - spaCyライブラリのインストール
   
2. **テスト実行時**: パイプラインを無効化してスパイダーのみテスト可能
   ```bash
   scrapy crawl qiita -s ITEM_PIPELINES="{}" -s CLOSESPIDER_ITEMCOUNT=3
   ```

3. **設定可能なパラメータ**:
   - `max_pages`: 取得する最大ページ数（デフォルト: 5）
   - `days_back`: 取得対象の日数（デフォルト: 7日）
   - `DOWNLOAD_DELAY`: リクエスト間隔（秒）

## トラブルシューティング

- **タイムアウト**: DOWNLOAD_DELAYを調整
- **パイプラインエラー**: 一時的に`ITEM_PIPELINES="{}"`で無効化
- **記事が取得されない**: `LOG_LEVEL=DEBUG`でデバッグ情報を確認