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
        # Qiitaの実際のHTML構造に合わせて記事リンクを抽出
        article_selectors = [
            'article h2 a::attr(href)',  # 記事タイトルリンク
            '.css-1k6ikq9 a::attr(href)',  # トップページの記事
            '.css-u6dbcd a::attr(href)',  # リスト形式の記事
            'h1 a[href*="/items/"]::attr(href)',  # 一般的な記事リンク
            'a[href*="/items/"]::attr(href)',  # 記事URLパターンマッチ
        ]
        
        article_links = []
        for selector in article_selectors:
            links = response.css(selector).getall()
            if links:
                article_links.extend(links)
                break
        
        # 重複除去
        article_links = list(set(article_links))
        
        self.logger.info(f'Found {len(article_links)} article links on {response.url}')
        
        # 各記事ページにリクエスト
        for link in article_links[:10]:  # 最初の10件に制限
            article_url = urljoin(response.url, link)
            if self.should_follow_link(article_url) and '/items/' in article_url:
                yield scrapy.Request(
                    url=article_url,
                    callback=self.parse_article,
                    errback=self.handle_error
                )
        
        # ページネーション（最大ページ数まで）
        current_page = response.meta.get('page', 1)
        if current_page < self.max_pages:
            next_selectors = [
                'a[rel="next"]::attr(href)',
                '.css-1t6wm19 a::attr(href)',  # ページネーション
                'a[aria-label="次のページ"]::attr(href)',
            ]
            
            next_url = None
            for selector in next_selectors:
                next_links = response.css(selector).getall()
                if next_links:
                    next_url = urljoin(response.url, next_links[0])
                    break
            
            if next_url:
                yield scrapy.Request(
                    url=next_url,
                    callback=self.parse,
                    meta={'page': current_page + 1}
                )
    
    def parse_article(self, response):
        """個別記事のパース"""
        try:
            # タイトル取得（Qiitaの実際の構造）
            title_selectors = [
                'h1[data-cy="article-title"]::text',
                '.css-19ak7s2::text',  # 新しいデザイン
                'h1::text',
                'title::text',
            ]
            
            title = None
            for selector in title_selectors:
                title = response.css(selector).get()
                if title:
                    break
            
            title = title.strip() if title else ''
            
            # 作者取得
            author_selectors = [
                '.css-1t6wm19 a::text',  # プロフィールリンク
                'a[href*="/users/"]::text',
                '.user-info a::text',
                '[data-cy="author-link"]::text',
            ]
            
            author = None
            for selector in author_selectors:
                author = response.css(selector).get()
                if author:
                    break
            
            # 投稿日時取得
            published_at = None
            date_selectors = [
                'time::attr(datetime)',
                '[data-cy="created-at"]::attr(datetime)',
                '.css-1t6wm19 time::attr(datetime)',
            ]
            
            for selector in date_selectors:
                date_text = response.css(selector).get()
                if date_text:
                    try:
                        published_at = datetime.fromisoformat(date_text.replace('Z', '+00:00'))
                        break
                    except ValueError:
                        published_at = self.parse_date(date_text)
                        if published_at:
                            break
            
            # 記事本文取得
            content_selectors = [
                '.markdown-body',  # メインコンテンツ
                '[data-cy="article-body"]',
                '.css-1t6wm19 .markdown',
                'article .content',
                '.post-content',
            ]
            
            content = ''
            for selector in content_selectors:
                content_elements = response.css(selector)
                if content_elements:
                    content = content_elements.get()
                    break
            
            # contentが見つからない場合は本文全体から抽出
            if not content:
                content = response.css('body').get()
                self.logger.warning(f'Using body content for {response.url}')
            
            if not content:
                self.logger.warning(f'No content found for {response.url}')
                return
            
            # 統計情報取得
            view_count = 0
            like_count = 0
            comment_count = 0
            
            # いいね数の取得（複数のパターンを試行）
            like_selectors = [
                '.css-1t6wm19 button span::text',
                '[data-cy="like-count"]::text',
                '.like-count::text',
                'button[aria-label*="いいね"] span::text',
            ]
            
            for selector in like_selectors:
                like_text = response.css(selector).get()
                if like_text and like_text.strip().isdigit():
                    try:
                        like_count = int(like_text.strip())
                        break
                    except ValueError:
                        pass
            
            # タグ取得
            tag_selectors = [
                '.css-1t6wm19 a[href*="/tags/"]::text',
                '[data-cy="tag"]::text',
                '.tag::text',
                'a[href*="/tags/"] span::text',
            ]
            
            tags = []
            for selector in tag_selectors:
                tag_elements = response.css(selector).getall()
                if tag_elements:
                    tags = [tag.strip() for tag in tag_elements if tag.strip()]
                    break
            
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