"""
系统托盘模块，负责管理系统托盘图标和菜单。
"""
from typing import Optional

from PyQt6.QtGui import QIcon, QAction
from PyQt6.QtWidgets import QSystemTrayIcon, QMenu

from ..core.config_manager import ConfigManager
from ..core.event_system import EventSystem


class SystemTray:
    """系统托盘类，负责管理系统托盘图标和菜单。"""

    def __init__(self, config_manager: Optional[ConfigManager] = None, event_system: Optional[EventSystem] = None):
        """
        初始化系统托盘。

        Args:
            config_manager: 配置管理器实例
            event_system: 事件系统实例
        """
        self._config_manager = config_manager or ConfigManager()
        self._event_system = event_system or EventSystem()
        self._tray_icon = None
        self._tray_menu = None
        
        # 初始化系统托盘
        self._init_tray()
        
        # 注册事件处理器
        self._event_system.subscribe("app_exit", self._handle_app_exit)

    def _init_tray(self) -> None:
        """初始化系统托盘图标和菜单。"""
        # 创建托盘菜单
        self._tray_menu = QMenu()
        
        # 添加菜单项
        self._add_menu_items()
        
        # 创建托盘图标
        self._tray_icon = QSystemTrayIcon()
        self._tray_icon.setToolTip("ideaSystemXS")
        self._tray_icon.setContextMenu(self._tray_menu)
        
        # 设置图标
        self._set_icon()
        
        # 连接信号
        self._tray_icon.activated.connect(self._handle_tray_activated)

    def _add_menu_items(self) -> None:
        """添加托盘菜单项。"""
        # 新建想法
        new_idea_action = QAction("新建想法", self._tray_menu)
        new_idea_action.triggered.connect(self._handle_new_idea)
        self._tray_menu.addAction(new_idea_action)
        
        # 打开主窗口
        open_main_action = QAction("打开主窗口", self._tray_menu)
        open_main_action.triggered.connect(self._handle_open_main)
        self._tray_menu.addAction(open_main_action)
        
        # 分隔线
        self._tray_menu.addSeparator()
        
        # 设置
        settings_action = QAction("设置", self._tray_menu)
        settings_action.triggered.connect(self._handle_settings)
        self._tray_menu.addAction(settings_action)
        
        # 分隔线
        self._tray_menu.addSeparator()
        
        # 退出
        exit_action = QAction("退出", self._tray_menu)
        exit_action.triggered.connect(self._handle_exit)
        self._tray_menu.addAction(exit_action)

    def _set_icon(self) -> None:
        """设置托盘图标。"""
        # 根据主题设置图标
        theme = self._config_manager.get_theme()
        if theme == "dark":
            # 深色主题图标
            self._tray_icon.setIcon(QIcon(":/icons/app_icon_light.png"))
        else:
            # 浅色主题图标
            self._tray_icon.setIcon(QIcon(":/icons/app_icon_dark.png"))

    def _handle_tray_activated(self, reason: QSystemTrayIcon.ActivationReason) -> None:
        """
        处理托盘图标激活事件。

        Args:
            reason: 激活原因
        """
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            # 单击托盘图标，显示输入窗口
            self._event_system.publish("show_input_window")
        elif reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            # 双击托盘图标，显示主窗口
            self._event_system.publish("show_main_window")

    def _handle_new_idea(self) -> None:
        """处理新建想法菜单项。"""
        self._event_system.publish("show_input_window")

    def _handle_open_main(self) -> None:
        """处理打开主窗口菜单项。"""
        self._event_system.publish("show_main_window")

    def _handle_settings(self) -> None:
        """处理设置菜单项。"""
        self._event_system.publish("show_settings_window")

    def _handle_exit(self) -> None:
        """处理退出菜单项。"""
        self._event_system.publish("app_exit")

    def _handle_app_exit(self, data=None) -> None:
        """
        处理应用程序退出事件。

        Args:
            data: 事件数据
        """
        if self._tray_icon:
            self._tray_icon.hide()

    def show(self) -> None:
        """显示系统托盘图标。"""
        if self._tray_icon:
            self._tray_icon.show()

    def hide(self) -> None:
        """隐藏系统托盘图标。"""
        if self._tray_icon:
            self._tray_icon.hide()

    def show_message(self, title: str, message: str, icon: QSystemTrayIcon.MessageIcon = QSystemTrayIcon.MessageIcon.Information, timeout: int = 5000) -> None:
        """
        显示托盘消息。

        Args:
            title: 消息标题
            message: 消息内容
            icon: 消息图标
            timeout: 超时时间（毫秒）
        """
        if self._tray_icon:
            self._tray_icon.showMessage(title, message, icon, timeout)

    def update_theme(self) -> None:
        """更新主题。"""
        self._set_icon()
