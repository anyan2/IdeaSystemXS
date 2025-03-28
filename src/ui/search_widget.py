"""
搜索界面模块，用于搜索想法。
"""
from typing import List, Optional

from PyQt6.QtCore import QSize, Qt, pyqtSignal
from PyQt6.QtGui import QColor, QIcon
from PyQt6.QtWidgets import (
    QApplication, QCheckBox, QComboBox, QFrame, QHBoxLayout, QLabel, 
    QLineEdit, QPushButton, QScrollArea, QSlider, QVBoxLayout, QWidget
)

from ..business.idea_manager import IdeaManager
from ..business.search_engine import SearchEngine
from ..business.tag_manager import TagManager
from ..core.config_manager import ConfigManager
from ..core.event_system import EventSystem
from .theme_manager import ThemeManager
from .ui_utils import RoundedRectWidget, ShadowEffect


class SearchResultItem(QWidget):
    """搜索结果项类，用于显示单个搜索结果。"""

    # 结果操作信号
    view_clicked = pyqtSignal(int)

    def __init__(
        self,
        idea_id: int,
        title: str,
        content: str,
        tags: List[str],
        similarity: float,
        parent: Optional[QWidget] = None,
        theme_manager: Optional[ThemeManager] = None,
    ):
        """
        初始化搜索结果项。

        Args:
            idea_id: 想法ID
            title: 标题
            content: 内容
            tags: 标签列表
            similarity: 相似度
            parent: 父窗口
            theme_manager: 主题管理器实例
        """
        super().__init__(parent)
        self._idea_id = idea_id
        self._title = title
        self._content = content
        self._tags = tags
        self._similarity = similarity
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
        
        # 标题和相似度
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(10)
        
        title_label = QLabel(self._title)
        title_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        
        similarity_label = QLabel(f"相似度: {self._similarity:.2f}")
        similarity_label.setStyleSheet("color: #888888;")
        
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        header_layout.addWidget(similarity_label)
        
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
                tags_layout.addWidget(tag_btn)
            
            tags_layout.addStretch()
            main_layout.addLayout(tags_layout)
        
        # 查看按钮
        view_btn = QPushButton("查看详情")
        view_btn.setStyleSheet("""
            QPushButton {
                background-color: #0078D7;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 5px 10px;
            }
            QPushButton:hover {
                background-color: #1C88E6;
            }
            QPushButton:pressed {
                background-color: #0067C0;
            }
        """)
        view_btn.clicked.connect(lambda: self.view_clicked.emit(self._idea_id))
        
        buttons_layout = QHBoxLayout()
        buttons_layout.setContentsMargins(0, 0, 0, 0)
        buttons_layout.setSpacing(10)
        buttons_layout.addStretch()
        buttons_layout.addWidget(view_btn)
        
        main_layout.addLayout(buttons_layout)
        
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
                if isinstance(item, QVBoxLayout):
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
                if isinstance(item, QVBoxLayout):
                    for j in range(item.count()):
                        widget = item.itemAt(j).widget()
                        if isinstance(widget, QLabel) and widget.text() == self._content:
                            widget.setStyleSheet("color: #FFFFFF;")


class SearchWidget(QWidget):
    """搜索界面类，用于搜索想法。"""

    # 搜索结果操作信号
    view_idea = pyqtSignal(int)

    def __init__(
        self,
        parent: Optional[QWidget] = None,
        config_manager: Optional[ConfigManager] = None,
        event_system: Optional[EventSystem] = None,
        theme_manager: Optional[ThemeManager] = None,
        idea_manager: Optional[IdeaManager] = None,
        tag_manager: Optional[TagManager] = None,
        search_engine: Optional[SearchEngine] = None,
    ):
        """
        初始化搜索界面。

        Args:
            parent: 父窗口
            config_manager: 配置管理器实例
            event_system: 事件系统实例
            theme_manager: 主题管理器实例
            idea_manager: 想法管理器实例
            tag_manager: 标签管理器实例
            search_engine: 搜索引擎实例
        """
        super().__init__(parent)
        self._config_manager = config_manager or ConfigManager()
        self._event_system = event_system or EventSystem()
        self._theme_manager = theme_manager or ThemeManager(self._config_manager)
        self._idea_manager = idea_manager or IdeaManager(self._config_manager, self._event_system)
        self._tag_manager = tag_manager or TagManager(self._config_manager, self._event_system)
        self._search_engine = search_engine or SearchEngine(self._config_manager, self._event_system)
        
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
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # 搜索框
        search_layout = QHBoxLayout()
        search_layout.setContentsMargins(0, 0, 0, 0)
        search_layout.setSpacing(10)
        
        self._search_edit = QLineEdit()
        self._search_edit.setPlaceholderText("输入搜索关键词...")
        self._search_edit.setClearButtonEnabled(True)
        
        search_btn = QPushButton("搜索")
        search_btn.setStyleSheet("""
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
        search_btn.clicked.connect(self._handle_search)
        
        search_layout.addWidget(self._search_edit)
        search_layout.addWidget(search_btn)
        
        main_layout.addLayout(search_layout)
        
        # 高级搜索选项
        advanced_options = QWidget()
        advanced_layout = QVBoxLayout(advanced_options)
        advanced_layout.setContentsMargins(0, 0, 0, 0)
        advanced_layout.setSpacing(10)
        
        # 搜索类型
        type_layout = QHBoxLayout()
        type_layout.setContentsMargins(0, 0, 0, 0)
        type_layout.setSpacing(10)
        
        type_label = QLabel("搜索类型:")
        
        self._keyword_check = QCheckBox("关键词搜索")
        self._keyword_check.setChecked(True)
        
        self._semantic_check = QCheckBox("语义搜索")
        self._semantic_check.setChecked(True)
        
        type_layout.addWidget(type_label)
        type_layout.addWidget(self._keyword_check)
        type_layout.addWidget(self._semantic_check)
        type_layout.addStretch()
        
        advanced_layout.addLayout(type_layout)
        
        # 相似度阈值
        similarity_layout = QHBoxLayout()
        similarity_layout.setContentsMargins(0, 0, 0, 0)
        similarity_layout.setSpacing(10)
        
        similarity_label = QLabel("相似度阈值:")
        
        self._similarity_slider = QSlider(Qt.Orientation.Horizontal)
        self._similarity_slider.setRange(0, 100)
        self._similarity_slider.setValue(70)
        
        self._similarity_value = QLabel("0.7")
        
        similarity_layout.addWidget(similarity_label)
        similarity_layout.addWidget(self._similarity_slider)
        similarity_layout.addWidget(self._similarity_value)
        
        advanced_layout.addLayout(similarity_layout)
        
        # 标签筛选
        tags_layout = QHBoxLayout()
        tags_layout.setContentsMargins(0, 0, 0, 0)
        tags_layout.setSpacing(10)
        
        tags_label = QLabel("标签筛选:")
        
        self._tags_combo = QComboBox()
        self._tags_combo.addItem("所有标签", None)
        
        # 添加标签
        tags = self._tag_manager.get_tags()
        for tag in tags:
            self._tags_combo.addItem(tag["name"], tag["name"])
        
        tags_layout.addWidget(tags_label)
        tags_layout.addWidget(self._tags_combo)
        tags_layout.addStretch()
        
        advanced_layout.addLayout(tags_layout)
        
        main_layout.addWidget(advanced_options)
        
        # 分隔线
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        separator.setFixedHeight(1)
        main_layout.addWidget(separator)
        
        # 搜索结果
        results_layout = QVBoxLayout()
        results_layout.setContentsMargins(0, 0, 0, 0)
        results_layout.setSpacing(10)
        
        results_label = QLabel("搜索结果")
        results_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        results_layout.addWidget(results_label)
        
        self._results_container = QWidget()
        self._results_layout = QVBoxLayout(self._results_container)
        self._results_layout.setContentsMargins(0, 0, 0, 0)
        self._results_layout.setSpacing(10)
        self._results_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        # 滚动区域
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setWidget(self._results_container)
        
        results_layout.addWidget(scroll_area)
        
        main_layout.addLayout(results_layout)

    def _connect_signals(self):
        """连接信号。"""
        # 相似度滑块
        self._similarity_slider.valueChanged.connect(self._handle_similarity_changed)
        
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
        # 刷新标签下拉框
        self._refresh_tags_combo()

    def _handle_tag_updated(self, data):
        """
        处理标签更新事件。

        Args:
            data: 事件数据
        """
        # 刷新标签下拉框
        self._refresh_tags_combo()

    def _handle_tag_deleted(self, data):
        """
        处理标签删除事件。

        Args:
            data: 事件数据
        """
        # 刷新标签下拉框
        self._refresh_tags_combo()

    def _handle_similarity_changed(self, value):
        """
        处理相似度变更事件。

        Args:
            value: 值
        """
        # 更新相似度值
        self._similarity_value.setText(f"{value / 100:.1f}")

    def _update_theme(self, theme: str):
        """
        更新主题。

        Args:
            theme: 主题名称
        """
        # 更新搜索结果项主题
        for i in range(self._results_layout.count()):
            widget = self._results_layout.itemAt(i).widget()
            if isinstance(widget, SearchResultItem):
                widget._update_theme(theme)

    def _refresh_tags_combo(self):
        """刷新标签下拉框。"""
        # 保存当前选中的标签
        current_tag = self._tags_combo.currentData()
        
        # 清空标签下拉框
        self._tags_combo.clear()
        
        # 添加"所有标签"选项
        self._tags_combo.addItem("所有标签", None)
        
        # 添加标签
        tags = self._tag_manager.get_tags()
        for tag in tags:
            self._tags_combo.addItem(tag["name"], tag["name"])
        
        # 恢复选中的标签
        if current_tag:
            index = self._tags_combo.findData(current_tag)
            if index >= 0:
                self._tags_combo.setCurrentIndex(index)

    def _handle_search(self):
        """处理搜索事件。"""
        # 获取搜索关键词
        query = self._search_edit.text().strip()
        
        # 如果关键词为空，不搜索
        if not query:
            return
        
        # 获取搜索类型
        use_keyword = self._keyword_check.isChecked()
        use_semantic = self._semantic_check.isChecked()
        
        # 如果两种搜索类型都未选中，不搜索
        if not use_keyword and not use_semantic:
            return
        
        # 获取相似度阈值
        similarity_threshold = self._similarity_slider.value() / 100
        
        # 获取标签筛选
        tag_filter = self._tags_combo.currentData()
        
        # 执行搜索
        results = self._search_engine.search(
            query,
            use_keyword=use_keyword,
            use_semantic=use_semantic,
            similarity_threshold=similarity_threshold,
            tag_filter=tag_filter,
        )
        
        # 显示搜索结果
        self._show_search_results(results)

    def _show_search_results(self, results):
        """
        显示搜索结果。

        Args:
            results: 搜索结果
        """
        # 清空搜索结果
        while self._results_layout.count():
            item = self._results_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        
        # 如果没有结果，显示提示
        if not results:
            no_results_label = QLabel("没有找到匹配的想法")
            no_results_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            no_results_label.setStyleSheet("color: #888888; font-size: 14px; padding: 20px;")
            self._results_layout.addWidget(no_results_label)
            return
        
        # 添加搜索结果
        for result in results:
            result_item = SearchResultItem(
                result["id"],
                result["title"],
                result["content"],
                result["tags"],
                result["similarity"],
                self._results_container,
                self._theme_manager,
            )
            
            # 连接信号
            result_item.view_clicked.connect(self._handle_view_idea)
            
            # 添加到布局
            self._results_layout.addWidget(result_item)

    def _handle_view_idea(self, idea_id):
        """
        处理查看想法事件。

        Args:
            idea_id: 想法ID
        """
        # 发射查看想法信号
        self.view_idea.emit(idea_id)
