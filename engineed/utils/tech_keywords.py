import json
import os

class TechKeywordManager:
    """技術キーワード管理"""
    
    def __init__(self, keywords_file='data/tech_keywords.json'):
        self.keywords_file = keywords_file
        self.keywords = self._load_keywords()
    
    def _load_keywords(self):
        """キーワードファイルを読み込み"""
        if os.path.exists(self.keywords_file):
            with open(self.keywords_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            return self._create_default_keywords()
    
    def _create_default_keywords(self):
        """デフォルトキーワードを作成"""
        keywords = {
            "languages": [
                "Python", "JavaScript", "TypeScript", "Java", "Go", "Rust", 
                "C++", "C#", "PHP", "Ruby", "Swift", "Kotlin", "Dart",
                "HTML", "CSS", "SQL", "Shell", "PowerShell"
            ],
            "frameworks": [
                "React", "Vue.js", "Angular", "Next.js", "Nuxt.js", "Svelte",
                "Django", "Flask", "FastAPI", "Express.js", "Node.js",
                "Spring", "Laravel", "Rails", "ASP.NET", "Flutter",
                "React Native", "Electron"
            ],
            "tools": [
                "Docker", "Kubernetes", "Git", "GitHub", "GitLab",
                "Jenkins", "CircleCI", "GitHub Actions", "Terraform",
                "Ansible", "Chef", "Puppet", "Vagrant", "VS Code",
                "Vim", "Emacs", "IntelliJ", "Eclipse"
            ],
            "databases": [
                "MySQL", "PostgreSQL", "SQLite", "MongoDB", "Redis",
                "Elasticsearch", "Cassandra", "DynamoDB", "Firebase",
                "Supabase", "PlanetScale", "Prisma", "TypeORM", "Sequelize"
            ],
            "cloud": [
                "AWS", "Azure", "GCP", "Google Cloud", "Heroku", "Vercel",
                "Netlify", "DigitalOcean", "Linode", "Cloudflare",
                "Firebase", "Supabase", "Railway", "Render"
            ],
            "concepts": [
                "Machine Learning", "AI", "Deep Learning", "Neural Network",
                "API", "REST", "GraphQL", "Microservices", "Serverless",
                "DevOps", "CI/CD", "Agile", "Scrum", "TDD", "Clean Code",
                "Design Patterns", "SOLID", "DDD", "Event Sourcing",
                "CQRS", "WebAssembly", "PWA", "SPA", "JAMstack"
            ],
            "trending": [
                "ChatGPT", "OpenAI", "LLM", "Generative AI", "Stable Diffusion",
                "WebGPU", "Deno", "Bun", "Tauri", "SvelteKit", "Remix",
                "Astro", "Vite", "esbuild", "Turbopack", "pnpm", "Yarn",
                "Edge Computing", "Web3", "Blockchain", "NFT", "DeFi"
            ]
        }
        
        # ファイルに保存
        os.makedirs(os.path.dirname(self.keywords_file), exist_ok=True)
        with open(self.keywords_file, 'w', encoding='utf-8') as f:
            json.dump(keywords, f, ensure_ascii=False, indent=2)
        
        return keywords
    
    def get_all_keywords(self):
        """全キーワードを取得"""
        all_keywords = []
        for category, keywords in self.keywords.items():
            all_keywords.extend(keywords)
        return all_keywords
    
    def get_keywords_by_category(self, category):
        """カテゴリ別キーワードを取得"""
        return self.keywords.get(category, [])
    
    def add_keyword(self, category, keyword):
        """キーワードを追加"""
        if category not in self.keywords:
            self.keywords[category] = []
        
        if keyword not in self.keywords[category]:
            self.keywords[category].append(keyword)
            self._save_keywords()
    
    def _save_keywords(self):
        """キーワードをファイルに保存"""
        with open(self.keywords_file, 'w', encoding='utf-8') as f:
            json.dump(self.keywords, f, ensure_ascii=False, indent=2)