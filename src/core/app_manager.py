"""
应用管理器模块，负责应用程序的生命周期管理。
"""
import sys
from typing import Optional

from src.core.config_manager import ConfigManager
from src.core.event_system import EventSystem
from src.data.database_manager import DatabaseManager
from src.data.vector_db_manager import VectorDBManager


class AppManager:
    """应用管理器类，负责应用程序的生命周期管理。"""
    def start(self):

        return self.start_app()
    def initialize_app(self):
    
        return self.initialize()
    _instance = None

    def __new__(cls, config_manager=None, event_system=None):
        """
        实现单例模式，确保只创建一个实例。

        Args:
            config_manager: 配置管理器实例
            event_system: 事件系统实例

        Returns:
            AppManager 实例
        """
        if cls._instance is None:
            cls._instance = super(AppManager, cls).__new__(cls)
            cls._instance._initialized = False  # 标记未初始化
        return cls._instance

    def __init__(self, config_manager=None, event_system=None):
        """初始化应用管理器，确保只执行一次"""
        if self._initialized:
            return  # 已初始化，直接返回

        self._config_manager = config_manager or ConfigManager()
        self._event_system = event_system or EventSystem()

        # 初始化数据层组件
        self._database_manager = DatabaseManager(self._config_manager)
        self._vector_db_manager = VectorDBManager(self._config_manager)

        # 其他组件将在需要时初始化
        self._hotkey_manager = None
        self._window_manager = None
        self._system_tray = None
        self._notification_manager = None
        self._ai_manager = None

        # 标记为已初始化
        self._initialized = True

        # 注册事件处理器
        self._register_event_handlers()

    def _register_event_handlers(self):
        """注册事件处理器。"""
        # 应用程序退出事件
        self._event_system.subscribe("app_exit", self._handle_app_exit)
        
        # 配置更改事件
        self._event_system.subscribe("config_changed", self._handle_config_changed)

    def _handle_app_exit(self, data=None):
        """
        处理应用程序退出事件。
        
        Args:
            data: 事件数据
        """
        # 关闭数据库连接
        if self._database_manager:
            self._database_manager.close()
        
        # 执行其他清理操作
        # ...

    def _handle_config_changed(self, data=None):
        """
        处理配置更改事件。
        
        Args:
            data: 事件数据
        """
        # 更新向量数据库嵌入函数
        if self._vector_db_manager and data and "ai" in data:
            self._vector_db_manager.update_embedding_function()

    def get_config_manager(self) -> ConfigManager:
        """
        获取配置管理器。
        
        Returns:
            配置管理器实例
        """
        return self._config_manager

    def get_event_system(self) -> EventSystem:
        """
        获取事件系统。
        
        Returns:
            事件系统实例
        """
        return self._event_system

    def get_database_manager(self) -> DatabaseManager:
        """
        获取数据库管理器。
        
        Returns:
            数据库管理器实例
        """
        return self._database_manager

    def get_vector_db_manager(self) -> VectorDBManager:
        """
        获取向量数据库管理器。
        
        Returns:
            向量数据库管理器实例
        """
        return self._vector_db_manager

    def get_hotkey_manager(self):
        """
        获取快捷键管理器。
        
        Returns:
            快捷键管理器实例
        """
        if self._hotkey_manager is None:
            # 延迟导入，避免循环依赖
            from ..system_integration.hotkey_manager import HotkeyManager
            self._hotkey_manager = HotkeyManager(self._config_manager, self._event_system)
        return self._hotkey_manager

    def get_window_manager(self):
        """
        获取窗口管理器。
        
        Returns:
            窗口管理器实例
        """
        if self._window_manager is None:
            # 延迟导入，避免循环依赖
            from ..ui.window_manager import WindowManager
            self._window_manager = WindowManager(self._config_manager, self._event_system)
        return self._window_manager

    def get_system_tray(self):
        """
        获取系统托盘。
        
        Returns:
            系统托盘实例
        """
        if self._system_tray is None:
            # 延迟导入，避免循环依赖
            from ..system_integration.system_tray import SystemTray
            self._system_tray = SystemTray(self._config_manager, self._event_system)
        return self._system_tray

    def get_notification_manager(self):
        """
        获取通知管理器。
        
        Returns:
            通知管理器实例
        """
        if self._notification_manager is None:
            # 延迟导入，避免循环依赖
            from ..system_integration.notification_manager import NotificationManager
            self._notification_manager = NotificationManager(self._config_manager, self._event_system)
        return self._notification_manager

    def get_ai_manager(self):
        """
        获取AI管理器。
        
        Returns:
            AI管理器实例
        """
        if self._ai_manager is None:
            # 延迟导入，避免循环依赖
            from ..ai.ai_manager import AIManager
            self._ai_manager = AIManager(self._config_manager, self._event_system, self._database_manager, self._vector_db_manager)
        return self._ai_manager

    def initialize(self):
        """初始化应用程序。"""
        # 初始化快捷键管理器
        self.get_hotkey_manager()
        
        # 初始化窗口管理器
        self.get_window_manager()
        
        # 初始化系统托盘
        self.get_system_tray()
        
        # 初始化通知管理器
        self.get_notification_manager()
        
        # 如果AI功能已启用，初始化AI管理器
        if self._config_manager.is_ai_enabled():
            self.get_ai_manager()
        
        # 发布应用程序初始化完成事件
        self._event_system.publish("app_initialized")

    def start_app(self):
        """启动应用程序。"""
        # 初始化应用程序
        self.initialize_app()
        
        # 注册全局快捷键
        self.get_hotkey_manager().register_hotkeys()
        
        # 显示系统托盘图标
        self.get_system_tray().show()
        
        # 如果是首次运行，显示主窗口
        if self._config_manager.is_first_run():
            self.get_window_manager().show_main_window()
            self._config_manager.set_first_run_completed()
        
        # 发布应用程序启动完成事件
        self._event_system.publish("app_started")

    def exit_app(self):
        """退出应用程序。"""
        # 发布应用程序退出事件
        self._event_system.publish("app_exit")
        
        # 退出应用程序
        sys.exit(0)
