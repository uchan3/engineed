import scrapy
import json
import re
from datetime import datetime
from urllib.parse import urljoin, urlparse
from engineed.spiders.base_spider import BaseTechSpider


class HatebSpider(BaseTechSpider):
    """はてなブックマーク（テクノロジー）の記事を収集するSpider"""
    
    name = 'hateb'
    allowed_domains = ['b.hatena.ne.jp', 'hatena.ne.jp']
    start_urls = ['https://b.hatena.ne.jp/hotentry/it']
    
    custom_settings = {
        'DOWNLOAD_DELAY': 2,  # はてなは少し長めに設定
        'RANDOMIZE_DOWNLOAD_DELAY': 1,
        'CONCURRENT_REQUESTS_PER_DOMAIN': 2,
    }
    
    def start_requests(self):
        """初期リクエストを生成"""
        urls = [
            'https://b.hatena.ne.jp/hotentry/it',  # ITカテゴリ人気エントリ
            'https://b.hatena.ne.jp/hotentry/technology',  # テクノロジーカテゴリ
            'https://b.hatena.ne.jp/newentry/it',  # IT新着エントリ
            'https://b.hatena.ne.jp/newentry/technology',  # テクノロジー新着
        ]
        
        for url in urls:
            yield scrapy.Request(
                url=url,
                callback=self.parse,
                meta={'page': 1}
            )
    
    def parse(self, response):
        """記事一覧ページのパース"""
        # はてなブックマークの記事リンクを抽出
        article_selectors = [
            '.entrylist-contents-title a::attr(href)',  # 記事タイトルリンク
            '.entrylist-title a::attr(href)',  # タイトルリンク（別パターン）
            '.entry-link::attr(href)',  # エントリリンク
            'h3 a::attr(href)',  # 一般的なタイトルリンク
        ]
        
        article_links = []
        for selector in article_selectors:
            links = response.css(selector).getall()
            if links:
                article_links.extend(links)
        
        # 重複除去とフィルタリング
        article_links = list(set(article_links))
        # 技術系サイトの記事のみを対象とする
        tech_domains = [
            'qiita.com', 'zenn.dev', 'note.com', 'github.com',
            'dev.to', 'medium.com', 'speakerdeck.com',
            'tech.mercari.com', 'engineering.linecorp.com',
            'developers.cyberagent.co.jp', 'techblog.yahoo.co.jp',
            'blog.recruit.co.jp', 'engineering.rakuten.co.jp'
        ]
        
        filtered_links = []
        for link in article_links:
            parsed_url = urlparse(link)
            if any(domain in parsed_url.netloc for domain in tech_domains):
                filtered_links.append(link)
        
        self.logger.info(f'Found {len(filtered_links)} tech article links on {response.url}')
        
        # 各記事ページにリクエスト
        for link in filtered_links[:15]:  # 最初の15件に制限
            if self.should_follow_external_link(link):
                yield scrapy.Request(
                    url=link,
                    callback=self.parse_external_article,
                    errback=self.handle_error,
                    meta={'source_page': response.url}
                )
        
        # ページネーション
        current_page = response.meta.get('page', 1)
        if current_page < self.max_pages:
            next_selectors = [
                'a[rel="next"]::attr(href)',
                '.pager-next a::attr(href)',
                'a:contains("次の")::attr(href)',
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
    
    def parse_external_article(self, response):
        """外部記事のパース"""
        try:
            # ドメインに応じて適切なパーサーを選択
            parsed_url = urlparse(response.url)
            domain = parsed_url.netloc
            
            if 'qiita.com' in domain:
                return self.parse_qiita_article(response)
            elif 'zenn.dev' in domain:
                return self.parse_zenn_article(response)
            elif 'note.com' in domain:
                return self.parse_note_article(response)
            elif 'github.com' in domain:
                return self.parse_github_article(response)
            else:
                return self.parse_generic_article(response)
                
        except Exception as e:
            self.logger.error(f'Error parsing external article {response.url}: {str(e)}')
    
    def parse_qiita_article(self, response):
        """Qiita記事の専用パーサー"""
        # Qiitaスパイダーのロジックを再利用
        title_selectors = [
            'h1[data-cy="article-title"]::text',
            'h1::text',
            'title::text',
        ]
        
        title = None
        for selector in title_selectors:
            title = response.css(selector).get()
            if title:
                title = title.strip()
                break
        
        author_selectors = [
            'a[href*="/users/"]::text',
            '.user-info a::text',
        ]
        
        author = None
        for selector in author_selectors:
            author = response.css(selector).get()
            if author:
                break
        
        # 基本的な記事情報を抽出
        content = response.css('.markdown-body').get() or response.css('article').get()
        tags = [tag.strip() for tag in response.css('a[href*="/tags/"]::text').getall()]
        
        return self.create_hateb_item(response, title, author, content, tags)
    
    def parse_zenn_article(self, response):
        """Zenn記事の専用パーサー"""
        title = response.css('h1::text').get()
        author = response.css('a[href*="/users/"]::text').get()
        content = response.css('.zenn-markdown').get() or response.css('.ArticleBody_content').get()
        tags = [tag.strip() for tag in response.css('a[href*="/topics/"]::text').getall()]
        
        return self.create_hateb_item(response, title, author, content, tags)
    
    def parse_note_article(self, response):
        """note記事の専用パーサー"""
        title = response.css('h1::text').get()
        author = response.css('.note-user-name::text').get()
        content = response.css('.note-body').get()
        tags = [tag.strip() for tag in response.css('.tag::text').getall()]
        
        return self.create_hateb_item(response, title, author, content, tags)
    
    def parse_github_article(self, response):
        """GitHub記事（README等）の専用パーサー"""
        title_selectors = [
            '.js-navigation-open[title]::attr(title)',
            'h1::text',
            '.repository-content h1::text',
        ]
        
        title = None
        for selector in title_selectors:
            title = response.css(selector).get()
            if title:
                break
        
        author = response.css('.author a::text').get()
        content = response.css('.markdown-body').get() or response.css('article').get()
        
        # GitHubのトピックをタグとして使用
        tags = [tag.strip() for tag in response.css('.topic-tag::text').getall()]
        
        return self.create_hateb_item(response, title, author, content, tags)
    
    def parse_generic_article(self, response):
        """汎用記事パーサー"""
        # 一般的なHTML構造から情報を抽出
        title_selectors = [
            'h1::text',
            'title::text',
            '.title::text',
            '.post-title::text',
        ]
        
        title = None
        for selector in title_selectors:
            title = response.css(selector).get()
            if title:
                title = title.strip()
                break
        
        # 作者の抽出を試行
        author_selectors = [
            '.author::text',
            '.by-author::text',
            '[rel="author"]::text',
            '.post-author::text',
        ]
        
        author = None
        for selector in author_selectors:
            author = response.css(selector).get()
            if author:
                break
        
        # コンテンツの抽出
        content_selectors = [
            'article',
            '.content',
            '.post-content',
            '.entry-content',
            'main',
        ]
        
        content = None
        for selector in content_selectors:
            content = response.css(selector).get()
            if content:
                break
        
        return self.create_hateb_item(response, title, author, content, [])
    
    def create_hateb_item(self, response, title, author, content, tags):
        """はてブ経由記事用のアイテム作成"""
        if not title or not content:
            self.logger.warning(f'Missing essential data for {response.url}')
            return
        
        # 記事の種類判定
        is_tutorial = any(keyword in title.lower() for keyword in 
                        ['チュートリアル', 'tutorial', '入門', '初心者', 'はじめて', '使い方', '基礎'])
        
        # ArticleItemを作成
        item = self.create_article_item(
            response,
            title=title,
            content=content,
            author=author,
            published_at=None,  # はてブ経由では取得困難
            view_count=0,
            like_count=0,
            comment_count=0,
            tags=tags,
            is_tutorial=is_tutorial
        )
        
        # ソースサイトをドメインから判定
        parsed_url = urlparse(response.url)
        if 'qiita.com' in parsed_url.netloc:
            item['source_site'] = 'qiita'
        elif 'zenn.dev' in parsed_url.netloc:
            item['source_site'] = 'zenn'
        elif 'note.com' in parsed_url.netloc:
            item['source_site'] = 'note'
        elif 'github.com' in parsed_url.netloc:
            item['source_site'] = 'github'
        else:
            item['source_site'] = 'hateb'
        
        # 有効性チェック
        if self.is_valid_article(item):
            yield item
        else:
            self.logger.warning(f'Invalid article: {response.url}')
    
    def should_follow_external_link(self, url):
        """外部リンクをフォローするかの判断"""
        try:
            parsed_url = urlparse(url)
            
            # 除外パターン
            exclude_patterns = [
                r'/users?/',
                r'/profile',
                r'/settings',
                r'/login',
                r'/signup',
                r'\.(css|js|png|jpg|gif|svg|ico|pdf)$',
            ]
            
            for pattern in exclude_patterns:
                if re.search(pattern, url, re.IGNORECASE):
                    return False
            
            return True
            
        except Exception:
            return False
    
    def handle_error(self, failure):
        """エラーハンドリング"""
        self.logger.error(f'Request failed: {failure.request.url} - {failure.value}')