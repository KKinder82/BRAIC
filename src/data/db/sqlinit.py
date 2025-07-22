import os
import sys
#项目包
from src.config import config
from src.utils.sqlite_utils import SQLiteUtils


DB_PATH = config.DB_PATH

def init_db():
    db = SQLiteUtils(DB_PATH)
    # 创建文档表
    db.execute("""
        CREATE TABLE IF NOT EXISTS documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            UID varchar(255) NOT NULL,
            title TEXT NOT NULL,
            author TEXT,
            created_at TEXT DEFAULT (datetime('now', 'localtime')),
            updated_at TEXT DEFAULT (datetime('now', 'localtime')),
            download_url TEXT,
            finish_url TEXT,
            status varchar(10) DEFAULT 'init',
            file_size number,
            local_path TEXT,
            hash_code varchar(256)
        )
    """)
    print("数据库初始化完成，文档表已创建。")

if __name__ == "__main__":
    init_db()
