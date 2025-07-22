import os

class Config:
    # 数据库文件路径
    DB_PATH = os.environ.get(
        "DB_PATH",
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "db", "sqlite.db")
    )

    # 日志配置
    LOG_LEVEL = os.environ.get("LOG_LEVEL", "info") # 日志级别 默认info 可选debug info warning error critical
    LOG_FILE = os.environ.get("LOG_FILE", "app.log")

    # FastAPI 配置
    API_TITLE = os.environ.get("API_TITLE", "BoriAICenter")
    API_DESC = os.environ.get("API_DESC", "博日科技AI服务中心")
    API_VERSION = os.environ.get("API_VERSION", "1.0.0")
    DEBUG = os.environ.get("DEBUG", "true").lower() == "true"
    HOST = os.environ.get("HOST", "0.0.0.0")
    PORT = int(os.environ.get("PORT", 8000))

    # 文件路径
    DOC_PATH = os.environ.get("DOC_PATH", os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "docs"))

    # vLLM 配置
    #AI_URL = os.environ.get("AI_URL", "http://ds.kaoxve.com:9999/v1")
    AI_URL = os.environ.get("AI_URL", "http://192.168.91.210:8000/v1")
    AI_MODEL = os.environ.get("AI_MODEL", "Qwen3-32B")
    AI_KEY = os.environ.get("AI_KEY", "bori-qwen3-2012")
   
    # 其它自定义配置可在此添加

config = Config()
