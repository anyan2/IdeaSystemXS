"""
输入窗口模块，用于快速记录想法。
"""
import os
from typing import Optional

from PyQt6.QtCore import QEasingCurve, QPropertyAnimation, QRect, QSize, Qt, pyqtSignal
from PyQt6.QtGui import QColor, QIcon, QKeyEvent, QPixmap
from PyQt6.QtWidgets import (
    QApplication, QFrame, QHBoxLayout, QLabel, QPushButton, 
    QTextEdit, QVBoxLayout, QWidget
)

from src.business.idea_manager import IdeaManager
from src.core.config_manager import ConfigManager
from src.core.event_system import EventSystem
from .theme_manager import ThemeManager
from .ui_utils import AnimationHelper, RoundedRectWidget, ShadowEffect


class InputWindow(QWidget):
    """输入窗口类，用于快速记录想法。"""

    # 关闭信号
    closed = pyqtSignal()

    def __init__(
        self,
        config_manager: Optional[ConfigManager] = None,
        event_system: Optional[EventSystem] = None,
        theme_manager: Optional[ThemeManager] = None,
        idea_manager: Optional[IdeaManager] = None,
    ):
        """
        初始化输入窗口。

        Args:
            config_manager: 配置管理器实例
            event_system: 事件系统实例
            theme_manager: 主题管理器实例
            idea_manager: 想法管理器实例
        """
        super().__init__()
        self._config_manager = config_manager or ConfigManager()
        self._event_system = event_system or EventSystem()
        self._theme_manager = theme_manager or ThemeManager(self._config_manager)
        self._idea_manager = idea_manager or IdeaManager(self._config_manager, self._event_system)
        
        # 设置窗口属性
        self.setWindowTitle("记录想法")
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # 设置窗口大小
        self.resize(500, 300)
        
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
        
        # 添加阴影效果
        shadow = ShadowEffect(self._container)
        self._container.setGraphicsEffect(shadow)
        
        # 主布局
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(self._container)
        
        # 容器布局
        container_layout = QVBoxLayout(self._container)
        container_layout.setContentsMargins(15, 15, 15, 15)
        container_layout.setSpacing(10)
        
        # 标题栏
        title_layout = QHBoxLayout()
        title_layout.setContentsMargins(0, 0, 0, 0)
        title_layout.setSpacing(10)
        
        title_label = QLabel("记录想法")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        
        close_btn = QPushButton()
        close_btn.setIcon(QIcon(":/icons/close.png"))
        close_btn.setFixedSize(24, 24)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                border-radius: 12px;
            }
            QPushButton:hover {
                background-color: rgba(255, 0, 0, 0.1);
            }
        """)
        close_btn.clicked.connect(self.close)
        
        title_layout.addWidget(title_label)
        title_layout.addStretch()
        title_layout.addWidget(close_btn)
        
        container_layout.addLayout(title_layout)
        
        # 分隔线
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        separator.setFixedHeight(1)
        container_layout.addWidget(separator)
        
        # 输入区域
        self._input_text = QTextEdit()
        self._input_text.setPlaceholderText("在这里输入你的想法...")
        self._input_text.setStyleSheet("""
            QTextEdit {
                border: 1px solid #E0E0E0;
                border-radius: 5px;
                padding: 8px;
            }
        """)
        container_layout.addWidget(self._input_text)
        
        # 按钮区域
        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(0, 0, 0, 0)
        button_layout.setSpacing(10)
        
        self._save_btn = QPushButton("保存")
        self._save_btn.setStyleSheet("""
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
            QPushButton:disabled {
                background-color: #CCCCCC;
                color: #888888;
            }
        """)
        self._save_btn.clicked.connect(self._save_idea)
        
        cancel_btn = QPushButton("取消")
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #E0E0E0;
                color: #333333;
                border: none;
                border-radius: 5px;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: #D0D0D0;
            }
            QPushButton:pressed {
                background-color: #C0C0C0;
            }
        """)
        cancel_btn.clicked.connect(self.close)
        
        button_layout.addStretch()
        button_layout.addWidget(cancel_btn)
        button_layout.addWidget(self._save_btn)
        
        container_layout.addLayout(button_layout)
        
        # 设置初始焦点
        self._input_text.setFocus()

    def _connect_signals(self):
        """连接信号。"""
        # 主题变更信号
        self._theme_manager.theme_changed.connect(self._update_theme)
        
        # 输入文本变更信号
        self._input_text.textChanged.connect(self._update_save_button)

    def _register_event_handlers(self):
        """注册事件处理器。"""
        # 显示输入窗口事件
        self._event_system.subscribe("show_input_window", self._handle_show_input_window)

    def _handle_show_input_window(self, data=None):
        """
        处理显示输入窗口事件。

        Args:
            data: 事件数据
        """
        # 清空输入
        self._input_text.clear()
        
        # 显示窗口
        self.show_with_animation()
        
        # 激活窗口
        self.activateWindow()
        self._input_text.setFocus()

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
            
            # 更新输入框样式
            self._input_text.setStyleSheet("""
                QTextEdit {
                    background-color: white;
                    color: #333333;
                    border: 1px solid #E0E0E0;
                    border-radius: 5px;
                    padding: 8px;
                }
            """)
        else:
            self._container.setProperty("_background_color", QColor(45, 45, 45))
            self._container.setProperty("_border_color", QColor(60, 60, 60))
            
            # 更新输入框样式
            self._input_text.setStyleSheet("""
                QTextEdit {
                    background-color: #3D3D3D;
                    color: white;
                    border: 1px solid #5D5D5D;
                    border-radius: 5px;
                    padding: 8px;
                }
            """)
        
        # 刷新窗口
        self._container.update()

    def _update_save_button(self):
        """更新保存按钮状态。"""
        # 如果输入为空，禁用保存按钮
        self._save_btn.setEnabled(len(self._input_text.toPlainText().strip()) > 0)

    def _save_idea(self):
        """保存想法。"""
        # 获取输入内容
        content = self._input_text.toPlainText().strip()
        
        # 如果内容为空，不保存
        if not content:
            return
        
        # 保存想法
        try:
            idea = self._idea_manager.create_idea(content)
            
            # 发布想法创建成功事件
            self._event_system.publish("idea_created_by_user", {"idea": idea})
            
            # 关闭窗口
            self.close()
        except Exception as e:
            print(f"保存想法失败: {e}")
            # TODO: 显示错误消息

    def keyPressEvent(self, event: QKeyEvent):
        """
        键盘按下事件。

        Args:
            event: 键盘事件
        """
        # Ctrl+Enter 保存想法
        if event.key() == Qt.Key.Key_Return and event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            if self._save_btn.isEnabled():
                self._save_idea()
            event.accept()
        # Esc 关闭窗口
        elif event.key() == Qt.Key.Key_Escape:
            self.close()
            event.accept()
        else:
            super().keyPressEvent(event)

    def show_with_animation(self):
        """使用动画显示窗口。"""
        # 居中显示
        screen_geometry = QApplication.primaryScreen().geometry()
        x = (screen_geometry.width() - self.width()) // 2
        y = (screen_geometry.height() - self.height()) // 2
        self.move(x, y)
        
        # 设置初始透明度
        self.setWindowOpacity(0.0)
        
        # 显示窗口
        self.show()
        
        # 创建淡入动画
        fade_in_anim = AnimationHelper.fade_in(self)
        fade_in_anim.start()

    def closeEvent(self, event):
        """
        关闭事件。

        Args:
            event: 关闭事件
        """
        # 发射关闭信号
        self.closed.emit()
        event.accept()
