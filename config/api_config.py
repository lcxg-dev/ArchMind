import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class APIConfig:
    """API配置类"""
    # DeepSeek API配置
    DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
    DEEPSEEK_API_BASE = os.getenv("DEEPSEEK_API_BASE", "https://api.deepseek.com")
    DEEPSEEK_MODEL = os.getenv("DEEPSEEK_MODEL", "deepseek-coder-v2")
    
    # API请求配置
    TIMEOUT = int(os.getenv("API_TIMEOUT", "30"))
    MAX_RETRIES = int(os.getenv("API_MAX_RETRIES", "3"))
    
    # 请求头配置
    HEADERS = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}"
    }