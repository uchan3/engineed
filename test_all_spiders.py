#!/usr/bin/env python3
"""全スパイダーの動作テスト用スクリプト"""

import sys
import os
from datetime import datetime

# プロジェクトルートをパスに追加
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from engineed.spiders.qiita_spider import QiitaSpider
from engineed.spiders.zenn_spider import ZennSpider
from engineed.spiders.hateb_spider import HatebSpider

def test_spider_creation():
    """スパイダー作成テスト"""
    print("Testing spider creation...")
    
    spiders = [
        ('Qiita', QiitaSpider),
        ('Zenn', ZennSpider),
        ('Hateb', HatebSpider),
    ]
    
    for name, spider_class in spiders:
        try:
            spider = spider_class()
            print(f"✅ {name} Spider:")
            print(f"   Name: {spider.name}")
            print(f"   Domains: {spider.allowed_domains}")
            print(f"   Start URLs: {spider.start_urls}")
            print(f"   Max pages: {spider.max_pages}")
        except Exception as e:
            print(f"❌ {name} Spider failed: {e}")

def test_url_filtering():
    """URLフィルタリングテスト"""
    print("\nTesting URL filtering...")
    
    test_urls = [
        # Qiita URLs
        ('qiita', 'https://qiita.com/items/abc123', True),
        ('qiita', 'https://qiita.com/users/test', False),
        ('qiita', 'https://qiita.com/organizations/test', False),
        
        # Zenn URLs  
        ('zenn', 'https://zenn.dev/articles/abc123', True),
        ('zenn', 'https://zenn.dev/users/test', False),
        ('zenn', 'https://zenn.dev/books/test', False),
        
        # External URLs for Hateb
        ('hateb', 'https://qiita.com/items/test', True),
        ('hateb', 'https://zenn.dev/articles/test', True),
        ('hateb', 'https://example.com/malware.exe', False),
    ]
    
    spiders = {
        'qiita': QiitaSpider(),
        'zenn': ZennSpider(),
        'hateb': HatebSpider(),
    }
    
    for spider_name, url, expected in test_urls:
        spider = spiders[spider_name]
        if spider_name == 'hateb':
            result = spider.should_follow_external_link(url)
        else:
            result = spider.should_follow_link(url)
        
        status = "✅" if result == expected else "❌"
        print(f"   {status} {spider_name}: {url} -> {result} (expected: {expected})")

def test_item_creation():
    """アイテム作成テスト"""
    print("\nTesting item creation...")
    
    class DummyResponse:
        def __init__(self, url):
            self.url = url
    
    spiders = [
        ('Qiita', QiitaSpider()),
        ('Zenn', ZennSpider()),
        ('Hateb', HatebSpider()),
    ]
    
    for name, spider in spiders:
        try:
            response = DummyResponse(f"https://{spider.allowed_domains[0]}/test/123")
            
            item = spider.create_article_item(
                response,
                title=f"テスト記事 - {name}",
                content="これはテスト記事の内容です。" * 20,  # 十分な長さ
                author=f"test_author_{name.lower()}",
                tags=["Python", "テスト", "Web開発"]
            )
            
            print(f"✅ {name} Item:")
            print(f"   Title: {item['title']}")
            print(f"   Source: {item['source_site']}")
            print(f"   Tags: {item.get('tags', [])}")
            print(f"   Valid: {spider.is_valid_article(item)}")
            
        except Exception as e:
            print(f"❌ {name} Item creation failed: {e}")

def test_tech_keywords():
    """技術キーワード抽出テスト"""
    print("\nTesting tech keyword extraction...")
    
    test_content = """
    Pythonを使った機械学習プロジェクトの始め方について解説します。
    今回はReactとTypeScriptを組み合わせたWebアプリケーション開発と、
    DockerとKubernetesを使ったコンテナ化について説明します。
    """
    
    spider = QiitaSpider()
    extracted_tags = spider.extract_tags_from_text(test_content)
    
    print(f"   Content: {test_content[:50]}...")
    print(f"   Extracted tags: {extracted_tags}")
    
    expected_tags = ['python', '機械学習', 'react', 'typescript', 'docker', 'kubernetes']
    found_tags = [tag for tag in expected_tags if tag in [t.lower() for t in extracted_tags]]
    
    print(f"   Expected tags found: {found_tags}")
    print(f"   ✅ Tag extraction working: {len(found_tags) > 0}")

if __name__ == "__main__":
    print("Starting comprehensive spider tests...")
    print("=" * 60)
    
    try:
        test_spider_creation()
        test_url_filtering()
        test_item_creation()
        test_tech_keywords()
        
        print("\n" + "=" * 60)
        print("All tests completed! ✅")
        
    except Exception as e:
        print(f"\nTest failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)