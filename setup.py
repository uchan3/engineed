from setuptools import setup, find_packages

setup(
    name='tech_feed',
    version='0.1.0',
    description='AI-powered technical news aggregator',
    packages=find_packages(),
    install_requires=[
        'scrapy>=2.11.0',
        'sqlalchemy>=2.0.0',
        'pydantic>=2.0.0',
        'fastapi>=0.104.0',
        'uvicorn>=0.24.0',
        'beautifulsoup4>=4.12.0',
        'requests>=2.31.0',
        'openai>=1.0.0',
        'transformers>=4.35.0',
        'scikit-learn>=1.3.0',
        'pandas>=2.1.0',
    ],
    python_requires='>=3.9',
    entry_points={
        'console_scripts': [
            'tech-feed=tech_feed.cli:main',
        ],
    },
)

print("セットアップファイルを作成しました！")
print("\n次のコマンドでプロジェクトを初期化できます：")
print("1. mkdir tech_feed && cd tech_feed")
print("2. 上記のファイル構造を作成")
print("3. pip install -r requirements.txt")
print("4. scrapy startproject tech_feed")