import re
from bs4 import BeautifulSoup
import unicodedata

class TextProcessor:
    """テキスト処理ユーティリティ"""
    
    def __init__(self):
        # HTML除去用の正規表現
        self.html_pattern = re.compile(r'<[^>]+>')
        self.whitespace_pattern = re.compile(r'\s+')
        self.url_pattern = re.compile(r'https?://[^\s]+')
        
    def clean_html(self, html_content):
        """HTMLタグを除去してテキストを抽出"""
        if not html_content:
            return ""
        
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # スクリプトとスタイルタグを除去
        for script in soup(["script", "style"]):
            script.decompose()
        
        # テキスト抽出
        text = soup.get_text()
        
        # 改行とスペースの正規化
        text = self.whitespace_pattern.sub(' ', text)
        
        return text.strip()
    
    def normalize_text(self, text):
        """テキストの正規化"""
        if not text:
            return ""
        
        # Unicode正規化
        text = unicodedata.normalize('NFKC', text)
        
        # 余分な空白を除去
        text = self.whitespace_pattern.sub(' ', text)
        
        # 前後の空白を除去
        text = text.strip()
        
        return text
    
    def extract_code_blocks(self, content):
        """コードブロックを抽出"""
        code_patterns = [
            r'```[\s\S]*?```',  # Markdown
            r'<code>[\s\S]*?</code>',  # HTML
            r'<pre>[\s\S]*?</pre>',  # HTML
        ]
        
        code_blocks = []
        for pattern in code_patterns:
            matches = re.findall(pattern, content, re.MULTILINE)
            code_blocks.extend(matches)
        
        return code_blocks
    
    def calculate_reading_time(self, text, wpm=400):
        """読了時間を計算（日本語ベース）"""
        if not text:
            return 0
        
        # 日本語の場合、文字数ベースで計算
        char_count = len(text)
        # 日本語は約400-600文字/分
        minutes = max(1, char_count // wpm)
        
        return minutes