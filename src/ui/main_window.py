"""
主窗口模块，应用程序的主界面。
"""
import os
from typing import Optional

from PyQt6.QtCore import QEasingCurve, QPropertyAnimation, QRect, QSize, Qt, pyqtSignal
from PyQt6.QtGui import QAction, QCloseEvent, QColor, QIcon, QPixmap
from PyQt6.QtWidgets import (
    QApplication, QFrame, QHBoxLayout, QLabel, QMainWindow, QMenu, 
    QPushButton, QSizePolicy, QStackedWidget, QVBoxLayout, QWidget
)

from ..core.config_manager import ConfigManager
from ..core.event_system import EventSystem
from .theme_manager import ThemeManager
from .ui_utils import AnimationHelper, GlassWidget, RoundedRectWidget, ShadowEffect


class SidebarButton(QPushButton):
    """侧边栏按钮类，自定义的侧边栏按钮。"""

    def __init__(self, icon_path: str, text: str, parent: Optional[QWidget] = None):
        """
        初始化侧边栏按钮。

        Args:
            icon_path: 图标路径
            text: 按钮文本
            parent: 父窗口
        """
        super().__init__(parent)
        self.setText(text)
        self.setIcon(QIcon(icon_path))
        self.setIconSize(QSize(24, 24))
        self.setCheckable(True)
        self.setFixedHeight(40)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setStyleSheet("""
            QPushButton {
                text-align: left;
                padding-left: 15px;
                border: none;
                border-radius: 5px;
                margin: 2px 5px;
            }
            
            QPushButton:checked {
                background-color: rgba(0, 120, 215, 0.2);
            }
            
            QPushButton:hover:!checked {
                background-color: rgba(0, 0, 0, 0.05);
            }
        """)


class Sidebar(QWidget):
    """侧边栏类，应用程序的导航侧边栏。"""

    # 页面切换信号
    page_changed = pyqtSignal(int)

    def __init__(
        self,
        parent: Optional[QWidget] = None,
        config_manager: Optional[ConfigManager] = None,
        theme_manager: Optional[ThemeManager] = None,
    ):
        """
        初始化侧边栏。

        Args:
            parent: 父窗口
            config_manager: 配置管理器实例
            theme_manager: 主题管理器实例
        """
        super().__init__(parent)
        self._config_manager = config_manager or ConfigManager()
        self._theme_manager = theme_manager or ThemeManager(self._config_manager)
        self._current_page = 0
        self._buttons = []
        
        # 设置布局
        self._init_ui()
        
        # 连接信号
        self._theme_manager.theme_changed.connect(self._update_theme)

    def _init_ui(self):
        """初始化UI。"""
        # 主布局
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 10, 0, 10)
        main_layout.setSpacing(5)
        
        # 应用标题
        title_layout = QHBoxLayout()
        title_layout.setContentsMargins(15, 5, 15, 15)
        
        app_icon = QLabel()
        icon_pixmap = QPixmap(":/icons/app_icon.png")
        if not icon_pixmap.isNull():
            app_icon.setPixmap(icon_pixmap.scaled(32, 32, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        app_icon.setFixedSize(32, 32)
        
        app_title = QLabel("ideaSystemXS")
        app_title.setStyleSheet("font-size: 16px; font-weight: bold;")
        
        title_layout.addWidget(app_icon)
        title_layout.addWidget(app_title)
        title_layout.addStretch()
        
        main_layout.addLayout(title_layout)
        
        # 分隔线
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        separator.setFixedHeight(1)
        main_layout.addWidget(separator)
        main_layout.addSpacing(10)
        
        # 导航按钮
        self._add_nav_buttons(main_layout)
        
        # 底部按钮
        main_layout.addStretch()
        self._add_bottom_buttons(main_layout)

    def _add_nav_buttons(self, layout: QVBoxLayout):
        """
        添加导航按钮。

        Args:
            layout: 布局
        """
        # 仪表盘
        dashboard_btn = SidebarButton(":/icons/dashboard.png", "仪表盘", self)
        dashboard_btn.setChecked(True)
        dashboard_btn.clicked.connect(lambda: self._handle_button_click(0))
        layout.addWidget(dashboard_btn)
        self._buttons.append(dashboard_btn)
        
        # 想法管理
        ideas_btn = SidebarButton(":/icons/ideas.png", "想法管理", self)
        ideas_btn.clicked.connect(lambda: self._handle_button_click(1))
        layout.addWidget(ideas_btn)
        self._buttons.append(ideas_btn)
        
        # 标签管理
        tags_btn = SidebarButton(":/icons/tags.png", "标签管理", self)
        tags_btn.clicked.connect(lambda: self._handle_button_click(2))
        layout.addWidget(tags_btn)
        self._buttons.append(tags_btn)
        
        # 搜索
        search_btn = SidebarButton(":/icons/search.png", "搜索", self)
        search_btn.clicked.connect(lambda: self._handle_button_click(3))
        layout.addWidget(search_btn)
        self._buttons.append(search_btn)
        
        # AI控制台
        ai_console_btn = SidebarButton(":/icons/ai.png", "AI控制台", self)
        ai_console_btn.clicked.connect(lambda: self._handle_button_click(4))
        layout.addWidget(ai_console_btn)
        self._buttons.append(ai_console_btn)

    def _add_bottom_buttons(self, layout: QVBoxLayout):
        """
        添加底部按钮。

        Args:
            layout: 布局
        """
        # 设置
        settings_btn = SidebarButton(":/icons/settings.png", "设置", self)
        settings_btn.clicked.connect(lambda: self._handle_button_click(5))
        layout.addWidget(settings_btn)
        self._buttons.append(settings_btn)

    def _handle_button_click(self, index: int):
        """
        处理按钮点击事件。

        Args:
            index: 按钮索引
        """
        if index == self._current_page:
            return
        
        # 更新按钮状态
        for i, btn in enumerate(self._buttons):
            btn.setChecked(i == index)
        
        # 更新当前页面
        self._current_page = index
        
        # 发射页面切换信号
        self.page_changed.emit(index)

    def _update_theme(self, theme: str):
        """
        更新主题。

        Args:
            theme: 主题名称
        """
        # 更新按钮样式
        for btn in self._buttons:
            if theme == "dark":
                btn.setStyleSheet("""
                    QPushButton {
                        text-align: left;
                        padding-left: 15px;
                        border: none;
                        border-radius: 5px;
                        margin: 2px 5px;
                        color: #FFFFFF;
                    }
                    
                    QPushButton:checked {
                        background-color: rgba(0, 120, 215, 0.3);
                    }
                    
                    QPushButton:hover:!checked {
                        background-color: rgba(255, 255, 255, 0.1);
                    }
                """)
            else:
                btn.setStyleSheet("""
                    QPushButton {
                        text-align: left;
                        padding-left: 15px;
                        border: none;
                        border-radius: 5px;
                        margin: 2px 5px;
                        color: #333333;
                    }
                    
                    QPushButton:checked {
                        background-color: rgba(0, 120, 215, 0.2);
                    }
                    
                    QPushButton:hover:!checked {
                        background-color: rgba(0, 0, 0, 0.05);
                    }
                """)

    def set_current_page(self, index: int):
        """
        设置当前页面。

        Args:
            index: 页面索引
        """
        self._handle_button_click(index)


class TitleBar(QWidget):
    """标题栏类，自定义的窗口标题栏。"""

    # 窗口控制信号
    minimize_clicked = pyqtSignal()
    maximize_clicked = pyqtSignal()
    close_clicked = pyqtSignal()

    def __init__(
        self,
        parent: Optional[QWidget] = None,
        config_manager: Optional[ConfigManager] = None,
        theme_manager: Optional[ThemeManager] = None,
    ):
        """
        初始化标题栏。

        Args:
            parent: 父窗口
            config_manager: 配置管理器实例
            theme_manager: 主题管理器实例
        """
        super().__init__(parent)
        self._config_manager = config_manager or ConfigManager()
        self._theme_manager = theme_manager or ThemeManager(self._config_manager)
        self._is_maximized = False
        self._drag_position = None
        
        # 设置布局
        self._init_ui()
        
        # 连接信号
        self._theme_manager.theme_changed.connect(self._update_theme)

    def _init_ui(self):
        """初始化UI。"""
        # 设置固定高度
        self.setFixedHeight(40)
        
        # 主布局
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(10, 0, 10, 0)
        main_layout.setSpacing(0)
        
        # 标题
        self._title_label = QLabel("ideaSystemXS")
        self._title_label.setStyleSheet("font-size: 14px;")
        main_layout.addWidget(self._title_label)
        main_layout.addStretch()
        
        # 窗口控制按钮
        self._minimize_btn = QPushButton()
        self._minimize_btn.setFixedSize(16, 16)
        self._minimize_btn.setStyleSheet("""
            QPushButton {
                background-color: #FFBD44;
                border: none;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #FFD369;
            }
        """)
        self._minimize_btn.clicked.connect(self.minimize_clicked)
        
        self._maximize_btn = QPushButton()
        self._maximize_btn.setFixedSize(16, 16)
        self._maximize_btn.setStyleSheet("""
            QPushButton {
                background-color: #00CA4E;
                border: none;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #2EE66E;
            }
        """)
        self._maximize_btn.clicked.connect(self._handle_maximize_clicked)
        
        self._close_btn = QPushButton()
        self._close_btn.setFixedSize(16, 16)
        self._close_btn.setStyleSheet("""
            QPushButton {
                background-color: #FF605C;
                border: none;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #FF8A87;
            }
        """)
        self._close_btn.clicked.connect(self.close_clicked)
        
        # 按macOS风格，从左到右依次是关闭、最小化、最大化
        main_layout.addWidget(self._close_btn)
        main_layout.addSpacing(8)
        main_layout.addWidget(self._minimize_btn)
        main_layout.addSpacing(8)
        main_layout.addWidget(self._maximize_btn)

    def _handle_maximize_clicked(self):
        """处理最大化按钮点击事件。"""
        self._is_maximized = not self._is_maximized
        self.maximize_clicked.emit()

    def _update_theme(self, theme: str):
        """
        更新主题。

        Args:
            theme: 主题名称
        """
        if theme == "dark":
            self._title_label.setStyleSheet("font-size: 14px; color: #FFFFFF;")
        else:
            self._title_label.setStyleSheet("font-size: 14px; color: #333333;")

    def mousePressEvent(self, event):
        """
        鼠标按下事件。

        Args:
            event: 鼠标事件
        """
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_position = event.globalPosition().toPoint() - self.parent().frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        """
        鼠标移动事件。

        Args:
            event: 鼠标事件
        """
        if event.buttons() == Qt.MouseButton.LeftButton and self._drag_position is not None:
            self.parent().move(event.globalPosition().toPoint() - self._drag_position)
            event.accept()

    def mouseDoubleClickEvent(self, event):
        """
        鼠标双击事件。

        Args:
            event: 鼠标事件
        """
        if event.button() == Qt.MouseButton.LeftButton:
            self._handle_maximize_clicked()
            event.accept()

    def set_title(self, title: str):
        """
        设置标题。

        Args:
            title: 标题
        """
        self._title_label.setText(title)

    def set_maximized(self, maximized: bool):
        """
        设置最大化状态。

        Args:
            maximized: 是否最大化
        """
        self._is_maximized = maximized


class MainWindow(QMainWindow):
    """主窗口类，应用程序的主界面。"""

    def __init__(
        self,
        config_manager: Optional[ConfigManager] = None,
        event_system: Optional[EventSystem] = None,
        theme_manager: Optional[ThemeManager] = None,
    ):
        """
        初始化主窗口。

        Args:
            config_manager: 配置管理器实例
            event_system: 事件系统实例
            theme_manager: 主题管理器实例
        """
        super().__init__()
        self._config_manager = config_manager or ConfigManager()
        self._event_system = event_system or EventSystem()
        self._theme_manager = theme_manager or ThemeManager(self._config_manager)
        
        # 设置窗口属性
        self.setWindowTitle("ideaSystemXS")
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # 设置窗口大小
        self.resize(1200, 800)
        
        # 初始化UI
        self._init_ui()
        
        # 连接信号
        self._connect_signals()
        
        # 注册事件处理器
        self._register_event_handlers()

    def _init_ui(self):
        """初始化UI。"""
        # 主窗口容器
        self._container = RoundedRectWidget(
            self,
            radius=10,
            background_color=QColor(245, 245, 245) if self._theme_manager.get_current_theme() == "light" else QColor(45, 45, 45),
            border_color=QColor(200, 200, 200) if self._theme_manager.get_current_theme() == "light" else QColor(60, 60, 60),
            border_width=1,
        )
        self.setCentralWidget(self._container)
        
        # 添加阴影效果
        shadow = ShadowEffect(self._container)
        self._container.setGraphicsEffect(shadow)
        
        # 主布局
        main_layout = QVBoxLayout(self._container)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # 标题栏
        self._title_bar = TitleBar(self._container, self._config_manager, self._theme_manager)
        main_layout.addWidget(self._title_bar)
        
        # 内容区域
        content_layout = QHBoxLayout()
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)
        
        # 侧边栏
        self._sidebar = Sidebar(self._container, self._config_manager, self._theme_manager)
        self._sidebar.setFixedWidth(200)
        content_layout.addWidget(self._sidebar)
        
        # 分隔线
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.VLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        separator.setFixedWidth(1)
        content_layout.addWidget(separator)
        
        # 内容区域
        self._content_stack = QStackedWidget()
        content_layout.addWidget(self._content_stack)
        
        # 添加页面
        self._add_pages()
        
        main_layout.addLayout(content_layout)

    def _add_pages(self):
        """添加页面。"""
        # 仪表盘页面
        dashboard_page = QWidget()
        dashboard_layout = QVBoxLayout(dashboard_page)
        dashboard_layout.addWidget(QLabel("仪表盘页面"))
        self._content_stack.addWidget(dashboard_page)
        
        # 想法管理页面
        ideas_page = QWidget()
        ideas_layout = QVBoxLayout(ideas_page)
        ideas_layout.addWidget(QLabel("想法管理页面"))
        self._content_stack.addWidget(ideas_page)
        
        # 标签管理页面
        tags_page = QWidget()
        tags_layout = QVBoxLayout(tags_page)
        tags_layout.addWidget(QLabel("标签管理页面"))
        self._content_stack.addWidget(tags_page)
        
        # 搜索页面
        search_page = QWidget()
        search_layout = QVBoxLayout(search_page)
        search_layout.addWidget(QLabel("搜索页面"))
        self._content_stack.addWidget(search_page)
        
        # AI控制台页面
        ai_console_page = QWidget()
        ai_console_layout = QVBoxLayout(ai_console_page)
        ai_console_layout.addWidget(QLabel("AI控制台页面"))
        self._content_stack.addWidget(ai_console_page)
        
        # 设置页面
        settings_page = QWidget()
        settings_layout = QVBoxLayout(settings_page)
        settings_layout.addWidget(QLabel("设置页面"))
        self._content_stack.addWidget(settings_page)

    def _connect_signals(self):
        """连接信号。"""
        # 侧边栏页面切换信号
        self._sidebar.page_changed.connect(self._content_stack.setCurrentIndex)
        
        # 标题栏窗口控制信号
        self._title_bar.minimize_clicked.connect(self.showMinimized)
        self._title_bar.maximize_clicked.connect(self._toggle_maximize)
        self._title_bar.close_clicked.connect(self.close)
        
        # 主题变更信号
        self._theme_manager.theme_changed.connect(self._update_theme)

    def _register_event_handlers(self):
        """注册事件处理器。"""
        # 显示主窗口事件
        self._event_system.subscribe("show_main_window", self._handle_show_main_window)
        
        # 显示设置窗口事件
        self._event_system.subscribe("show_settings_window", self._handle_show_settings_window)

    def _handle_show_main_window(self, data=None):
        """
        处理显示主窗口事件。

        Args:
            data: 事件数据
        """
        self.show()
        self.activateWindow()

    def _handle_show_settings_window(self, data=None):
        """
        处理显示设置窗口事件。

        Args:
            data: 事件数据
        """
        self._sidebar.set_current_page(5)  # 设置页面索引为5

    def _toggle_maximize(self):
        """切换最大化状态。"""
        if self.isMaximized():
            self.showNormal()
            self._title_bar.set_maximized(False)
        else:
            self.showMaximized()
            self._title_bar.set_maximized(True)

    def _update_theme(self, theme: str):
        """
        更新主题。

        Args:
            theme: 主题名称
        """
        # 更新窗口背景颜色
        if theme == "light":
            self._container.setProperty("_background_color", QColor(245, 245, 245))
            self._container.setProperty("_border_color", QColor(200, 200, 200))
        else:
            self._container.setProperty("_background_color", QColor(45, 45, 45))
            self._container.setProperty("_border_color", QColor(60, 60, 60))
        
        # 刷新窗口
        self._container.update()

    def closeEvent(self, event: QCloseEvent):
        """
        关闭事件。

        Args:
            event: 关闭事件
        """
        # 发布应用程序退出事件
        self._event_system.publish("app_exit")
        event.accept()

    def show_with_animation(self):
        """使用动画显示窗口。"""
        # 设置初始透明度
        self.setWindowOpacity(0.0)
        
        # 显示窗口
        self.show()
        
        # 创建淡入动画
        fade_in_anim = AnimationHelper.fade_in(self)
        fade_in_anim.start()
