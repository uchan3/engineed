#!/usr/bin/env python3
"""スパイダーの動作テスト用スクリプト"""

import sys
import os
from datetime import datetime

# プロジェクトルートをパスに追加
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from engineed.spiders.qiita_spider import QiitaSpider
from engineed.items import ArticleItem

def test_spider_creation():
    """スパイダー作成テスト"""
    print("Testing spider creation...")
    spider = QiitaSpider()
    print(f"Spider name: {spider.name}")
    print(f"Allowed domains: {spider.allowed_domains}")
    print(f"Start URLs: {spider.start_urls}")
    print("Spider creation: OK")

def test_article_item_creation():
    """ArticleItem作成テスト"""
    print("\nTesting article item creation...")
    spider = QiitaSpider()
    
    # ダミーレスポンスオブジェクト
    class DummyResponse:
        def __init__(self, url):
            self.url = url
    
    response = DummyResponse("https://qiita.com/test/items/123")
    
    item = spider.create_article_item(
        response,
        title="テスト記事タイトル",
        content="これはテスト記事の内容です。" * 10,  # 十分な長さ
        author="test_author",
        tags=["Python", "テスト"]
    )
    
    print(f"Title: {item['title']}")
    print(f"URL: {item['url']}")
    print(f"Source site: {item['source_site']}")
    print(f"Tags: {item['tags']}")
    print(f"Reading time: {item.get('reading_time')}")
    print("Article item creation: OK")

def test_validation():
    """バリデーションテスト"""
    print("\nTesting validation...")
    spider = QiitaSpider()
    
    # 有効な記事
    valid_item = {
        'title': 'Valid Article',
        'content': 'This is a valid article with sufficient content length. ' * 10,
        'url': 'https://qiita.com/valid'
    }
    
    # 無効な記事（短すぎるコンテンツ）
    invalid_item = {
        'title': 'Invalid Article',
        'content': 'Too short',
        'url': 'https://qiita.com/invalid'
    }
    
    print(f"Valid item check: {spider.is_valid_article(valid_item)}")
    print(f"Invalid item check: {spider.is_valid_article(invalid_item)}")
    print("Validation: OK")

def test_text_processing():
    """テキスト処理テスト"""
    print("\nTesting text processing...")
    spider = QiitaSpider()
    
    html_content = """
    <div>
        <h1>テストタイトル</h1>
        <p>これは<strong>テスト</strong>コンテンツです。</p>
        <script>alert('script');</script>
        <style>.test { color: red; }</style>
    </div>
    """
    
    clean_content = spider.clean_content(html_content)
    print(f"Original length: {len(html_content)}")
    print(f"Cleaned length: {len(clean_content)}")
    print(f"Cleaned content: {clean_content[:100]}...")
    
    reading_time = spider.extract_reading_time(clean_content)
    print(f"Estimated reading time: {reading_time} minutes")
    print("Text processing: OK")

if __name__ == "__main__":
    print("Starting spider tests...")
    print("=" * 50)
    
    try:
        test_spider_creation()
        test_article_item_creation()
        test_validation()
        test_text_processing()
        
        print("\n" + "=" * 50)
        print("All tests passed! ✅")
        
    except Exception as e:
        print(f"\nTest failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)