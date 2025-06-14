# CLAUDE.md
必ず日本語で回答してください。
This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is "Engineed" - an AI-powered technical news aggregator built with Scrapy, SQLAlchemy, and FastAPI. The project scrapes technical articles from Japanese tech sites (Qiita, Zenn, Hatena Blog), uses OpenAI GPT for content analysis, and provides personalized learning recommendations.
This tool focuses on engineers' growth.

## Development Commands

### Initial Setup
```bash
pip install -r requirements.txt
python -m engineed.cli init-db  # Initialize SQLite database
```

### CLI Commands (via engineed.cli)
```bash
# Run specific spider
python -m engineed.cli crawl -s qiita    # Qiita記事収集
python -m engineed.cli crawl -s zenn     # Zenn記事収集
python -m engineed.cli crawl -s hateb    # はてブ経由記事収集

# Test mode (limited items, no pipelines)
python -m engineed.cli crawl -s qiita --test
python -m engineed.cli crawl -s zenn --test
python -m engineed.cli crawl -s hateb --test

# Run all spiders
python -m engineed.cli crawl --all
python -m engineed.cli crawl --all --test

# Start web server
python -m engineed.cli serve --host 127.0.0.1 --port 8000

# Check system status
python -m engineed.cli status
```

### Scrapy Commands
```bash
# Run individual spiders directly
scrapy crawl qiita    # Qiita技術記事
scrapy crawl zenn     # Zenn技術記事
scrapy crawl hateb    # はてなブックマーク経由

# List available spiders
scrapy list

# Test run with limited items
scrapy crawl qiita -s CLOSESPIDER_ITEMCOUNT=5 -s ITEM_PIPELINES="{}"
```

### Testing & Development
```bash
# Test all spiders functionality
python test_all_spiders.py

# Test individual spider logic
python test_spider.py

# Run minimal web test
python test_minimal.py
```

All spiders are fully implemented:
- `qiita_spider.py` - Qiita articles with real-world HTML parsing
- `zenn_spider.py` - Zenn articles with modern web structure
- `hateb_spider.py` - Hatena Bookmark tech entries with multi-site support

## Architecture

### Core Components

**Data Flow**: Web Scraping → AI Analysis → Database Storage → Web Interface/API

**Key Modules**:
- `engineed/spiders/` - Scrapy spiders for different tech sites (planned)
- `engineed/models/database.py` - SQLAlchemy models for articles, users, tags, learning paths
- `engineed/ai/keyword_extractor.py` - OpenAI-powered content analysis
- `engineed/pipelines.py` - Data processing pipeline for scraped content
- `engineed/cli.py` - Click-based CLI interface
- `web/app.py` - FastAPI web application (planned)

**Database Schema**:
- Articles with AI-generated summaries, difficulty levels, and metadata
- Hierarchical tech tags with popularity/trend scoring
- User learning tracking with reading records and skill progression
- Learning paths with structured steps and recommendations
- Scraping job monitoring

### AI Integration
- Uses OpenAI API for content summarization and keyword extraction
- Implements difficulty level estimation (1-5 scale)
- Generates personalized learning recommendations
- Tech trend analysis and scoring

### Data Sources
- Qiita (Japanese tech articles)
- Zenn (Japanese developer platform)
- Hatena Blog (Japanese blogging platform)

## Important Notes

- Database: SQLite stored in `data/articles.db`
- AI Features: Requires OpenAI API key configuration
- Language: Primarily Japanese content with some English support
- The project uses package name "tech_feed" in setup.py but directory name "engineed"
- Web interface planned but not yet implemented
- Spiders directory structure exists in README but files not yet created