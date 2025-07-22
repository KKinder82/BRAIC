import os
import sys
import threading
from typing import Any, Dict
import requests
import hashlib
import os

#项目包
from src.config import config
from src.utils.sqlite_utils import SQLiteUtils

DB_PATH = config.DB_PATH
db = SQLiteUtils(DB_PATH)

def download_file(download_url: str, uid: str) -> Any:
    """
    下载文件
    """
    # 获取文件名
    file_name = os.path.basename(download_url)
    # 获取文件后缀
    file_ext = os.path.splitext(file_name)[1]
    # 获取文件名
    file_name = str(uid) + file_ext
    # 获取文件路径
    file_path = os.path.join(config.DOC_PATH, file_name)
    # 如果文件存在，则删除
    if os.path.exists(file_path):
        os.remove(file_path)
    # 下载文件
    response = requests.get(download_url)
    if response.status_code != 200:
        _message = f"下载失败：HTTP {response.status_code} - URL: {download_url}"
        print(_message)
        return False, _message
    
    # 保存文件
    with open(file_path, "wb") as f:
        f.write(response.content)
    return True, file_path

def vectorize_file(file_path: str, doc_id: str, finish_url: str) -> Any:
    """
    向量化文件
    """
    # # 读取文件
    # with open(file_path, "r") as f:
    #     content = f.read()
    # # 向量化文件
    # vector = vectorize_document(content)
    return [131, 33, 12]

def vectorize_document(content: str) -> Any:
    """
    调用 langchain 对文档内容进行向量化
    这里仅作示例，实际请替换为 langchain 的调用
    """
    # TODO: 替换为实际的 langchain 向量化代码
    vector = [0.1, 0.2, 0.3]  # 示例向量
    return vector


def vectorize_document_by_doc(doc: Dict):
    doc_id = doc["id"] # 文档ID
    # 根据 finish_url 下载文件
    download_url = doc["download_url"]
    finish_url = doc["finish_url"]
    # 更新状态为 doing
    db.execute(
        "UPDATE documents SET status='doing' WHERE id=?",
        (doc_id,)
    )
    # 下载文件
    success, message = download_file(download_url, doc_id)
    if success:
        file_path = message
        # 计算文件hash值
        hash_code = hashlib.md5(open(file_path, "rb").read()).hexdigest()
        # 向量化文件
        vector = vectorize_file(file_path, doc_id, finish_url)
        print(f"正在向量化文档ID: {doc_id}")
        # 读取文件大小
        file_size = os.path.getsize(file_path)
        # 更新向量和状态
        db.execute(
            "UPDATE documents SET status='ok', local_path=?, hash_code=?, file_size=? WHERE id=?",
            (file_path, hash_code, file_size, doc_id)
        )
        # 向 finish_url 发送通知
        requests.get(finish_url, params={"success": success, "message": "OK"})
        print(f"文档ID {doc_id} 向量化完成。")
        return True

    # 更新向量和状态
    db.execute(
        "UPDATE documents SET status='failed', status_message=? WHERE id=?",
        (message, doc_id)
    )
    # 向 finish_url 发送通知
    requests.get(finish_url, params={"success": success, "message": message})
    print(f"文档ID {doc_id} 向量化失败。")
    
    return success

def vectorize_document_by_uid(uid: str):
    # 查询 status=0 的文档
    docs = db.fetchall("SELECT id, download_url, finish_url FROM documents WHERE status='init' and UID=? ", (uid,))
    if not docs:
        print("没有需要向量化的文档。")
        return

    for doc in docs:
        vectorize_document_by_doc(doc)

async def vectorize_document_by_uid_async(uid: str):
    # 查询 status=0 的文档
    docs = db.fetchall("SELECT id, download_url, finish_url FROM documents WHERE status='init' and UID=? ", (uid,))
    if not docs:
        print("没有需要向量化的文档。")
        return

    for doc in docs:
        vectorize_document_by_doc(doc)    

def vectorize_documents():
    db = SQLiteUtils(DB_PATH)
    # 查询 status=0 的文档 仅读取 100条
    docs = db.fetchall("SELECT id, download_url, finish_url FROM documents WHERE status='init' limit 100")
    if not docs:
        print("没有需要向量化的文档。")
        return

    for doc in docs:
        vectorize_document_by_doc(doc)


def schedule_task(interval: int = 60):
    """
    定时任务，每 interval 秒执行一次
    """
    def _task():
        vectorize_documents()
        # 下讯下载执行
        threading.Timer(interval, _task).start()
    _task()

def task():
    vectorize_documents()

