"""
UI主题管理器模块，负责管理应用程序的主题和样式。
"""
import os
from typing import Optional

from PyQt6.QtCore import QObject, pyqtSignal, Qt
from PyQt6.QtGui import QColor, QPalette
from PyQt6.QtWidgets import QApplication

from ..core.config_manager import ConfigManager
from ..core.event_system import EventSystem


class ThemeManager(QObject):
    """UI主题管理器类，负责管理应用程序的主题和样式。"""

    # 主题变更信号
    theme_changed = pyqtSignal(str)

    def __init__(self, config_manager: Optional[ConfigManager] = None, event_system: Optional[EventSystem] = None):
        """
        初始化主题管理器。

        Args:
            config_manager: 配置管理器实例
            event_system: 事件系统实例
        """
        super().__init__()
        self._config_manager = config_manager or ConfigManager()
        self._event_system = event_system or EventSystem()
        self._current_theme = self._config_manager.get_theme()
        
        # 注册事件处理器
        self._event_system.subscribe("config_changed", self._handle_config_changed)

    def _handle_config_changed(self, data=None):
        """
        处理配置更改事件。

        Args:
            data: 事件数据
        """
        if data and "general" in data and "theme" in data["general"]:
            new_theme = data["general"]["theme"]
            if new_theme != self._current_theme:
                self.set_theme(new_theme)

    def get_current_theme(self) -> str:
        """
        获取当前主题。

        Returns:
            主题名称
        """
        return self._current_theme

    def set_theme(self, theme: str) -> None:
        """
        设置主题。

        Args:
            theme: 主题名称
        """
        if theme not in ["light", "dark"]:
            theme = "light"
        
        if theme == self._current_theme:
            return
        
        self._current_theme = theme
        self._config_manager.set("general", "theme", theme)
        
        # 应用主题
        self._apply_theme()
        
        # 发布主题变更事件
        self._event_system.publish("theme_changed", {"theme": theme})
        
        # 发射主题变更信号
        self.theme_changed.emit(theme)

    def toggle_theme(self) -> None:
        """切换主题。"""
        new_theme = "dark" if self._current_theme == "light" else "light"
        self.set_theme(new_theme)

    def _apply_theme(self) -> None:
        """应用主题。"""
        app = QApplication.instance()
        if not app:
            return
        
        # 设置应用程序样式表
        style_sheet = self._get_style_sheet()
        app.setStyleSheet(style_sheet)
        
        # 设置调色板
        palette = self._get_palette()
        app.setPalette(palette)

    def _get_style_sheet(self) -> str:
        """
        获取样式表。

        Returns:
            样式表字符串
        """
        # 基于当前主题获取样式表
        if self._current_theme == "dark":
            return self._get_dark_style_sheet()
        else:
            return self._get_light_style_sheet()

    def _get_dark_style_sheet(self) -> str:
        """
        获取深色主题样式表。

        Returns:
            样式表字符串
        """
        return """
        /* 全局样式 */
        QWidget {
            background-color: #2D2D2D;
            color: #FFFFFF;
            font-family: "Segoe UI", "Microsoft YaHei", "微软雅黑", sans-serif;
            font-size: 12px;
        }
        
        /* 主窗口 */
        QMainWindow {
            background-color: #2D2D2D;
        }
        
        /* 菜单栏 */
        QMenuBar {
            background-color: #2D2D2D;
            color: #FFFFFF;
            border-bottom: 1px solid #3D3D3D;
        }
        
        QMenuBar::item {
            background-color: transparent;
            padding: 6px 10px;
            border-radius: 4px;
        }
        
        QMenuBar::item:selected {
            background-color: #3D3D3D;
        }
        
        QMenuBar::item:pressed {
            background-color: #4D4D4D;
        }
        
        /* 菜单 */
        QMenu {
            background-color: #2D2D2D;
            border: 1px solid #3D3D3D;
            border-radius: 4px;
            padding: 4px;
        }
        
        QMenu::item {
            padding: 6px 24px 6px 8px;
            border-radius: 4px;
        }
        
        QMenu::item:selected {
            background-color: #3D3D3D;
        }
        
        /* 按钮 */
        QPushButton {
            background-color: #4D4D4D;
            color: #FFFFFF;
            border: none;
            border-radius: 4px;
            padding: 8px 16px;
            min-width: 80px;
        }
        
        QPushButton:hover {
            background-color: #5D5D5D;
        }
        
        QPushButton:pressed {
            background-color: #3D3D3D;
        }
        
        QPushButton:disabled {
            background-color: #3D3D3D;
            color: #7D7D7D;
        }
        
        /* 主要按钮 */
        QPushButton[primary="true"] {
            background-color: #0078D7;
            color: #FFFFFF;
        }
        
        QPushButton[primary="true"]:hover {
            background-color: #1C88E6;
        }
        
        QPushButton[primary="true"]:pressed {
            background-color: #0067C0;
        }
        
        QPushButton[primary="true"]:disabled {
            background-color: #3D3D3D;
            color: #7D7D7D;
        }
        
        /* 输入框 */
        QLineEdit, QTextEdit, QPlainTextEdit {
            background-color: #3D3D3D;
            color: #FFFFFF;
            border: 1px solid #5D5D5D;
            border-radius: 4px;
            padding: 6px;
            selection-background-color: #0078D7;
            selection-color: #FFFFFF;
        }
        
        QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {
            border: 1px solid #0078D7;
        }
        
        QLineEdit:disabled, QTextEdit:disabled, QPlainTextEdit:disabled {
            background-color: #2D2D2D;
            color: #7D7D7D;
            border: 1px solid #3D3D3D;
        }
        
        /* 标签 */
        QLabel {
            color: #FFFFFF;
            background-color: transparent;
        }
        
        /* 复选框 */
        QCheckBox {
            color: #FFFFFF;
            background-color: transparent;
            spacing: 8px;
        }
        
        QCheckBox::indicator {
            width: 16px;
            height: 16px;
            border: 1px solid #5D5D5D;
            border-radius: 3px;
            background-color: #3D3D3D;
        }
        
        QCheckBox::indicator:checked {
            background-color: #0078D7;
            border: 1px solid #0078D7;
            image: url(:/icons/check_white.png);
        }
        
        QCheckBox::indicator:unchecked:hover {
            border: 1px solid #0078D7;
        }
        
        /* 单选按钮 */
        QRadioButton {
            color: #FFFFFF;
            background-color: transparent;
            spacing: 8px;
        }
        
        QRadioButton::indicator {
            width: 16px;
            height: 16px;
            border: 1px solid #5D5D5D;
            border-radius: 8px;
            background-color: #3D3D3D;
        }
        
        QRadioButton::indicator:checked {
            background-color: #0078D7;
            border: 1px solid #0078D7;
            image: url(:/icons/radio_white.png);
        }
        
        QRadioButton::indicator:unchecked:hover {
            border: 1px solid #0078D7;
        }
        
        /* 组合框 */
        QComboBox {
            background-color: #3D3D3D;
            color: #FFFFFF;
            border: 1px solid #5D5D5D;
            border-radius: 4px;
            padding: 6px;
            min-width: 80px;
        }
        
        QComboBox:hover {
            border: 1px solid #0078D7;
        }
        
        QComboBox:disabled {
            background-color: #2D2D2D;
            color: #7D7D7D;
            border: 1px solid #3D3D3D;
        }
        
        QComboBox::drop-down {
            subcontrol-origin: padding;
            subcontrol-position: top right;
            width: 20px;
            border-left: 1px solid #5D5D5D;
            border-top-right-radius: 4px;
            border-bottom-right-radius: 4px;
        }
        
        QComboBox::down-arrow {
            image: url(:/icons/down_arrow_white.png);
        }
        
        QComboBox QAbstractItemView {
            background-color: #3D3D3D;
            color: #FFFFFF;
            border: 1px solid #5D5D5D;
            border-radius: 4px;
            selection-background-color: #0078D7;
            selection-color: #FFFFFF;
        }
        
        /* 滚动条 */
        QScrollBar:vertical {
            background-color: #2D2D2D;
            width: 12px;
            margin: 0px;
        }
        
        QScrollBar::handle:vertical {
            background-color: #5D5D5D;
            min-height: 20px;
            border-radius: 6px;
            margin: 2px;
        }
        
        QScrollBar::handle:vertical:hover {
            background-color: #7D7D7D;
        }
        
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
            height: 0px;
        }
        
        QScrollBar:horizontal {
            background-color: #2D2D2D;
            height: 12px;
            margin: 0px;
        }
        
        QScrollBar::handle:horizontal {
            background-color: #5D5D5D;
            min-width: 20px;
            border-radius: 6px;
            margin: 2px;
        }
        
        QScrollBar::handle:horizontal:hover {
            background-color: #7D7D7D;
        }
        
        QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
            width: 0px;
        }
        
        /* 选项卡 */
        QTabWidget::pane {
            border: 1px solid #3D3D3D;
            border-radius: 4px;
            top: -1px;
        }
        
        QTabBar::tab {
            background-color: #2D2D2D;
            color: #FFFFFF;
            border: 1px solid #3D3D3D;
            border-bottom: none;
            border-top-left-radius: 4px;
            border-top-right-radius: 4px;
            padding: 8px 16px;
            min-width: 80px;
        }
        
        QTabBar::tab:selected {
            background-color: #3D3D3D;
            border-bottom: none;
        }
        
        QTabBar::tab:!selected {
            margin-top: 2px;
        }
        
        /* 进度条 */
        QProgressBar {
            background-color: #3D3D3D;
            color: #FFFFFF;
            border: none;
            border-radius: 4px;
            text-align: center;
        }
        
        QProgressBar::chunk {
            background-color: #0078D7;
            border-radius: 4px;
        }
        
        /* 列表视图 */
        QListView {
            background-color: #2D2D2D;
            color: #FFFFFF;
            border: 1px solid #3D3D3D;
            border-radius: 4px;
            outline: none;
        }
        
        QListView::item {
            padding: 6px;
            border-radius: 4px;
            margin: 2px;
        }
        
        QListView::item:selected {
            background-color: #0078D7;
            color: #FFFFFF;
        }
        
        QListView::item:hover:!selected {
            background-color: #3D3D3D;
        }
        
        /* 表格视图 */
        QTableView {
            background-color: #2D2D2D;
            color: #FFFFFF;
            border: 1px solid #3D3D3D;
            border-radius: 4px;
            gridline-color: #3D3D3D;
            outline: none;
        }
        
        QTableView::item {
            padding: 6px;
        }
        
        QTableView::item:selected {
            background-color: #0078D7;
            color: #FFFFFF;
        }
        
        QHeaderView::section {
            background-color: #3D3D3D;
            color: #FFFFFF;
            padding: 6px;
            border: none;
            border-right: 1px solid #2D2D2D;
            border-bottom: 1px solid #2D2D2D;
        }
        
        /* 树视图 */
        QTreeView {
            background-color: #2D2D2D;
            color: #FFFFFF;
            border: 1px solid #3D3D3D;
            border-radius: 4px;
            outline: none;
        }
        
        QTreeView::item {
            padding: 6px;
            border-radius: 4px;
            margin: 2px;
        }
        
        QTreeView::item:selected {
            background-color: #0078D7;
            color: #FFFFFF;
        }
        
        QTreeView::item:hover:!selected {
            background-color: #3D3D3D;
        }
        
        /* 分割线 */
        QFrame[frameShape="4"], QFrame[frameShape="5"] {
            color: #3D3D3D;
        }
        
        /* 工具提示 */
        QToolTip {
            background-color: #2D2D2D;
            color: #FFFFFF;
            border: 1px solid #3D3D3D;
            border-radius: 4px;
            padding: 4px;
        }
        
        /* 状态栏 */
        QStatusBar {
            background-color: #2D2D2D;
            color: #FFFFFF;
            border-top: 1px solid #3D3D3D;
        }
        
        /* 滑块 */
        QSlider::groove:horizontal {
            height: 4px;
            background-color: #3D3D3D;
            border-radius: 2px;
        }
        
        QSlider::handle:horizontal {
            background-color: #0078D7;
            border: none;
            width: 16px;
            height: 16px;
            margin: -6px 0;
            border-radius: 8px;
        }
        
        QSlider::handle:horizontal:hover {
            background-color: #1C88E6;
        }
        
        QSlider::sub-page:horizontal {
            background-color: #0078D7;
            border-radius: 2px;
        }
        """

    def _get_light_style_sheet(self) -> str:
        """
        获取浅色主题样式表。

        Returns:
            样式表字符串
        """
        return """
        /* 全局样式 */
        QWidget {
            background-color: #F5F5F5;
            color: #333333;
            font-family: "Segoe UI", "Microsoft YaHei", "微软雅黑", sans-serif;
            font-size: 12px;
        }
        
        /* 主窗口 */
        QMainWindow {
            background-color: #F5F5F5;
        }
        
        /* 菜单栏 */
        QMenuBar {
            background-color: #F5F5F5;
            color: #333333;
            border-bottom: 1px solid #E0E0E0;
        }
        
        QMenuBar::item {
            background-color: transparent;
            padding: 6px 10px;
            border-radius: 4px;
        }
        
        QMenuBar::item:selected {
            background-color: #E0E0E0;
        }
        
        QMenuBar::item:pressed {
            background-color: #D0D0D0;
        }
        
        /* 菜单 */
        QMenu {
            background-color: #FFFFFF;
            border: 1px solid #E0E0E0;
            border-radius: 4px;
            padding: 4px;
        }
        
        QMenu::item {
            padding: 6px 24px 6px 8px;
            border-radius: 4px;
        }
        
        QMenu::item:selected {
            background-color: #E0E0E0;
        }
        
        /* 按钮 */
        QPushButton {
            background-color: #E0E0E0;
            color: #333333;
            border: none;
            border-radius: 4px;
            padding: 8px 16px;
            min-width: 80px;
        }
        
        QPushButton:hover {
            background-color: #D0D0D0;
        }
        
        QPushButton:pressed {
            background-color: #C0C0C0;
        }
        
        QPushButton:disabled {
            background-color: #F0F0F0;
            color: #A0A0A0;
        }
        
        /* 主要按钮 */
        QPushButton[primary="true"] {
            background-color: #0078D7;
            color: #FFFFFF;
        }
        
        QPushButton[primary="true"]:hover {
            background-color: #1C88E6;
        }
        
        QPushButton[primary="true"]:pressed {
            background-color: #0067C0;
        }
        
        QPushButton[primary="true"]:disabled {
            background-color: #F0F0F0;
            color: #A0A0A0;
        }
        
        /* 输入框 */
        QLineEdit, QTextEdit, QPlainTextEdit {
            background-color: #FFFFFF;
            color: #333333;
            border: 1px solid #E0E0E0;
            border-radius: 4px;
            padding: 6px;
            selection-background-color: #0078D7;
            selection-color: #FFFFFF;
        }
        
        QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {
            border: 1px solid #0078D7;
        }
        
        QLineEdit:disabled, QTextEdit:disabled, QPlainTextEdit:disabled {
            background-color: #F5F5F5;
            color: #A0A0A0;
            border: 1px solid #E0E0E0;
        }
        
        /* 标签 */
        QLabel {
            color: #333333;
            background-color: transparent;
        }
        
        /* 复选框 */
        QCheckBox {
            color: #333333;
            background-color: transparent;
            spacing: 8px;
        }
        
        QCheckBox::indicator {
            width: 16px;
            height: 16px;
            border: 1px solid #C0C0C0;
            border-radius: 3px;
            background-color: #FFFFFF;
        }
        
        QCheckBox::indicator:checked {
            background-color: #0078D7;
            border: 1px solid #0078D7;
            image: url(:/icons/check_white.png);
        }
        
        QCheckBox::indicator:unchecked:hover {
            border: 1px solid #0078D7;
        }
        
        /* 单选按钮 */
        QRadioButton {
            color: #333333;
            background-color: transparent;
            spacing: 8px;
        }
        
        QRadioButton::indicator {
            width: 16px;
            height: 16px;
            border: 1px solid #C0C0C0;
            border-radius: 8px;
            background-color: #FFFFFF;
        }
        
        QRadioButton::indicator:checked {
            background-color: #0078D7;
            border: 1px solid #0078D7;
            image: url(:/icons/radio_white.png);
        }
        
        QRadioButton::indicator:unchecked:hover {
            border: 1px solid #0078D7;
        }
        
        /* 组合框 */
        QComboBox {
            background-color: #FFFFFF;
            color: #333333;
            border: 1px solid #E0E0E0;
            border-radius: 4px;
            padding: 6px;
            min-width: 80px;
        }
        
        QComboBox:hover {
            border: 1px solid #0078D7;
        }
        
        QComboBox:disabled {
            background-color: #F5F5F5;
            color: #A0A0A0;
            border: 1px solid #E0E0E0;
        }
        
        QComboBox::drop-down {
            subcontrol-origin: padding;
            subcontrol-position: top right;
            width: 20px;
            border-left: 1px solid #E0E0E0;
            border-top-right-radius: 4px;
            border-bottom-right-radius: 4px;
        }
        
        QComboBox::down-arrow {
            image: url(:/icons/down_arrow_dark.png);
        }
        
        QComboBox QAbstractItemView {
            background-color: #FFFFFF;
            color: #333333;
            border: 1px solid #E0E0E0;
            border-radius: 4px;
            selection-background-color: #0078D7;
            selection-color: #FFFFFF;
        }
        
        /* 滚动条 */
        QScrollBar:vertical {
            background-color: #F5F5F5;
            width: 12px;
            margin: 0px;
        }
        
        QScrollBar::handle:vertical {
            background-color: #C0C0C0;
            min-height: 20px;
            border-radius: 6px;
            margin: 2px;
        }
        
        QScrollBar::handle:vertical:hover {
            background-color: #A0A0A0;
        }
        
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
            height: 0px;
        }
        
        QScrollBar:horizontal {
            background-color: #F5F5F5;
            height: 12px;
            margin: 0px;
        }
        
        QScrollBar::handle:horizontal {
            background-color: #C0C0C0;
            min-width: 20px;
            border-radius: 6px;
            margin: 2px;
        }
        
        QScrollBar::handle:horizontal:hover {
            background-color: #A0A0A0;
        }
        
        QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
            width: 0px;
        }
        
        /* 选项卡 */
        QTabWidget::pane {
            border: 1px solid #E0E0E0;
            border-radius: 4px;
            top: -1px;
        }
        
        QTabBar::tab {
            background-color: #F5F5F5;
            color: #333333;
            border: 1px solid #E0E0E0;
            border-bottom: none;
            border-top-left-radius: 4px;
            border-top-right-radius: 4px;
            padding: 8px 16px;
            min-width: 80px;
        }
        
        QTabBar::tab:selected {
            background-color: #FFFFFF;
            border-bottom: none;
        }
        
        QTabBar::tab:!selected {
            margin-top: 2px;
        }
        
        /* 进度条 */
        QProgressBar {
            background-color: #F0F0F0;
            color: #333333;
            border: none;
            border-radius: 4px;
            text-align: center;
        }
        
        QProgressBar::chunk {
            background-color: #0078D7;
            border-radius: 4px;
        }
        
        /* 列表视图 */
        QListView {
            background-color: #FFFFFF;
            color: #333333;
            border: 1px solid #E0E0E0;
            border-radius: 4px;
            outline: none;
        }
        
        QListView::item {
            padding: 6px;
            border-radius: 4px;
            margin: 2px;
        }
        
        QListView::item:selected {
            background-color: #0078D7;
            color: #FFFFFF;
        }
        
        QListView::item:hover:!selected {
            background-color: #F0F0F0;
        }
        
        /* 表格视图 */
        QTableView {
            background-color: #FFFFFF;
            color: #333333;
            border: 1px solid #E0E0E0;
            border-radius: 4px;
            gridline-color: #E0E0E0;
            outline: none;
        }
        
        QTableView::item {
            padding: 6px;
        }
        
        QTableView::item:selected {
            background-color: #0078D7;
            color: #FFFFFF;
        }
        
        QHeaderView::section {
            background-color: #F0F0F0;
            color: #333333;
            padding: 6px;
            border: none;
            border-right: 1px solid #E0E0E0;
            border-bottom: 1px solid #E0E0E0;
        }
        
        /* 树视图 */
        QTreeView {
            background-color: #FFFFFF;
            color: #333333;
            border: 1px solid #E0E0E0;
            border-radius: 4px;
            outline: none;
        }
        
        QTreeView::item {
            padding: 6px;
            border-radius: 4px;
            margin: 2px;
        }
        
        QTreeView::item:selected {
            background-color: #0078D7;
            color: #FFFFFF;
        }
        
        QTreeView::item:hover:!selected {
            background-color: #F0F0F0;
        }
        
        /* 分割线 */
        QFrame[frameShape="4"], QFrame[frameShape="5"] {
            color: #E0E0E0;
        }
        
        /* 工具提示 */
        QToolTip {
            background-color: #FFFFFF;
            color: #333333;
            border: 1px solid #E0E0E0;
            border-radius: 4px;
            padding: 4px;
        }
        
        /* 状态栏 */
        QStatusBar {
            background-color: #F5F5F5;
            color: #333333;
            border-top: 1px solid #E0E0E0;
        }
        
        /* 滑块 */
        QSlider::groove:horizontal {
            height: 4px;
            background-color: #E0E0E0;
            border-radius: 2px;
        }
        
        QSlider::handle:horizontal {
            background-color: #0078D7;
            border: none;
            width: 16px;
            height: 16px;
            margin: -6px 0;
            border-radius: 8px;
        }
        
        QSlider::handle:horizontal:hover {
            background-color: #1C88E6;
        }
        
        QSlider::sub-page:horizontal {
            background-color: #0078D7;
            border-radius: 2px;
        }
        """

    def _get_palette(self) -> QPalette:
        """
        获取调色板。

        Returns:
            调色板
        """
        palette = QPalette()
        
        if self._current_theme == "dark":
            # 深色主题调色板
            palette.setColor(QPalette.ColorRole.Window, QColor("#2D2D2D"))
            palette.setColor(QPalette.ColorRole.WindowText, QColor("#FFFFFF"))
            palette.setColor(QPalette.ColorRole.Base, QColor("#3D3D3D"))
            palette.setColor(QPalette.ColorRole.AlternateBase, QColor("#2D2D2D"))
            palette.setColor(QPalette.ColorRole.ToolTipBase, QColor("#2D2D2D"))
            palette.setColor(QPalette.ColorRole.ToolTipText, QColor("#FFFFFF"))
            palette.setColor(QPalette.ColorRole.Text, QColor("#FFFFFF"))
            palette.setColor(QPalette.ColorRole.Button, QColor("#4D4D4D"))
            palette.setColor(QPalette.ColorRole.ButtonText, QColor("#FFFFFF"))
            palette.setColor(QPalette.ColorRole.BrightText, QColor("#FFFFFF"))
            palette.setColor(QPalette.ColorRole.Link, QColor("#0078D7"))
            palette.setColor(QPalette.ColorRole.Highlight, QColor("#0078D7"))
            palette.setColor(QPalette.ColorRole.HighlightedText, QColor("#FFFFFF"))
        else:
            # 浅色主题调色板
            palette.setColor(QPalette.ColorRole.Window, QColor("#F5F5F5"))
            palette.setColor(QPalette.ColorRole.WindowText, QColor("#333333"))
            palette.setColor(QPalette.ColorRole.Base, QColor("#FFFFFF"))
            palette.setColor(QPalette.ColorRole.AlternateBase, QColor("#F5F5F5"))
            palette.setColor(QPalette.ColorRole.ToolTipBase, QColor("#FFFFFF"))
            palette.setColor(QPalette.ColorRole.ToolTipText, QColor("#333333"))
            palette.setColor(QPalette.ColorRole.Text, QColor("#333333"))
            palette.setColor(QPalette.ColorRole.Button, QColor("#E0E0E0"))
            palette.setColor(QPalette.ColorRole.ButtonText, QColor("#333333"))
            palette.setColor(QPalette.ColorRole.BrightText, QColor("#000000"))
            palette.setColor(QPalette.ColorRole.Link, QColor("#0078D7"))
            palette.setColor(QPalette.ColorRole.Highlight, QColor("#0078D7"))
            palette.setColor(QPalette.ColorRole.HighlightedText, QColor("#FFFFFF"))
        
        return palette

    def get_color(self, name: str) -> QColor:
        """
        获取主题颜色。

        Args:
            name: 颜色名称

        Returns:
            颜色
        """
        if self._current_theme == "dark":
            # 深色主题颜色
            colors = {
                "background": QColor("#2D2D2D"),
                "foreground": QColor("#FFFFFF"),
                "primary": QColor("#0078D7"),
                "secondary": QColor("#4D4D4D"),
                "accent": QColor("#0078D7"),
                "success": QColor("#107C10"),
                "warning": QColor("#D83B01"),
                "error": QColor("#E81123"),
                "info": QColor("#0078D7"),
                "border": QColor("#3D3D3D"),
                "hover": QColor("#5D5D5D"),
                "pressed": QColor("#3D3D3D"),
                "disabled": QColor("#7D7D7D"),
                "highlight": QColor("#0078D7"),
                "highlight_text": QColor("#FFFFFF"),
            }
        else:
            # 浅色主题颜色
            colors = {
                "background": QColor("#F5F5F5"),
                "foreground": QColor("#333333"),
                "primary": QColor("#0078D7"),
                "secondary": QColor("#E0E0E0"),
                "accent": QColor("#0078D7"),
                "success": QColor("#107C10"),
                "warning": QColor("#D83B01"),
                "error": QColor("#E81123"),
                "info": QColor("#0078D7"),
                "border": QColor("#E0E0E0"),
                "hover": QColor("#D0D0D0"),
                "pressed": QColor("#C0C0C0"),
                "disabled": QColor("#A0A0A0"),
                "highlight": QColor("#0078D7"),
                "highlight_text": QColor("#FFFFFF"),
            }
        
        return colors.get(name, QColor("#000000"))

    def get_blur_opacity(self) -> float:
        """
        获取毛玻璃效果的不透明度。

        Returns:
            不透明度（0-1）
        """
        return self._config_manager.get("ui", "opacity", 0.95)

    def is_blur_effect_enabled(self) -> bool:
        """
        检查是否启用毛玻璃效果。

        Returns:
            是否启用毛玻璃效果
        """
        return self._config_manager.get("ui", "blur_effect", True)

    def get_animation_speed(self) -> int:
        """
        获取动画速度。

        Returns:
            动画速度（毫秒）
        """
        return self._config_manager.get("ui", "animation_speed", 300)

    def get_font_size(self) -> int:
        """
        获取字体大小。

        Returns:
            字体大小
        """
        return self._config_manager.get("ui", "font_size", 12)
