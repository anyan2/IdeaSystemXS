"""
搜索引擎模块，提供基于关键词和向量的搜索功能。
"""
from typing import Dict, List, Optional, Union

from ..core.config_manager import ConfigManager
from ..core.event_system import EventSystem
from ..data.database_manager import DatabaseManager
from ..data.vector_db_manager import VectorDBManager
from .idea_manager import IdeaManager


class SearchEngine:
    """搜索引擎类，提供基于关键词和向量的搜索功能。"""

    def __init__(
        self,
        config_manager: Optional[ConfigManager] = None,
        event_system: Optional[EventSystem] = None,
        database_manager: Optional[DatabaseManager] = None,
        vector_db_manager: Optional[VectorDBManager] = None,
        idea_manager: Optional[IdeaManager] = None,
    ):
        """
        初始化搜索引擎。

        Args:
            config_manager: 配置管理器实例
            event_system: 事件系统实例
            database_manager: 数据库管理器实例
            vector_db_manager: 向量数据库管理器实例
            idea_manager: 想法管理器实例
        """
        self._config_manager = config_manager or ConfigManager()
        self._event_system = event_system or EventSystem()
        self._database_manager = database_manager or DatabaseManager(self._config_manager)
        self._vector_db_manager = vector_db_manager or VectorDBManager(self._config_manager)
        self._idea_manager = idea_manager or IdeaManager(
            self._config_manager, self._event_system, self._database_manager, self._vector_db_manager
        )

    def search(
        self,
        query: str,
        search_type: str = "hybrid",
        limit: int = 10,
        offset: int = 0,
        filters: Optional[Dict] = None,
    ) -> List[Dict]:
        """
        搜索想法。

        Args:
            query: 搜索查询
            search_type: 搜索类型，可选值：keyword（关键词搜索）、vector（向量搜索）、hybrid（混合搜索）
            limit: 限制数量
            offset: 偏移量
            filters: 过滤条件

        Returns:
            想法字典列表
        """
        if not query:
            return []

        # 准备过滤条件
        if filters is None:
            filters = {}

        # 根据搜索类型执行搜索
        if search_type == "keyword":
            return self._keyword_search(query, limit, offset, filters)
        elif search_type == "vector":
            return self._vector_search(query, limit, offset, filters)
        else:  # hybrid
            return self._hybrid_search(query, limit, offset, filters)

    def _keyword_search(self, query: str, limit: int, offset: int, filters: Dict) -> List[Dict]:
        """
        关键词搜索。

        Args:
            query: 搜索查询
            limit: 限制数量
            offset: 偏移量
            filters: 过滤条件

        Returns:
            想法字典列表
        """
        # 构建查询
        sql_query = """
            SELECT i.* FROM Ideas i
            WHERE (i.content LIKE ? OR i.title LIKE ?)
        """
        params = [f"%{query}%", f"%{query}%"]

        # 添加过滤条件
        if "is_archived" in filters:
            sql_query += " AND i.is_archived = ?"
            params.append(1 if filters["is_archived"] else 0)

        if "is_favorite" in filters:
            sql_query += " AND i.is_favorite = ?"
            params.append(1 if filters["is_favorite"] else 0)

        if "tag_ids" in filters and filters["tag_ids"]:
            tag_ids = filters["tag_ids"]
            placeholders = ", ".join(["?"] * len(tag_ids))
            sql_query += f" AND i.id IN (SELECT idea_id FROM IdeaTags WHERE tag_id IN ({placeholders}))"
            params.extend(tag_ids)

        # 添加排序和分页
        sql_query += " ORDER BY i.created_at DESC LIMIT ? OFFSET ?"
        params.append(limit)
        params.append(offset)

        # 执行查询
        self._database_manager.execute(sql_query, tuple(params))
        ideas = self._database_manager.fetchall()

        # 获取每个想法的标签、关键词、关联和提醒
        for idea in ideas:
            idea_id = idea["id"]
            
            # 获取标签
            idea["tags"] = self._idea_manager.get_idea_tags(idea_id)
            
            # 获取关键词
            idea["keywords"] = self._idea_manager.get_idea_keywords(idea_id)
            
            # 获取关联
            idea["relations"] = self._idea_manager.get_idea_relations(idea_id)
            
            # 获取提醒
            idea["reminders"] = self._idea_manager.get_idea_reminders(idea_id)
            
            # 添加搜索相关性分数（简单实现）
            idea["relevance"] = self._calculate_keyword_relevance(idea, query)

        # 按相关性排序
        ideas.sort(key=lambda x: x["relevance"], reverse=True)

        return ideas

    def _vector_search(self, query: str, limit: int, offset: int, filters: Dict) -> List[Dict]:
        """
        向量搜索。

        Args:
            query: 搜索查询
            limit: 限制数量
            offset: 偏移量
            filters: 过滤条件

        Returns:
            想法字典列表
        """
        # 检查AI功能是否启用
        if not self._config_manager.is_ai_enabled() or self._config_manager.is_offline_mode():
            # 如果AI功能未启用或处于离线模式，回退到关键词搜索
            return self._keyword_search(query, limit, offset, filters)

        try:
            # 准备元数据过滤条件
            metadata_filter = {}
            
            if "is_archived" in filters:
                metadata_filter["is_archived"] = 1 if filters["is_archived"] else 0
                
            if "is_favorite" in filters:
                metadata_filter["is_favorite"] = 1 if filters["is_favorite"] else 0

            # 执行向量搜索
            similar_ideas = self._vector_db_manager.search_similar_ideas(
                query=query,
                n_results=limit + offset,  # 考虑偏移量
                filter_metadata=metadata_filter if metadata_filter else None
            )
            
            # 应用偏移量
            similar_ideas = similar_ideas[offset:offset + limit]
            
            # 获取完整想法信息
            results = []
            for similar in similar_ideas:
                idea = self._idea_manager.get_idea(similar["idea_id"])
                if idea:
                    # 添加相似度分数
                    idea["relevance"] = 1.0 - (similar["distance"] or 0.0)  # 转换距离为相似度
                    
                    # 如果有标签过滤条件，检查想法是否包含所有指定标签
                    if "tag_ids" in filters and filters["tag_ids"]:
                        tag_ids = set(filters["tag_ids"])
                        idea_tag_ids = {tag["id"] for tag in idea["tags"]}
                        if not tag_ids.issubset(idea_tag_ids):
                            continue  # 跳过不包含所有指定标签的想法
                    
                    results.append(idea)
            
            return results
        except Exception as e:
            print(f"向量搜索失败: {e}")
            # 如果向量搜索失败，回退到关键词搜索
            return self._keyword_search(query, limit, offset, filters)

    def _hybrid_search(self, query: str, limit: int, offset: int, filters: Dict) -> List[Dict]:
        """
        混合搜索（结合关键词搜索和向量搜索）。

        Args:
            query: 搜索查询
            limit: 限制数量
            offset: 偏移量
            filters: 过滤条件

        Returns:
            想法字典列表
        """
        # 检查AI功能是否启用
        if not self._config_manager.is_ai_enabled() or self._config_manager.is_offline_mode():
            # 如果AI功能未启用或处于离线模式，只使用关键词搜索
            return self._keyword_search(query, limit, offset, filters)

        try:
            # 执行关键词搜索
            keyword_results = self._keyword_search(query, limit, 0, filters)
            
            # 执行向量搜索
            vector_results = self._vector_search(query, limit, 0, filters)
            
            # 合并结果
            merged_results = {}
            
            # 添加关键词搜索结果
            for idea in keyword_results:
                idea_id = idea["id"]
                merged_results[idea_id] = idea
                # 标记来源
                merged_results[idea_id]["search_source"] = "keyword"
            
            # 添加向量搜索结果
            for idea in vector_results:
                idea_id = idea["id"]
                if idea_id in merged_results:
                    # 如果已存在，更新相关性分数为两者的最大值
                    merged_results[idea_id]["relevance"] = max(
                        merged_results[idea_id]["relevance"],
                        idea["relevance"]
                    )
                    # 更新来源
                    merged_results[idea_id]["search_source"] = "both"
                else:
                    merged_results[idea_id] = idea
                    # 标记来源
                    merged_results[idea_id]["search_source"] = "vector"
            
            # 转换为列表并按相关性排序
            results = list(merged_results.values())
            results.sort(key=lambda x: x["relevance"], reverse=True)
            
            # 应用偏移量和限制
            return results[offset:offset + limit]
        except Exception as e:
            print(f"混合搜索失败: {e}")
            # 如果混合搜索失败，回退到关键词搜索
            return self._keyword_search(query, limit, offset, filters)

    def _calculate_keyword_relevance(self, idea: Dict, query: str) -> float:
        """
        计算关键词搜索相关性分数。

        Args:
            idea: 想法字典
            query: 搜索查询

        Returns:
            相关性分数（0-1）
        """
        # 简单实现：计算查询词在内容和标题中的出现次数
        query_lower = query.lower()
        content_lower = idea["content"].lower()
        title_lower = idea["title"].lower() if idea["title"] else ""
        
        # 计算出现次数
        content_count = content_lower.count(query_lower)
        title_count = title_lower.count(query_lower)
        
        # 标题匹配权重更高
        score = content_count * 0.1 + title_count * 0.5
        
        # 归一化分数到0-1范围
        return min(1.0, score)

    def suggest_tags(self, query: str, limit: int = 5) -> List[Dict]:
        """
        根据查询建议标签。

        Args:
            query: 搜索查询
            limit: 限制数量

        Returns:
            标签字典列表
        """
        if not query:
            return []

        # 搜索匹配的标签
        self._database_manager.execute(
            """
            SELECT * FROM Tags
            WHERE name LIKE ?
            ORDER BY name
            LIMIT ?
            """,
            (f"%{query}%", limit),
        )
        return self._database_manager.fetchall()

    def get_trending_keywords(self, days: int = 7, limit: int = 10) -> List[Dict]:
        """
        获取热门关键词。

        Args:
            days: 天数
            limit: 限制数量

        Returns:
            关键词字典列表
        """
        self._database_manager.execute(
            """
            SELECT keyword, COUNT(*) as count, AVG(weight) as avg_weight
            FROM Keywords k
            JOIN Ideas i ON k.idea_id = i.id
            WHERE i.created_at >= datetime('now', ?) AND i.is_archived = 0
            GROUP BY keyword
            ORDER BY count DESC, avg_weight DESC
            LIMIT ?
            """,
            (f"-{days} days", limit),
        )
        return self._database_manager.fetchall()

    def get_related_ideas(self, idea_id: int, limit: int = 5) -> List[Dict]:
        """
        获取相关想法。

        Args:
            idea_id: 想法ID
            limit: 限制数量

        Returns:
            想法字典列表
        """
        # 获取想法
        idea = self._idea_manager.get_idea(idea_id)
        if not idea:
            return []

        # 首先尝试从关联表中获取
        self._database_manager.execute(
            """
            SELECT i.* FROM Ideas i
            JOIN Relations r ON i.id = r.target_idea_id
            WHERE r.source_idea_id = ?
            ORDER BY r.confidence DESC
            LIMIT ?
            """,
            (idea_id, limit),
        )
        related_from_relations = self._database_manager.fetchall()

        # 如果关联表中有足够的结果，直接返回
        if len(related_from_relations) >= limit:
            # 获取每个想法的标签、关键词、关联和提醒
            for related in related_from_relations:
                related_id = related["id"]
                related["tags"] = self._idea_manager.get_idea_tags(related_id)
                related["keywords"] = self._idea_manager.get_idea_keywords(related_id)
                related["relations"] = self._idea_manager.get_idea_relations(related_id)
                related["reminders"] = self._idea_manager.get_idea_reminders(related_id)
            return related_from_relations[:limit]

        # 如果关联表中结果不足，尝试使用向量搜索补充
        remaining = limit - len(related_from_relations)
        
        # 检查AI功能是否启用
        if self._config_manager.is_ai_enabled() and not self._config_manager.is_offline_mode():
            try:
                # 使用向量搜索
                similar_ideas = self._vector_db_manager.search_similar_ideas(
                    query=idea["content"],
                    n_results=remaining + 1,  # +1 是因为可能会包含自身
                )
                
                # 过滤掉自身
                similar_ideas = [similar for similar in similar_ideas if similar["idea_id"] != idea_id][:remaining]
                
                # 获取完整想法信息
                vector_results = []
                for similar in similar_ideas:
                    related = self._idea_manager.get_idea(similar["idea_id"])
                    if related:
                        vector_results.append(related)
                
                # 合并结果
                results = related_from_relations + vector_results
                return results[:limit]
            except Exception as e:
                print(f"获取相关想法失败: {e}")
        
        # 如果向量搜索失败或AI功能未启用，使用标签匹配补充
        # 获取想法的标签
        idea_tags = self._idea_manager.get_idea_tags(idea_id)
        if not idea_tags:
            return related_from_relations  # 如果没有标签，直接返回关联表中的结果
        
        # 构建标签ID列表
        tag_ids = [tag["id"] for tag in idea_tags]
        placeholders = ", ".join(["?"] * len(tag_ids))
        
        # 查询具有相同标签的想法
        self._database_manager.execute(
            f"""
            SELECT i.*, COUNT(it.tag_id) as tag_count
            FROM Ideas i
            JOIN IdeaTags it ON i.id = it.idea_id
            WHERE it.tag_id IN ({placeholders})
            AND i.id != ?
            AND i.id NOT IN ({", ".join(["?"] * len(related_from_relations))})
            GROUP BY i.id
            ORDER BY tag_count DESC, i.created_at DESC
            LIMIT ?
            """,
            tuple(tag_ids + [idea_id] + [r["id"] for r in related_from_relations] + [remaining]),
        )
        tag_results = self._database_manager.fetchall()
        
        # 获取每个想法的标签、关键词、关联和提醒
        for related in tag_results:
            related_id = related["id"]
            related["tags"] = self._idea_manager.get_idea_tags(related_id)
            related["keywords"] = self._idea_manager.get_idea_keywords(related_id)
            related["relations"] = self._idea_manager.get_idea_relations(related_id)
            related["reminders"] = self._idea_manager.get_idea_reminders(related_id)
        
        # 合并结果
        results = related_from_relations + tag_results
        return results[:limit]
