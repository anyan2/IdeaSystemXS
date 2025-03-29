"""
数据库管理器模块，负责管理SQLite数据库连接和操作。
"""
import os
import sqlite3
import threading
from typing import Any, Dict, List, Optional, Tuple, Union

from src.core.config_manager import ConfigManager


class DatabaseManager:
    """数据库管理器类，负责管理SQLite数据库连接和操作。"""

    _instance = None
    _lock = threading.Lock()

    def __new__(cls, config_manager: Optional[ConfigManager] = None):
        """
        实现单例模式。

        Args:
            config_manager: 配置管理器实例

        Returns:
            DatabaseManager实例
        """
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(DatabaseManager, cls).__new__(cls)
                cls._instance._initialized = False
            return cls._instance

    def __init__(self, config_manager: Optional[ConfigManager] = None):
        """
        初始化数据库管理器。

        Args:
            config_manager: 配置管理器实例
        """
        if self._initialized:
            return

        self._config_manager = config_manager or ConfigManager()
        self._db_path = self._config_manager.get_sqlite_path()
        self._connection = None
        self._cursor = None
        self._local = threading.local()
        self._initialized = True

        # 确保数据库目录存在
        os.makedirs(os.path.dirname(self._db_path), exist_ok=True)

        # 初始化数据库
        self._init_database()

    def _get_connection(self) -> sqlite3.Connection:
        """
        获取数据库连接。

        Returns:
            数据库连接
        """
        if not hasattr(self._local, "connection") or self._local.connection is None:
            self._local.connection = sqlite3.connect(
                self._db_path, 
                detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES
            )
            self._local.connection.row_factory = sqlite3.Row
        return self._local.connection

    def _get_cursor(self) -> sqlite3.Cursor:
        """
        获取数据库游标。

        Returns:
            数据库游标
        """
        if not hasattr(self._local, "cursor") or self._local.cursor is None:
            self._local.cursor = self._get_connection().cursor()
        return self._local.cursor

    def _init_database(self) -> None:
        """初始化数据库，创建表结构。"""
        # 创建Ideas表
        self.execute("""
            CREATE TABLE IF NOT EXISTS Ideas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content TEXT NOT NULL,
                title TEXT,
                created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                is_archived BOOLEAN NOT NULL DEFAULT 0,
                is_favorite BOOLEAN NOT NULL DEFAULT 0,
                ai_processed BOOLEAN NOT NULL DEFAULT 0,
                summary TEXT,
                importance INTEGER DEFAULT 3,
                reminder_date TIMESTAMP
            )
        """)

        # 创建Tags表
        self.execute("""
            CREATE TABLE IF NOT EXISTS Tags (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                color TEXT DEFAULT '#808080',
                created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 创建IdeaTags表
        self.execute("""
            CREATE TABLE IF NOT EXISTS IdeaTags (
                idea_id INTEGER NOT NULL,
                tag_id INTEGER NOT NULL,
                PRIMARY KEY (idea_id, tag_id),
                FOREIGN KEY (idea_id) REFERENCES Ideas(id) ON DELETE CASCADE,
                FOREIGN KEY (tag_id) REFERENCES Tags(id) ON DELETE CASCADE
            )
        """)

        # 创建Relations表
        self.execute("""
            CREATE TABLE IF NOT EXISTS Relations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_idea_id INTEGER NOT NULL,
                target_idea_id INTEGER NOT NULL,
                relation_type TEXT NOT NULL,
                confidence REAL NOT NULL,
                created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (source_idea_id) REFERENCES Ideas(id) ON DELETE CASCADE,
                FOREIGN KEY (target_idea_id) REFERENCES Ideas(id) ON DELETE CASCADE
            )
        """)

        # 创建Keywords表
        self.execute("""
            CREATE TABLE IF NOT EXISTS Keywords (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                idea_id INTEGER NOT NULL,
                keyword TEXT NOT NULL,
                weight REAL NOT NULL,
                FOREIGN KEY (idea_id) REFERENCES Ideas(id) ON DELETE CASCADE
            )
        """)

        # 创建Settings表
        self.execute("""
            CREATE TABLE IF NOT EXISTS Settings (
                key TEXT PRIMARY KEY,
                value TEXT,
                updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 创建AITasks表
        self.execute("""
            CREATE TABLE IF NOT EXISTS AITasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                idea_id INTEGER,
                task_type TEXT NOT NULL,
                status TEXT NOT NULL,
                created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                processed_at TIMESTAMP,
                result TEXT,
                error TEXT,
                FOREIGN KEY (idea_id) REFERENCES Ideas(id) ON DELETE CASCADE
            )
        """)

        # 创建Reminders表
        self.execute("""
            CREATE TABLE IF NOT EXISTS Reminders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                idea_id INTEGER NOT NULL,
                reminder_time TIMESTAMP NOT NULL,
                is_completed BOOLEAN NOT NULL DEFAULT 0,
                note TEXT,
                created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (idea_id) REFERENCES Ideas(id) ON DELETE CASCADE
            )
        """)

        # 创建索引
        self.execute("CREATE INDEX IF NOT EXISTS idx_ideas_created_at ON Ideas(created_at)")
        self.execute("CREATE INDEX IF NOT EXISTS idx_ideas_updated_at ON Ideas(updated_at)")
        self.execute("CREATE INDEX IF NOT EXISTS idx_ideas_is_archived ON Ideas(is_archived)")
        self.execute("CREATE INDEX IF NOT EXISTS idx_ideas_is_favorite ON Ideas(is_favorite)")
        self.execute("CREATE INDEX IF NOT EXISTS idx_ideas_ai_processed ON Ideas(ai_processed)")
        self.execute("CREATE INDEX IF NOT EXISTS idx_ideas_reminder_date ON Ideas(reminder_date)")
        self.execute("CREATE INDEX IF NOT EXISTS idx_keywords_idea_id ON Keywords(idea_id)")
        self.execute("CREATE INDEX IF NOT EXISTS idx_keywords_keyword ON Keywords(keyword)")
        self.execute("CREATE INDEX IF NOT EXISTS idx_relations_source_idea_id ON Relations(source_idea_id)")
        self.execute("CREATE INDEX IF NOT EXISTS idx_relations_target_idea_id ON Relations(target_idea_id)")
        self.execute("CREATE INDEX IF NOT EXISTS idx_reminders_idea_id ON Reminders(idea_id)")
        self.execute("CREATE INDEX IF NOT EXISTS idx_reminders_reminder_time ON Reminders(reminder_time)")
        self.execute("CREATE INDEX IF NOT EXISTS idx_reminders_is_completed ON Reminders(is_completed)")

        # 创建触发器
        self.execute("""
            CREATE TRIGGER IF NOT EXISTS update_ideas_timestamp 
            AFTER UPDATE ON Ideas
            FOR EACH ROW
            BEGIN
                UPDATE Ideas SET updated_at = CURRENT_TIMESTAMP WHERE id = OLD.id;
            END
        """)

        self.execute("""
            CREATE TRIGGER IF NOT EXISTS update_settings_timestamp 
            AFTER UPDATE ON Settings
            FOR EACH ROW
            BEGIN
                UPDATE Settings SET updated_at = CURRENT_TIMESTAMP WHERE key = OLD.key;
            END
        """)

        # 提交更改
        self.commit()

    def execute(self, query: str, params: Union[Tuple, Dict, None] = None) -> sqlite3.Cursor:
        """
        执行SQL查询。

        Args:
            query: SQL查询语句
            params: 查询参数

        Returns:
            数据库游标
        """
        cursor = self._get_cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        return cursor

    def executemany(self, query: str, params_list: List[Union[Tuple, Dict]]) -> sqlite3.Cursor:
        """
        执行多个SQL查询。

        Args:
            query: SQL查询语句
            params_list: 查询参数列表

        Returns:
            数据库游标
        """
        cursor = self._get_cursor()
        cursor.executemany(query, params_list)
        return cursor

    def commit(self) -> None:
        """提交事务。"""
        if hasattr(self._local, "connection") and self._local.connection:
            self._local.connection.commit()

    def rollback(self) -> None:
        """回滚事务。"""
        if hasattr(self._local, "connection") and self._local.connection:
            self._local.connection.rollback()

    def close(self) -> None:
        """关闭数据库连接。"""
        if hasattr(self._local, "cursor") and self._local.cursor:
            self._local.cursor.close()
            self._local.cursor = None

        if hasattr(self._local, "connection") and self._local.connection:
            self._local.connection.close()
            self._local.connection = None

    def fetchone(self) -> Optional[Dict[str, Any]]:
        """
        获取一条记录。

        Returns:
            记录字典
        """
        cursor = self._get_cursor()
        row = cursor.fetchone()
        if row:
            return dict(row)
        return None

    def fetchall(self) -> List[Dict[str, Any]]:
        """
        获取所有记录。

        Returns:
            记录字典列表
        """
        cursor = self._get_cursor()
        rows = cursor.fetchall()
        return [dict(row) for row in rows]

    def fetchmany(self, size: int) -> List[Dict[str, Any]]:
        """
        获取多条记录。

        Args:
            size: 记录数量

        Returns:
            记录字典列表
        """
        cursor = self._get_cursor()
        rows = cursor.fetchmany(size)
        return [dict(row) for row in rows]

    def get_last_row_id(self) -> int:
        """
        获取最后插入的行ID。

        Returns:
            行ID
        """
        return self._get_cursor().lastrowid

    def table_exists(self, table_name: str) -> bool:
        """
        检查表是否存在。

        Args:
            table_name: 表名

        Returns:
            表是否存在
        """
        cursor = self.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
            (table_name,)
        )
        return cursor.fetchone() is not None

    def begin_transaction(self) -> None:
        """开始事务。"""
        self.execute("BEGIN TRANSACTION")

    def end_transaction(self) -> None:
        """结束事务。"""
        self.commit()

    def backup_database(self, backup_path: Optional[str] = None) -> str:
        """
        备份数据库。

        Args:
            backup_path: 备份路径，如果为None则使用默认路径

        Returns:
            备份文件路径
        """
        import shutil
        import datetime

        if backup_path is None:
            backup_dir = self._config_manager.get("database", "backup_dir")
            os.makedirs(backup_dir, exist_ok=True)
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = os.path.join(backup_dir, f"ideas_backup_{timestamp}.db")

        # 关闭当前连接
        self.close()

        # 复制数据库文件
        shutil.copy2(self._db_path, backup_path)

        # 重新连接数据库
        self._get_connection()

        return backup_path

    def restore_database(self, backup_path: str) -> bool:
        """
        从备份恢复数据库。

        Args:
            backup_path: 备份路径

        Returns:
            是否成功
        """
        import shutil

        if not os.path.exists(backup_path):
            return False

        # 关闭当前连接
        self.close()

        # 复制备份文件到数据库文件
        shutil.copy2(backup_path, self._db_path)

        # 重新连接数据库
        self._get_connection()

        return True

    def get_db_path(self) -> str:
        """
        获取数据库路径。

        Returns:
            数据库路径
        """
        return self._db_path

    def get_db_size(self) -> int:
        """
        获取数据库大小。

        Returns:
            数据库大小（字节）
        """
        return os.path.getsize(self._db_path) if os.path.exists(self._db_path) else 0

    def vacuum(self) -> None:
        """压缩数据库。"""
        self.execute("VACUUM")
        self.commit()
