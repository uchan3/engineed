import re
import spacy
from collections import Counter
from engineed.utils.tech_keywords import TechKeywordManager
import openai
import os

class TechKeywordExtractor:
    """技術キーワード抽出とAI機能"""
    
    def __init__(self):
        self.keyword_manager = TechKeywordManager()
        self.tech_keywords = set(kw.lower() for kw in self.keyword_manager.get_all_keywords())
        
        # OpenAI設定
        self.openai_client = None
        if os.getenv('OPENAI_API_KEY'):
            openai.api_key = os.getenv('OPENAI_API_KEY')
            self.openai_client = openai.OpenAI()
        
        # spaCyモデル（日本語）
        try:
            self.nlp = spacy.load("ja_core_news_sm")
        except OSError:
            print("Warning: Japanese spaCy model not found. Install with: python -m spacy download ja_core_news_sm")
            self.nlp = None
    
    def extract_keywords(self, text):
        """テキストから技術キーワードを抽出"""
        if not text:
            return []
        
        text_lower = text.lower()
        found_keywords = []
        
        # 既知のキーワードをマッチング
        for keyword in self.tech_keywords:
            if keyword in text_lower:
                found_keywords.append(keyword)
        
        # 新しいキーワードの発見（大文字で始まる技術用語など）
        tech_patterns = [
            r'\b[A-Z][a-z]*(?:[A-Z][a-z]*)*\b',  # CamelCase
            r'\b[A-Z]+(?:\.[A-Z]+)*\b',  # 略語 (API, REST等)
            r'\b\w+\.(js|py|rb|go|rs|java|kt|swift)\b',  # ファイル拡張子
        ]
        
        for pattern in tech_patterns:
            matches = re.findall(pattern, text)
            found_keywords.extend([m.lower() for m in matches if len(m) > 2])
        
        # 重複除去と頻度ソート
        keyword_counts = Counter(found_keywords)
        return [kw for kw, count in keyword_counts.most_common(10)]
    
    def estimate_difficulty(self, text):
        """記事の難易度を推定（1-5）"""
        if not text:
            return 1
        
        difficulty_score = 1
        
        # 高度なキーワードの存在
        advanced_keywords = [
            'architecture', 'microservices', 'kubernetes', 'terraform',
            'algorithm', 'optimization', 'performance', 'scalability',
            'distributed', 'concurrent', 'asynchronous', 'parallel'
        ]
        
        for keyword in advanced_keywords:
            if keyword in text.lower():
                difficulty_score += 0.5
        
        # コードブロックの複雑さ
        code_blocks = re.findall(r'```[\s\S]*?```', text)
        if len(code_blocks) > 3:
            difficulty_score += 1
        
        # 文章の長さ
        if len(text) > 5000:
            difficulty_score += 1
        
        return min(5, max(1, int(difficulty_score)))
    
    def is_tutorial(self, text):
        """チュートリアル記事かどうか判定"""
        tutorial_indicators = [
            'tutorial', 'guide', 'how to', 'step by step', '入門',
            '初心者', 'はじめて', '始め方', 'やり方', '方法',
            'インストール', 'セットアップ', '導入'
        ]
        
        text_lower = text.lower()
        return any(indicator in text_lower for indicator in tutorial_indicators)
    
    def generate_summary(self, content):
        """AI要約生成"""
        if not self.openai_client or not content:
            return self._simple_summary(content)
        
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "あなたは技術記事の要約を作成するAIです。記事の要点を3-5文で簡潔にまとめてください。"},
                    {"role": "user", "content": f"以下の技術記事を要約してください:\n\n{content[:2000]}"}
                ],
                max_tokens=200,
                temperature=0.3
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"OpenAI API error: {e}")
            return self._simple_summary(content)
    
    def _simple_summary(self, content):
        """シンプルな要約（最初の数文を抽出）"""
        if not content:
            return ""
        
        sentences = re.split(r'[。！？]', content)
        # 最初の2-3文を使用
        summary_sentences = [s.strip() for s in sentences[:3] if s.strip()]
        return '。'.join(summary_sentences) + '。' if summary_sentences else ""