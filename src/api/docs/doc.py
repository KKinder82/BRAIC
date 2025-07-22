import asyncio
import urllib
from fastapi import APIRouter

#项目库
from src.config import config
from src.utils.sqlite_utils import SQLiteUtils
from src.api.ApiModel import ApiResponse
from src.services.file_services import vectorize_document_by_uid
from src.services.exec_services import run_async

doc_router = APIRouter()

@doc_router.get("/docVector", response_model=ApiResponse, tags=["文件向量化"])
async def docVector(docid: str, filename: str, filesize: str, downloadUrl: str, finishUrl: str):
    # 向数据库中插入文件信息
    db = SQLiteUtils(config.DB_PATH)
    # 对 downloadUrl 进行URL解码
    _downloadUrl = urllib.parse.unquote(downloadUrl)
    _finishUrl = urllib.parse.unquote(finishUrl)
    # 根据docid查询文件是否存在
    file = db.fetchone("SELECT * FROM documents WHERE UID=?", (docid,))
    if file:
        return ApiResponse(
            success=False,
            message="文件已存在，请勿重复上传",
            data={}
        )
    #插入文件信息
    db.execute("INSERT INTO documents (UID, title, download_url, finish_url, status, file_size) VALUES (?, ?, ?, ?, ?, ?)"
        , (docid, filename, downloadUrl, finishUrl, "init", filesize))
    
    #向量化服务发送请求
    run_async(vectorize_document_by_uid, docid)
    
    """文件向量化"""
    return ApiResponse(
        success=True,
        message="文件向量化调用成功",
        data={}
    )


@doc_router.get("/finish", response_model=ApiResponse, tags=["路由测试"])
async def finish(success: bool, message: str):
    return ApiResponse(
        success=success,
        message=message,
        data={}
    )


@doc_router.get("/docHealth", response_model=ApiResponse, tags=["路由测试"])
async def test():
    return ApiResponse(
        success=True,
        message="路由测试成功",
        data={}
    )

