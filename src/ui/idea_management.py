"""
想法管理界面模块，用于管理和查看想法。
"""
from typing import List, Optional

from PyQt6.QtCore import QDate, QDateTime, QSize, Qt, pyqtSignal
from PyQt6.QtGui import QColor, QIcon
from PyQt6.QtWidgets import (
    QApplication, QCalendarWidget, QComboBox, QDateEdit, QFrame, QHBoxLayout, 
    QLabel, QLineEdit, QListWidget, QListWidgetItem, QPushButton, QScrollArea, 
    QSizePolicy, QSplitter, QStackedWidget, QTextEdit, QVBoxLayout, QWidget
)

from src.business.idea_manager import IdeaManager
from src.business.tag_manager import TagManager
from src.core.config_manager import ConfigManager
from src.core.event_system import EventSystem
from .theme_manager import ThemeManager
from .ui_utils import RoundedRectWidget, ShadowEffect


class IdeaCard(QWidget):
    """想法卡片类，用于显示单个想法。"""

    # 想法操作信号
    edit_clicked = pyqtSignal(int)
    delete_clicked = pyqtSignal(int)
    tag_clicked = pyqtSignal(str)

    def __init__(
        self,
        idea_id: int,
        title: str,
        content: str,
        created_at: QDateTime,
        tags: List[str] = None,
        parent: Optional[QWidget] = None,
        theme_manager: Optional[ThemeManager] = None,
    ):
        """
        初始化想法卡片。

        Args:
            idea_id: 想法ID
            title: 标题
            content: 内容
            created_at: 创建时间
            tags: 标签列表
            parent: 父窗口
            theme_manager: 主题管理器实例
        """
        super().__init__(parent)
        self._idea_id = idea_id
        self._title = title
        self._content = content
        self._created_at = created_at
        self._tags = tags or []
        self._theme_manager = theme_manager or ThemeManager()
        
        # 初始化UI
        self._init_ui()
        
        # 连接信号
        self._connect_signals()

    def _init_ui(self):
        """初始化UI。"""
        # 主布局
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(10)
        
        # 标题和时间
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(10)
        
        title_label = QLabel(self._title)
        title_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        
        time_label = QLabel(self._created_at.toString("yyyy-MM-dd hh:mm"))
        time_label.setStyleSheet("color: #888888;")
        
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        header_layout.addWidget(time_label)
        
        main_layout.addLayout(header_layout)
        
        # 内容
        content_label = QLabel(self._content)
        content_label.setWordWrap(True)
        content_label.setStyleSheet("color: #333333;")
        main_layout.addWidget(content_label)
        
        # 标签
        if self._tags:
            tags_layout = QHBoxLayout()
            tags_layout.setContentsMargins(0, 0, 0, 0)
            tags_layout.setSpacing(5)
            
            for tag in self._tags:
                tag_btn = QPushButton(tag)
                tag_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #E0E0E0;
                        color: #333333;
                        border: none;
                        border-radius: 10px;
                        padding: 3px 8px;
                        font-size: 12px;
                    }
                    QPushButton:hover {
                        background-color: #D0D0D0;
                    }
                """)
                tag_btn.clicked.connect(lambda checked, t=tag: self.tag_clicked.emit(t))
                tags_layout.addWidget(tag_btn)
            
            tags_layout.addStretch()
            main_layout.addLayout(tags_layout)
        
        # 操作按钮
        actions_layout = QHBoxLayout()
        actions_layout.setContentsMargins(0, 0, 0, 0)
        actions_layout.setSpacing(10)
        
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
        edit_btn.clicked.connect(lambda: self.edit_clicked.emit(self._idea_id))
        
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
        delete_btn.clicked.connect(lambda: self.delete_clicked.emit(self._idea_id))
        
        actions_layout.addStretch()
        actions_layout.addWidget(edit_btn)
        actions_layout.addWidget(delete_btn)
        
        main_layout.addLayout(actions_layout)
        
        # 设置样式
        self.setStyleSheet("""
            QWidget {
                background-color: white;
                border-radius: 10px;
                border: 1px solid #E0E0E0;
            }
        """)
        
        # 添加阴影效果
        shadow = ShadowEffect(self)
        self.setGraphicsEffect(shadow)

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
                    border-radius: 10px;
                    border: 1px solid #E0E0E0;
                }
            """)
            
            # 更新内容标签样式
            for i in range(self.layout().count()):
                item = self.layout().itemAt(i)
                if isinstance(item, QHBoxLayout):
                    for j in range(item.count()):
                        widget = item.itemAt(j).widget()
                        if isinstance(widget, QLabel) and widget.text() == self._content:
                            widget.setStyleSheet("color: #333333;")
        else:
            self.setStyleSheet("""
                QWidget {
                    background-color: #3D3D3D;
                    border-radius: 10px;
                    border: 1px solid #5D5D5D;
                }
            """)
            
            # 更新内容标签样式
            for i in range(self.layout().count()):
                item = self.layout().itemAt(i)
                if isinstance(item, QHBoxLayout):
                    for j in range(item.count()):
                        widget = item.itemAt(j).widget()
                        if isinstance(widget, QLabel) and widget.text() == self._content:
                            widget.setStyleSheet("color: #FFFFFF;")


class IdeaListWidget(QWidget):
    """想法列表类，用于显示想法列表。"""

    # 想法操作信号
    idea_selected = pyqtSignal(int)
    idea_edit = pyqtSignal(int)
    idea_delete = pyqtSignal(int)
    tag_selected = pyqtSignal(str)

    def __init__(
        self,
        parent: Optional[QWidget] = None,
        config_manager: Optional[ConfigManager] = None,
        event_system: Optional[EventSystem] = None,
        theme_manager: Optional[ThemeManager] = None,
        idea_manager: Optional[IdeaManager] = None,
    ):
        """
        初始化想法列表。

        Args:
            parent: 父窗口
            config_manager: 配置管理器实例
            event_system: 事件系统实例
            theme_manager: 主题管理器实例
            idea_manager: 想法管理器实例
        """
        super().__init__(parent)
        self._config_manager = config_manager or ConfigManager()
        self._event_system = event_system or EventSystem()
        self._theme_manager = theme_manager or ThemeManager(self._config_manager)
        self._idea_manager = idea_manager or IdeaManager(self._config_manager, self._event_system)
        
        # 初始化UI
        self._init_ui()
        
        # 连接信号
        self._connect_signals()
        
        # 注册事件处理器
        self._register_event_handlers()

    def _init_ui(self):
        """初始化UI。"""
        # 主布局
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # 工具栏
        toolbar_layout = QHBoxLayout()
        toolbar_layout.setContentsMargins(10, 10, 10, 10)
        toolbar_layout.setSpacing(10)
        
        # 排序下拉框
        self._sort_combo = QComboBox()
        self._sort_combo.addItem("按时间排序（最新）", "time_desc")
        self._sort_combo.addItem("按时间排序（最早）", "time_asc")
        self._sort_combo.addItem("按标题排序（A-Z）", "title_asc")
        self._sort_combo.addItem("按标题排序（Z-A）", "title_desc")
        toolbar_layout.addWidget(self._sort_combo)
        
        # 搜索框
        self._search_edit = QLineEdit()
        self._search_edit.setPlaceholderText("搜索想法...")
        self._search_edit.setClearButtonEnabled(True)
        toolbar_layout.addWidget(self._search_edit)
        
        # 日期筛选
        self._date_edit = QDateEdit()
        self._date_edit.setCalendarPopup(True)
        self._date_edit.setDate(QDate.currentDate())
        self._date_edit.setDisplayFormat("yyyy-MM-dd")
        
        date_filter_btn = QPushButton("按日期筛选")
        date_filter_btn.clicked.connect(self._filter_by_date)
        
        date_clear_btn = QPushButton("清除日期筛选")
        date_clear_btn.clicked.connect(self._clear_date_filter)
        
        date_layout = QHBoxLayout()
        date_layout.addWidget(self._date_edit)
        date_layout.addWidget(date_filter_btn)
        date_layout.addWidget(date_clear_btn)
        
        toolbar_layout.addLayout(date_layout)
        
        main_layout.addLayout(toolbar_layout)
        
        # 分隔线
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        separator.setFixedHeight(1)
        main_layout.addWidget(separator)
        
        # 想法列表
        self._ideas_layout = QVBoxLayout()
        self._ideas_layout.setContentsMargins(10, 10, 10, 10)
        self._ideas_layout.setSpacing(10)
        self._ideas_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        # 滚动区域
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        scroll_content = QWidget()
        scroll_content.setLayout(self._ideas_layout)
        scroll_area.setWidget(scroll_content)
        
        main_layout.addWidget(scroll_area)

    def _connect_signals(self):
        """连接信号。"""
        # 排序下拉框
        self._sort_combo.currentIndexChanged.connect(self._handle_sort_changed)
        
        # 搜索框
        self._search_edit.textChanged.connect(self._handle_search_changed)
        
        # 主题变更信号
        self._theme_manager.theme_changed.connect(self._update_theme)

    def _register_event_handlers(self):
        """注册事件处理器。"""
        # 想法创建事件
        self._event_system.subscribe("idea_created", self._handle_idea_created)
        
        # 想法更新事件
        self._event_system.subscribe("idea_updated", self._handle_idea_updated)
        
        # 想法删除事件
        self._event_system.subscribe("idea_deleted", self._handle_idea_deleted)

    def _handle_idea_created(self, data):
        """
        处理想法创建事件。

        Args:
            data: 事件数据
        """
        # 刷新想法列表
        self.refresh_ideas()

    def _handle_idea_updated(self, data):
        """
        处理想法更新事件。

        Args:
            data: 事件数据
        """
        # 刷新想法列表
        self.refresh_ideas()

    def _handle_idea_deleted(self, data):
        """
        处理想法删除事件。

        Args:
            data: 事件数据
        """
        # 刷新想法列表
        self.refresh_ideas()

    def _handle_sort_changed(self, index):
        """
        处理排序变更事件。

        Args:
            index: 索引
        """
        # 刷新想法列表
        self.refresh_ideas()

    def _handle_search_changed(self, text):
        """
        处理搜索变更事件。

        Args:
            text: 搜索文本
        """
        # 刷新想法列表
        self.refresh_ideas()

    def _filter_by_date(self):
        """按日期筛选。"""
        # 刷新想法列表
        self.refresh_ideas()

    def _clear_date_filter(self):
        """清除日期筛选。"""
        # 清除日期
        self._date_edit.setDate(QDate.currentDate())
        
        # 刷新想法列表
        self.refresh_ideas()

    def _update_theme(self, theme: str):
        """
        更新主题。

        Args:
            theme: 主题名称
        """
        # 更新想法卡片主题
        for i in range(self._ideas_layout.count()):
            widget = self._ideas_layout.itemAt(i).widget()
            if isinstance(widget, IdeaCard):
                widget._update_theme(theme)

    def _handle_idea_edit(self, idea_id):
        """
        处理想法编辑事件。

        Args:
            idea_id: 想法ID
        """
        # 发射想法编辑信号
        self.idea_edit.emit(idea_id)

    def _handle_idea_delete(self, idea_id):
        """
        处理想法删除事件。

        Args:
            idea_id: 想法ID
        """
        # 发射想法删除信号
        self.idea_delete.emit(idea_id)

    def _handle_tag_clicked(self, tag):
        """
        处理标签点击事件。

        Args:
            tag: 标签
        """
        # 发射标签选择信号
        self.tag_selected.emit(tag)

    def refresh_ideas(self):
        """刷新想法列表。"""
        # 清空想法列表
        while self._ideas_layout.count():
            item = self._ideas_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        
        # 获取排序方式
        sort_by = self._sort_combo.currentData()
        
        # 获取搜索文本
        search_text = self._search_edit.text().strip()
        
        # 获取日期筛选
        date_filter = self._date_edit.date().toString("yyyy-MM-dd")
        
        # 获取想法列表
        ideas = self._idea_manager.get_ideas(sort_by, search_text, date_filter)
        
        # 添加想法卡片
        for idea in ideas:
            idea_card = IdeaCard(
                idea["id"],
                idea["title"],
                idea["content"],
                idea["created_at"],
                idea["tags"],
                self,
                self._theme_manager,
            )
            
            # 连接信号
            idea_card.edit_clicked.connect(self._handle_idea_edit)
            idea_card.delete_clicked.connect(self._handle_idea_delete)
            idea_card.tag_clicked.connect(self._handle_tag_clicked)
            
            # 添加到布局
            self._ideas_layout.addWidget(idea_card)
        
        # 如果没有想法，显示提示
        if not ideas:
            no_ideas_label = QLabel("没有找到想法")
            no_ideas_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            no_ideas_label.setStyleSheet("color: #888888; font-size: 14px; padding: 20px;")
            self._ideas_layout.addWidget(no_ideas_label)


class IdeaDetailWidget(QWidget):
    """想法详情类，用于显示想法详情。"""

    # 想法操作信号
    idea_save = pyqtSignal(int, str, str, list)
    idea_cancel = pyqtSignal()

    def __init__(
        self,
        parent: Optional[QWidget] = None,
        config_manager: Optional[ConfigManager] = None,
        event_system: Optional[EventSystem] = None,
        theme_manager: Optional[ThemeManager] = None,
        idea_manager: Optional[IdeaManager] = None,
        tag_manager: Optional[TagManager] = None,
    ):
        """
        初始化想法详情。

        Args:
            parent: 父窗口
            config_manager: 配置管理器实例
            event_system: 事件系统实例
            theme_manager: 主题管理器实例
            idea_manager: 想法管理器实例
            tag_manager: 标签管理器实例
        """
        super().__init__(parent)
        self._config_manager = config_manager or ConfigManager()
        self._event_system = event_system or EventSystem()
        self._theme_manager = theme_manager or ThemeManager(self._config_manager)
        self._idea_manager = idea_manager or IdeaManager(self._config_manager, self._event_system)
        self._tag_manager = tag_manager or TagManager(self._config_manager, self._event_system)
        self._current_idea_id = None
        
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
        title_layout = QHBoxLayout()
        title_layout.setContentsMargins(0, 0, 0, 0)
        title_layout.setSpacing(10)
        
        title_label = QLabel("标题:")
        title_label.setFixedWidth(50)
        
        self._title_edit = QLineEdit()
        self._title_edit.setPlaceholderText("输入标题...")
        
        title_layout.addWidget(title_label)
        title_layout.addWidget(self._title_edit)
        
        main_layout.addLayout(title_layout)
        
        # 内容
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(10)
        
        content_label = QLabel("内容:")
        
        self._content_edit = QTextEdit()
        self._content_edit.setPlaceholderText("输入内容...")
        self._content_edit.setMinimumHeight(200)
        
        content_layout.addWidget(content_label)
        content_layout.addWidget(self._content_edit)
        
        main_layout.addLayout(content_layout)
        
        # 标签
        tags_layout = QVBoxLayout()
        tags_layout.setContentsMargins(0, 0, 0, 0)
        tags_layout.setSpacing(10)
        
        tags_label = QLabel("标签:")
        
        tags_input_layout = QHBoxLayout()
        tags_input_layout.setContentsMargins(0, 0, 0, 0)
        tags_input_layout.setSpacing(10)
        
        self._tag_edit = QLineEdit()
        self._tag_edit.setPlaceholderText("输入标签...")
        
        add_tag_btn = QPushButton("添加")
        add_tag_btn.clicked.connect(self._add_tag)
        
        tags_input_layout.addWidget(self._tag_edit)
        tags_input_layout.addWidget(add_tag_btn)
        
        self._tags_container = QWidget()
        self._tags_layout = QHBoxLayout(self._tags_container)
        self._tags_layout.setContentsMargins(0, 0, 0, 0)
        self._tags_layout.setSpacing(5)
        self._tags_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        
        tags_layout.addWidget(tags_label)
        tags_layout.addLayout(tags_input_layout)
        tags_layout.addWidget(self._tags_container)
        
        main_layout.addLayout(tags_layout)
        
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
        cancel_btn.clicked.connect(self._cancel_edit)
        
        buttons_layout.addStretch()
        buttons_layout.addWidget(cancel_btn)
        buttons_layout.addWidget(self._save_btn)
        
        main_layout.addLayout(buttons_layout)
        
        # 添加伸缩项
        main_layout.addStretch()

    def _connect_signals(self):
        """连接信号。"""
        # 标题和内容变更信号
        self._title_edit.textChanged.connect(self._update_save_button)
        self._content_edit.textChanged.connect(self._update_save_button)
        
        # 主题变更信号
        self._theme_manager.theme_changed.connect(self._update_theme)

    def _update_save_button(self):
        """更新保存按钮状态。"""
        # 如果标题和内容都不为空，启用保存按钮
        title = self._title_edit.text().strip()
        content = self._content_edit.toPlainText().strip()
        self._save_btn.setEnabled(title and content)

    def _update_theme(self, theme: str):
        """
        更新主题。

        Args:
            theme: 主题名称
        """
        # 更新标签样式
        for i in range(self._tags_layout.count()):
            widget = self._tags_layout.itemAt(i).widget()
            if isinstance(widget, QPushButton):
                if theme == "light":
                    widget.setStyleSheet("""
                        QPushButton {
                            background-color: #E0E0E0;
                            color: #333333;
                            border: none;
                            border-radius: 10px;
                            padding: 3px 8px;
                            font-size: 12px;
                        }
                        QPushButton:hover {
                            background-color: #D0D0D0;
                        }
                    """)
                else:
                    widget.setStyleSheet("""
                        QPushButton {
                            background-color: #5D5D5D;
                            color: #FFFFFF;
                            border: none;
                            border-radius: 10px;
                            padding: 3px 8px;
                            font-size: 12px;
                        }
                        QPushButton:hover {
                            background-color: #6D6D6D;
                        }
                    """)

    def _add_tag(self):
        """添加标签。"""
        # 获取标签
        tag = self._tag_edit.text().strip()
        
        # 如果标签为空，不添加
        if not tag:
            return
        
        # 如果标签已存在，不添加
        for i in range(self._tags_layout.count()):
            widget = self._tags_layout.itemAt(i).widget()
            if isinstance(widget, QPushButton) and widget.text() == tag:
                return
        
        # 创建标签按钮
        tag_btn = QPushButton(tag)
        tag_btn.setStyleSheet("""
            QPushButton {
                background-color: #E0E0E0;
                color: #333333;
                border: none;
                border-radius: 10px;
                padding: 3px 8px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #D0D0D0;
            }
        """)
        
        # 添加删除按钮
        remove_btn = QPushButton("×")
        remove_btn.setFixedSize(16, 16)
        remove_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #888888;
                border: none;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                color: #E81123;
            }
        """)
        remove_btn.clicked.connect(lambda: self._remove_tag(tag_btn))
        
        # 创建标签布局
        tag_layout = QHBoxLayout()
        tag_layout.setContentsMargins(0, 0, 0, 0)
        tag_layout.setSpacing(0)
        tag_layout.addWidget(tag_btn)
        tag_layout.addWidget(remove_btn)
        
        # 添加到标签布局
        self._tags_layout.addLayout(tag_layout)
        
        # 清空标签输入框
        self._tag_edit.clear()

    def _remove_tag(self, tag_btn):
        """
        删除标签。

        Args:
            tag_btn: 标签按钮
        """
        # 查找标签布局
        for i in range(self._tags_layout.count()):
            item = self._tags_layout.itemAt(i)
            if isinstance(item, QHBoxLayout):
                for j in range(item.count()):
                    widget = item.itemAt(j).widget()
                    if widget == tag_btn:
                        # 删除标签布局
                        while item.count():
                            w = item.takeAt(0).widget()
                            if w:
                                w.deleteLater()
                        
                        # 从标签布局中移除
                        self._tags_layout.removeItem(item)
                        return

    def _get_tags(self):
        """
        获取标签列表。

        Returns:
            标签列表
        """
        tags = []
        
        # 遍历标签布局
        for i in range(self._tags_layout.count()):
            item = self._tags_layout.itemAt(i)
            if isinstance(item, QHBoxLayout):
                for j in range(item.count()):
                    widget = item.itemAt(j).widget()
                    if isinstance(widget, QPushButton) and widget.text() != "×":
                        tags.append(widget.text())
        
        return tags

    def _save_idea(self):
        """保存想法。"""
        # 获取标题和内容
        title = self._title_edit.text().strip()
        content = self._content_edit.toPlainText().strip()
        
        # 如果标题或内容为空，不保存
        if not title or not content:
            return
        
        # 获取标签
        tags = self._get_tags()
        
        # 发射想法保存信号
        self.idea_save.emit(self._current_idea_id, title, content, tags)

    def _cancel_edit(self):
        """取消编辑。"""
        # 发射想法取消信号
        self.idea_cancel.emit()

    def set_idea(self, idea_id, title, content, tags):
        """
        设置想法。

        Args:
            idea_id: 想法ID
            title: 标题
            content: 内容
            tags: 标签列表
        """
        # 设置当前想法ID
        self._current_idea_id = idea_id
        
        # 设置标题和内容
        self._title_edit.setText(title)
        self._content_edit.setText(content)
        
        # 清空标签
        while self._tags_layout.count():
            item = self._tags_layout.takeAt(0)
            if isinstance(item, QHBoxLayout):
                while item.count():
                    w = item.takeAt(0).widget()
                    if w:
                        w.deleteLater()
            elif item.widget():
                item.widget().deleteLater()
        
        # 添加标签
        for tag in tags:
            # 创建标签按钮
            tag_btn = QPushButton(tag)
            tag_btn.setStyleSheet("""
                QPushButton {
                    background-color: #E0E0E0;
                    color: #333333;
                    border: none;
                    border-radius: 10px;
                    padding: 3px 8px;
                    font-size: 12px;
                }
                QPushButton:hover {
                    background-color: #D0D0D0;
                }
            """)
            
            # 添加删除按钮
            remove_btn = QPushButton("×")
            remove_btn.setFixedSize(16, 16)
            remove_btn.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    color: #888888;
                    border: none;
                    font-size: 12px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    color: #E81123;
                }
            """)
            remove_btn.clicked.connect(lambda checked, t=tag_btn: self._remove_tag(t))
            
            # 创建标签布局
            tag_layout = QHBoxLayout()
            tag_layout.setContentsMargins(0, 0, 0, 0)
            tag_layout.setSpacing(0)
            tag_layout.addWidget(tag_btn)
            tag_layout.addWidget(remove_btn)
            
            # 添加到标签布局
            self._tags_layout.addLayout(tag_layout)
        
        # 更新保存按钮状态
        self._update_save_button()

    def clear(self):
        """清空想法详情。"""
        # 清空当前想法ID
        self._current_idea_id = None
        
        # 清空标题和内容
        self._title_edit.clear()
        self._content_edit.clear()
        
        # 清空标签
        while self._tags_layout.count():
            item = self._tags_layout.takeAt(0)
            if isinstance(item, QHBoxLayout):
                while item.count():
                    w = item.takeAt(0).widget()
                    if w:
                        w.deleteLater()
            elif item.widget():
                item.widget().deleteLater()
        
        # 更新保存按钮状态
        self._update_save_button()


class IdeaManagementWidget(QWidget):
    """想法管理界面类，用于管理想法。"""

    def __init__(
        self,
        parent: Optional[QWidget] = None,
        config_manager: Optional[ConfigManager] = None,
        event_system: Optional[EventSystem] = None,
        theme_manager: Optional[ThemeManager] = None,
        idea_manager: Optional[IdeaManager] = None,
        tag_manager: Optional[TagManager] = None,
    ):
        """
        初始化想法管理界面。

        Args:
            parent: 父窗口
            config_manager: 配置管理器实例
            event_system: 事件系统实例
            theme_manager: 主题管理器实例
            idea_manager: 想法管理器实例
            tag_manager: 标签管理器实例
        """
        super().__init__(parent)
        self._config_manager = config_manager or ConfigManager()
        self._event_system = event_system or EventSystem()
        self._theme_manager = theme_manager or ThemeManager(self._config_manager)
        self._idea_manager = idea_manager or IdeaManager(self._config_manager, self._event_system)
        self._tag_manager = tag_manager or TagManager(self._config_manager, self._event_system)
        
        # 初始化UI
        self._init_ui()
        
        # 连接信号
        self._connect_signals()
        
        # 注册事件处理器
        self._register_event_handlers()
        
        # 刷新想法列表
        self._idea_list.refresh_ideas()

    def _init_ui(self):
        """初始化UI。"""
        # 主布局
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # 分割器
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setChildrenCollapsible(False)
        
        # 想法列表
        self._idea_list = IdeaListWidget(
            splitter,
            self._config_manager,
            self._event_system,
            self._theme_manager,
            self._idea_manager,
        )
        
        # 想法详情
        self._idea_detail = IdeaDetailWidget(
            splitter,
            self._config_manager,
            self._event_system,
            self._theme_manager,
            self._idea_manager,
            self._tag_manager,
        )
        
        # 设置分割器初始大小
        splitter.setSizes([300, 500])
        
        main_layout.addWidget(splitter)

    def _connect_signals(self):
        """连接信号。"""
        # 想法列表信号
        self._idea_list.idea_selected.connect(self._handle_idea_selected)
        self._idea_list.idea_edit.connect(self._handle_idea_edit)
        self._idea_list.idea_delete.connect(self._handle_idea_delete)
        self._idea_list.tag_selected.connect(self._handle_tag_selected)
        
        # 想法详情信号
        self._idea_detail.idea_save.connect(self._handle_idea_save)
        self._idea_detail.idea_cancel.connect(self._handle_idea_cancel)

    def _register_event_handlers(self):
        """注册事件处理器。"""
        # 创建新想法事件
        self._event_system.subscribe("create_new_idea", self._handle_create_new_idea)

    def _handle_idea_selected(self, idea_id):
        """
        处理想法选择事件。

        Args:
            idea_id: 想法ID
        """
        # 获取想法详情
        idea = self._idea_manager.get_idea(idea_id)
        
        # 设置想法详情
        self._idea_detail.set_idea(idea["id"], idea["title"], idea["content"], idea["tags"])

    def _handle_idea_edit(self, idea_id):
        """
        处理想法编辑事件。

        Args:
            idea_id: 想法ID
        """
        # 获取想法详情
        idea = self._idea_manager.get_idea(idea_id)
        
        # 设置想法详情
        self._idea_detail.set_idea(idea["id"], idea["title"], idea["content"], idea["tags"])

    def _handle_idea_delete(self, idea_id):
        """
        处理想法删除事件。

        Args:
            idea_id: 想法ID
        """
        # 发布确认删除想法事件
        self._event_system.publish("confirm_delete_idea", {"idea_id": idea_id})

    def _handle_tag_selected(self, tag):
        """
        处理标签选择事件。

        Args:
            tag: 标签
        """
        # 设置搜索框文本
        # TODO: 实现标签筛选

    def _handle_idea_save(self, idea_id, title, content, tags):
        """
        处理想法保存事件。

        Args:
            idea_id: 想法ID
            title: 标题
            content: 内容
            tags: 标签列表
        """
        # 如果是新想法
        if idea_id is None:
            # 创建新想法
            self._idea_manager.create_idea(content, title, tags)
        else:
            # 更新想法
            self._idea_manager.update_idea(idea_id, content, title, tags)
        
        # 清空想法详情
        self._idea_detail.clear()
        
        # 刷新想法列表
        self._idea_list.refresh_ideas()

    def _handle_idea_cancel(self):
        """处理想法取消事件。"""
        # 清空想法详情
        self._idea_detail.clear()

    def _handle_create_new_idea(self, data=None):
        """
        处理创建新想法事件。

        Args:
            data: 事件数据
        """
        # 清空想法详情
        self._idea_detail.clear()
        
        # 设置新想法
        self._idea_detail.set_idea(None, "", "", [])
