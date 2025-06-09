BOT_NAME = 'engineed'

SPIDER_MODULES = ['engineed.spiders']
NEWSPIDER_MODULE = 'engineed.spiders'

# ロボットプロトコルの遵守
ROBOTSTXT_OBEY = True

# パイプライン設定
ITEM_PIPELINES = {
    'engineed.pipelines.ValidationPipeline': 100,
    'engineed.pipelines.DuplicationFilterPipeline': 200,
    'engineed.pipelines.TextProcessingPipeline': 300,
    'engineed.pipelines.AIEnrichmentPipeline': 400,
    'engineed.pipelines.DatabasePipeline': 500,
}

# ダウンロード設定
DOWNLOAD_DELAY = 1  # 1秒間隔
RANDOMIZE_DOWNLOAD_DELAY = 0.5
CONCURRENT_REQUESTS = 16
CONCURRENT_REQUESTS_PER_DOMAIN = 8

# User-Agent設定
USER_AGENT = 'engineed (+https://github.com/yourrepo/engineed)'

# AutoThrottle設定（サーバー負荷を考慮した自動調整）
AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_START_DELAY = 1
AUTOTHROTTLE_MAX_DELAY = 10
AUTOTHROTTLE_TARGET_CONCURRENCY = 2.0
AUTOTHROTTLE_DEBUG = False

# メモリ使用量制限
MEMUSAGE_ENABLED = True
MEMUSAGE_LIMIT_MB = 512

# ログ設定
LOG_LEVEL = 'INFO'
LOG_FILE = 'logs/scrapy.log'

# キャッシュ設定
HTTPCACHE_ENABLED = True
HTTPCACHE_EXPIRATION_SECS = 3600  # 1時間
HTTPCACHE_DIR = 'httpcache'

# データベース設定
DATABASE_URL = 'sqlite:///data/articles.db'

# AI/ML設定
OPENAI_API_KEY = ''  # 環境変数から取得
HUGGINGFACE_API_KEY = ''

# カスタム設定
TECH_KEYWORDS_FILE = 'data/tech_keywords.json'
MIN_ARTICLE_LENGTH = 200  # 最小記事長
MAX_ARTICLE_AGE_DAYS = 30  # 収集対象記事の最大日数