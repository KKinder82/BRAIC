import logging
from pydantic import BaseModel
from pydantic_core.core_schema import ExpectedSerializationTypes
import uvicorn 

#项目
from services.file_services import schedule_task
from src.config import config
from src.services.exec_services import close_executer


# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    try:
        schedule_task()
    except Exception as e:
        logger.error(f"定时任务启动失败: {e}")
    
    """启动API服务器"""
    uvicorn.run(
        "src.api.base:app",
        host=config.HOST,
        port=config.PORT,
        reload=True,
        log_level=config.LOG_LEVEL,
    )
    close_executer()