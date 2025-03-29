"""
智能归纳和总结模块，用于归纳和总结想法。
"""
from typing import Dict, List, Optional, Tuple, Union

from src.ai.ai_service import AIService
from src.business.idea_manager import IdeaManager
from src.business.tag_manager import TagManager
from src.core.config_manager import ConfigManager
from src.core.event_system import EventSystem


class IdeasSummarizer:
    """想法总结器类，用于归纳和总结想法。"""

    def __init__(
        self,
        config_manager: Optional[ConfigManager] = None,
        event_system: Optional[EventSystem] = None,
        ai_service: Optional[AIService] = None,
        idea_manager: Optional[IdeaManager] = None,
        tag_manager: Optional[TagManager] = None,
    ):
        """
        初始化想法总结器。

        Args:
            config_manager: 配置管理器实例
            event_system: 事件系统实例
            ai_service: AI服务实例
            idea_manager: 想法管理器实例
            tag_manager: 标签管理器实例
        """
        self._config_manager = config_manager or ConfigManager()
        self._event_system = event_system or EventSystem()
        self._ai_service = ai_service or AIService(self._config_manager, self._event_system)
        self._idea_manager = idea_manager or IdeaManager(self._config_manager, self._event_system)
        self._tag_manager = tag_manager or TagManager(self._config_manager, self._event_system)
        
        # 注册事件处理器
        self._register_event_handlers()

    def _register_event_handlers(self):
        """注册事件处理器。"""
        # 总结想法事件
        self._event_system.subscribe("summarize_ideas", self._handle_summarize_ideas)
        
        # 总结标签想法事件
        self._event_system.subscribe("summarize_tag_ideas", self._handle_summarize_tag_ideas)
        
        # 总结时间段想法事件
        self._event_system.subscribe("summarize_time_period_ideas", self._handle_summarize_time_period_ideas)

    def _handle_summarize_ideas(self, data):
        """
        处理总结想法事件。

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
        
        # 获取想法列表
        ideas = []
        for idea_id in idea_ids:
            idea = self._idea_manager.get_idea(idea_id)
            if idea:
                # 获取标签
                tags = self._tag_manager.get_idea_tags(idea_id)
                
                # 添加标签到想法
                idea["tags"] = tags
                
                # 添加到想法列表
                ideas.append(idea)
        
        # 总结想法
        summary = self.summarize_ideas(ideas)
        
        # 如果有回调函数，调用回调函数
        if callback:
            callback(summary)

    def _handle_summarize_tag_ideas(self, data):
        """
        处理总结标签想法事件。

        Args:
            data: 事件数据，包含tag和callback字段
        """
        # 获取标签
        tag = data.get("tag", "")
        
        # 获取回调函数
        callback = data.get("callback", None)
        
        # 如果标签为空，不处理
        if not tag:
            return
        
        # 获取标签想法
        ideas = self._idea_manager.get_ideas_by_tag(tag)
        
        # 总结想法
        summary = self.summarize_ideas(ideas)
        
        # 如果有回调函数，调用回调函数
        if callback:
            callback(summary)

    def _handle_summarize_time_period_ideas(self, data):
        """
        处理总结时间段想法事件。

        Args:
            data: 事件数据，包含start_time、end_time和callback字段
        """
        # 获取开始时间
        start_time = data.get("start_time", None)
        
        # 获取结束时间
        end_time = data.get("end_time", None)
        
        # 获取回调函数
        callback = data.get("callback", None)
        
        # 如果开始时间或结束时间为空，不处理
        if start_time is None or end_time is None:
            return
        
        # 获取时间段想法
        ideas = self._idea_manager.get_ideas_by_time_range(start_time, end_time)
        
        # 总结想法
        summary = self.summarize_ideas(ideas)
        
        # 如果有回调函数，调用回调函数
        if callback:
            callback(summary)

    def summarize_ideas(self, ideas: List[Dict]) -> str:
        """
        总结想法列表。

        Args:
            ideas: 想法列表

        Returns:
            总结文本
        """
        # 如果想法列表为空，返回空字符串
        if not ideas:
            return ""
        
        # 使用AI服务总结想法
        summary = self._ai_service.summarize_ideas(ideas)
        
        # 如果AI服务不可用或总结失败，使用备用方法总结
        if not summary:
            summary = self._summarize_ideas_fallback(ideas)
        
        return summary

    def _summarize_ideas_fallback(self, ideas: List[Dict]) -> str:
        """
        备用的想法总结方法，当AI服务不可用时使用。

        Args:
            ideas: 想法列表

        Returns:
            总结文本
        """
        # 简单的总结方法
        # 注意：这只是一个非常简单的备用方法，不适合生产环境
        
        # 如果想法列表为空，返回空字符串
        if not ideas:
            return ""
        
        # 提取所有标签
        all_tags = []
        for idea in ideas:
            tags = idea.get("tags", [])
            all_tags.extend(tags)
        
        # 统计标签频率
        tag_freq = {}
        for tag in all_tags:
            tag_freq[tag] = tag_freq.get(tag, 0) + 1
        
        # 按频率排序
        sorted_tags = sorted(tag_freq.items(), key=lambda x: x[1], reverse=True)
        
        # 取前5个作为主要标签
        main_tags = [tag for tag, _ in sorted_tags[:5]]
        
        # 生成总结
        summary = f"这组想法包含{len(ideas)}个条目，主要涉及以下主题：{', '.join(main_tags)}。"
        
        # 添加每个想法的简短描述
        summary += "\n\n主要想法包括："
        for i, idea in enumerate(ideas[:5]):  # 只取前5个想法
            title = idea.get("title", "")
            content = idea.get("content", "")
            summary += f"\n{i+1}. {title}: {content[:50]}..."
        
        # 如果想法超过5个，添加提示
        if len(ideas) > 5:
            summary += f"\n\n还有{len(ideas) - 5}个其他想法未列出。"
        
        return summary

    def generate_daily_summary(self, date: str) -> str:
        """
        生成指定日期的想法总结。

        Args:
            date: 日期，格式为YYYY-MM-DD

        Returns:
            总结文本
        """
        # 获取指定日期的想法
        ideas = self._idea_manager.get_ideas_by_date(date)
        
        # 总结想法
        summary = self.summarize_ideas(ideas)
        
        return summary

    def generate_weekly_summary(self, start_date: str, end_date: str) -> str:
        """
        生成指定周的想法总结。

        Args:
            start_date: 开始日期，格式为YYYY-MM-DD
            end_date: 结束日期，格式为YYYY-MM-DD

        Returns:
            总结文本
        """
        # 获取指定周的想法
        ideas = self._idea_manager.get_ideas_by_time_range(start_date, end_date)
        
        # 总结想法
        summary = self.summarize_ideas(ideas)
        
        return summary

    def generate_monthly_summary(self, year: int, month: int) -> str:
        """
        生成指定月份的想法总结。

        Args:
            year: 年份
            month: 月份

        Returns:
            总结文本
        """
        # 获取指定月份的想法
        ideas = self._idea_manager.get_ideas_by_month(year, month)
        
        # 总结想法
        summary = self.summarize_ideas(ideas)
        
        return summary

    def generate_tag_summary(self, tag: str) -> str:
        """
        生成指定标签的想法总结。

        Args:
            tag: 标签

        Returns:
            总结文本
        """
        # 获取指定标签的想法
        ideas = self._idea_manager.get_ideas_by_tag(tag)
        
        # 总结想法
        summary = self.summarize_ideas(ideas)
        
        return summary
