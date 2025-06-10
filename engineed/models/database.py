# tech_feed/models/database.py
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Float, Boolean, ForeignKey, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.dialects.sqlite import JSON
from datetime import datetime
import sqlite3

Base = declarative_base()

# 多対多関係のためのアソシエーションテーブル
article_tags = Table(
    'article_tags',
    Base.metadata,
    Column('article_id', Integer, ForeignKey('articles.id')),
    Column('tag_id', Integer, ForeignKey('tech_tags.id'))
)

user_interests = Table(
    'user_interests',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id')),
    Column('tag_id', Integer, ForeignKey('tech_tags.id'))
)

class Article(Base):
    __tablename__ = 'articles'
    
    id = Column(Integer, primary_key=True)
    title = Column(String(500), nullable=False)
    url = Column(String(1000), unique=True, nullable=False)
    content = Column(Text)
    summary = Column(Text)  # AI生成要約
    author = Column(String(200))
    source_site = Column(String(100), nullable=False)  # qiita, zenn, etc.
    published_at = Column(DateTime)
    scraped_at = Column(DateTime, default=datetime.utcnow)
    
    # スコアリング
    view_count = Column(Integer, default=0)
    like_count = Column(Integer, default=0)
    comment_count = Column(Integer, default=0)
    tech_feed_score = Column(Float, default=0.0)  # 独自スコア
    difficulty_level = Column(Integer, default=1)  # 1-5の難易度
    
    # メタデータ
    reading_time = Column(Integer)  # 推定読了時間（分）
    language = Column(String(10), default='ja')
    is_tutorial = Column(Boolean, default=False)
    is_official_doc = Column(Boolean, default=False)
    
    # リレーション
    tags = relationship("TechTag", secondary=article_tags, back_populates="articles")
    read_records = relationship("ReadRecord", back_populates="article")

class TechTag(Base):
    __tablename__ = 'tech_tags'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)
    category = Column(String(50))  # language, framework, tool, concept, etc.
    parent_id = Column(Integer, ForeignKey('tech_tags.id'))  # 階層構造
    description = Column(Text)
    popularity_score = Column(Float, default=0.0)
    trend_score = Column(Float, default=0.0)  # トレンド度
    
    # 自己参照リレーション
    children = relationship("TechTag", backref="parent", remote_side=[id])
    articles = relationship("Article", secondary=article_tags, back_populates="tags")
    user_interests = relationship("User", secondary=user_interests, back_populates="interested_tags")

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(100), unique=True, nullable=False)
    email = Column(String(200), unique=True)
    experience_level = Column(Integer, default=1)  # 1-5の経験レベル
    created_at = Column(DateTime, default=datetime.utcnow)
    last_active = Column(DateTime, default=datetime.utcnow)
    
    # 学習進捗
    total_articles_read = Column(Integer, default=0)
    learning_streak = Column(Integer, default=0)  # 連続学習日数
    skill_points = Column(Integer, default=0)
    
    # リレーション
    interested_tags = relationship("TechTag", secondary=user_interests, back_populates="user_interests")
    read_records = relationship("ReadRecord", back_populates="user")
    learning_paths = relationship("LearningPath", back_populates="user")

class ReadRecord(Base):
    __tablename__ = 'read_records'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    article_id = Column(Integer, ForeignKey('articles.id'), nullable=False)
    read_at = Column(DateTime, default=datetime.utcnow)
    reading_time = Column(Integer)  # 実際の読了時間（秒）
    completion_rate = Column(Float, default=0.0)  # 0.0-1.0
    rating = Column(Integer)  # 1-5の評価
    is_bookmarked = Column(Boolean, default=False)
    notes = Column(Text)  # ユーザーメモ
    
    # リレーション
    user = relationship("User", back_populates="read_records")
    article = relationship("Article", back_populates="read_records")

class LearningPath(Base):
    __tablename__ = 'learning_paths'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    target_tags = Column(JSON)  # 学習対象のタグIDリスト
    current_step = Column(Integer, default=0)
    total_steps = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    
    # リレーション
    user = relationship("User", back_populates="learning_paths")
    steps = relationship("LearningStep", back_populates="path")

class LearningStep(Base):
    __tablename__ = 'learning_steps'
    
    id = Column(Integer, primary_key=True)
    path_id = Column(Integer, ForeignKey('learning_paths.id'), nullable=False)
    step_number = Column(Integer, nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    recommended_articles = Column(JSON)  # 推奨記事IDリスト
    prerequisites = Column(JSON)  # 前提条件タグIDリスト
    estimated_time = Column(Integer)  # 推定学習時間（分）
    is_completed = Column(Boolean, default=False)
    completed_at = Column(DateTime)
    
    # リレーション
    path = relationship("LearningPath", back_populates="steps")

class ScrapingJob(Base):
    __tablename__ = 'scraping_jobs'
    
    id = Column(Integer, primary_key=True)
    spider_name = Column(String(100), nullable=False)
    status = Column(String(20), default='pending')  # pending, running, completed, failed
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    articles_scraped = Column(Integer, default=0)
    errors_count = Column(Integer, default=0)
    logs = Column(Text)

# データベース接続
DATABASE_URL = "sqlite:///data/articles.db"
engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_database(database_url=DATABASE_URL):
    global engine, SessionLocal
    engine = create_engine(database_url, echo=False)
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return engine, SessionLocal

def get_db_session(SessionLocal):
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()