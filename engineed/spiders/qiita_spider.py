import scrapy
import json
import re
from datetime import datetime
from urllib.parse import urljoin
from engineed.spiders.base_spider import BaseTechSpider


class QiitaSpider(BaseTechSpider):
    """Qiitaの記事を収集するSpider"""
    
    name = 'qiita'
    allowed_domains = ['qiita.com']
    start_urls = ['https://qiita.com']
    
    custom_settings = {
        'DOWNLOAD_DELAY': 2,  # Qiitaは少し長めに設定
        'RANDOMIZE_DOWNLOAD_DELAY': 1,
        'CONCURRENT_REQUESTS_PER_DOMAIN': 2,
    }
    
    def start_requests(self):
        """初期リクエストを生成"""
        # 人気記事、新着記事、タグ別記事を取得
        urls = [
            'https://qiita.com',  # トップページ
            'https://qiita.com/popular-items',  # 人気記事
            'https://qiita.com/items',  # 新着記事
        ]
        
        # 主要技術タグ
        tech_tags = [
            'Python', 'JavaScript', 'React', 'Vue.js', 'Node.js',
            'TypeScript', 'Go', 'Rust', 'Java', 'PHP',
            'Docker', 'Kubernetes', 'AWS', 'GCP', 'Azure',
            'MachineLearning', 'AI', 'DeepLearning', 'DataScience',
            'WebDevelopment', 'Frontend', 'Backend', 'DevOps'
        ]
        
        for tag in tech_tags:
            urls.append(f'https://qiita.com/tags/{tag}/items')
        
        for url in urls:
            yield scrapy.Request(
                url=url,
                callback=self.parse,
                meta={'page': 1}
            )
    
    def parse(self, response):
        """記事一覧ページのパース"""
        # 記事リンクを抽出
        article_links = response.css('h1.css-4vcdee a::attr(href)').getall()
        if not article_links:
            # 別のセレクタパターンを試す
            article_links = response.css('article h2 a::attr(href)').getall()
        
        if not article_links:
            # さらに別のパターン
            article_links = response.css('.item-title a::attr(href)').getall()
        
        self.logger.info(f'Found {len(article_links)} article links on {response.url}')
        
        # 各記事ページにリクエスト
        for link in article_links:
            article_url = urljoin(response.url, link)
            if self.should_follow_link(article_url):
                yield scrapy.Request(
                    url=article_url,
                    callback=self.parse_article,
                    errback=self.handle_error
                )
        
        # ページネーション（最大ページ数まで）
        current_page = response.meta.get('page', 1)
        if current_page < self.max_pages:
            next_page_links = response.css('a[rel="next"]::attr(href)').getall()
            if next_page_links:
                next_url = urljoin(response.url, next_page_links[0])
                yield scrapy.Request(
                    url=next_url,
                    callback=self.parse,
                    meta={'page': current_page + 1}
                )
    
    def parse_article(self, response):
        """個別記事のパース"""
        try:
            # タイトル取得
            title = response.css('h1.css-161ziad::text').get()
            if not title:
                title = response.css('.item-title::text').get()
            if not title:
                title = response.css('h1::text').get()
            
            title = title.strip() if title else ''
            
            # 作者取得
            author = response.css('.author-name a::text').get()
            if not author:
                author = response.css('[data-testid="profile-link"]::text').get()
            
            # 投稿日時取得
            published_at = None
            date_text = response.css('time::attr(datetime)').get()
            if date_text:
                try:
                    published_at = datetime.fromisoformat(date_text.replace('Z', '+00:00'))
                except ValueError:
                    published_at = self.parse_date(date_text)
            
            # 記事本文取得
            content_selectors = [
                '.markdown-body',  # メインコンテンツ
                '.item-content',
                '.post-content',
                'article'
            ]
            
            content = ''
            for selector in content_selectors:
                content_elements = response.css(selector)
                if content_elements:
                    content = content_elements.get()
                    break
            
            if not content:
                self.logger.warning(f'No content found for {response.url}')
                return
            
            # 統計情報取得
            view_count = 0
            like_count = 0
            comment_count = 0
            
            # いいね数
            like_text = response.css('.like-count::text').get()
            if like_text:
                try:
                    like_count = int(like_text.strip())
                except ValueError:
                    pass
            
            # コメント数
            comment_text = response.css('.comment-count::text').get()
            if comment_text:
                try:
                    comment_count = int(comment_text.strip())
                except ValueError:
                    pass
            
            # タグ取得
            tags = []
            tag_elements = response.css('.tag-list .tag::text').getall()
            if not tag_elements:
                tag_elements = response.css('[data-testid="tag-link"]::text').getall()
            
            if tag_elements:
                tags = [tag.strip() for tag in tag_elements if tag.strip()]
            
            # 記事の種類判定
            is_tutorial = any(keyword in title.lower() for keyword in 
                            ['チュートリアル', 'tutorial', '入門', '初心者', 'はじめて', '使い方'])
            
            # ArticleItemを作成
            item = self.create_article_item(
                response,
                title=title,
                content=content,
                author=author,
                published_at=published_at.isoformat() if published_at else None,
                view_count=view_count,
                like_count=like_count,
                comment_count=comment_count,
                tags=tags,
                is_tutorial=is_tutorial
            )
            
            # 有効性チェック
            if self.is_valid_article(item):
                # 最近の記事かチェック
                if not published_at or self.is_recent_article(published_at):
                    yield item
                else:
                    self.logger.info(f'Skipping old article: {response.url}')
            else:
                self.logger.warning(f'Invalid article: {response.url}')
                
        except Exception as e:
            self.logger.error(f'Error parsing article {response.url}: {str(e)}')
    
    def handle_error(self, failure):
        """エラーハンドリング"""
        self.logger.error(f'Request failed: {failure.request.url} - {failure.value}')
    
    def should_follow_link(self, url):
        """Qiita固有のリンクフィルタリング"""
        if not super().should_follow_link(url):
            return False
        
        # Qiita固有の除外パターン
        qiita_exclude_patterns = [
            r'/organizations/',
            r'/advent-calendar/',
            r'/drafts/',
            r'/private/',
            r'/following',
            r'/followers',
            r'/likes',
            r'/stocks',
        ]
        
        for pattern in qiita_exclude_patterns:
            if re.search(pattern, url, re.IGNORECASE):
                return False
        
        # 記事URLのパターンチェック
        if '/items/' in url:
            return True
        
        return False