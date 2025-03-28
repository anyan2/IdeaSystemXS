"""
想法分析和关联模块，用于分析想法并找出关联。
"""
from typing import Dict, List, Optional, Tuple, Union

from ..ai.ai_service import AIService
from ..ai.embedding_generator import EmbeddingGenerator
from ..business.idea_manager import IdeaManager
from ..business.tag_manager import TagManager
from ..core.config_manager import ConfigManager
from ..core.event_system import EventSystem


class IdeaAnalyzer:
    """想法分析器类，用于分析想法并找出关联。"""

    def __init__(
        self,
        config_manager: Optional[ConfigManager] = None,
        event_system: Optional[EventSystem] = None,
        ai_service: Optional[AIService] = None,
        embedding_generator: Optional[EmbeddingGenerator] = None,
        idea_manager: Optional[IdeaManager] = None,
        tag_manager: Optional[TagManager] = None,
    ):
        """
        初始化想法分析器。

        Args:
            config_manager: 配置管理器实例
            event_system: 事件系统实例
            ai_service: AI服务实例
            embedding_generator: 向量嵌入生成器实例
            idea_manager: 想法管理器实例
            tag_manager: 标签管理器实例
        """
        self._config_manager = config_manager or ConfigManager()
        self._event_system = event_system or EventSystem()
        self._ai_service = ai_service or AIService(self._config_manager, self._event_system)
        self._embedding_generator = embedding_generator or EmbeddingGenerator(
            self._config_manager, self._event_system, self._ai_service
        )
        self._idea_manager = idea_manager or IdeaManager(self._config_manager, self._event_system)
        self._tag_manager = tag_manager or TagManager(self._config_manager, self._event_system)
        
        # 注册事件处理器
        self._register_event_handlers()

    def _register_event_handlers(self):
        """注册事件处理器。"""
        # 分析想法事件
        self._event_system.subscribe("analyze_idea", self._handle_analyze_idea)
        
        # 查找相关想法事件
        self._event_system.subscribe("find_related_ideas", self._handle_find_related_ideas)
        
        # 批量分析想法事件
        self._event_system.subscribe("batch_analyze_ideas", self._handle_batch_analyze_ideas)

    def _handle_analyze_idea(self, data):
        """
        处理分析想法事件。

        Args:
            data: 事件数据，包含idea_id和callback字段
        """
        # 获取想法ID
        idea_id = data.get("idea_id", None)
        
        # 获取回调函数
        callback = data.get("callback", None)
        
        # 如果想法ID为空，不处理
        if idea_id is None:
            return
        
        # 获取想法
        idea = self._idea_manager.get_idea(idea_id)
        
        # 如果想法不存在，不处理
        if not idea:
            return
        
        # 分析想法
        analysis_result = self.analyze_idea(idea["content"])
        
        # 更新想法
        self._idea_manager.update_idea(
            idea_id,
            title=analysis_result.get("title", idea.get("title", "")),
            summary=analysis_result.get("summary", ""),
            tags=analysis_result.get("tags", [])
        )
        
        # 如果有回调函数，调用回调函数
        if callback:
            callback(analysis_result)

    def _handle_find_related_ideas(self, data):
        """
        处理查找相关想法事件。

        Args:
            data: 事件数据，包含idea_id、limit和callback字段
        """
        # 获取想法ID
        idea_id = data.get("idea_id", None)
        
        # 获取限制数量
        limit = data.get("limit", 5)
        
        # 获取回调函数
        callback = data.get("callback", None)
        
        # 如果想法ID为空，不处理
        if idea_id is None:
            return
        
        # 获取想法
        idea = self._idea_manager.get_idea(idea_id)
        
        # 如果想法不存在，不处理
        if not idea:
            return
        
        # 查找相关想法
        related_ideas = self.find_related_ideas(idea["content"], idea_id, limit)
        
        # 如果有回调函数，调用回调函数
        if callback:
            callback(related_ideas)

    def _handle_batch_analyze_ideas(self, data):
        """
        处理批量分析想法事件。

        Args:
            data: 事件数据，包含idea_ids和callback字段
        """
        # 获取想法ID列表
        idea_ids = data.get("idea_ids", [])
        
        # 获取回调函数
        callback = data.get("callback", None)
        
        # 如果想法ID列表为空，不处理
        if not idea_ids:
            return
        
        # 批量分析想法
        results = {}
        for idea_id in idea_ids:
            # 获取想法
            idea = self._idea_manager.get_idea(idea_id)
            
            # 如果想法不存在，跳过
            if not idea:
                continue
            
            # 分析想法
            analysis_result = self.analyze_idea(idea["content"])
            
            # 更新想法
            self._idea_manager.update_idea(
                idea_id,
                title=analysis_result.get("title", idea.get("title", "")),
                summary=analysis_result.get("summary", ""),
                tags=analysis_result.get("tags", [])
            )
            
            # 保存结果
            results[idea_id] = analysis_result
        
        # 如果有回调函数，调用回调函数
        if callback:
            callback(results)

    def analyze_idea(self, content: str) -> Dict[str, Union[str, List[str]]]:
        """
        分析想法，提取标题、摘要和标签。

        Args:
            content: 想法内容

        Returns:
            分析结果，包含title、summary和tags字段
        """
        # 如果内容为空，返回空结果
        if not content:
            return {
                "title": "",
                "summary": "",
                "tags": []
            }
        
        # 使用AI服务分析想法
        analysis_result = self._ai_service.analyze_idea(content)
        
        # 如果AI服务不可用或分析失败，使用备用方法分析
        if not analysis_result.get("title") and not analysis_result.get("tags"):
            analysis_result = self._analyze_idea_fallback(content)
        
        return analysis_result

    def _analyze_idea_fallback(self, content: str) -> Dict[str, Union[str, List[str]]]:
        """
        备用的想法分析方法，当AI服务不可用时使用。

        Args:
            content: 想法内容

        Returns:
            分析结果，包含title、summary和tags字段
        """
        # 简单的分析方法
        # 注意：这只是一个非常简单的备用方法，不适合生产环境
        
        # 提取标题
        lines = content.strip().split("\n")
        title = lines[0][:20] if lines else ""
        
        # 提取摘要
        summary = content[:100] if len(content) > 100 else content
        
        # 提取标签
        words = content.lower().split()
        word_freq = {}
        for word in words:
            if len(word) > 2:
                word_freq[word] = word_freq.get(word, 0) + 1
        
        # 按频率排序
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        
        # 取前5个作为标签
        tags = [word for word, _ in sorted_words[:5]]
        
        return {
            "title": title,
            "summary": summary,
            "tags": tags
        }

    def find_related_ideas(self, content: str, exclude_id: Optional[int] = None, limit: int = 5) -> List[Dict]:
        """
        查找与给定内容相关的想法。

        Args:
            content: 想法内容
            exclude_id: 要排除的想法ID
            limit: 返回结果数量限制

        Returns:
            相关想法列表
        """
        # 如果内容为空，返回空列表
        if not content:
            return []
        
        # 生成嵌入向量
        embedding = self._embedding_generator.generate_embedding(content)
        
        # 如果生成嵌入向量失败，返回空列表
        if embedding is None:
            return []
        
        # 获取所有想法
        ideas = self._idea_manager.get_ideas()
        
        # 计算相似度
        similarities = []
        for idea in ideas:
            # 如果是要排除的想法，跳过
            if exclude_id is not None and idea["id"] == exclude_id:
                continue
            
            # 如果想法没有嵌入向量，生成嵌入向量
            if "embedding" not in idea or not idea["embedding"]:
                idea_embedding = self._embedding_generator.generate_embedding(idea["content"])
                
                # 如果生成嵌入向量失败，跳过
                if idea_embedding is None:
                    continue
                
                # 更新想法的嵌入向量
                self._idea_manager.update_idea_embedding(idea["id"], idea_embedding)
            else:
                idea_embedding = idea["embedding"]
            
            # 计算相似度
            similarity = self._embedding_generator.calculate_similarity(embedding, idea_embedding)
            
            # 添加到相似度列表
            similarities.append((idea, similarity))
        
        # 按相似度排序
        similarities.sort(key=lambda x: x[1], reverse=True)
        
        # 取前limit个
        related_ideas = []
        for idea, similarity in similarities[:limit]:
            # 获取标签
            tags = self._tag_manager.get_idea_tags(idea["id"])
            
            # 添加到相关想法列表
            related_ideas.append({
                "id": idea["id"],
                "title": idea["title"],
                "content": idea["content"],
                "tags": tags,
                "similarity": similarity
            })
        
        return related_ideas

    def batch_find_related_ideas(self, idea_ids: List[int], limit_per_idea: int = 3) -> Dict[int, List[Dict]]:
        """
        批量查找与给定想法相关的其他想法。

        Args:
            idea_ids: 想法ID列表
            limit_per_idea: 每个想法返回的相关想法数量限制

        Returns:
            相关想法字典，键为想法ID，值为相关想法列表
        """
        # 如果想法ID列表为空，返回空字典
        if not idea_ids:
            return {}
        
        # 批量查找相关想法
        results = {}
        for idea_id in idea_ids:
            # 获取想法
            idea = self._idea_manager.get_idea(idea_id)
            
            # 如果想法不存在，跳过
            if not idea:
                continue
            
            # 查找相关想法
            related_ideas = self.find_related_ideas(idea["content"], idea_id, limit_per_idea)
            
            # 保存结果
            results[idea_id] = related_ideas
        
        return results
