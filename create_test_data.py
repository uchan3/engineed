#!/usr/bin/env python3
"""テストデータ作成スクリプト"""

import sys
import os
from datetime import datetime, timedelta
from pathlib import Path

# プロジェクトルートをパスに追加
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from engineed.models.database import create_database, SessionLocal, Article, TechTag, article_tags

def create_sample_data():
    """サンプルデータを作成"""
    
    # データベース初期化
    print("データベースを初期化中...")
    create_database()
    
    # セッション作成
    db = SessionLocal()
    
    try:
        # 既存データクリア
        db.query(Article).delete()
        db.query(TechTag).delete()
        db.commit()
        
        # 技術タグ作成
        print("技術タグを作成中...")
        tags_data = [
            {"name": "Python", "category": "language", "popularity_score": 95.0},
            {"name": "JavaScript", "category": "language", "popularity_score": 92.0},
            {"name": "React", "category": "framework", "popularity_score": 88.0},
            {"name": "Vue.js", "category": "framework", "popularity_score": 82.0},
            {"name": "Django", "category": "framework", "popularity_score": 75.0},
            {"name": "FastAPI", "category": "framework", "popularity_score": 70.0},
            {"name": "Docker", "category": "tool", "popularity_score": 85.0},
            {"name": "Kubernetes", "category": "tool", "popularity_score": 72.0},
            {"name": "AWS", "category": "cloud", "popularity_score": 90.0},
            {"name": "機械学習", "category": "concept", "popularity_score": 80.0},
            {"name": "データサイエンス", "category": "concept", "popularity_score": 78.0},
            {"name": "Web開発", "category": "concept", "popularity_score": 85.0},
        ]
        
        tags = []
        for tag_data in tags_data:
            tag = TechTag(**tag_data)
            db.add(tag)
            tags.append(tag)
        
        db.commit()
        
        # サンプル記事作成
        print("サンプル記事を作成中...")
        articles_data = [
            {
                "title": "Pythonで始める機械学習入門 - scikit-learnの基本",
                "url": "https://qiita.com/example/python-ml-intro",
                "content": "機械学習は現代のソフトウェア開発において重要な技術です。Pythonのscikit-learnライブラリを使用することで、初心者でも簡単に機械学習を始めることができます。この記事では、データの前処理から予測モデルの作成まで、基本的な流れを解説します。まず、必要なライブラリをインストールし、データセットを準備します。次に、データの可視化と前処理を行い、最終的に予測モデルを構築して性能を評価します。",
                "summary": "Pythonのscikit-learnを使った機械学習の基本的な流れを初心者向けに解説。データ前処理から予測モデル作成まで網羅。",
                "author": "ml_engineer",
                "source_site": "qiita",
                "published_at": datetime.now() - timedelta(days=2),
                "view_count": 1250,
                "like_count": 45,
                "comment_count": 8,
                "reading_time": 12,
                "difficulty_level": 2,
                "is_tutorial": True,
                "tag_names": ["Python", "機械学習", "データサイエンス"]
            },
            {
                "title": "React + TypeScriptで作るモダンWebアプリケーション",
                "url": "https://qiita.com/example/react-typescript-modern",
                "content": "ReactとTypeScriptを組み合わせることで、保守性の高いWebアプリケーションを開発できます。この記事では、プロジェクトのセットアップから実際のコンポーネント作成まで、実践的な内容を紹介します。TypeScriptの型システムを活用することで、バグを事前に防ぎ、開発効率を向上させることができます。また、Hooksを使った状態管理やAPIとの連携についても詳しく説明します。",
                "summary": "ReactとTypeScriptを使ったモダンなWebアプリ開発手法を解説。型安全性と開発効率の向上に焦点。",
                "author": "frontend_dev",
                "source_site": "qiita",
                "published_at": datetime.now() - timedelta(days=1),
                "view_count": 890,
                "like_count": 32,
                "comment_count": 5,
                "reading_time": 15,
                "difficulty_level": 3,
                "is_tutorial": True,
                "tag_names": ["React", "JavaScript", "Web開発"]
            },
            {
                "title": "DockerとKubernetesで構築するマイクロサービス基盤",
                "url": "https://qiita.com/example/docker-k8s-microservices",
                "content": "マイクロサービスアーキテクチャは、大規模なアプリケーションを小さな独立したサービスに分割するアプローチです。DockerコンテナとKubernetesを使用することで、スケーラブルで信頼性の高いマイクロサービス基盤を構築できます。この記事では、サービス間通信、負荷分散、監視、ログ管理など、実運用で必要な要素について詳しく解説します。",
                "summary": "DockerとKubernetesを活用したマイクロサービス基盤の構築方法。実運用に必要な要素を網羅的に解説。",
                "author": "devops_engineer",
                "source_site": "qiita",
                "published_at": datetime.now() - timedelta(hours=12),
                "view_count": 654,
                "like_count": 28,
                "comment_count": 12,
                "reading_time": 20,
                "difficulty_level": 4,
                "is_tutorial": False,
                "tag_names": ["Docker", "Kubernetes", "AWS"]
            },
            {
                "title": "Vue.js 3とComposition APIで作るリアクティブなUIコンポーネント",
                "url": "https://qiita.com/example/vuejs3-composition-api",
                "content": "Vue.js 3で導入されたComposition APIは、コンポーネントロジックをより柔軟に組織化できる新しいAPIです。従来のOptions APIと比較して、再利用性とテスタビリティが向上します。この記事では、基本的な使い方から実践的なパターンまで、サンプルコードと共に解説します。また、TypeScriptとの組み合わせ方についても触れています。",
                "summary": "Vue.js 3のComposition APIを使ったモダンなコンポーネント開発手法を実例とともに紹介。",
                "author": "vue_developer",
                "source_site": "qiita",
                "published_at": datetime.now() - timedelta(hours=6),
                "view_count": 423,
                "like_count": 19,
                "comment_count": 3,
                "reading_time": 10,
                "difficulty_level": 3,
                "is_tutorial": True,
                "tag_names": ["Vue.js", "JavaScript", "Web開発"]
            },
            {
                "title": "FastAPIで作る高速WebAPI開発入門",
                "url": "https://qiita.com/example/fastapi-intro",
                "content": "FastAPIはPythonで書かれた現代的なWebフレームワークで、高いパフォーマンスと開発者体験を提供します。自動的なAPIドキュメント生成、型ヒントによる堅牢性、非同期処理のサポートなど、多くの利点があります。この記事では、プロジェクトのセットアップから認証機能の実装まで、実際のAPI開発の流れを紹介します。",
                "summary": "FastAPIを使った高速なWebAPI開発の入門ガイド。自動ドキュメント生成や型安全性の活用方法を解説。",
                "author": "api_developer",
                "source_site": "qiita",
                "published_at": datetime.now() - timedelta(hours=3),
                "view_count": 312,
                "like_count": 15,
                "comment_count": 2,
                "reading_time": 8,
                "difficulty_level": 2,
                "is_tutorial": True,
                "tag_names": ["Python", "FastAPI", "Web開発"]
            }
        ]
        
        for article_data in articles_data:
            # タグ名を取得してタグオブジェクトに変換
            tag_names = article_data.pop('tag_names', [])
            
            # 記事作成
            article = Article(**article_data)
            article.scraped_at = datetime.now()
            
            # タグを関連付け
            for tag_name in tag_names:
                tag = db.query(TechTag).filter(TechTag.name == tag_name).first()
                if tag:
                    article.tags.append(tag)
            
            db.add(article)
        
        db.commit()
        
        # 作成されたデータの確認
        article_count = db.query(Article).count()
        tag_count = db.query(TechTag).count()
        
        print(f"✅ テストデータ作成完了!")
        print(f"   📰 記事数: {article_count}")
        print(f"   🏷️  タグ数: {tag_count}")
        print(f"   📁 データベース: data/articles.db")
        
    except Exception as e:
        print(f"❌ エラーが発生しました: {e}")
        db.rollback()
        
    finally:
        db.close()

if __name__ == "__main__":
    # データディレクトリ作成
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)
    
    create_sample_data()