"""
标签管理器模块，管理标签的创建、更新和关联。
"""
from typing import Dict, List, Optional

from src.core.config_manager import ConfigManager
from src.core.event_system import EventSystem
from src.data.database_manager import DatabaseManager


class TagManager:
    """标签管理器类，管理标签的创建、更新和关联。"""

    def __init__(
        self,
        config_manager: Optional[ConfigManager] = None,
        event_system: Optional[EventSystem] = None,
        database_manager: Optional[DatabaseManager] = None,
    ):
        """
        初始化标签管理器。

        Args:
            config_manager: 配置管理器实例
            event_system: 事件系统实例
            database_manager: 数据库管理器实例
        """
        self._config_manager = config_manager or ConfigManager()
        self._event_system = event_system or EventSystem()
        self._database_manager = database_manager or DatabaseManager(self._config_manager)

    def create_tag(self, name: str, color: str = "#808080") -> Optional[Dict]:
        """
        创建新标签。

        Args:
            name: 标签名称
            color: 标签颜色（十六进制）

        Returns:
            创建的标签字典，如果失败则返回None
        """
        try:
            # 检查标签是否已存在
            self._database_manager.execute("SELECT * FROM Tags WHERE name = ?", (name,))
            existing_tag = self._database_manager.fetchone()
            if existing_tag:
                return existing_tag

            # 插入标签
            self._database_manager.execute(
                """
                INSERT INTO Tags (name, color, created_at)
                VALUES (?, ?, CURRENT_TIMESTAMP)
                """,
                (name, color),
            )
            tag_id = self._database_manager.get_last_row_id()
            self._database_manager.commit()

            # 获取新创建的标签
            self._database_manager.execute("SELECT * FROM Tags WHERE id = ?", (tag_id,))
            tag = self._database_manager.fetchone()

            # 发布标签创建事件
            self._event_system.publish("tag_created", {"tag": tag})

            return tag
        except Exception as e:
            print(f"创建标签失败: {e}")
            return None

    def update_tag(self, tag_id: int, name: Optional[str] = None, color: Optional[str] = None) -> Optional[Dict]:
        """
        更新标签。

        Args:
            tag_id: 标签ID
            name: 标签名称
            color: 标签颜色（十六进制）

        Returns:
            更新后的标签字典，如果失败则返回None
        """
        # 获取原始标签
        self._database_manager.execute("SELECT * FROM Tags WHERE id = ?", (tag_id,))
        original_tag = self._database_manager.fetchone()
        if not original_tag:
            return None

        # 准备更新字段
        update_fields = []
        params = []

        if name is not None:
            update_fields.append("name = ?")
            params.append(name)

        if color is not None:
            update_fields.append("color = ?")
            params.append(color)

        # 如果没有更新字段，直接返回原始标签
        if not update_fields:
            return original_tag

        try:
            # 更新标签
            query = f"UPDATE Tags SET {', '.join(update_fields)} WHERE id = ?"
            params.append(tag_id)
            self._database_manager.execute(query, tuple(params))
            self._database_manager.commit()

            # 获取更新后的标签
            self._database_manager.execute("SELECT * FROM Tags WHERE id = ?", (tag_id,))
            updated_tag = self._database_manager.fetchone()

            # 发布标签更新事件
            self._event_system.publish("tag_updated", {"tag": updated_tag, "original": original_tag})

            return updated_tag
        except Exception as e:
            print(f"更新标签失败: {e}")
            return None

    def delete_tag(self, tag_id: int) -> bool:
        """
        删除标签。

        Args:
            tag_id: 标签ID

        Returns:
            是否成功删除
        """
        # 获取原始标签
        self._database_manager.execute("SELECT * FROM Tags WHERE id = ?", (tag_id,))
        original_tag = self._database_manager.fetchone()
        if not original_tag:
            return False

        try:
            # 删除标签
            self._database_manager.execute("DELETE FROM Tags WHERE id = ?", (tag_id,))
            self._database_manager.commit()

            # 发布标签删除事件
            self._event_system.publish("tag_deleted", {"tag": original_tag})

            return True
        except Exception as e:
            print(f"删除标签失败: {e}")
            return False

    def get_tag(self, tag_id: int) -> Optional[Dict]:
        """
        获取标签。

        Args:
            tag_id: 标签ID

        Returns:
            标签字典，如果不存在则返回None
        """
        self._database_manager.execute("SELECT * FROM Tags WHERE id = ?", (tag_id,))
        return self._database_manager.fetchone()

    def get_tag_by_name(self, name: str) -> Optional[Dict]:
        """
        根据名称获取标签。

        Args:
            name: 标签名称

        Returns:
            标签字典，如果不存在则返回None
        """
        self._database_manager.execute("SELECT * FROM Tags WHERE name = ?", (name,))
        return self._database_manager.fetchone()

    def get_all_tags(self) -> List[Dict]:
        """
        获取所有标签。

        Returns:
            标签字典列表
        """
        self._database_manager.execute("SELECT * FROM Tags ORDER BY name")
        return self._database_manager.fetchall()

    def get_tags_with_idea_count(self) -> List[Dict]:
        """
        获取所有标签及其关联的想法数量。

        Returns:
            标签字典列表，每个字典包含idea_count字段
        """
        self._database_manager.execute(
            """
            SELECT t.*, COUNT(it.idea_id) as idea_count
            FROM Tags t
            LEFT JOIN IdeaTags it ON t.id = it.tag_id
            GROUP BY t.id
            ORDER BY t.name
            """
        )
        return self._database_manager.fetchall()

    def get_ideas_by_tag(self, tag_id: int, limit: int = 100, offset: int = 0) -> List[Dict]:
        """
        获取标签关联的想法。

        Args:
            tag_id: 标签ID
            limit: 限制数量
            offset: 偏移量

        Returns:
            想法字典列表
        """
        self._database_manager.execute(
            """
            SELECT i.* FROM Ideas i
            JOIN IdeaTags it ON i.id = it.idea_id
            WHERE it.tag_id = ?
            ORDER BY i.created_at DESC
            LIMIT ? OFFSET ?
            """,
            (tag_id, limit, offset),
        )
        return self._database_manager.fetchall()

    def get_or_create_tag(self, name: str, color: str = "#808080") -> Optional[Dict]:
        """
        获取或创建标签。

        Args:
            name: 标签名称
            color: 标签颜色（十六进制）

        Returns:
            标签字典，如果失败则返回None
        """
        # 尝试获取标签
        tag = self.get_tag_by_name(name)
        if tag:
            return tag

        # 创建标签
        return self.create_tag(name, color)
