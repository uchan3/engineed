from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
from engineed.models.database import Article, TechTag, article_tags, create_database
from engineed.ai.keyword_extractor import TechKeywordExtractor
from engineed.utils.text_processor import TextProcessor
from datetime import datetime
import logging
import hashlib

class ValidationPipeline:
    """データバリデーションパイプライン"""
    
    def process_item(self, item, spider):
        try:
            # Pydanticでバリデーション
            validated_item = ArticleSchema(**dict(item))
            
            # 必要フィールドの確認
            if not validated_item.title or not validated_item.url:
                raise ValueError("Title and URL are required")
            
            # バリデート済みデータでアイテムを更新
            for key, value in validated_item.dict().items():
                item[key] = value
                
            return item
        except Exception as e:
            spider.logger.error(f"Validation failed for item: {e}")
            raise

class DuplicationFilterPipeline:
    """重複除去パイプライン"""
    
    def __init__(self):
        self.seen_urls = set()
        
    def process_item(self, item, spider):
        url = item.get('url')
        if url in self.seen_urls:
            spider.logger.info(f"Duplicate item found: {url}")
            raise Exception("Duplicate item")
        else:
            self.seen_urls.add(url)
            return item

class TextProcessingPipeline:
    """テキスト処理パイプライン"""
    
    def __init__(self):
        self.text_processor = TextProcessor()
        
    def process_item(self, item, spider):
        # コンテンツのクリーニング
        if item.get('content'):
            item['content'] = self.text_processor.clean_html(item['content'])
            item['content'] = self.text_processor.normalize_text(item['content'])
        
        # タイトルの正規化
        if item.get('title'):
            item['title'] = self.text_processor.normalize_text(item['title'])
        
        return item

class AIEnrichmentPipeline:
    """AI機能による記事エンリッチメント"""
    
    def __init__(self):
        self.keyword_extractor = TechKeywordExtractor()
        
    def process_item(self, item, spider):
        content = item.get('content', '')
        title = item.get('title', '')
        text = f"{title} {content}"
        
        # 技術キーワード抽出
        extracted_tags = self.keyword_extractor.extract_keywords(text)
        
        # 既存タグとマージ
        existing_tags = item.get('tags', [])
        all_tags = list(set(existing_tags + extracted_tags))
        item['tags'] = all_tags
        
        # 難易度推定
        item['difficulty_level'] = self.keyword_extractor.estimate_difficulty(text)
        
        # チュートリアル判定
        item['is_tutorial'] = self.keyword_extractor.is_tutorial(text)
        
        # 要約生成（オプション）
        if len(content) > 1000:
            item['summary'] = self.keyword_extractor.generate_summary(content)
        
        return item

class DatabasePipeline:
    """データベース保存パイプライン"""
    
    def __init__(self, database_url='sqlite:///data/articles.db'):
        self.database_url = database_url
        
    def open_spider(self, spider):
        self.engine, self.SessionLocal = create_database(self.database_url)
        
    def close_spider(self, spider):
        self.engine.dispose()
        
    def process_item(self, item, spider):
        session = self.SessionLocal()
        try:
            # 既存記事チェック
            existing_article = session.query(Article).filter_by(url=item['url']).first()
            
            if existing_article:
                # 更新
                self._update_article(existing_article, item, session)
                spider.logger.info(f"Updated article: {item['title']}")
            else:
                # 新規作成
                self._create_article(item, session)
                spider.logger.info(f"Created new article: {item['title']}")
                
            session.commit()
            return item
            
        except Exception as e:
            session.rollback()
            spider.logger.error(f"Database error: {e}")
            raise
        finally:
            session.close()
    
    def _create_article(self, item, session):
        # 記事作成
        article = Article(
            title=item['title'],
            url=item['url'],
            content=item.get('content'),
            summary=item.get('summary'),
            author=item.get('author'),
            source_site=item['source_site'],
            published_at=item.get('published_at'),
            view_count=item.get('view_count', 0),
            like_count=item.get('like_count', 0),
            comment_count=item.get('comment_count', 0),
            difficulty_level=item.get('difficulty_level', 1),
            reading_time=item.get('reading_time'),
            language=item.get('language', 'ja'),
            is_tutorial=item.get('is_tutorial', False),
            scraped_at=datetime.utcnow()
        )
        
        session.add(article)
        session.flush()  # IDを取得
        
        # タグ処理
        self._process_tags(article, item.get('tags', []), session)
        
    def _update_article(self, article, item, session):
        # 既存記事を更新
        article.content = item.get('content', article.content)
        article.summary = item.get('summary', article.summary)
        article.view_count = item.get('view_count', article.view_count)
        article.like_count = item.get('like_count', article.like_count)
        article.comment_count = item.get('comment_count', article.comment_count)
        article.scraped_at = datetime.utcnow()
        
        # タグ更新
        self._process_tags(article, item.get('tags', []), session)
        
    def _process_tags(self, article, tag_names, session):
        """タグの作成・関連付け"""
        for tag_name in tag_names:
            # 既存タグ検索または作成
            tag = session.query(TechTag).filter_by(name=tag_name).first()
            if not tag:
                tag = TechTag(
                    name=tag_name,
                    category=self._categorize_tag(tag_name)
                )
                session.add(tag)
                session.flush()
            
            # 記事とタグの関連付け
            if tag not in article.tags:
                article.tags.append(tag)
    
    def _categorize_tag(self, tag_name):
        """タグのカテゴリ推定"""
        # 簡易的なカテゴリ分類
        languages = ['python', 'javascript', 'java', 'go', 'rust', 'typescript']
        frameworks = ['react', 'vue', 'angular', 'django', 'flask', 'express']
        tools = ['docker', 'kubernetes', 'git', 'jenkins', 'terraform']
        
        tag_lower = tag_name.lower()
        
        if any(lang in tag_lower for lang in languages):
            return 'language'
        elif any(fw in tag_lower for fw in frameworks):
            return 'framework'
        elif any(tool in tag_lower for tool in tools):
            return 'tool'
        else:
            return 'concept'