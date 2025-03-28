"""
想法管理器模块，处理想法的创建、更新、删除和查询。
"""
import datetime
from typing import Dict, List, Optional, Union

from ..core.config_manager import ConfigManager
from ..core.event_system import EventSystem
from ..data.database_manager import DatabaseManager
from ..data.vector_db_manager import VectorDBManager


class IdeaManager:
    """想法管理器类，处理想法的创建、更新、删除和查询。"""

    def __init__(
        self,
        config_manager: Optional[ConfigManager] = None,
        event_system: Optional[EventSystem] = None,
        database_manager: Optional[DatabaseManager] = None,
        vector_db_manager: Optional[VectorDBManager] = None,
    ):
        """
        初始化想法管理器。

        Args:
            config_manager: 配置管理器实例
            event_system: 事件系统实例
            database_manager: 数据库管理器实例
            vector_db_manager: 向量数据库管理器实例
        """
        self._config_manager = config_manager or ConfigManager()
        self._event_system = event_system or EventSystem()
        self._database_manager = database_manager or DatabaseManager(self._config_manager)
        self._vector_db_manager = vector_db_manager or VectorDBManager(self._config_manager)

    def create_idea(self, content: str, title: Optional[str] = None) -> Dict:
        """
        创建新想法。

        Args:
            content: 想法内容
            title: 想法标题，如果为None则自动生成

        Returns:
            创建的想法字典
        """
        # 如果标题为None，自动生成标题
        if title is None:
            title = self._generate_title(content)

        # 开始事务
        self._database_manager.begin_transaction()

        try:
            # 插入想法
            self._database_manager.execute(
                """
                INSERT INTO Ideas (content, title, created_at, updated_at)
                VALUES (?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                """,
                (content, title),
            )

            # 获取新想法ID
            idea_id = self._database_manager.get_last_row_id()

            # 提交事务
            self._database_manager.commit()

            # 获取新创建的想法
            idea = self.get_idea(idea_id)

            # 如果AI功能已启用且不处于离线模式，添加向量嵌入
            if self._config_manager.is_ai_enabled() and not self._config_manager.is_offline_mode():
                try:
                    self._vector_db_manager.add_idea_embedding(
                        idea_id=idea_id,
                        content=content,
                        metadata={
                            "title": title,
                            "created_at": idea["created_at"],
                            "updated_at": idea["updated_at"],
                            "is_archived": idea["is_archived"],
                            "is_favorite": idea["is_favorite"],
                        },
                    )
                except Exception as e:
                    print(f"添加向量嵌入失败: {e}")

                # 创建AI分析任务
                self._database_manager.execute(
                    """
                    INSERT INTO AITasks (idea_id, task_type, status, created_at)
                    VALUES (?, ?, ?, CURRENT_TIMESTAMP)
                    """,
                    (idea_id, "analyze", "pending"),
                )

            # 发布想法创建事件
            self._event_system.publish("idea_created", {"idea": idea})

            return idea
        except Exception as e:
            # 回滚事务
            self._database_manager.rollback()
            raise e

    def update_idea(
        self,
        idea_id: int,
        content: Optional[str] = None,
        title: Optional[str] = None,
        is_archived: Optional[bool] = None,
        is_favorite: Optional[bool] = None,
        summary: Optional[str] = None,
        importance: Optional[int] = None,
        reminder_date: Optional[datetime.datetime] = None,
    ) -> Dict:
        """
        更新想法。

        Args:
            idea_id: 想法ID
            content: 想法内容
            title: 想法标题
            is_archived: 是否归档
            is_favorite: 是否收藏
            summary: 摘要
            importance: 重要性
            reminder_date: 提醒日期

        Returns:
            更新后的想法字典
        """
        # 获取原始想法
        original_idea = self.get_idea(idea_id)
        if not original_idea:
            raise ValueError(f"想法不存在: {idea_id}")

        # 准备更新字段
        update_fields = []
        params = []

        if content is not None:
            update_fields.append("content = ?")
            params.append(content)

        if title is not None:
            update_fields.append("title = ?")
            params.append(title)

        if is_archived is not None:
            update_fields.append("is_archived = ?")
            params.append(1 if is_archived else 0)

        if is_favorite is not None:
            update_fields.append("is_favorite = ?")
            params.append(1 if is_favorite else 0)

        if summary is not None:
            update_fields.append("summary = ?")
            params.append(summary)

        if importance is not None:
            update_fields.append("importance = ?")
            params.append(importance)

        if reminder_date is not None:
            update_fields.append("reminder_date = ?")
            params.append(reminder_date)

        # 如果没有更新字段，直接返回原始想法
        if not update_fields:
            return original_idea

        # 开始事务
        self._database_manager.begin_transaction()

        try:
            # 更新想法
            query = f"UPDATE Ideas SET {', '.join(update_fields)} WHERE id = ?"
            params.append(idea_id)
            self._database_manager.execute(query, tuple(params))

            # 提交事务
            self._database_manager.commit()

            # 获取更新后的想法
            updated_idea = self.get_idea(idea_id)

            # 如果内容或标题更新了，且AI功能已启用且不处于离线模式，更新向量嵌入
            if (content is not None or title is not None) and self._config_manager.is_ai_enabled() and not self._config_manager.is_offline_mode():
                try:
                    self._vector_db_manager.update_idea_embedding(
                        idea_id=idea_id,
                        content=updated_idea["content"],
                        metadata={
                            "title": updated_idea["title"],
                            "created_at": updated_idea["created_at"],
                            "updated_at": updated_idea["updated_at"],
                            "is_archived": updated_idea["is_archived"],
                            "is_favorite": updated_idea["is_favorite"],
                        },
                    )
                except Exception as e:
                    print(f"更新向量嵌入失败: {e}")

                # 创建AI分析任务
                self._database_manager.execute(
                    """
                    INSERT INTO AITasks (idea_id, task_type, status, created_at)
                    VALUES (?, ?, ?, CURRENT_TIMESTAMP)
                    """,
                    (idea_id, "analyze", "pending"),
                )

            # 发布想法更新事件
            self._event_system.publish("idea_updated", {"idea": updated_idea, "original": original_idea})

            return updated_idea
        except Exception as e:
            # 回滚事务
            self._database_manager.rollback()
            raise e

    def delete_idea(self, idea_id: int) -> bool:
        """
        删除想法。

        Args:
            idea_id: 想法ID

        Returns:
            是否成功删除
        """
        # 获取原始想法
        original_idea = self.get_idea(idea_id)
        if not original_idea:
            return False

        # 开始事务
        self._database_manager.begin_transaction()

        try:
            # 删除想法
            self._database_manager.execute("DELETE FROM Ideas WHERE id = ?", (idea_id,))

            # 提交事务
            self._database_manager.commit()

            # 如果AI功能已启用，删除向量嵌入
            if self._config_manager.is_ai_enabled():
                try:
                    self._vector_db_manager.delete_idea_embedding(idea_id)
                except Exception as e:
                    print(f"删除向量嵌入失败: {e}")

            # 发布想法删除事件
            self._event_system.publish("idea_deleted", {"idea": original_idea})

            return True
        except Exception as e:
            # 回滚事务
            self._database_manager.rollback()
            print(f"删除想法失败: {e}")
            return False

    def get_idea(self, idea_id: int) -> Optional[Dict]:
        """
        获取想法。

        Args:
            idea_id: 想法ID

        Returns:
            想法字典，如果不存在则返回None
        """
        self._database_manager.execute("SELECT * FROM Ideas WHERE id = ?", (idea_id,))
        idea = self._database_manager.fetchone()
        
        if idea:
            # 获取标签
            tags = self.get_idea_tags(idea_id)
            idea["tags"] = tags
            
            # 获取关键词
            keywords = self.get_idea_keywords(idea_id)
            idea["keywords"] = keywords
            
            # 获取关联
            relations = self.get_idea_relations(idea_id)
            idea["relations"] = relations
            
            # 获取提醒
            reminders = self.get_idea_reminders(idea_id)
            idea["reminders"] = reminders
        
        return idea

    def get_ideas(
        self,
        limit: int = 100,
        offset: int = 0,
        sort_by: str = "created_at",
        sort_order: str = "DESC",
        is_archived: Optional[bool] = None,
        is_favorite: Optional[bool] = None,
        tag_ids: Optional[List[int]] = None,
        search_query: Optional[str] = None,
    ) -> List[Dict]:
        """
        获取想法列表。

        Args:
            limit: 限制数量
            offset: 偏移量
            sort_by: 排序字段
            sort_order: 排序顺序
            is_archived: 是否归档
            is_favorite: 是否收藏
            tag_ids: 标签ID列表
            search_query: 搜索查询

        Returns:
            想法字典列表
        """
        # 构建查询
        query = "SELECT * FROM Ideas"
        params = []
        where_clauses = []

        # 添加过滤条件
        if is_archived is not None:
            where_clauses.append("is_archived = ?")
            params.append(1 if is_archived else 0)

        if is_favorite is not None:
            where_clauses.append("is_favorite = ?")
            params.append(1 if is_favorite else 0)

        if tag_ids:
            placeholders = ", ".join(["?"] * len(tag_ids))
            where_clauses.append(f"id IN (SELECT idea_id FROM IdeaTags WHERE tag_id IN ({placeholders}))")
            params.extend(tag_ids)

        if search_query:
            where_clauses.append("(content LIKE ? OR title LIKE ?)")
            search_param = f"%{search_query}%"
            params.append(search_param)
            params.append(search_param)

        # 添加WHERE子句
        if where_clauses:
            query += " WHERE " + " AND ".join(where_clauses)

        # 添加排序
        valid_sort_fields = ["id", "created_at", "updated_at", "importance"]
        valid_sort_orders = ["ASC", "DESC"]
        
        if sort_by not in valid_sort_fields:
            sort_by = "created_at"
        
        if sort_order not in valid_sort_orders:
            sort_order = "DESC"
        
        query += f" ORDER BY {sort_by} {sort_order}"

        # 添加分页
        query += " LIMIT ? OFFSET ?"
        params.append(limit)
        params.append(offset)

        # 执行查询
        self._database_manager.execute(query, tuple(params))
        ideas = self._database_manager.fetchall()

        # 获取每个想法的标签、关键词、关联和提醒
        for idea in ideas:
            idea_id = idea["id"]
            
            # 获取标签
            tags = self.get_idea_tags(idea_id)
            idea["tags"] = tags
            
            # 获取关键词
            keywords = self.get_idea_keywords(idea_id)
            idea["keywords"] = keywords
            
            # 获取关联
            relations = self.get_idea_relations(idea_id)
            idea["relations"] = relations
            
            # 获取提醒
            reminders = self.get_idea_reminders(idea_id)
            idea["reminders"] = reminders

        return ideas

    def search_ideas(self, query: str, limit: int = 10) -> List[Dict]:
        """
        搜索想法。

        Args:
            query: 搜索查询
            limit: 限制数量

        Returns:
            想法字典列表
        """
        # 如果AI功能已启用且不处于离线模式，使用向量搜索
        if self._config_manager.is_ai_enabled() and not self._config_manager.is_offline_mode():
            try:
                # 使用向量搜索
                similar_ideas = self._vector_db_manager.search_similar_ideas(query, n_results=limit)
                
                # 获取完整想法信息
                results = []
                for similar in similar_ideas:
                    idea = self.get_idea(similar["idea_id"])
                    if idea:
                        idea["similarity"] = 1.0 - (similar["distance"] or 0.0)  # 转换距离为相似度
                        results.append(idea)
                
                return results
            except Exception as e:
                print(f"向量搜索失败: {e}")
                # 如果向量搜索失败，回退到关键词搜索
                return self.get_ideas(search_query=query, limit=limit)
        else:
            # 使用关键词搜索
            return self.get_ideas(search_query=query, limit=limit)

    def get_idea_tags(self, idea_id: int) -> List[Dict]:
        """
        获取想法的标签。

        Args:
            idea_id: 想法ID

        Returns:
            标签字典列表
        """
        self._database_manager.execute(
            """
            SELECT t.* FROM Tags t
            JOIN IdeaTags it ON t.id = it.tag_id
            WHERE it.idea_id = ?
            ORDER BY t.name
            """,
            (idea_id,),
        )
        return self._database_manager.fetchall()

    def add_tag_to_idea(self, idea_id: int, tag_id: int) -> bool:
        """
        为想法添加标签。

        Args:
            idea_id: 想法ID
            tag_id: 标签ID

        Returns:
            是否成功添加
        """
        try:
            # 检查关联是否已存在
            self._database_manager.execute(
                "SELECT 1 FROM IdeaTags WHERE idea_id = ? AND tag_id = ?",
                (idea_id, tag_id),
            )
            if self._database_manager.fetchone():
                return True  # 已存在，视为成功

            # 添加关联
            self._database_manager.execute(
                "INSERT INTO IdeaTags (idea_id, tag_id) VALUES (?, ?)",
                (idea_id, tag_id),
            )
            self._database_manager.commit()

            # 获取标签信息
            self._database_manager.execute("SELECT * FROM Tags WHERE id = ?", (tag_id,))
            tag = self._database_manager.fetchone()

            # 发布标签添加事件
            self._event_system.publish("tag_added_to_idea", {"idea_id": idea_id, "tag": tag})

            return True
        except Exception as e:
            print(f"为想法添加标签失败: {e}")
            return False

    def remove_tag_from_idea(self, idea_id: int, tag_id: int) -> bool:
        """
        从想法中移除标签。

        Args:
            idea_id: 想法ID
            tag_id: 标签ID

        Returns:
            是否成功移除
        """
        try:
            # 获取标签信息
            self._database_manager.execute("SELECT * FROM Tags WHERE id = ?", (tag_id,))
            tag = self._database_manager.fetchone()

            # 移除关联
            self._database_manager.execute(
                "DELETE FROM IdeaTags WHERE idea_id = ? AND tag_id = ?",
                (idea_id, tag_id),
            )
            self._database_manager.commit()

            # 发布标签移除事件
            if tag:
                self._event_system.publish("tag_removed_from_idea", {"idea_id": idea_id, "tag": tag})

            return True
        except Exception as e:
            print(f"从想法中移除标签失败: {e}")
            return False

    def get_idea_keywords(self, idea_id: int) -> List[Dict]:
        """
        获取想法的关键词。

        Args:
            idea_id: 想法ID

        Returns:
            关键词字典列表
        """
        self._database_manager.execute(
            "SELECT * FROM Keywords WHERE idea_id = ? ORDER BY weight DESC",
            (idea_id,),
        )
        return self._database_manager.fetchall()

    def get_idea_relations(self, idea_id: int) -> List[Dict]:
        """
        获取想法的关联。

        Args:
            idea_id: 想法ID

        Returns:
            关联字典列表
        """
        self._database_manager.execute(
            """
            SELECT r.*, i.title as target_title FROM Relations r
            JOIN Ideas i ON r.target_idea_id = i.id
            WHERE r.source_idea_id = ?
            ORDER BY r.confidence DESC
            """,
            (idea_id,),
        )
        return self._database_manager.fetchall()

    def get_idea_reminders(self, idea_id: int) -> List[Dict]:
        """
        获取想法的提醒。

        Args:
            idea_id: 想法ID

        Returns:
            提醒字典列表
        """
        self._database_manager.execute(
            "SELECT * FROM Reminders WHERE idea_id = ? ORDER BY reminder_time",
            (idea_id,),
        )
        return self._database_manager.fetchall()

    def add_reminder(self, idea_id: int, reminder_time: datetime.datetime, note: Optional[str] = None) -> Optional[Dict]:
        """
        添加提醒。

        Args:
            idea_id: 想法ID
            reminder_time: 提醒时间
            note: 提醒备注

        Returns:
            添加的提醒字典，如果失败则返回None
        """
        try:
            # 添加提醒
            self._database_manager.execute(
                """
                INSERT INTO Reminders (idea_id, reminder_time, note, created_at)
                VALUES (?, ?, ?, CURRENT_TIMESTAMP)
                """,
                (idea_id, reminder_time, note),
            )
            reminder_id = self._database_manager.get_last_row_id()
            self._database_manager.commit()

            # 获取添加的提醒
            self._database_manager.execute("SELECT * FROM Reminders WHERE id = ?", (reminder_id,))
            reminder = self._database_manager.fetchone()

            # 发布提醒添加事件
            self._event_system.publish("reminder_added", {"reminder": reminder, "idea_id": idea_id})

            return reminder
        except Exception as e:
            print(f"添加提醒失败: {e}")
            return None

    def update_reminder(
        self,
        reminder_id: int,
        reminder_time: Optional[datetime.datetime] = None,
        note: Optional[str] = None,
        is_completed: Optional[bool] = None,
    ) -> Optional[Dict]:
        """
        更新提醒。

        Args:
            reminder_id: 提醒ID
            reminder_time: 提醒时间
            note: 提醒备注
            is_completed: 是否已完成

        Returns:
            更新后的提醒字典，如果失败则返回None
        """
        # 获取原始提醒
        self._database_manager.execute("SELECT * FROM Reminders WHERE id = ?", (reminder_id,))
        original_reminder = self._database_manager.fetchone()
        if not original_reminder:
            return None

        # 准备更新字段
        update_fields = []
        params = []

        if reminder_time is not None:
            update_fields.append("reminder_time = ?")
            params.append(reminder_time)

        if note is not None:
            update_fields.append("note = ?")
            params.append(note)

        if is_completed is not None:
            update_fields.append("is_completed = ?")
            params.append(1 if is_completed else 0)

        # 如果没有更新字段，直接返回原始提醒
        if not update_fields:
            return original_reminder

        try:
            # 更新提醒
            query = f"UPDATE Reminders SET {', '.join(update_fields)} WHERE id = ?"
            params.append(reminder_id)
            self._database_manager.execute(query, tuple(params))
            self._database_manager.commit()

            # 获取更新后的提醒
            self._database_manager.execute("SELECT * FROM Reminders WHERE id = ?", (reminder_id,))
            updated_reminder = self._database_manager.fetchone()

            # 发布提醒更新事件
            self._event_system.publish(
                "reminder_updated",
                {"reminder": updated_reminder, "original": original_reminder, "idea_id": original_reminder["idea_id"]},
            )

            return updated_reminder
        except Exception as e:
            print(f"更新提醒失败: {e}")
            return None

    def delete_reminder(self, reminder_id: int) -> bool:
        """
        删除提醒。

        Args:
            reminder_id: 提醒ID

        Returns:
            是否成功删除
        """
        # 获取原始提醒
        self._database_manager.execute("SELECT * FROM Reminders WHERE id = ?", (reminder_id,))
        original_reminder = self._database_manager.fetchone()
        if not original_reminder:
            return False

        try:
            # 删除提醒
            self._database_manager.execute("DELETE FROM Reminders WHERE id = ?", (reminder_id,))
            self._database_manager.commit()

            # 发布提醒删除事件
            self._event_system.publish(
                "reminder_deleted",
                {"reminder": original_reminder, "idea_id": original_reminder["idea_id"]},
            )

            return True
        except Exception as e:
            print(f"删除提醒失败: {e}")
            return False

    def get_due_reminders(self) -> List[Dict]:
        """
        获取到期提醒。

        Returns:
            到期提醒字典列表
        """
        self._database_manager.execute(
            """
            SELECT r.*, i.title as idea_title FROM Reminders r
            JOIN Ideas i ON r.idea_id = i.id
            WHERE r.reminder_time <= CURRENT_TIMESTAMP AND r.is_completed = 0
            ORDER BY r.reminder_time
            """
        )
        return self._database_manager.fetchall()

    def _generate_title(self, content: str) -> str:
        """
        根据内容生成标题。

        Args:
            content: 想法内容

        Returns:
            生成的标题
        """
        # 简单实现：使用内容的前20个字符作为标题
        title = content[:20].strip()
        if len(content) > 20:
            title += "..."
        return title
