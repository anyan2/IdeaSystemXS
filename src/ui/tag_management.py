"""
标签管理界面模块，用于管理标签。
"""
from typing import List, Optional

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor, QIcon
from PyQt6.QtWidgets import (
    QApplication, QFrame, QHBoxLayout, QLabel, QLineEdit, QListWidget, 
    QListWidgetItem, QPushButton, QVBoxLayout, QWidget
)

from src.business.tag_manager import TagManager
from src.core.config_manager import ConfigManager
from src.core.event_system import EventSystem
from .theme_manager import ThemeManager
from .ui_utils import RoundedRectWidget, ShadowEffect


class TagItem(QWidget):
    """标签项类，用于显示单个标签。"""

    # 标签操作信号
    edit_clicked = pyqtSignal(str)
    delete_clicked = pyqtSignal(str)

    def __init__(
        self,
        tag: str,
        count: int,
        parent: Optional[QWidget] = None,
        theme_manager: Optional[ThemeManager] = None,
    ):
        """
        初始化标签项。

        Args:
            tag: 标签名称
            count: 使用次数
            parent: 父窗口
            theme_manager: 主题管理器实例
        """
        super().__init__(parent)
        self._tag = tag
        self._count = count
        self._theme_manager = theme_manager or ThemeManager()
        
        # 初始化UI
        self._init_ui()
        
        # 连接信号
        self._connect_signals()

    def _init_ui(self):
        """初始化UI。"""
        # 主布局
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(10, 5, 10, 5)
        main_layout.setSpacing(10)
        
        # 标签名称
        tag_label = QLabel(self._tag)
        tag_label.setStyleSheet("font-size: 14px;")
        
        # 使用次数
        count_label = QLabel(f"({self._count})")
        count_label.setStyleSheet("color: #888888;")
        
        # 编辑按钮
        edit_btn = QPushButton("编辑")
        edit_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #0078D7;
                border: none;
                padding: 3px 8px;
                font-size: 12px;
            }
            QPushButton:hover {
                text-decoration: underline;
            }
        """)
        edit_btn.clicked.connect(lambda: self.edit_clicked.emit(self._tag))
        
        # 删除按钮
        delete_btn = QPushButton("删除")
        delete_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #E81123;
                border: none;
                padding: 3px 8px;
                font-size: 12px;
            }
            QPushButton:hover {
                text-decoration: underline;
            }
        """)
        delete_btn.clicked.connect(lambda: self.delete_clicked.emit(self._tag))
        
        main_layout.addWidget(tag_label)
        main_layout.addWidget(count_label)
        main_layout.addStretch()
        main_layout.addWidget(edit_btn)
        main_layout.addWidget(delete_btn)
        
        # 设置样式
        self.setStyleSheet("""
            QWidget {
                background-color: white;
                border-radius: 5px;
            }
            QWidget:hover {
                background-color: #F5F5F5;
            }
        """)

    def _connect_signals(self):
        """连接信号。"""
        # 主题变更信号
        if self._theme_manager:
            self._theme_manager.theme_changed.connect(self._update_theme)

    def _update_theme(self, theme: str):
        """
        更新主题。

        Args:
            theme: 主题名称
        """
        if theme == "light":
            self.setStyleSheet("""
                QWidget {
                    background-color: white;
                    border-radius: 5px;
                }
                QWidget:hover {
                    background-color: #F5F5F5;
                }
            """)
        else:
            self.setStyleSheet("""
                QWidget {
                    background-color: #3D3D3D;
                    border-radius: 5px;
                }
                QWidget:hover {
                    background-color: #4D4D4D;
                }
            """)


class TagManagementWidget(QWidget):
    """标签管理界面类，用于管理标签。"""

    def __init__(
        self,
        parent: Optional[QWidget] = None,
        config_manager: Optional[ConfigManager] = None,
        event_system: Optional[EventSystem] = None,
        theme_manager: Optional[ThemeManager] = None,
        tag_manager: Optional[TagManager] = None,
    ):
        """
        初始化标签管理界面。

        Args:
            parent: 父窗口
            config_manager: 配置管理器实例
            event_system: 事件系统实例
            theme_manager: 主题管理器实例
            tag_manager: 标签管理器实例
        """
        super().__init__(parent)
        self._config_manager = config_manager or ConfigManager()
        self._event_system = event_system or EventSystem()
        self._theme_manager = theme_manager or ThemeManager(self._config_manager)
        self._tag_manager = tag_manager or TagManager(self._config_manager, self._event_system)
        self._current_tag = None
        
        # 初始化UI
        self._init_ui()
        
        # 连接信号
        self._connect_signals()
        
        # 注册事件处理器
        self._register_event_handlers()
        
        # 刷新标签列表
        self.refresh_tags()

    def _init_ui(self):
        """初始化UI。"""
        # 主布局
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # 左侧面板
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(10)
        
        # 标题
        title_label = QLabel("标签管理")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        left_layout.addWidget(title_label)
        
        # 搜索框
        self._search_edit = QLineEdit()
        self._search_edit.setPlaceholderText("搜索标签...")
        self._search_edit.setClearButtonEnabled(True)
        left_layout.addWidget(self._search_edit)
        
        # 标签列表
        self._tag_list = QListWidget()
        self._tag_list.setFrameShape(QFrame.Shape.NoFrame)
        left_layout.addWidget(self._tag_list)
        
        # 添加标签按钮
        add_tag_btn = QPushButton("添加新标签")
        add_tag_btn.setStyleSheet("""
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
        add_tag_btn.clicked.connect(self._handle_add_tag)
        left_layout.addWidget(add_tag_btn)
        
        # 右侧面板
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(15)
        
        # 标签编辑
        edit_group = QWidget()
        edit_layout = QVBoxLayout(edit_group)
        edit_layout.setContentsMargins(0, 0, 0, 0)
        edit_layout.setSpacing(10)
        
        edit_title = QLabel("编辑标签")
        edit_title.setStyleSheet("font-size: 16px; font-weight: bold;")
        edit_layout.addWidget(edit_title)
        
        # 标签名称
        name_layout = QHBoxLayout()
        name_layout.setContentsMargins(0, 0, 0, 0)
        name_layout.setSpacing(10)
        
        name_label = QLabel("名称:")
        name_label.setFixedWidth(50)
        
        self._name_edit = QLineEdit()
        self._name_edit.setPlaceholderText("输入标签名称...")
        
        name_layout.addWidget(name_label)
        name_layout.addWidget(self._name_edit)
        
        edit_layout.addLayout(name_layout)
        
        # 按钮
        buttons_layout = QHBoxLayout()
        buttons_layout.setContentsMargins(0, 0, 0, 0)
        buttons_layout.setSpacing(10)
        
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
        self._save_btn.clicked.connect(self._save_tag)
        
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
        cancel_btn.clicked.connect(self._cancel_edit)
        
        buttons_layout.addStretch()
        buttons_layout.addWidget(cancel_btn)
        buttons_layout.addWidget(self._save_btn)
        
        edit_layout.addLayout(buttons_layout)
        
        right_layout.addWidget(edit_group)
        right_layout.addStretch()
        
        # 设置面板大小
        left_panel.setFixedWidth(300)
        
        main_layout.addWidget(left_panel)
        main_layout.addWidget(right_panel)
        
        # 禁用编辑面板
        self._enable_edit_panel(False)

    def _connect_signals(self):
        """连接信号。"""
        # 搜索框
        self._search_edit.textChanged.connect(self._handle_search_changed)
        
        # 标签名称
        self._name_edit.textChanged.connect(self._update_save_button)
        
        # 主题变更信号
        self._theme_manager.theme_changed.connect(self._update_theme)

    def _register_event_handlers(self):
        """注册事件处理器。"""
        # 标签创建事件
        self._event_system.subscribe("tag_created", self._handle_tag_created)
        
        # 标签更新事件
        self._event_system.subscribe("tag_updated", self._handle_tag_updated)
        
        # 标签删除事件
        self._event_system.subscribe("tag_deleted", self._handle_tag_deleted)

    def _handle_tag_created(self, data):
        """
        处理标签创建事件。

        Args:
            data: 事件数据
        """
        # 刷新标签列表
        self.refresh_tags()

    def _handle_tag_updated(self, data):
        """
        处理标签更新事件。

        Args:
            data: 事件数据
        """
        # 刷新标签列表
        self.refresh_tags()

    def _handle_tag_deleted(self, data):
        """
        处理标签删除事件。

        Args:
            data: 事件数据
        """
        # 刷新标签列表
        self.refresh_tags()

    def _handle_search_changed(self, text):
        """
        处理搜索变更事件。

        Args:
            text: 搜索文本
        """
        # 刷新标签列表
        self.refresh_tags()

    def _update_theme(self, theme: str):
        """
        更新主题。

        Args:
            theme: 主题名称
        """
        # 更新标签项主题
        for i in range(self._tag_list.count()):
            item = self._tag_list.item(i)
            widget = self._tag_list.itemWidget(item)
            if isinstance(widget, TagItem):
                widget._update_theme(theme)

    def _update_save_button(self):
        """更新保存按钮状态。"""
        # 如果标签名称为空，禁用保存按钮
        self._save_btn.setEnabled(bool(self._name_edit.text().strip()))

    def _enable_edit_panel(self, enabled: bool):
        """
        启用或禁用编辑面板。

        Args:
            enabled: 是否启用
        """
        self._name_edit.setEnabled(enabled)
        self._save_btn.setEnabled(enabled and bool(self._name_edit.text().strip()))

    def _handle_add_tag(self):
        """处理添加标签事件。"""
        # 清空当前标签
        self._current_tag = None
        
        # 清空标签名称
        self._name_edit.clear()
        
        # 启用编辑面板
        self._enable_edit_panel(True)
        
        # 设置焦点
        self._name_edit.setFocus()

    def _handle_edit_tag(self, tag: str):
        """
        处理编辑标签事件。

        Args:
            tag: 标签名称
        """
        # 设置当前标签
        self._current_tag = tag
        
        # 设置标签名称
        self._name_edit.setText(tag)
        
        # 启用编辑面板
        self._enable_edit_panel(True)
        
        # 设置焦点
        self._name_edit.setFocus()

    def _handle_delete_tag(self, tag: str):
        """
        处理删除标签事件。

        Args:
            tag: 标签名称
        """
        # 发布确认删除标签事件
        self._event_system.publish("confirm_delete_tag", {"tag": tag})

    def _save_tag(self):
        """保存标签。"""
        # 获取标签名称
        name = self._name_edit.text().strip()
        
        # 如果标签名称为空，不保存
        if not name:
            return
        
        # 如果是新标签
        if self._current_tag is None:
            # 创建新标签
            self._tag_manager.create_tag(name)
        else:
            # 更新标签
            self._tag_manager.update_tag(self._current_tag, name)
        
        # 清空当前标签
        self._current_tag = None
        
        # 清空标签名称
        self._name_edit.clear()
        
        # 禁用编辑面板
        self._enable_edit_panel(False)
        
        # 刷新标签列表
        self.refresh_tags()

    def _cancel_edit(self):
        """取消编辑。"""
        # 清空当前标签
        self._current_tag = None
        
        # 清空标签名称
        self._name_edit.clear()
        
        # 禁用编辑面板
        self._enable_edit_panel(False)

    def refresh_tags(self):
        """刷新标签列表。"""
        # 清空标签列表
        self._tag_list.clear()
        
        # 获取搜索文本
        search_text = self._search_edit.text().strip()
        
        # 获取标签列表
        tags = self._tag_manager.get_tags(search_text)
        
        # 添加标签项
        for tag in tags:
            # 创建列表项
            item = QListWidgetItem()
            item.setSizeHint(QSize(0, 40))
            
            # 创建标签项
            tag_item = TagItem(
                tag["name"],
                tag["count"],
                self._tag_list,
                self._theme_manager,
            )
            
            # 连接信号
            tag_item.edit_clicked.connect(self._handle_edit_tag)
            tag_item.delete_clicked.connect(self._handle_delete_tag)
            
            # 添加到列表
            self._tag_list.addItem(item)
            self._tag_list.setItemWidget(item, tag_item)
        
        # 如果没有标签，显示提示
        if not tags:
            # 创建列表项
            item = QListWidgetItem("没有找到标签")
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsSelectable)
            
            # 添加到列表
            self._tag_list.addItem(item)
