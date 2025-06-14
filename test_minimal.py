#!/usr/bin/env python3
"""最小限のScrapyテスト"""

import scrapy
from scrapy.crawler import CrawlerProcess
from engineed.spiders.qiita_spider import QiitaSpider

class MinimalTestSpider(QiitaSpider):
    name = 'minimal_test'
    start_urls = ['https://httpbin.org/html']  # テスト用サイト
    
    def parse(self, response):
        print(f"Successfully accessed: {response.url}")
        print(f"Response status: {response.status}")
        print(f"Content length: {len(response.text)}")
        return

if __name__ == '__main__':
    process = CrawlerProcess({
        'USER_AGENT': 'engineed test',
        'ROBOTSTXT_OBEY': False,  # テストのため
        'ITEM_PIPELINES': {},  # パイプライン無効化
        'LOG_LEVEL': 'INFO',
        'CLOSESPIDER_ITEMCOUNT': 1,
    })
    
    process.crawl(MinimalTestSpider)
    print("Starting minimal test...")
    process.start()