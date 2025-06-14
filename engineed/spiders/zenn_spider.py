import scrapy
import json
import re
from datetime import datetime
from urllib.parse import urljoin
from engineed.spiders.base_spider import BaseTechSpider


class ZennSpider(BaseTechSpider):
    """Zennの記事を収集するSpider"""
    
    name = 'zenn'
    allowed_domains = ['zenn.dev']
    start_urls = ['https://zenn.dev']
    
    custom_settings = {
        'DOWNLOAD_DELAY': 1.5,  # Zennは適度な間隔
        'RANDOMIZE_DOWNLOAD_DELAY': 0.5,
        'CONCURRENT_REQUESTS_PER_DOMAIN': 3,
    }
    
    def start_requests(self):
        """初期リクエストを生成"""
        urls = [
            'https://zenn.dev',  # トップページ
            'https://zenn.dev/trending',  # トレンド記事
            'https://zenn.dev/tech',  # Tech記事
        ]
        
        # 主要技術トピック
        tech_topics = [
            'python', 'javascript', 'react', 'vue', 'nodejs',
            'typescript', 'go', 'rust', 'java', 'php',
            'docker', 'kubernetes', 'aws', 'gcp', 'azure',
            'ai', 'ml', 'web', 'frontend', 'backend', 'devops'
        ]
        
        for topic in tech_topics:
            urls.append(f'https://zenn.dev/topics/{topic}')
        
        for url in urls:
            yield scrapy.Request(
                url=url,
                callback=self.parse,
                meta={'page': 1}
            )
    
    def parse(self, response):
        """記事一覧ページのパース"""
        # Zennの実際のHTML構造に合わせて記事リンクを抽出
        article_selectors = [
            'article a[href*="/articles/"]::attr(href)',  # 記事リンク
            '.ArticleListItem_title a::attr(href)',  # 記事タイトルリンク
            'a[href*="/articles/"]::attr(href)',  # 記事URLパターンマッチ
            '.css-1wl4jvr a::attr(href)',  # 記事カード
        ]
        
        article_links = []
        for selector in article_selectors:
            links = response.css(selector).getall()
            if links:
                # Zennの記事URLフィルタ
                filtered_links = [link for link in links if '/articles/' in link and len(link.split('/')) >= 4]
                article_links.extend(filtered_links)
        
        # 重複除去
        article_links = list(set(article_links))
        
        self.logger.info(f'Found {len(article_links)} article links on {response.url}')
        
        # 各記事ページにリクエスト
        for link in article_links[:12]:  # 最初の12件に制限
            article_url = urljoin(response.url, link)
            if self.should_follow_link(article_url):
                yield scrapy.Request(
                    url=article_url,
                    callback=self.parse_article,
                    errback=self.handle_error
                )
        
        # ページネーション
        current_page = response.meta.get('page', 1)
        if current_page < self.max_pages:
            next_selectors = [
                'a[rel="next"]::attr(href)',
                'a[aria-label="次のページ"]::attr(href)',
                '.Pagination_next a::attr(href)',
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
            # タイトル取得
            title_selectors = [
                'h1.ArticleHeader_title::text',
                'h1[data-testid="article-title"]::text',
                '.css-1wl4jvr h1::text',
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
                '.ArticleHeader_authorInfo a::text',
                'a[href*="/users/"]::text',
                '.UserLink_displayName::text',
                '.css-1wl4jvr a[href*="/users/"]::text',
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
                '.ArticleHeader_publishedAt time::attr(datetime)',
                '[data-testid="published-at"]::attr(datetime)',
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
                '.ArticleBody_content',
                '.zenn-markdown',
                '[data-testid="article-body"]',
                '.markdown-body',
                'article .content',
            ]
            
            content = ''
            for selector in content_selectors:
                content_elements = response.css(selector)
                if content_elements:
                    content = content_elements.get()
                    break
            
            if not content:
                content = response.css('main').get()
                self.logger.warning(f'Using main content for {response.url}')
            
            if not content:
                self.logger.warning(f'No content found for {response.url}')
                return
            
            # 統計情報取得
            view_count = 0
            like_count = 0
            comment_count = 0
            
            # いいね数の取得
            like_selectors = [
                '.ArticleHeader_likeCount::text',
                'button[aria-label*="いいね"] span::text',
                '.LikeButton_count::text',
                '[data-testid="like-count"]::text',
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
                '.ArticleHeader_topics a::text',
                'a[href*="/topics/"]::text',
                '.TopicBadge_name::text',
                '[data-testid="topic"] span::text',
            ]
            
            tags = []
            for selector in tag_selectors:
                tag_elements = response.css(selector).getall()
                if tag_elements:
                    tags = [tag.strip() for tag in tag_elements if tag.strip()]
                    break
            
            # 記事の種類判定
            is_tutorial = any(keyword in title.lower() for keyword in 
                            ['チュートリアル', 'tutorial', '入門', '初心者', 'はじめて', '使い方', '基礎'])
            
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
        """Zenn固有のリンクフィルタリング"""
        if not super().should_follow_link(url):
            return False
        
        # Zenn固有の除外パターン
        zenn_exclude_patterns = [
            r'/users/',
            r'/books/',
            r'/scraps/',
            r'/following',
            r'/followers',
            r'/likes',
            r'/drafts',
        ]
        
        for pattern in zenn_exclude_patterns:
            if re.search(pattern, url, re.IGNORECASE):
                return False
        
        # 記事URLのパターンチェック
        if '/articles/' in url:
            return True
        
        return False