import click
import subprocess
import sys
from engineed.models.database import create_database

@click.group()
def main():
    """Tech Feed - AI-powered technical news aggregator"""
    pass

@main.command()
@click.option('--spider', '-s', help='Spider name to run (qiita, zenn, hateb)')
@click.option('--all', 'run_all', is_flag=True, help='Run all spiders')
@click.option('--test', is_flag=True, help='Run in test mode (limited items)')
def crawl(spider, run_all, test):
    """Run scrapy spiders"""
    test_args = []
    if test:
        test_args = ['-s', 'CLOSESPIDER_ITEMCOUNT=3', '-s', 'ITEM_PIPELINES={}']
    
    if run_all:
        spiders = ['qiita', 'zenn', 'hateb']
        for spider_name in spiders:
            click.echo(f"Running spider: {spider_name}")
            cmd = ['scrapy', 'crawl', spider_name] + test_args
            subprocess.run(cmd)
    elif spider:
        if spider not in ['qiita', 'zenn', 'hateb']:
            click.echo(f"Error: Unknown spider '{spider}'. Available: qiita, zenn, hateb")
            return
        click.echo(f"Running spider: {spider}")
        cmd = ['scrapy', 'crawl', spider] + test_args
        subprocess.run(cmd)
    else:
        click.echo("Available spiders: qiita, zenn, hateb")
        click.echo("Use: python -m engineed.cli crawl -s <spider_name>")
        click.echo("Or:  python -m engineed.cli crawl --all")

@main.command()
def init_db():
    """Initialize database"""
    click.echo("Initializing database...")
    create_database()
    click.echo("Database initialized successfully!")

@main.command()
@click.option('--host', default='127.0.0.1', help='Host to bind')
@click.option('--port', default=8000, help='Port to bind')
def serve(host, port):
    """Start web server"""
    click.echo(f"Starting web server on {host}:{port}")
    subprocess.run(['uvicorn', 'web.app:app', '--host', host, '--port', str(port), '--reload'])

@main.command()
def status():
    """Show system status"""
    click.echo("Tech Feed Status:")
    # TODO: データベース接続確認、記事数統計など

if __name__ == '__main__':
    main()