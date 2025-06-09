import click
import subprocess
import sys
from engineed.models.database import create_database

@click.group()
def main():
    """Tech Feed - AI-powered technical news aggregator"""
    pass

@main.command()
@click.option('--spider', '-s', help='Spider name to run')
@click.option('--all', 'run_all', is_flag=True, help='Run all spiders')
def crawl(spider, run_all):
    """Run scrapy spiders"""
    if run_all:
        spiders = ['qiita', 'zenn', 'hateb']
        for spider_name in spiders:
            click.echo(f"Running spider: {spider_name}")
            subprocess.run(['scrapy', 'crawl', spider_name])
    elif spider:
        click.echo(f"Running spider: {spider}")
        subprocess.run(['scrapy', 'crawl', spider])
    else:
        click.echo("Please specify a spider with -s or use --all")

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