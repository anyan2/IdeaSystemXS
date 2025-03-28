"""
AI查询控制台模块，用于与AI进行交互式对话。
"""
from typing import Dict, List, Optional, Tuple, Union

from ..ai.ai_service import AIService
from ..business.idea_manager import IdeaManager
from ..business.search_engine import SearchEngine
from ..core.config_manager import ConfigManager
from ..core.event_system import EventSystem


class AIQueryConsole:
    """AI查询控制台类，用于与AI进行交互式对话。"""

    def __init__(
        self,
        config_manager: Optional[ConfigManager] = None,
        event_system: Optional[EventSystem] = None,
        ai_service: Optional[AIService] = None,
        idea_manager: Optional[IdeaManager] = None,
        search_engine: Optional[SearchEngine] = None,
    ):
        """
        初始化AI查询控制台。

        Args:
            config_manager: 配置管理器实例
            event_system: 事件系统实例
            ai_service: AI服务实例
            idea_manager: 想法管理器实例
            search_engine: 搜索引擎实例
        """
        self._config_manager = config_manager or ConfigManager()
        self._event_system = event_system or EventSystem()
        self._ai_service = ai_service or AIService(self._config_manager, self._event_system)
        self._idea_manager = idea_manager or IdeaManager(self._config_manager, self._event_system)
        self._search_engine = search_engine or SearchEngine(self._config_manager, self._event_system)
        
        # 对话历史
        self._conversation_history = []
        
        # 注册事件处理器
        self._register_event_handlers()

    def _register_event_handlers(self):
        """注册事件处理器。"""
        # 查询AI事件
        self._event_system.subscribe("query_ai", self._handle_query_ai)
        
        # 清空对话历史事件
        self._event_system.subscribe("clear_ai_conversation", self._handle_clear_conversation)

    def _handle_query_ai(self, data):
        """
        处理查询AI事件。

        Args:
            data: 事件数据，包含query和callback字段
        """
        # 获取查询
        query = data.get("query", "")
        
        # 获取回调函数
        callback = data.get("callback", None)
        
        # 如果查询为空，不处理
        if not query:
            return
        
        # 查询AI
        response = self.query_ai(query)
        
        # 如果有回调函数，调用回调函数
        if callback:
            callback(response)

    def _handle_clear_conversation(self, data=None):
        """
        处理清空对话历史事件。

        Args:
            data: 事件数据
        """
        # 清空对话历史
        self.clear_conversation()
        
        # 发布对话历史已清空事件
        self._event_system.publish("ai_conversation_cleared", {})

    def query_ai(self, query: str) -> str:
        """
        查询AI。

        Args:
            query: 查询内容

        Returns:
            AI回答
        """
        # 如果AI服务不可用，返回错误消息
        if not self._ai_service.is_available():
            return "AI服务不可用，请检查设置。"
        
        # 添加用户查询到对话历史
        self._conversation_history.append({
            "role": "user",
            "content": query
        })
        
        # 搜索相关想法
        related_ideas = self._search_related_ideas(query)
        
        # 查询AI
        response = self._ai_service.ask_ai(query, related_ideas)
        
        # 添加AI回答到对话历史
        self._conversation_history.append({
            "role": "assistant",
            "content": response
        })
        
        # 保持对话历史在合理长度
        self._trim_conversation_history()
        
        return response

    def _search_related_ideas(self, query: str) -> List[Dict]:
        """
        搜索与查询相关的想法。

        Args:
            query: 查询内容

        Returns:
            相关想法列表
        """
        # 使用搜索引擎搜索相关想法
        results = self._search_engine.search(
            query,
            use_keyword=True,
            use_semantic=True,
            similarity_threshold=0.5,
            limit=5
        )
        
        # 获取完整的想法信息
        ideas = []
        for result in results:
            idea = self._idea_manager.get_idea(result["id"])
            if idea:
                ideas.append(idea)
        
        return ideas

    def get_conversation_history(self) -> List[Dict]:
        """
        获取对话历史。

        Returns:
            对话历史列表
        """
        return self._conversation_history.copy()

    def clear_conversation(self):
        """清空对话历史。"""
        self._conversation_history = []

    def _trim_conversation_history(self, max_length: int = 10):
        """
        裁剪对话历史，保持在合理长度。

        Args:
            max_length: 最大对话轮数
        """
        # 如果对话历史长度超过最大长度，裁剪
        if len(self._conversation_history) > max_length * 2:
            # 保留系统消息和最近的对话
            self._conversation_history = self._conversation_history[-max_length * 2:]


class AIQueryManager:
    """AI查询管理器类，用于管理AI查询控制台。"""

    def __init__(
        self,
        config_manager: Optional[ConfigManager] = None,
        event_system: Optional[EventSystem] = None,
        ai_service: Optional[AIService] = None,
        idea_manager: Optional[IdeaManager] = None,
        search_engine: Optional[SearchEngine] = None,
    ):
        """
        初始化AI查询管理器。

        Args:
            config_manager: 配置管理器实例
            event_system: 事件系统实例
            ai_service: AI服务实例
            idea_manager: 想法管理器实例
            search_engine: 搜索引擎实例
        """
        self._config_manager = config_manager or ConfigManager()
        self._event_system = event_system or EventSystem()
        self._ai_service = ai_service or AIService(self._config_manager, self._event_system)
        self._idea_manager = idea_manager or IdeaManager(self._config_manager, self._event_system)
        self._search_engine = search_engine or SearchEngine(self._config_manager, self._event_system)
        
        # AI查询控制台实例
        self._console = AIQueryConsole(
            self._config_manager,
            self._event_system,
            self._ai_service,
            self._idea_manager,
            self._search_engine
        )
        
        # 注册事件处理器
        self._register_event_handlers()

    def _register_event_handlers(self):
        """注册事件处理器。"""
        # 获取AI查询控制台实例事件
        self._event_system.subscribe("get_ai_query_console", self._handle_get_console)

    def _handle_get_console(self, data):
        """
        处理获取AI查询控制台实例事件。

        Args:
            data: 事件数据，包含callback字段
        """
        # 获取回调函数
        callback = data.get("callback", None)
        
        # 如果有回调函数，调用回调函数
        if callback:
            callback(self._console)

    def get_console(self) -> AIQueryConsole:
        """
        获取AI查询控制台实例。

        Returns:
            AI查询控制台实例
        """
        return self._console
