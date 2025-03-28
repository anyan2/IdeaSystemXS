"""
AI配置界面模块，用于配置AI服务。
"""
from typing import Optional

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor, QIcon
from PyQt6.QtWidgets import (
    QApplication, QCheckBox, QComboBox, QFrame, QHBoxLayout, QLabel, 
    QLineEdit, QMessageBox, QPushButton, QVBoxLayout, QWidget
)

from ..ai.ai_service import AIService
from ..core.config_manager import ConfigManager
from ..core.event_system import EventSystem
from .theme_manager import ThemeManager
from .ui_utils import RoundedRectWidget, ShadowEffect


class APIConfigWidget(QWidget):
    """API配置界面类，用于配置AI API。"""

    def __init__(
        self,
        parent: Optional[QWidget] = None,
        config_manager: Optional[ConfigManager] = None,
        event_system: Optional[EventSystem] = None,
        theme_manager: Optional[ThemeManager] = None,
        ai_service: Optional[AIService] = None,
    ):
        """
        初始化API配置界面。

        Args:
            parent: 父窗口
            config_manager: 配置管理器实例
            event_system: 事件系统实例
            theme_manager: 主题管理器实例
            ai_service: AI服务实例
        """
        super().__init__(parent)
        self._config_manager = config_manager or ConfigManager()
        self._event_system = event_system or EventSystem()
        self._theme_manager = theme_manager or ThemeManager(self._config_manager)
        self._ai_service = ai_service or AIService(self._config_manager, self._event_system)
        
        # 初始化UI
        self._init_ui()
        
        # 连接信号
        self._connect_signals()
        
        # 注册事件处理器
        self._register_event_handlers()
        
        # 加载配置
        self._load_config()

    def _init_ui(self):
        """初始化UI。"""
        # 主布局
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # 标题
        title_label = QLabel("AI API配置")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        main_layout.addWidget(title_label)
        
        # AI功能启用
        enable_layout = QHBoxLayout()
        enable_layout.setContentsMargins(0, 0, 0, 0)
        enable_layout.setSpacing(10)
        
        self._enable_ai_check = QCheckBox("启用AI功能")
        self._enable_ai_check.setChecked(True)
        
        enable_layout.addWidget(self._enable_ai_check)
        enable_layout.addStretch()
        
        main_layout.addLayout(enable_layout)
        
        # API配置面板
        api_panel = RoundedRectWidget(
            radius=10,
            background_color=QColor(245, 245, 245),
            border_color=QColor(200, 200, 200),
            border_width=1,
        )
        api_layout = QVBoxLayout(api_panel)
        api_layout.setContentsMargins(20, 20, 20, 20)
        api_layout.setSpacing(15)
        
        # API URL
        url_layout = QHBoxLayout()
        url_layout.setContentsMargins(0, 0, 0, 0)
        url_layout.setSpacing(10)
        
        url_label = QLabel("API URL:")
        url_label.setFixedWidth(80)
        
        self._url_edit = QLineEdit()
        self._url_edit.setPlaceholderText("输入API URL，例如：https://api.openai.com/v1")
        
        url_layout.addWidget(url_label)
        url_layout.addWidget(self._url_edit)
        
        api_layout.addLayout(url_layout)
        
        # API密钥
        key_layout = QHBoxLayout()
        key_layout.setContentsMargins(0, 0, 0, 0)
        key_layout.setSpacing(10)
        
        key_label = QLabel("API密钥:")
        key_label.setFixedWidth(80)
        
        self._key_edit = QLineEdit()
        self._key_edit.setPlaceholderText("输入API密钥")
        self._key_edit.setEchoMode(QLineEdit.EchoMode.Password)
        
        key_layout.addWidget(key_label)
        key_layout.addWidget(self._key_edit)
        
        api_layout.addLayout(key_layout)
        
        # 模型选择
        model_layout = QHBoxLayout()
        model_layout.setContentsMargins(0, 0, 0, 0)
        model_layout.setSpacing(10)
        
        model_label = QLabel("模型:")
        model_label.setFixedWidth(80)
        
        self._model_combo = QComboBox()
        self._model_combo.addItem("GPT-3.5 Turbo", "gpt-3.5-turbo")
        self._model_combo.addItem("GPT-4", "gpt-4")
        self._model_combo.addItem("GPT-4 Turbo", "gpt-4-turbo")
        
        model_layout.addWidget(model_label)
        model_layout.addWidget(self._model_combo)
        
        api_layout.addLayout(model_layout)
        
        # 离线模式
        offline_layout = QHBoxLayout()
        offline_layout.setContentsMargins(0, 0, 0, 0)
        offline_layout.setSpacing(10)
        
        self._offline_check = QCheckBox("离线模式（禁用AI功能，但保留基本功能）")
        
        offline_layout.addWidget(self._offline_check)
        offline_layout.addStretch()
        
        api_layout.addLayout(offline_layout)
        
        # 测试连接按钮
        test_btn = QPushButton("测试连接")
        test_btn.setStyleSheet("""
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
        test_btn.clicked.connect(self._test_connection)
        
        api_layout.addWidget(test_btn, 0, Qt.AlignmentFlag.AlignRight)
        
        main_layout.addWidget(api_panel)
        
        # 保存按钮
        save_btn = QPushButton("保存配置")
        save_btn.setStyleSheet("""
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
        save_btn.clicked.connect(self._save_config)
        
        main_layout.addWidget(save_btn, 0, Qt.AlignmentFlag.AlignRight)
        
        # 添加伸缩项
        main_layout.addStretch()
        
        # 添加阴影效果
        shadow = ShadowEffect(api_panel)
        api_panel.setGraphicsEffect(shadow)

    def _connect_signals(self):
        """连接信号。"""
        # 启用AI功能复选框
        self._enable_ai_check.stateChanged.connect(self._update_ui_state)
        
        # 离线模式复选框
        self._offline_check.stateChanged.connect(self._update_ui_state)
        
        # 主题变更信号
        self._theme_manager.theme_changed.connect(self._update_theme)

    def _register_event_handlers(self):
        """注册事件处理器。"""
        # 测试API结果事件
        self._event_system.subscribe("test_ai_api_result", self._handle_test_result)

    def _handle_test_result(self, data):
        """
        处理测试API结果事件。

        Args:
            data: 事件数据
        """
        # 显示测试结果
        success = data.get("success", False)
        message = data.get("message", "")
        
        if success:
            QMessageBox.information(self, "测试成功", message)
        else:
            QMessageBox.warning(self, "测试失败", message)

    def _update_theme(self, theme: str):
        """
        更新主题。

        Args:
            theme: 主题名称
        """
        # 更新面板样式
        for i in range(self.layout().count()):
            widget = self.layout().itemAt(i).widget()
            if isinstance(widget, RoundedRectWidget):
                if theme == "light":
                    widget.set_background_color(QColor(245, 245, 245))
                    widget.set_border_color(QColor(200, 200, 200))
                else:
                    widget.set_background_color(QColor(60, 60, 60))
                    widget.set_border_color(QColor(80, 80, 80))

    def _update_ui_state(self):
        """更新UI状态。"""
        # 获取启用状态
        enabled = self._enable_ai_check.isChecked()
        offline = self._offline_check.isChecked()
        
        # 更新UI状态
        self._url_edit.setEnabled(enabled and not offline)
        self._key_edit.setEnabled(enabled and not offline)
        self._model_combo.setEnabled(enabled and not offline)

    def _load_config(self):
        """加载配置。"""
        # 加载AI功能启用状态
        self._enable_ai_check.setChecked(self._config_manager.is_ai_enabled())
        
        # 加载离线模式状态
        self._offline_check.setChecked(self._config_manager.is_offline_mode())
        
        # 加载API URL
        self._url_edit.setText(self._config_manager.get("ai", "api_url", ""))
        
        # 加载API密钥
        self._key_edit.setText(self._config_manager.get("ai", "api_key", ""))
        
        # 加载模型
        model = self._config_manager.get("ai", "model", "gpt-3.5-turbo")
        index = self._model_combo.findData(model)
        if index >= 0:
            self._model_combo.setCurrentIndex(index)
        
        # 更新UI状态
        self._update_ui_state()

    def _save_config(self):
        """保存配置。"""
        # 保存AI功能启用状态
        self._config_manager.set("ai", "enabled", self._enable_ai_check.isChecked())
        
        # 保存离线模式状态
        self._config_manager.set("ai", "offline_mode", self._offline_check.isChecked())
        
        # 保存API URL
        self._config_manager.set("ai", "api_url", self._url_edit.text())
        
        # 保存API密钥
        self._config_manager.set("ai", "api_key", self._key_edit.text())
        
        # 保存模型
        self._config_manager.set("ai", "model", self._model_combo.currentData())
        
        # 显示保存成功消息
        QMessageBox.information(self, "保存成功", "AI配置已保存。")

    def _test_connection(self):
        """测试API连接。"""
        # 如果AI功能未启用或处于离线模式，显示提示
        if not self._enable_ai_check.isChecked():
            QMessageBox.warning(self, "测试失败", "AI功能未启用。")
            return
        
        if self._offline_check.isChecked():
            QMessageBox.warning(self, "测试失败", "系统处于离线模式。")
            return
        
        # 检查API URL和API密钥是否已填写
        if not self._url_edit.text():
            QMessageBox.warning(self, "测试失败", "请输入API URL。")
            return
        
        if not self._key_edit.text():
            QMessageBox.warning(self, "测试失败", "请输入API密钥。")
            return
        
        # 临时保存配置
        self._config_manager.set("ai", "api_url", self._url_edit.text())
        self._config_manager.set("ai", "api_key", self._key_edit.text())
        self._config_manager.set("ai", "model", self._model_combo.currentData())
        
        # 发布测试API事件
        self._event_system.publish("test_ai_api", {})
        
        # 显示测试中消息
        QMessageBox.information(self, "测试中", "正在测试API连接，请稍候...")


class AIConsoleWidget(QWidget):
    """AI控制台界面类，用于与AI交互。"""

    def __init__(
        self,
        parent: Optional[QWidget] = None,
        config_manager: Optional[ConfigManager] = None,
        event_system: Optional[EventSystem] = None,
        theme_manager: Optional[ThemeManager] = None,
        ai_service: Optional[AIService] = None,
    ):
        """
        初始化AI控制台界面。

        Args:
            parent: 父窗口
            config_manager: 配置管理器实例
            event_system: 事件系统实例
            theme_manager: 主题管理器实例
            ai_service: AI服务实例
        """
        super().__init__(parent)
        self._config_manager = config_manager or ConfigManager()
        self._event_system = event_system or EventSystem()
        self._theme_manager = theme_manager or ThemeManager(self._config_manager)
        self._ai_service = ai_service or AIService(self._config_manager, self._event_system)
        
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
        
        # 标题
        title_label = QLabel("AI控制台")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        main_layout.addWidget(title_label)
        
        # 对话面板
        dialog_panel = RoundedRectWidget(
            radius=10,
            background_color=QColor(245, 245, 245),
            border_color=QColor(200, 200, 200),
            border_width=1,
        )
        dialog_layout = QVBoxLayout(dialog_panel)
        dialog_layout.setContentsMargins(20, 20, 20, 20)
        dialog_layout.setSpacing(15)
        
        # 对话历史
        self._dialog_label = QLabel("欢迎使用AI控制台，您可以在这里向AI提问关于您想法的问题。")
        self._dialog_label.setWordWrap(True)
        self._dialog_label.setStyleSheet("color: #333333;")
        self._dialog_label.setMinimumHeight(200)
        
        dialog_layout.addWidget(self._dialog_label)
        
        # 分隔线
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        separator.setFixedHeight(1)
        dialog_layout.addWidget(separator)
        
        # 输入区域
        input_layout = QHBoxLayout()
        input_layout.setContentsMargins(0, 0, 0, 0)
        input_layout.setSpacing(10)
        
        self._input_edit = QLineEdit()
        self._input_edit.setPlaceholderText("输入您的问题...")
        
        send_btn = QPushButton("发送")
        send_btn.setStyleSheet("""
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
        send_btn.clicked.connect(self._send_question)
        
        input_layout.addWidget(self._input_edit)
        input_layout.addWidget(send_btn)
        
        dialog_layout.addLayout(input_layout)
        
        main_layout.addWidget(dialog_panel)
        
        # 添加伸缩项
        main_layout.addStretch()
        
        # 添加阴影效果
        shadow = ShadowEffect(dialog_panel)
        dialog_panel.setGraphicsEffect(shadow)

    def _connect_signals(self):
        """连接信号。"""
        # 输入框回车信号
        self._input_edit.returnPressed.connect(self._send_question)
        
        # 主题变更信号
        self._theme_manager.theme_changed.connect(self._update_theme)

    def _register_event_handlers(self):
        """注册事件处理器。"""
        pass

    def _update_theme(self, theme: str):
        """
        更新主题。

        Args:
            theme: 主题名称
        """
        # 更新面板样式
        for i in range(self.layout().count()):
            widget = self.layout().itemAt(i).widget()
            if isinstance(widget, RoundedRectWidget):
                if theme == "light":
                    widget.set_background_color(QColor(245, 245, 245))
                    widget.set_border_color(QColor(200, 200, 200))
                    self._dialog_label.setStyleSheet("color: #333333;")
                else:
                    widget.set_background_color(QColor(60, 60, 60))
                    widget.set_border_color(QColor(80, 80, 80))
                    self._dialog_label.setStyleSheet("color: #FFFFFF;")

    def _send_question(self):
        """发送问题。"""
        # 获取问题
        question = self._input_edit.text().strip()
        
        # 如果问题为空，不处理
        if not question:
            return
        
        # 清空输入框
        self._input_edit.clear()
        
        # 更新对话历史
        current_text = self._dialog_label.text()
        new_text = f"{current_text}\n\n<b>您:</b> {question}"
        self._dialog_label.setText(new_text)
        
        # 如果AI服务不可用，显示提示
        if not self._ai_service.is_available():
            self._dialog_label.setText(f"{new_text}\n\n<b>AI:</b> AI服务不可用，请检查设置。")
            return
        
        # 发布查询相关想法事件
        self._event_system.publish("search_ideas", {
            "query": question,
            "use_keyword": True,
            "use_semantic": True,
            "similarity_threshold": 0.5,
            "limit": 5,
            "callback": lambda results: self._ask_ai(question, results)
        })

    def _ask_ai(self, question: str, context: list):
        """
        向AI提问。

        Args:
            question: 问题
            context: 上下文，包含相关想法的列表
        """
        # 获取AI回答
        answer = self._ai_service.ask_ai(question, context)
        
        # 更新对话历史
        current_text = self._dialog_label.text()
        new_text = f"{current_text}\n\n<b>AI:</b> {answer}"
        self._dialog_label.setText(new_text)
