"""
AI管理器模块，负责管理AI相关组件。
"""
from typing import Optional

from src.ai.ai_service import AIService
from src.ai.embedding_generator import EmbeddingGenerator
from src.ai.idea_analyzer import IdeaAnalyzer
from src.ai.ideas_summarizer import IdeasSummarizer
from src.ai.ai_query_console import AIQueryManager
from src.ai.reminder_system import ReminderSystem
from src.business.idea_manager import IdeaManager
from src.business.tag_manager import TagManager
from src.core.config_manager import ConfigManager
from src.core.event_system import EventSystem
from src.data.database_manager import DatabaseManager
from src.data.vector_db_manager import VectorDBManager
from src.system_integration.notification_manager import NotificationManager


class AIManager:
    """AI管理器类，负责管理AI相关组件。"""

    _instance = None

    def __new__(cls, config_manager=None, event_system=None, database_manager=None, vector_db_manager=None):
        """
        实现单例模式，确保只创建一个实例。

        Args:
            config_manager: 配置管理器实例
            event_system: 事件系统实例
            database_manager: 数据库管理器实例
            vector_db_manager: 向量数据库管理器实例

        Returns:
            AIManager 实例
        """
        if cls._instance is None:
            cls._instance = super(AIManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(
        self,
        config_manager: Optional[ConfigManager] = None,
        event_system: Optional[EventSystem] = None,
        database_manager: Optional[DatabaseManager] = None,
        vector_db_manager: Optional[VectorDBManager] = None,
    ):
        """
        初始化AI管理器。

        Args:
            config_manager: 配置管理器实例
            event_system: 事件系统实例
            database_manager: 数据库管理器实例
            vector_db_manager: 向量数据库管理器实例
        """
        if self._initialized:
            return

        self._config_manager = config_manager or ConfigManager()
        self._event_system = event_system or EventSystem()
        self._database_manager = database_manager or DatabaseManager(self._config_manager)
        self._vector_db_manager = vector_db_manager or VectorDBManager(self._config_manager)

        # 初始化业务逻辑组件
        self._idea_manager = IdeaManager(self._config_manager, self._event_system)
        self._tag_manager = TagManager(self._config_manager, self._event_system)

        # 初始化AI服务
        self._ai_service = AIService(self._config_manager, self._event_system)
        
        # 初始化嵌入生成器
        self._embedding_generator = EmbeddingGenerator(
            self._config_manager, self._event_system, self._ai_service
        )
        
        # 初始化想法分析器
        self._idea_analyzer = IdeaAnalyzer(
            self._config_manager,
            self._event_system,
            self._ai_service,
            self._embedding_generator,
            self._idea_manager,
            self._tag_manager
        )
        
        # 初始化想法总结器
        self._ideas_summarizer = IdeasSummarizer(
            self._config_manager,
            self._event_system,
            self._ai_service,
            self._idea_manager,
            self._tag_manager
        )
        
        # 初始化AI查询管理器
        self._ai_query_manager = AIQueryManager(
            self._config_manager,
            self._event_system,
            self._ai_service,
            self._idea_manager
        )

        # 通知管理器会在需要时获取，避免循环依赖
        self._notification_manager = None
        
        # 初始化提醒系统
        self._reminder_system = None  # 延迟初始化

        # 注册事件处理器
        self._register_event_handlers()
        
        self._initialized = True

    def _register_event_handlers(self):
        """注册事件处理器。"""
        # 配置变更事件
        self._event_system.subscribe("config_changed", self._handle_config_changed)
        
        # 应用程序退出事件
        self._event_system.subscribe("app_exit", self._handle_app_exit)
        
        # 获取AI组件实例事件
        self._event_system.subscribe("get_ai_service", self._handle_get_ai_service)
        self._event_system.subscribe("get_embedding_generator", self._handle_get_embedding_generator)
        self._event_system.subscribe("get_idea_analyzer", self._handle_get_idea_analyzer)
        self._event_system.subscribe("get_ideas_summarizer", self._handle_get_ideas_summarizer)
        self._event_system.subscribe("get_reminder_system", self._handle_get_reminder_system)

    def _handle_config_changed(self, data=None):
        """
        处理配置变更事件。

        Args:
            data: 事件数据
        """
        # 如果AI相关配置发生变化，更新相关组件
        if data and "ai" in data:
            # 更新AI服务
            if self._ai_service:
                # AI服务本身会监听配置变更事件，无需手动更新
                pass
            
            # 更新向量数据库
            if self._vector_db_manager:
                self._vector_db_manager.update_embedding_function()

    def _handle_app_exit(self, data=None):
        """
        处理应用程序退出事件。

        Args:
            data: 事件数据
        """
        # 清理资源
        pass

    def _handle_get_ai_service(self, data):
        """
        处理获取AI服务实例事件。

        Args:
            data: 事件数据，包含callback字段
        """
        callback = data.get("callback", None)
        if callback:
            callback(self._ai_service)

    def _handle_get_embedding_generator(self, data):
        """
        处理获取嵌入生成器实例事件。

        Args:
            data: 事件数据，包含callback字段
        """
        callback = data.get("callback", None)
        if callback:
            callback(self._embedding_generator)

    def _handle_get_idea_analyzer(self, data):
        """
        处理获取想法分析器实例事件。

        Args:
            data: 事件数据，包含callback字段
        """
        callback = data.get("callback", None)
        if callback:
            callback(self._idea_analyzer)

    def _handle_get_ideas_summarizer(self, data):
        """
        处理获取想法总结器实例事件。

        Args:
            data: 事件数据，包含callback字段
        """
        callback = data.get("callback", None)
        if callback:
            callback(self._ideas_summarizer)

    def _handle_get_reminder_system(self, data):
        """
        处理获取提醒系统实例事件。

        Args:
            data: 事件数据，包含callback字段
        """
        callback = data.get("callback", None)
        if callback:
            callback(self.get_reminder_system())

    def get_ai_service(self) -> AIService:
        """
        获取AI服务实例。

        Returns:
            AI服务实例
        """
        return self._ai_service

    def get_embedding_generator(self) -> EmbeddingGenerator:
        """
        获取嵌入生成器实例。

        Returns:
            嵌入生成器实例
        """
        return self._embedding_generator

    def get_idea_analyzer(self) -> IdeaAnalyzer:
        """
        获取想法分析器实例。

        Returns:
            想法分析器实例
        """
        return self._idea_analyzer

    def get_ideas_summarizer(self) -> IdeasSummarizer:
        """
        获取想法总结器实例。

        Returns:
            想法总结器实例
        """
        return self._ideas_summarizer

    def get_ai_query_manager(self) -> AIQueryManager:
        """
        获取AI查询管理器实例。

        Returns:
            AI查询管理器实例
        """
        return self._ai_query_manager

    def get_reminder_system(self) -> ReminderSystem:
        """
        获取提醒系统实例。

        Returns:
            提醒系统实例
        """
        if self._reminder_system is None:
            # 延迟导入，避免循环依赖
            from src.system_integration.notification_manager import NotificationManager
            notification_manager = NotificationManager(self._config_manager, self._event_system)
            
            self._reminder_system = ReminderSystem(
                self._config_manager,
                self._event_system,
                self._ai_service,
                self._idea_manager,
                notification_manager
            )
        
        return self._reminder_system

    def initialize(self):
        """初始化AI管理器组件。"""
        # 如果AI功能已启用且不处于离线模式，初始化AI服务
        if self._config_manager.is_ai_enabled() and not self._config_manager.is_offline_mode():
            # 测试AI服务连接
            success, _ = self._ai_service.test_api_connection()
            
            if success:
                # 初始化提醒系统
                self.get_reminder_system()
                
                # 发布AI服务就绪事件
                self._event_system.publish("ai_service_ready")
            else:
                # 发布AI服务不可用事件
                self._event_system.publish("ai_service_unavailable")
        else:
            # 发布AI服务禁用事件
            self._event_system.publish("ai_service_disabled")

    def is_ai_available(self) -> bool:
        """
        检查AI服务是否可用。

        Returns:
            是否可用
        """
        return self._ai_service.is_available()
