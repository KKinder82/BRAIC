import os
import json
import logging
import datetime
import uuid
from typing import AsyncGenerator, Dict, List, Optional, Any
from pydantic import BaseModel

from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_openai import ChatOpenAI

#项目库
from src.config import config
from src.services.ai.chat_models import ChatCompletionChoice, ChatCompletionRequest, ChatCompletionResponse, ChatMessage
from src.services.ai.llm import llm

logger = logging.getLogger(__name__)


class AIService:
    def _convert_messages_to_langchain(self, messages: List[ChatMessage]) -> List:
        """
        将 OpenAI 格式的消息转换为 LangChain 格式
        """
        langchain_messages = []
        
        for msg in messages:
            if msg.role == "system":
                langchain_messages.append(SystemMessage(content=msg.content))
            elif msg.role == "user":
                langchain_messages.append(HumanMessage(content=msg.content))
            elif msg.role == "assistant":
                langchain_messages.append(AIMessage(content=msg.content))
        
        return langchain_messages
    
    def _convert_langchain_to_openai_format(self, content: str, role: str = "assistant") -> ChatMessage:
        """
        将 LangChain 响应转换为 OpenAI 格式
        """
        return ChatMessage(
            role=role,
            content=content
        )
    
    def _calculate_usage(self, messages: List[ChatMessage], response_content: str) -> Dict[str, int]:
        """
        计算 token 使用量（简化版本）
        """
        # 这里是一个简化的 token 计算，实际项目中可能需要更精确的计算
        prompt_tokens = sum(len(msg.content.split()) for msg in messages)
        completion_tokens = len(response_content.split())
        total_tokens = prompt_tokens + completion_tokens
        
        return {
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": total_tokens
        }
    
    def chat_completion(self, request: ChatCompletionRequest) -> ChatCompletionResponse:
        """
        执行聊天完成请求（非流式）
        """
        try:
            # 验证请求
            self._validate_request(request)
            
            # 转换消息格式
            langchain_messages = self._convert_messages_to_langchain(request.messages)
            
            # 设置生成参数
            generation_kwargs = {
                "temperature": request.temperature,
                # "max_new_tokens": request.max_tokens or 2048,
                "top_p": request.top_p,
                #"repetition_penalty": 1.0 + request.frequency_penalty
            }
            
            # 移除 None 值
            generation_kwargs = {k: v for k, v in generation_kwargs.items() if v is not None}
            
            # 调用 vLLM
            response = llm().invoke(langchain_messages, **generation_kwargs)
            
            # 构建响应
            assistant_message = self._convert_langchain_to_openai_format(response.content)
            
            choice = ChatCompletionChoice(
                index=0,
                message=assistant_message,
                finish_reason="stop"
            )
            
            # 计算使用量
            usage = self._calculate_usage(request.messages, response.content)
            
            return ChatCompletionResponse(
                id=f"chatcmpl-{uuid.uuid4().hex}",
                created=int(datetime.datetime.now().timestamp()),
                model=request.model,
                choices=[choice],
                usage=usage
            )
            
        except Exception as e:
            logger.error(f"AI 服务调用失败: {str(e)}")
            raise e
    
    async def chat_completion_stream(self, request: ChatCompletionRequest) -> AsyncGenerator[str, None]:
        """
        执行流式聊天完成请求
        """
        try:
            # 验证请求
            self._validate_request(request)
            
            # 转换消息格式
            langchain_messages = self._convert_messages_to_langchain(request.messages)
            
            # 设置生成参数
            generation_kwargs = {
                "temperature": request.temperature,
                #"max_new_tokens": request.max_tokens or 2048,
                "top_p": request.top_p,
                #"repetition_penalty": 1.0 + request.frequency_penalty
            }
            
            # 移除 None 值
            generation_kwargs = {k: v for k, v in generation_kwargs.items() if v is not None}
            
            # 生成响应 ID
            response_id = f"chatcmpl-{uuid.uuid4().hex}"
            created_time = int(datetime.datetime.now().timestamp())
            
            # 发送开始标记
            start_chunk = {
                "id": response_id,
                "object": "chat.completion.chunk",
                "created": created_time,
                "model": request.model,
                "choices": [
                    {
                        "index": 0,
                        "delta": {
                            "role": "assistant"
                        },
                        "finish_reason": None
                    }
                ]
            }
            yield f"data: {json.dumps(start_chunk)}\n\n"
            
            # 流式调用 vLLM
            full_response = ""
            async for chunk in llm().astream(langchain_messages, **generation_kwargs):
                if chunk.content:
                    full_response += chunk.content
                    
                    # 发送内容块
                    content_chunk = {
                        "id": response_id,
                        "object": "chat.completion.chunk",
                        "created": created_time,
                        "model": request.model,
                        "choices": [
                            {
                                "index": 0,
                                "delta": {
                                    "content": chunk.content
                                },
                                "finish_reason": None
                            }
                        ]
                    }
                    yield f"data: {json.dumps(content_chunk)}\n\n"
            
            # 发送结束标记
            end_chunk = {
                "id": response_id,
                "object": "chat.completion.chunk",
                "created": created_time,
                "model": request.model,
                "choices": [
                    {
                        "index": 0,
                        "delta": {},
                        "finish_reason": "stop"
                    }
                ]
            }
            yield f"data: {json.dumps(end_chunk)}\n\n"
            
            # 发送结束标记
            yield "data: [DONE]\n\n"
            
        except Exception as e:
            logger.error(f"流式 AI 服务调用失败: {str(e)}")
            # 发送错误信息
            error_chunk = {
                "id": response_id if 'response_id' in locals() else f"chatcmpl-{uuid.uuid4().hex}",
                "object": "chat.completion.chunk",
                "created": created_time if 'created_time' in locals() else int(datetime.datetime.now().timestamp()),
                "model": request.model,
                "choices": [
                    {
                        "index": 0,
                        "delta": {},
                        "finish_reason": "error"
                    }
                ],
                "error": {
                    "message": str(e),
                    "type": "server_error"
                }
            }
            yield f"data: {json.dumps(error_chunk)}\n\n"
            yield "data: [DONE]\n\n"
    
    def _validate_request(self, request: ChatCompletionRequest) -> bool:
        """
        验证请求参数
        """
        if not request.messages:
            raise ValueError("messages 不能为空")
        
        if not request.model:
            raise ValueError("model 不能为空")
        
        # 验证消息格式
        for msg in request.messages:
            if msg.role not in ["system", "user", "assistant"]:
                raise ValueError(f"无效的角色: {msg.role}")
            if not msg.content:
                raise ValueError("消息内容不能为空")
        
        # 验证参数范围
        if request.temperature is not None and (request.temperature < 0 or request.temperature > 2):
            raise ValueError("temperature 必须在 0-2 之间")
        
        if request.top_p is not None and (request.top_p < 0 or request.top_p > 1):
            raise ValueError("top_p 必须在 0-1 之间")
        
        return True

# 创建全局 AI 服务实例
ai_service = AIService()