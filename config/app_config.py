import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class AppConfig:
    """应用配置类"""
    # 应用基本配置
    APP_NAME = "LangConverter"
    APP_VERSION = "1.0.0"
    DEBUG = os.getenv("DEBUG", "True").lower() == "true"
    
    # Web服务器配置
    HOST = os.getenv("HOST", "127.0.0.1")
    PORT = int(os.getenv("PORT", "5000"))
    
    # 日志配置
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE = os.getenv("LOG_FILE", "logs/app.log")