
from langchain_openai import ChatOpenAI
from src.config import config
import logging

logger = logging.getLogger(__name__)

_llm = None
def llm():
    global _llm
    if _llm is None:
        try:
            _llm = ChatOpenAI(
                base_url=config.AI_URL,
                model=config.AI_MODEL,
                api_key=config.AI_KEY
            )
            logger.info(f"vLLM 客户端初始化成功，模型: {config.AI_MODEL}")
        except Exception as e:
            logger.error(f"vLLM 客户端初始化失败: {str(e)}")
            raise e
    return _llm

    
