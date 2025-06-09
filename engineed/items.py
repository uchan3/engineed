import scrapy
from pydantic import BaseModel, HttpUrl, validator
from typing import List, Optional
from datetime import datetime

class ArticleItem(scrapy.Item):
    title = scrapy.Field()
    url = scrapy.Field()
    content = scrapy.Field()
    author = scrapy.Field()
    source_site = scrapy.Field()
    published_at = scrapy.Field()
    view_count = scrapy.Field()
    like_count = scrapy.Field()
    comment_count = scrapy.Field()
    tags = scrapy.Field()  # 元サイトのタグ
    reading_time = scrapy.Field()
    language = scrapy.Field()
    is_tutorial = scrapy.Field()
    
    # 追加メタデータ
    scraped_at = scrapy.Field()
    raw_html = scrapy.Field()
    images = scrapy.Field()
    external_links = scrapy.Field()


class ArticleSchema(BaseModel):
    title: str
    url: HttpUrl
    content: Optional[str] = None
    author: Optional[str] = None
    source_site: str
    published_at: Optional[datetime] = None
    view_count: int = 0
    like_count: int = 0
    comment_count: int = 0
    tags: List[str] = []
    reading_time: Optional[int] = None
    language: str = 'ja'
    is_tutorial: bool = False
    
    @validator('reading_time')
    def estimate_reading_time(cls, v, values):
        if v is None and 'content' in values and values['content']:
            # 日本語の場合、約400-600文字/分で読める
            char_count = len(values['content'])
            v = max(1, char_count // 500)
        return v
    
    @validator('tags')
    def normalize_tags(cls, v):
        # タグの正規化
        return [tag.lower().strip() for tag in v if tag.strip()]