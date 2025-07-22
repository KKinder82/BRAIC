from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse, StreamingResponse
import uuid
import logging
import json

from src.api.ApiModel import ApiResponse
from src.config import config
from src.services.ai.chat_service import ChatCompletionRequest, ai_service
from src.utils.kkutils import timestamp

logger = logging.getLogger(__name__)

ai_chat_router = APIRouter()

@ai_chat_router.post("/chat/completions", tags=["AI"])
async def chat_completions(request: Request):
    """
    AI 聊天完成接口，与 OpenAI /v1/chat/completions 兼容
    支持流式和非流式调用
    """
    try:
        # API 请求头
        if config.AI_KEY:
            api_key = request.headers.get("Authorization")
            if api_key != "Bearer " + config.AI_KEY:
                raise ValueError("API_Key 验证失败")
        
        # 解析请求体
        body = await request.json()
        
        # 构建请求对象
        chat_request = ChatCompletionRequest(**body)
        
        # 检查是否为流式请求
        if chat_request.stream:
            # 流式响应
            async def generate_stream():
                async for chunk in ai_service.chat_completion_stream(chat_request):
                    yield chunk
            
            return StreamingResponse(
                generate_stream(),
                media_type="text/plain",
                headers={
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive",
                    "Content-Type": "text/event-stream",
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Headers": "*"
                }
            )
        else:
            # 非流式响应
            response = ai_service.chat_completion(chat_request)
            
            # 返回响应
            return JSONResponse(
                status_code=200,
                content=response.dict(exclude_none=True)
            )
        
    except ValueError as e:
        _message = f"请求参数验证失败: {str(e)}"
        logger.error(_message)
        return ApiResponse(
            success=False,
            message=_message,
            messagecode=400,
            data={}
        )
    except Exception as e:
        _message = f"AI 聊天调用失败: {str(e)}"
        logger.error(_message)
        return ApiResponse(
            success=False,
            message=_message,
            messagecode=500,
            data={}
        )

@ai_chat_router.get("/completions", response_model=ApiResponse, tags=["AI"])
async def completions(request: Request):
    """
    保持原有的 GET 接口兼容性
    """
    return ApiResponse(
        success=True,
        message="AI 聊天调用成功",
        data={}
    )

@ai_chat_router.get("/models", tags=["AI"])
async def list_models():
    """
    列出可用的模型
    """
    try:
        models = [
            {
                "id": "Qwen3-32B",
                "object": "model",
                "created": timestamp(),
                "owned_by": "vllm"
            },
        ]
        
        return JSONResponse(
            status_code=200,
            content={
                "object": "list",
                "data": models
            }
        )
    except Exception as e:
        logger.error(f"获取模型列表失败: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={
                "error": {
                    "message": "获取模型列表失败",
                    "type": "server_error",
                    "code": "internal_error"
                }
            }
        )