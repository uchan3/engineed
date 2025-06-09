import scrapy
import re
from datetime import datetime, timedelta
from urllib.parse import urljoin, urlparse
from engineed.items import ArticleItem
from engineed.utils.text_processor import TextProcessor


class BaseTechSpider(scrapy.Spider):
    """技術記事サイト用の基底Spider"""
    
    # 共通設定
    custom_settings = {
        'DOWNLOAD_DELAY': 1,
        'RANDOMIZE_DOWNLOAD_DELAY': 0.5,
        'CONCURRENT_REQUESTS_PER_DOMAIN': 4,
    }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.text_processor = TextProcessor()
        self.max_pages = int(kwargs.get('max_pages', 5))  # デフォルト5ページまで
        self.days_back = int(kwargs.get('days_back', 7))  # デフォルト7日前まで
        self.min_content_length = 200
        
    def parse_article_url(self, url):
        """記事URLの正規化"""
        return urljoin(self.start_urls[0], url)
    
    def extract_reading_time(self, content):
        """読了時間の推定（日本語基準）"""
        if not content:
            return None
        
        # HTMLタグを除去
        clean_content = re.sub(r'<[^>]+>', '', content)
        char_count = len(clean_content)
        
        # 日本語：約400-600文字/分で読める
        reading_time = max(1, char_count // 500)
        return reading_time
    
    def extract_tags_from_text(self, text):
        """テキストからタグを抽出"""
        if not text:
            return []
        
        # 技術キーワードのマッチング
        tech_keywords = [
            'python', 'javascript', 'react', 'vue', 'angular', 'node.js',
            'typescript', 'go', 'rust', 'java', 'c++', 'c#', 'php',
            'docker', 'kubernetes', 'aws', 'gcp', 'azure', 'terraform',
            'machine learning', '機械学習', 'ai', 'deep learning', 'データサイエンス',
            'web開発', 'フロントエンド', 'バックエンド', 'インフラ', 'devops',
            'アジャイル', 'スクラム', 'git', 'github', 'ci/cd'
        ]
        
        found_tags = []
        text_lower = text.lower()
        
        for keyword in tech_keywords:
            if keyword in text_lower:
                found_tags.append(keyword)
        
        return list(set(found_tags))  # 重複除去
    
    def clean_content(self, content):
        """コンテンツのクリーニング"""
        if not content:
            return ''
        
        # HTMLタグの除去
        content = re.sub(r'<script[^>]*>.*?</script>', '', content, flags=re.DOTALL)
        content = re.sub(r'<style[^>]*>.*?</style>', '', content, flags=re.DOTALL)
        content = re.sub(r'<[^>]+>', '', content)
        
        # 余分な空白の除去
        content = re.sub(r'\s+', ' ', content).strip()
        
        return content
    
    def is_valid_article(self, item):
        """記事の有効性をチェック"""
        # 最小文字数チェック
        if not item.get('content') or len(item['content']) < self.min_content_length:
            return False
        
        # タイトルの存在チェック
        if not item.get('title'):
            return False
        
        # URLの有効性チェック
        if not item.get('url'):
            return False
        
        return True
    
    def create_article_item(self, response, **kwargs):
        """ArticleItemの共通作成ロジック"""
        item = ArticleItem()
        
        # 共通フィールドの設定
        item['url'] = response.url
        item['source_site'] = self.name
        item['scraped_at'] = datetime.now().isoformat()
        item['language'] = 'ja'
        
        # 個別のフィールドは子クラスで設定
        for key, value in kwargs.items():
            item[key] = value
        
        # コンテンツのクリーニング
        if item.get('content'):
            item['content'] = self.clean_content(item['content'])
            item['reading_time'] = self.extract_reading_time(item['content'])
        
        # テキストからのタグ抽出
        text_for_tags = f"{item.get('title', '')} {item.get('content', '')}"
        extracted_tags = self.extract_tags_from_text(text_for_tags)
        
        # 既存のタグとマージ
        existing_tags = item.get('tags', [])
        if isinstance(existing_tags, str):
            existing_tags = [existing_tags]
        
        all_tags = list(set(existing_tags + extracted_tags))
        item['tags'] = all_tags
        
        return item
    
    def should_follow_link(self, url):
        """リンクをフォローするかの判断"""
        parsed_url = urlparse(url)
        base_domain = urlparse(self.start_urls[0]).netloc
        
        # 同一ドメインのみフォロー
        if parsed_url.netloc != base_domain:
            return False
        
        # 除外パターン
        exclude_patterns = [
            r'/users?/',
            r'/profile',
            r'/settings',
            r'/search',
            r'/api/',
            r'\.(css|js|png|jpg|gif|svg|ico)$',
        ]
        
        for pattern in exclude_patterns:
            if re.search(pattern, url, re.IGNORECASE):
                return False
        
        return True
    
    def parse_date(self, date_string):
        """日付文字列のパース"""
        if not date_string:
            return None
        
        # 様々な日付フォーマットに対応
        date_patterns = [
            r'(\d{4})[/-](\d{1,2})[/-](\d{1,2})',
            r'(\d{1,2})[/-](\d{1,2})[/-](\d{4})',
            r'(\d{4})年(\d{1,2})月(\d{1,2})日',
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, date_string)
            if match:
                try:
                    groups = match.groups()
                    if len(groups) == 3:
                        if len(groups[0]) == 4:  # 年が最初
                            year, month, day = groups
                        else:  # 年が最後
                            day, month, year = groups
                        
                        return datetime(int(year), int(month), int(day))
                except ValueError:
                    continue
        
        return None
    
    def is_recent_article(self, published_date):
        """記事が指定日数以内かチェック"""
        if not published_date:
            return True  # 日付不明の場合は取得
        
        cutoff_date = datetime.now() - timedelta(days=self.days_back)
        return published_date >= cutoff_date