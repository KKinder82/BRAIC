import logging
from pydantic import BaseModel
import uvicorn 

#项目
from src.config import config


# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


if __name__ == "__main__":
    """启动API服务器"""
    uvicorn.run(
        "src.api.base:app",
        host=config.HOST,
        port=config.PORT,
        reload=True,
        log_level=config.LOG_LEVEL,
    )