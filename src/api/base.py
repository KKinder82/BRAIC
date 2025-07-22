from ast import Str
from fastapi import APIRouter, FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.models import RequestBody
from fastapi.responses import FileResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Any, Dict, Optional
# 项目库
from src.config import config
from src.api.ApiModel import ApiResponse
from src.utils.sqlite_utils import SQLiteUtils


# 创建FastAPI应用实例
app = FastAPI(
    title="BoriAICenter",
    description="博日科技AI服务中心",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生产环境中应该设置具体的域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from src.api.docs.doc import doc_router
app.include_router(doc_router, prefix="", tags=["文档"])

from src.api.ai.chat import ai_chat_router
app.include_router(ai_chat_router, prefix="/v1", tags=["实现 Ai 聊天"])

from src.api.demo import demo_router
app.include_router(demo_router, prefix="/demo", tags=["Demo 示例"])


#静态文件
app.mount("/html", StaticFiles(directory="html"), name="static")

#jinja2 模板
templates = Jinja2Templates(directory="templates/jinja2")

@app.get("/jinja2", response_model=ApiResponse, tags=["Jinja2 模板"])
async def jinja2(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "name": "张三"})

#网址图标
@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return FileResponse("html/favicon.ico")

# 健康检查端点
@app.get("/health", response_model=ApiResponse, tags=["系统"])
async def health_check():
    """健康检查端点"""
    return ApiResponse(
        success=True,
        message="健康检查成功",
        data={}
    )

# 根端点
@app.get("/", response_model=ApiResponse, tags=["系统"])
async def root():
    """API根端点"""
    return ApiResponse(
        success=True,
        message="欢迎访问**博日科技**AI服务中心",
        data={}
    )


# 错误处理
@app.exception_handler(404)
async def http_exception_handler(request: Request, exception: HTTPException):
    return JSONResponse(
        status_code=exception.status_code,
        content={
            "message": "404 服务错误，请查看错误明细。",
            "detail": exception.detail
        },
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request, 
    exc: RequestValidationError
) -> JSONResponse:
    """
    自定义422参数验证错误响应
    """
    # 提取错误详情
    errors: List[Dict[str, Any]] = []
    for error in exc.errors():
        error_info = {
            "field": ".".join(str(loc) for loc in error["loc"]),
            "message": error["msg"],
            "type": error["type"]
        }
        errors.append(error_info)
    
    return ApiResponse(
        success=False,
        messagecode=422,
        message="参数验证失败",
        data={
            "errors": errors,
            "detail": "请检查输入参数是否符合要求"
        }
    ).toJsonResponse()


@app.exception_handler(500)
async def http_exception_handler(request: Request, exception: HTTPException):
    return ApiResponse(
        success=False,
        messagecode=500,
        message="500 服务错误，请联系网络管理员。",
        data={"message": exception.__str__}
    ).toJsonResponse()