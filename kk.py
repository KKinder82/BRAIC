from src.data.db.sqlinit import init_db
from src.utils.sqlite_utils import SQLiteUtils
from src.config import config
from src.services.file_services import task

if __name__ == "__main__":
    # init_db()
    # db = SQLiteUtils(config.DB_PATH)
    # print(config.DB_PATH)
    # file = db.fetchone("SELECT * FROM documents WHERE UID=?", ("123",))
    # print(file)

    task()
    print("任务已启动")

