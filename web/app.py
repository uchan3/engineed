from fastapi import FastAPI, Request, Depends
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, desc
from engineed.models.database import Article, TechTag, SessionLocal, create_database
import os
from pathlib import Path

# FastAPIアプリケーション初期化
app = FastAPI(title="Engineed - Tech News Aggregator", version="1.0.0")

# テンプレートとスタティックファイルの設定
BASE_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")

# データベース依存関数
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.on_event("startup")
async def startup_event():
    """アプリケーション起動時にデータベースを初期化"""
    try:
        # データベースディレクトリが存在しない場合は作成
        data_dir = Path("data")
        data_dir.mkdir(exist_ok=True)
        
        # データベース初期化
        create_database()
        print("Database initialized successfully")
    except Exception as e:
        print(f"Database initialization error: {e}")

@app.get("/", response_class=HTMLResponse)
async def home(request: Request, db: Session = Depends(get_db)):
    """ホームページ - 最新記事一覧"""
    try:
        # 最新記事を20件取得
        articles = db.query(Article).order_by(desc(Article.scraped_at)).limit(20).all()
        
        # 統計情報
        total_articles = db.query(Article).count()
        
        return templates.TemplateResponse("index.html", {
            "request": request,
            "articles": articles,
            "total_articles": total_articles,
            "page_title": "最新記事"
        })
    except Exception as e:
        print(f"Error loading articles: {e}")
        return templates.TemplateResponse("index.html", {
            "request": request,
            "articles": [],
            "total_articles": 0,
            "page_title": "最新記事",
            "error": str(e)
        })

@app.get("/article/{article_id}", response_class=HTMLResponse)
async def article_detail(request: Request, article_id: int, db: Session = Depends(get_db)):
    """記事詳細ページ"""
    try:
        article = db.query(Article).filter(Article.id == article_id).first()
        if not article:
            return templates.TemplateResponse("error.html", {
                "request": request,
                "error": "記事が見つかりません"
            })
        
        return templates.TemplateResponse("article.html", {
            "request": request,
            "article": article
        })
    except Exception as e:
        return templates.TemplateResponse("error.html", {
            "request": request,
            "error": str(e)
        })

@app.get("/tags", response_class=HTMLResponse)
async def tags_page(request: Request, db: Session = Depends(get_db)):
    """タグ一覧ページ"""
    try:
        tags = db.query(TechTag).order_by(desc(TechTag.popularity_score)).limit(50).all()
        
        return templates.TemplateResponse("tags.html", {
            "request": request,
            "tags": tags,
            "page_title": "技術タグ"
        })
    except Exception as e:
        return templates.TemplateResponse("tags.html", {
            "request": request,
            "tags": [],
            "page_title": "技術タグ",
            "error": str(e)
        })

@app.get("/stats", response_class=HTMLResponse)
async def stats_page(request: Request, db: Session = Depends(get_db)):
    """統計情報ページ"""
    try:
        stats = {
            "total_articles": db.query(Article).count(),
            "total_tags": db.query(TechTag).count(),
            "sources": db.query(Article.source_site, db.func.count(Article.id)).group_by(Article.source_site).all()
        }
        
        return templates.TemplateResponse("stats.html", {
            "request": request,
            "stats": stats,
            "page_title": "統計情報"
        })
    except Exception as e:
        return templates.TemplateResponse("stats.html", {
            "request": request,
            "stats": {},
            "page_title": "統計情報",
            "error": str(e)
        })

@app.get("/api/articles")
async def api_articles(db: Session = Depends(get_db), limit: int = 10):
    """API: 記事一覧取得"""
    try:
        articles = db.query(Article).order_by(desc(Article.scraped_at)).limit(limit).all()
        return {
            "articles": [
                {
                    "id": article.id,
                    "title": article.title,
                    "url": article.url,
                    "author": article.author,
                    "source_site": article.source_site,
                    "published_at": article.published_at.isoformat() if article.published_at else None,
                    "scraped_at": article.scraped_at.isoformat() if article.scraped_at else None,
                    "tags": [tag.name for tag in article.tags] if article.tags else []
                }
                for article in articles
            ]
        }
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)