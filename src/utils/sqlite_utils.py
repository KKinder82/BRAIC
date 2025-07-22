import sqlite3
from typing import Any, List, Tuple, Dict, Optional

class SQLiteUtils:
    def __init__(self, db_path: str):
        """
        初始化数据库工具类
        :param db_path: 数据库文件路径
        """
        self.db_path = db_path

    def _get_conn(self):
        """获取数据库连接"""
        return sqlite3.connect(self.db_path)

    def execute(self, sql: str, params: Optional[Tuple[Any, ...]] = None) -> None:
        """
        执行单条SQL语句（无返回结果，如建表、插入、更新、删除）
        :param sql: SQL语句
        :param params: 参数元组
        """
        with self._get_conn() as conn:
            cursor = conn.cursor()
            if params:
                cursor.execute(sql, params)
            else:
                cursor.execute(sql)
            conn.commit()

    def executemany(self, sql: str, param_list: List[Tuple[Any, ...]]) -> None:
        """
        批量执行SQL语句
        :param sql: SQL语句
        :param param_list: 参数列表
        """
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.executemany(sql, param_list)
            conn.commit()

    def fetchone(self, sql: str, params: Optional[Tuple[Any, ...]] = None) -> Optional[Dict[str, Any]]:
        """
        查询单条记录
        :param sql: SQL语句
        :param params: 参数元组
        :return: 单条记录（字典），无结果返回None
        """
        with self._get_conn() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(sql, params or ())
            row = cursor.fetchone()
            return dict(row) if row else None

    def fetchall(self, sql: str, params: Optional[Tuple[Any, ...]] = None) -> List[Dict[str, Any]]:
        """
        查询多条记录
        :param sql: SQL语句
        :param params: 参数元组
        :return: 记录列表（每条为字典）
        """
        with self._get_conn() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(sql, params or ())
            rows = cursor.fetchall()
            return [dict(row) for row in rows]

    def table_exists(self, table_name: str) -> bool:
        """
        判断表是否存在
        :param table_name: 表名
        :return: True/False
        """
        sql = "SELECT count(*) FROM sqlite_master WHERE type='table' AND name=?"
        result = self.fetchone(sql, (table_name,))
        return result is not None and list(result.values())[0] > 0
