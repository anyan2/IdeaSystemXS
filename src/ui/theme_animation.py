"""
主题切换功能模块，用于实现主题切换功能。
"""
from typing import Optional

from PyQt6.QtCore import QEasingCurve, QPropertyAnimation, QSize, Qt, pyqtSignal
from PyQt6.QtGui import QColor, QIcon
from PyQt6.QtWidgets import (
    QApplication, QFrame, QHBoxLayout, QLabel, QPushButton, 
    QStackedWidget, QVBoxLayout, QWidget
)

from src.core.config_manager import ConfigManager
from src.core.event_system import EventSystem
from .theme_manager import ThemeManager
from .ui_utils import AnimationHelper, RoundedRectWidget, ShadowEffect


class ThemeSwitcherWidget(QWidget):
    """主题切换器类，用于切换应用程序主题。"""

    def __init__(
        self,
        parent: Optional[QWidget] = None,
        config_manager: Optional[ConfigManager] = None,
        event_system: Optional[EventSystem] = None,
        theme_manager: Optional[ThemeManager] = None,
    ):
        """
        初始化主题切换器。

        Args:
            parent: 父窗口
            config_manager: 配置管理器实例
            event_system: 事件系统实例
            theme_manager: 主题管理器实例
        """
        super().__init__(parent)
        self._config_manager = config_manager or ConfigManager()
        self._event_system = event_system or EventSystem()
        self._theme_manager = theme_manager or ThemeManager(self._config_manager)
        
        # 初始化UI
        self._init_ui()
        
        # 连接信号
        self._connect_signals()

    def _init_ui(self):
        """初始化UI。"""
        # 主布局
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # 标题
        title_label = QLabel("主题设置")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        main_layout.addWidget(title_label)
        
        # 主题选择
        themes_layout = QHBoxLayout()
        themes_layout.setContentsMargins(0, 0, 0, 0)
        themes_layout.setSpacing(20)
        
        # 浅色主题
        light_theme = RoundedRectWidget(
            radius=10,
            background_color=QColor(245, 245, 245),
            border_color=QColor(200, 200, 200),
            border_width=1,
        )
        light_layout = QVBoxLayout(light_theme)
        light_layout.setContentsMargins(15, 15, 15, 15)
        light_layout.setSpacing(10)
        
        light_title = QLabel("浅色主题")
        light_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #333333;")
        light_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        light_preview = QWidget()
        light_preview.setFixedHeight(150)
        light_preview.setStyleSheet("""
            QWidget {
                background-color: white;
                border-radius: 5px;
                border: 1px solid #E0E0E0;
            }
        """)
        
        light_select_btn = QPushButton("选择")
        light_select_btn.setStyleSheet("""
            QPushButton {
                background-color: #0078D7;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1C88E6;
            }
            QPushButton:pressed {
                background-color: #0067C0;
            }
        """)
        light_select_btn.clicked.connect(lambda: self._set_theme("light"))
        
        light_layout.addWidget(light_title)
        light_layout.addWidget(light_preview)
        light_layout.addWidget(light_select_btn)
        
        # 深色主题
        dark_theme = RoundedRectWidget(
            radius=10,
            background_color=QColor(45, 45, 45),
            border_color=QColor(60, 60, 60),
            border_width=1,
        )
        dark_layout = QVBoxLayout(dark_theme)
        dark_layout.setContentsMargins(15, 15, 15, 15)
        dark_layout.setSpacing(10)
        
        dark_title = QLabel("深色主题")
        dark_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #FFFFFF;")
        dark_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        dark_preview = QWidget()
        dark_preview.setFixedHeight(150)
        dark_preview.setStyleSheet("""
            QWidget {
                background-color: #3D3D3D;
                border-radius: 5px;
                border: 1px solid #5D5D5D;
            }
        """)
        
        dark_select_btn = QPushButton("选择")
        dark_select_btn.setStyleSheet("""
            QPushButton {
                background-color: #0078D7;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1C88E6;
            }
            QPushButton:pressed {
                background-color: #0067C0;
            }
        """)
        dark_select_btn.clicked.connect(lambda: self._set_theme("dark"))
        
        dark_layout.addWidget(dark_title)
        dark_layout.addWidget(dark_preview)
        dark_layout.addWidget(dark_select_btn)
        
        themes_layout.addWidget(light_theme)
        themes_layout.addWidget(dark_theme)
        
        main_layout.addLayout(themes_layout)
        
        # 当前主题
        current_theme_layout = QHBoxLayout()
        current_theme_layout.setContentsMargins(0, 0, 0, 0)
        current_theme_layout.setSpacing(10)
        
        current_theme_label = QLabel("当前主题:")
        
        self._current_theme_value = QLabel(
            "浅色" if self._theme_manager.get_current_theme() == "light" else "深色"
        )
        self._current_theme_value.setStyleSheet("font-weight: bold;")
        
        current_theme_layout.addWidget(current_theme_label)
        current_theme_layout.addWidget(self._current_theme_value)
        current_theme_layout.addStretch()
        
        main_layout.addLayout(current_theme_layout)
        
        # 添加伸缩项
        main_layout.addStretch()
        
        # 添加阴影效果
        light_shadow = ShadowEffect(light_theme)
        light_theme.setGraphicsEffect(light_shadow)
        
        dark_shadow = ShadowEffect(dark_theme)
        dark_theme.setGraphicsEffect(dark_shadow)

    def _connect_signals(self):
        """连接信号。"""
        # 主题变更信号
        self._theme_manager.theme_changed.connect(self._update_current_theme)

    def _set_theme(self, theme: str):
        """
        设置主题。

        Args:
            theme: 主题名称
        """
        # 设置主题
        self._theme_manager.set_theme(theme)
        
        # 保存主题设置
        self._config_manager.set("general", "theme", theme)

    def _update_current_theme(self, theme: str):
        """
        更新当前主题显示。

        Args:
            theme: 主题名称
        """
        # 更新当前主题值
        self._current_theme_value.setText("浅色" if theme == "light" else "深色")


class AnimationDemoWidget(QWidget):
    """动画演示类，用于展示各种动画效果。"""

    def __init__(
        self,
        parent: Optional[QWidget] = None,
        config_manager: Optional[ConfigManager] = None,
        event_system: Optional[EventSystem] = None,
        theme_manager: Optional[ThemeManager] = None,
    ):
        """
        初始化动画演示。

        Args:
            parent: 父窗口
            config_manager: 配置管理器实例
            event_system: 事件系统实例
            theme_manager: 主题管理器实例
        """
        super().__init__(parent)
        self._config_manager = config_manager or ConfigManager()
        self._event_system = event_system or EventSystem()
        self._theme_manager = theme_manager or ThemeManager(self._config_manager)
        
        # 初始化UI
        self._init_ui()
        
        # 连接信号
        self._connect_signals()

    def _init_ui(self):
        """初始化UI。"""
        # 主布局
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # 标题
        title_label = QLabel("动画效果演示")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        main_layout.addWidget(title_label)
        
        # 动画类型
        animations_layout = QHBoxLayout()
        animations_layout.setContentsMargins(0, 0, 0, 0)
        animations_layout.setSpacing(10)
        
        fade_btn = QPushButton("淡入淡出")
        fade_btn.clicked.connect(self._demo_fade)
        
        slide_btn = QPushButton("滑动")
        slide_btn.clicked.connect(self._demo_slide)
        
        scale_btn = QPushButton("缩放")
        scale_btn.clicked.connect(self._demo_scale)
        
        animations_layout.addWidget(fade_btn)
        animations_layout.addWidget(slide_btn)
        animations_layout.addWidget(scale_btn)
        animations_layout.addStretch()
        
        main_layout.addLayout(animations_layout)
        
        # 动画演示区域
        self._demo_container = QWidget()
        self._demo_container.setFixedHeight(300)
        self._demo_container.setStyleSheet("""
            QWidget {
                background-color: #F5F5F5;
                border-radius: 10px;
                border: 1px solid #E0E0E0;
            }
        """)
        
        demo_layout = QVBoxLayout(self._demo_container)
        demo_layout.setContentsMargins(0, 0, 0, 0)
        demo_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self._demo_widget = RoundedRectWidget(
            radius=10,
            background_color=QColor(0, 120, 215),
            border_color=QColor(0, 100, 195),
            border_width=1,
        )
        self._demo_widget.setFixedSize(100, 100)
        
        demo_layout.addWidget(self._demo_widget, 0, Qt.AlignmentFlag.AlignCenter)
        
        main_layout.addWidget(self._demo_container)
        
        # 添加伸缩项
        main_layout.addStretch()

    def _connect_signals(self):
        """连接信号。"""
        # 主题变更信号
        self._theme_manager.theme_changed.connect(self._update_theme)

    def _update_theme(self, theme: str):
        """
        更新主题。

        Args:
            theme: 主题名称
        """
        if theme == "light":
            self._demo_container.setStyleSheet("""
                QWidget {
                    background-color: #F5F5F5;
                    border-radius: 10px;
                    border: 1px solid #E0E0E0;
                }
            """)
        else:
            self._demo_container.setStyleSheet("""
                QWidget {
                    background-color: #3D3D3D;
                    border-radius: 10px;
                    border: 1px solid #5D5D5D;
                }
            """)

    def _demo_fade(self):
        """演示淡入淡出动画。"""
        # 创建淡出动画
        fade_out = AnimationHelper.fade_out(self._demo_widget, duration=500)
        
        # 创建淡入动画
        fade_in = AnimationHelper.fade_in(self._demo_widget, duration=500)
        
        # 连接动画
        fade_out.finished.connect(fade_in.start)
        
        # 开始动画
        fade_out.start()

    def _demo_slide(self):
        """演示滑动动画。"""
        # 保存原始位置
        original_pos = self._demo_widget.pos()
        
        # 创建向右滑出动画
        slide_out = AnimationHelper.slide_out(self._demo_widget, direction="right", duration=500)
        
        # 创建向左滑入动画
        slide_in = AnimationHelper.slide_in(self._demo_widget, direction="left", duration=500)
        
        # 连接动画
        slide_out.finished.connect(slide_in.start)
        
        # 开始动画
        slide_out.start()

    def _demo_scale(self):
        """演示缩放动画。"""
        # 创建缩小动画
        scale_down = AnimationHelper.scale(self._demo_widget, duration=500, start_value=1.0, end_value=0.5)
        
        # 创建放大动画
        scale_up = AnimationHelper.scale(self._demo_widget, duration=500, start_value=0.5, end_value=1.0)
        
        # 连接动画
        scale_down.finished.connect(scale_up.start)
        
        # 开始动画
        scale_down.start()


class ThemeAndAnimationWidget(QWidget):
    """主题和动画设置界面类，用于设置主题和查看动画效果。"""

    def __init__(
        self,
        parent: Optional[QWidget] = None,
        config_manager: Optional[ConfigManager] = None,
        event_system: Optional[EventSystem] = None,
        theme_manager: Optional[ThemeManager] = None,
    ):
        """
        初始化主题和动画设置界面。

        Args:
            parent: 父窗口
            config_manager: 配置管理器实例
            event_system: 事件系统实例
            theme_manager: 主题管理器实例
        """
        super().__init__(parent)
        self._config_manager = config_manager or ConfigManager()
        self._event_system = event_system or EventSystem()
        self._theme_manager = theme_manager or ThemeManager(self._config_manager)
        
        # 初始化UI
        self._init_ui()
        
        # 连接信号
        self._connect_signals()

    def _init_ui(self):
        """初始化UI。"""
        # 主布局
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # 选项卡
        tabs_layout = QHBoxLayout()
        tabs_layout.setContentsMargins(20, 20, 20, 0)
        tabs_layout.setSpacing(10)
        
        self._theme_tab_btn = QPushButton("主题设置")
        self._theme_tab_btn.setCheckable(True)
        self._theme_tab_btn.setChecked(True)
        self._theme_tab_btn.clicked.connect(lambda: self._switch_tab(0))
        
        self._animation_tab_btn = QPushButton("动画效果")
        self._animation_tab_btn.setCheckable(True)
        self._animation_tab_btn.clicked.connect(lambda: self._switch_tab(1))
        
        tabs_layout.addWidget(self._theme_tab_btn)
        tabs_layout.addWidget(self._animation_tab_btn)
        tabs_layout.addStretch()
        
        main_layout.addLayout(tabs_layout)
        
        # 分隔线
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        separator.setFixedHeight(1)
        main_layout.addWidget(separator)
        
        # 内容区域
        self._content_stack = QStackedWidget()
        
        # 主题设置页面
        self._theme_switcher = ThemeSwitcherWidget(
            self._content_stack,
            self._config_manager,
            self._event_system,
            self._theme_manager,
        )
        self._content_stack.addWidget(self._theme_switcher)
        
        # 动画效果页面
        self._animation_demo = AnimationDemoWidget(
            self._content_stack,
            self._config_manager,
            self._event_system,
            self._theme_manager,
        )
        self._content_stack.addWidget(self._animation_demo)
        
        main_layout.addWidget(self._content_stack)
        
        # 更新按钮样式
        self._update_tab_buttons()

    def _connect_signals(self):
        """连接信号。"""
        # 主题变更信号
        self._theme_manager.theme_changed.connect(self._update_theme)

    def _update_theme(self, theme: str):
        """
        更新主题。

        Args:
            theme: 主题名称
        """
        # 更新按钮样式
        self._update_tab_buttons()

    def _update_tab_buttons(self):
        """更新选项卡按钮样式。"""
        # 获取当前主题
        theme = self._theme_manager.get_current_theme()
        
        # 设置按钮样式
        if theme == "light":
            self._theme_tab_btn.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    border: none;
                    border-bottom: 2px solid transparent;
                    padding: 8px 16px;
                    font-size: 14px;
                    color: #333333;
                }
                QPushButton:checked {
                    border-bottom: 2px solid #0078D7;
                    font-weight: bold;
                }
                QPushButton:hover:!checked {
                    background-color: rgba(0, 0, 0, 0.05);
                }
            """)
            
            self._animation_tab_btn.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    border: none;
                    border-bottom: 2px solid transparent;
                    padding: 8px 16px;
                    font-size: 14px;
                    color: #333333;
                }
                QPushButton:checked {
                    border-bottom: 2px solid #0078D7;
                    font-weight: bold;
                }
                QPushButton:hover:!checked {
                    background-color: rgba(0, 0, 0, 0.05);
                }
            """)
        else:
            self._theme_tab_btn.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    border: none;
                    border-bottom: 2px solid transparent;
                    padding: 8px 16px;
                    font-size: 14px;
                    color: #FFFFFF;
                }
                QPushButton:checked {
                    border-bottom: 2px solid #0078D7;
                    font-weight: bold;
                }
                QPushButton:hover:!checked {
                    background-color: rgba(255, 255, 255, 0.1);
                }
            """)
            
            self._animation_tab_btn.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    border: none;
                    border-bottom: 2px solid transparent;
                    padding: 8px 16px;
                    font-size: 14px;
                    color: #FFFFFF;
                }
                QPushButton:checked {
                    border-bottom: 2px solid #0078D7;
                    font-weight: bold;
                }
                QPushButton:hover:!checked {
                    background-color: rgba(255, 255, 255, 0.1);
                }
            """)

    def _switch_tab(self, index: int):
        """
        切换选项卡。

        Args:
            index: 选项卡索引
        """
        # 更新按钮状态
        self._theme_tab_btn.setChecked(index == 0)
        self._animation_tab_btn.setChecked(index == 1)
        
        # 切换内容
        self._content_stack.setCurrentIndex(index)
