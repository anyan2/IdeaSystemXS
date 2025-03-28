"""
设置窗口模块，用于配置应用程序设置。
"""
from typing import Optional

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor, QIcon
from PyQt6.QtWidgets import (
    QCheckBox, QColorDialog, QComboBox, QFormLayout, QFrame, QGroupBox, 
    QHBoxLayout, QLabel, QLineEdit, QPushButton, QScrollArea, QSpinBox, 
    QStackedWidget, QTabWidget, QVBoxLayout, QWidget
)

from ..core.config_manager import ConfigManager
from ..core.event_system import EventSystem
from .theme_manager import ThemeManager
from .ui_utils import RoundedRectWidget, ShadowEffect


class SettingsTab(QWidget):
    """设置选项卡基类，所有设置选项卡的基类。"""

    # 设置变更信号
    settings_changed = pyqtSignal(dict)

    def __init__(
        self,
        parent: Optional[QWidget] = None,
        config_manager: Optional[ConfigManager] = None,
        event_system: Optional[EventSystem] = None,
        theme_manager: Optional[ThemeManager] = None,
    ):
        """
        初始化设置选项卡。

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
        
        # 加载设置
        self._load_settings()

    def _init_ui(self):
        """初始化UI。"""
        # 主布局
        self._main_layout = QVBoxLayout(self)
        self._main_layout.setContentsMargins(20, 20, 20, 20)
        self._main_layout.setSpacing(15)

    def _connect_signals(self):
        """连接信号。"""
        pass

    def _load_settings(self):
        """加载设置。"""
        pass

    def save_settings(self):
        """保存设置。"""
        pass


class GeneralSettingsTab(SettingsTab):
    """通用设置选项卡，用于配置通用设置。"""

    def _init_ui(self):
        """初始化UI。"""
        super()._init_ui()
        
        # 主题设置
        theme_group = QGroupBox("主题设置")
        theme_layout = QFormLayout(theme_group)
        theme_layout.setContentsMargins(15, 15, 15, 15)
        theme_layout.setSpacing(10)
        
        self._theme_combo = QComboBox()
        self._theme_combo.addItem("浅色", "light")
        self._theme_combo.addItem("深色", "dark")
        theme_layout.addRow("主题:", self._theme_combo)
        
        self._blur_effect_check = QCheckBox("启用毛玻璃效果")
        theme_layout.addRow("", self._blur_effect_check)
        
        self._opacity_spin = QSpinBox()
        self._opacity_spin.setRange(50, 100)
        self._opacity_spin.setSuffix("%")
        theme_layout.addRow("不透明度:", self._opacity_spin)
        
        self._animation_speed_spin = QSpinBox()
        self._animation_speed_spin.setRange(100, 1000)
        self._animation_speed_spin.setSingleStep(50)
        self._animation_speed_spin.setSuffix(" ms")
        theme_layout.addRow("动画速度:", self._animation_speed_spin)
        
        self._main_layout.addWidget(theme_group)
        
        # 启动设置
        startup_group = QGroupBox("启动设置")
        startup_layout = QFormLayout(startup_group)
        startup_layout.setContentsMargins(15, 15, 15, 15)
        startup_layout.setSpacing(10)
        
        self._auto_start_check = QCheckBox("开机自启动")
        startup_layout.addRow("", self._auto_start_check)
        
        self._start_minimized_check = QCheckBox("启动时最小化到系统托盘")
        startup_layout.addRow("", self._start_minimized_check)
        
        self._main_layout.addWidget(startup_group)
        
        # 快捷键设置
        hotkey_group = QGroupBox("快捷键设置")
        hotkey_layout = QFormLayout(hotkey_group)
        hotkey_layout.setContentsMargins(15, 15, 15, 15)
        hotkey_layout.setSpacing(10)
        
        self._show_input_hotkey_edit = QLineEdit()
        self._show_input_hotkey_edit.setPlaceholderText("点击设置快捷键")
        self._show_input_hotkey_edit.setReadOnly(True)
        hotkey_layout.addRow("显示输入窗口:", self._show_input_hotkey_edit)
        
        self._main_layout.addWidget(hotkey_group)
        
        # 添加伸缩项
        self._main_layout.addStretch()

    def _connect_signals(self):
        """连接信号。"""
        super()._connect_signals()
        
        # 主题设置
        self._theme_combo.currentIndexChanged.connect(self._handle_theme_changed)
        self._blur_effect_check.stateChanged.connect(self._handle_blur_effect_changed)
        self._opacity_spin.valueChanged.connect(self._handle_opacity_changed)
        self._animation_speed_spin.valueChanged.connect(self._handle_animation_speed_changed)
        
        # 启动设置
        self._auto_start_check.stateChanged.connect(self._handle_auto_start_changed)
        self._start_minimized_check.stateChanged.connect(self._handle_start_minimized_changed)
        
        # 快捷键设置
        self._show_input_hotkey_edit.mousePressEvent = self._handle_show_input_hotkey_clicked

    def _load_settings(self):
        """加载设置。"""
        super()._load_settings()
        
        # 主题设置
        theme = self._config_manager.get_theme()
        index = self._theme_combo.findData(theme)
        if index >= 0:
            self._theme_combo.setCurrentIndex(index)
        
        self._blur_effect_check.setChecked(self._config_manager.get("ui", "blur_effect", True))
        self._opacity_spin.setValue(int(self._config_manager.get("ui", "opacity", 0.95) * 100))
        self._animation_speed_spin.setValue(self._config_manager.get("ui", "animation_speed", 300))
        
        # 启动设置
        self._auto_start_check.setChecked(self._config_manager.get("general", "auto_start", False))
        self._start_minimized_check.setChecked(self._config_manager.get("general", "start_minimized", False))
        
        # 快捷键设置
        self._show_input_hotkey_edit.setText(self._config_manager.get_show_input_hotkey())

    def _handle_theme_changed(self, index):
        """
        处理主题变更事件。

        Args:
            index: 索引
        """
        theme = self._theme_combo.itemData(index)
        self._config_manager.set("general", "theme", theme)
        self._theme_manager.set_theme(theme)
        self.settings_changed.emit({"general": {"theme": theme}})

    def _handle_blur_effect_changed(self, state):
        """
        处理毛玻璃效果变更事件。

        Args:
            state: 状态
        """
        enabled = state == Qt.CheckState.Checked.value
        self._config_manager.set("ui", "blur_effect", enabled)
        self.settings_changed.emit({"ui": {"blur_effect": enabled}})

    def _handle_opacity_changed(self, value):
        """
        处理不透明度变更事件。

        Args:
            value: 值
        """
        opacity = value / 100.0
        self._config_manager.set("ui", "opacity", opacity)
        self.settings_changed.emit({"ui": {"opacity": opacity}})

    def _handle_animation_speed_changed(self, value):
        """
        处理动画速度变更事件。

        Args:
            value: 值
        """
        self._config_manager.set("ui", "animation_speed", value)
        self.settings_changed.emit({"ui": {"animation_speed": value}})

    def _handle_auto_start_changed(self, state):
        """
        处理开机自启动变更事件。

        Args:
            state: 状态
        """
        enabled = state == Qt.CheckState.Checked.value
        self._config_manager.set("general", "auto_start", enabled)
        self.settings_changed.emit({"general": {"auto_start": enabled}})
        
        # 设置开机自启动
        if enabled:
            self._event_system.publish("enable_auto_start")
        else:
            self._event_system.publish("disable_auto_start")

    def _handle_start_minimized_changed(self, state):
        """
        处理启动时最小化变更事件。

        Args:
            state: 状态
        """
        enabled = state == Qt.CheckState.Checked.value
        self._config_manager.set("general", "start_minimized", enabled)
        self.settings_changed.emit({"general": {"start_minimized": enabled}})

    def _handle_show_input_hotkey_clicked(self, event):
        """
        处理显示输入窗口快捷键点击事件。

        Args:
            event: 事件
        """
        self._show_input_hotkey_edit.setText("按下快捷键...")
        self._show_input_hotkey_edit.setFocus()
        
        # 发布设置快捷键事件
        self._event_system.publish("set_hotkey", {
            "type": "show_input",
            "callback": self._set_show_input_hotkey
        })

    def _set_show_input_hotkey(self, hotkey):
        """
        设置显示输入窗口快捷键。

        Args:
            hotkey: 快捷键
        """
        self._show_input_hotkey_edit.setText(hotkey)
        self._config_manager.set_show_input_hotkey(hotkey)
        self.settings_changed.emit({"hotkeys": {"show_input": hotkey}})

    def save_settings(self):
        """保存设置。"""
        # 所有设置已经在变更时保存，无需额外操作
        pass


class AISettingsTab(SettingsTab):
    """AI设置选项卡，用于配置AI相关设置。"""

    def _init_ui(self):
        """初始化UI。"""
        super()._init_ui()
        
        # AI功能设置
        ai_group = QGroupBox("AI功能设置")
        ai_layout = QFormLayout(ai_group)
        ai_layout.setContentsMargins(15, 15, 15, 15)
        ai_layout.setSpacing(10)
        
        self._ai_enabled_check = QCheckBox("启用AI功能")
        ai_layout.addRow("", self._ai_enabled_check)
        
        self._offline_mode_check = QCheckBox("离线模式（禁用AI API调用）")
        ai_layout.addRow("", self._offline_mode_check)
        
        self._main_layout.addWidget(ai_group)
        
        # API设置
        api_group = QGroupBox("API设置")
        api_layout = QFormLayout(api_group)
        api_layout.setContentsMargins(15, 15, 15, 15)
        api_layout.setSpacing(10)
        
        self._api_url_edit = QLineEdit()
        self._api_url_edit.setPlaceholderText("例如：https://api.openai.com/v1")
        api_layout.addRow("API URL:", self._api_url_edit)
        
        self._api_key_edit = QLineEdit()
        self._api_key_edit.setPlaceholderText("输入API密钥")
        self._api_key_edit.setEchoMode(QLineEdit.EchoMode.Password)
        api_layout.addRow("API密钥:", self._api_key_edit)
        
        self._model_combo = QComboBox()
        self._model_combo.addItem("gpt-3.5-turbo", "gpt-3.5-turbo")
        self._model_combo.addItem("gpt-4", "gpt-4")
        self._model_combo.addItem("gpt-4-turbo", "gpt-4-turbo")
        api_layout.addRow("模型:", self._model_combo)
        
        self._test_api_btn = QPushButton("测试API连接")
        api_layout.addRow("", self._test_api_btn)
        
        self._main_layout.addWidget(api_group)
        
        # 自动处理设置
        auto_group = QGroupBox("自动处理设置")
        auto_layout = QFormLayout(auto_group)
        auto_layout.setContentsMargins(15, 15, 15, 15)
        auto_layout.setSpacing(10)
        
        self._auto_analyze_check = QCheckBox("自动分析新想法")
        auto_layout.addRow("", self._auto_analyze_check)
        
        self._auto_summarize_check = QCheckBox("自动生成摘要")
        auto_layout.addRow("", self._auto_summarize_check)
        
        self._auto_tag_check = QCheckBox("自动添加标签")
        auto_layout.addRow("", self._auto_tag_check)
        
        self._auto_relate_check = QCheckBox("自动关联相似想法")
        auto_layout.addRow("", self._auto_relate_check)
        
        self._check_interval_spin = QSpinBox()
        self._check_interval_spin.setRange(1, 60)
        self._check_interval_spin.setSuffix(" 分钟")
        auto_layout.addRow("检查间隔:", self._check_interval_spin)
        
        self._main_layout.addWidget(auto_group)
        
        # 添加伸缩项
        self._main_layout.addStretch()

    def _connect_signals(self):
        """连接信号。"""
        super()._connect_signals()
        
        # AI功能设置
        self._ai_enabled_check.stateChanged.connect(self._handle_ai_enabled_changed)
        self._offline_mode_check.stateChanged.connect(self._handle_offline_mode_changed)
        
        # API设置
        self._api_url_edit.editingFinished.connect(self._handle_api_url_changed)
        self._api_key_edit.editingFinished.connect(self._handle_api_key_changed)
        self._model_combo.currentIndexChanged.connect(self._handle_model_changed)
        self._test_api_btn.clicked.connect(self._handle_test_api_clicked)
        
        # 自动处理设置
        self._auto_analyze_check.stateChanged.connect(self._handle_auto_analyze_changed)
        self._auto_summarize_check.stateChanged.connect(self._handle_auto_summarize_changed)
        self._auto_tag_check.stateChanged.connect(self._handle_auto_tag_changed)
        self._auto_relate_check.stateChanged.connect(self._handle_auto_relate_changed)
        self._check_interval_spin.valueChanged.connect(self._handle_check_interval_changed)

    def _load_settings(self):
        """加载设置。"""
        super()._load_settings()
        
        # AI功能设置
        self._ai_enabled_check.setChecked(self._config_manager.is_ai_enabled())
        self._offline_mode_check.setChecked(self._config_manager.is_offline_mode())
        
        # API设置
        self._api_url_edit.setText(self._config_manager.get("ai", "api_url", ""))
        self._api_key_edit.setText(self._config_manager.get("ai", "api_key", ""))
        
        model = self._config_manager.get("ai", "model", "gpt-3.5-turbo")
        index = self._model_combo.findData(model)
        if index >= 0:
            self._model_combo.setCurrentIndex(index)
        
        # 自动处理设置
        self._auto_analyze_check.setChecked(self._config_manager.get("ai", "auto_analyze", True))
        self._auto_summarize_check.setChecked(self._config_manager.get("ai", "auto_summarize", True))
        self._auto_tag_check.setChecked(self._config_manager.get("ai", "auto_tag", True))
        self._auto_relate_check.setChecked(self._config_manager.get("ai", "auto_relate", True))
        self._check_interval_spin.setValue(self._config_manager.get("ai", "check_interval_minutes", 15))
        
        # 更新UI状态
        self._update_ui_state()

    def _update_ui_state(self):
        """更新UI状态。"""
        ai_enabled = self._ai_enabled_check.isChecked()
        offline_mode = self._offline_mode_check.isChecked()
        
        # API设置
        self._api_url_edit.setEnabled(ai_enabled and not offline_mode)
        self._api_key_edit.setEnabled(ai_enabled and not offline_mode)
        self._model_combo.setEnabled(ai_enabled and not offline_mode)
        self._test_api_btn.setEnabled(ai_enabled and not offline_mode)
        
        # 自动处理设置
        self._auto_analyze_check.setEnabled(ai_enabled)
        self._auto_summarize_check.setEnabled(ai_enabled)
        self._auto_tag_check.setEnabled(ai_enabled)
        self._auto_relate_check.setEnabled(ai_enabled)
        self._check_interval_spin.setEnabled(ai_enabled)

    def _handle_ai_enabled_changed(self, state):
        """
        处理AI功能启用状态变更事件。

        Args:
            state: 状态
        """
        enabled = state == Qt.CheckState.Checked.value
        self._config_manager.set("ai", "enabled", enabled)
        self.settings_changed.emit({"ai": {"enabled": enabled}})
        
        # 更新UI状态
        self._update_ui_state()

    def _handle_offline_mode_changed(self, state):
        """
        处理离线模式变更事件。

        Args:
            state: 状态
        """
        enabled = state == Qt.CheckState.Checked.value
        self._config_manager.set("ai", "offline_mode", enabled)
        self.settings_changed.emit({"ai": {"offline_mode": enabled}})
        
        # 更新UI状态
        self._update_ui_state()

    def _handle_api_url_changed(self):
        """处理API URL变更事件。"""
        url = self._api_url_edit.text().strip()
        self._config_manager.set("ai", "api_url", url)
        self.settings_changed.emit({"ai": {"api_url": url}})

    def _handle_api_key_changed(self):
        """处理API密钥变更事件。"""
        key = self._api_key_edit.text().strip()
        self._config_manager.set("ai", "api_key", key)
        self.settings_changed.emit({"ai": {"api_key": key}})

    def _handle_model_changed(self, index):
        """
        处理模型变更事件。

        Args:
            index: 索引
        """
        model = self._model_combo.itemData(index)
        self._config_manager.set("ai", "model", model)
        self.settings_changed.emit({"ai": {"model": model}})

    def _handle_test_api_clicked(self):
        """处理测试API连接按钮点击事件。"""
        # 发布测试API连接事件
        self._event_system.publish("test_ai_api")

    def _handle_auto_analyze_changed(self, state):
        """
        处理自动分析变更事件。

        Args:
            state: 状态
        """
        enabled = state == Qt.CheckState.Checked.value
        self._config_manager.set("ai", "auto_analyze", enabled)
        self.settings_changed.emit({"ai": {"auto_analyze": enabled}})

    def _handle_auto_summarize_changed(self, state):
        """
        处理自动生成摘要变更事件。

        Args:
            state: 状态
        """
        enabled = state == Qt.CheckState.Checked.value
        self._config_manager.set("ai", "auto_summarize", enabled)
        self.settings_changed.emit({"ai": {"auto_summarize": enabled}})

    def _handle_auto_tag_changed(self, state):
        """
        处理自动添加标签变更事件。

        Args:
            state: 状态
        """
        enabled = state == Qt.CheckState.Checked.value
        self._config_manager.set("ai", "auto_tag", enabled)
        self.settings_changed.emit({"ai": {"auto_tag": enabled}})

    def _handle_auto_relate_changed(self, state):
        """
        处理自动关联变更事件。

        Args:
            state: 状态
        """
        enabled = state == Qt.CheckState.Checked.value
        self._config_manager.set("ai", "auto_relate", enabled)
        self.settings_changed.emit({"ai": {"auto_relate": enabled}})

    def _handle_check_interval_changed(self, value):
        """
        处理检查间隔变更事件。

        Args:
            value: 值
        """
        self._config_manager.set("ai", "check_interval_minutes", value)
        self.settings_changed.emit({"ai": {"check_interval_minutes": value}})

    def save_settings(self):
        """保存设置。"""
        # 所有设置已经在变更时保存，无需额外操作
        pass


class DataSettingsTab(SettingsTab):
    """数据设置选项卡，用于配置数据相关设置。"""

    def _init_ui(self):
        """初始化UI。"""
        super()._init_ui()
        
        # 数据存储设置
        storage_group = QGroupBox("数据存储设置")
        storage_layout = QFormLayout(storage_group)
        storage_layout.setContentsMargins(15, 15, 15, 15)
        storage_layout.setSpacing(10)
        
        self._data_dir_edit = QLineEdit()
        self._data_dir_edit.setReadOnly(True)
        
        browse_btn = QPushButton("浏览...")
        browse_btn.clicked.connect(self._handle_browse_clicked)
        
        dir_layout = QHBoxLayout()
        dir_layout.addWidget(self._data_dir_edit)
        dir_layout.addWidget(browse_btn)
        
        storage_layout.addRow("数据目录:", dir_layout)
        
        self._auto_backup_check = QCheckBox("启用自动备份")
        storage_layout.addRow("", self._auto_backup_check)
        
        self._backup_interval_spin = QSpinBox()
        self._backup_interval_spin.setRange(1, 30)
        self._backup_interval_spin.setSuffix(" 天")
        storage_layout.addRow("备份间隔:", self._backup_interval_spin)
        
        backup_now_btn = QPushButton("立即备份")
        backup_now_btn.clicked.connect(self._handle_backup_now_clicked)
        storage_layout.addRow("", backup_now_btn)
        
        self._main_layout.addWidget(storage_group)
        
        # 数据管理设置
        manage_group = QGroupBox("数据管理设置")
        manage_layout = QFormLayout(manage_group)
        manage_layout.setContentsMargins(15, 15, 15, 15)
        manage_layout.setSpacing(10)
        
        export_btn = QPushButton("导出数据")
        export_btn.clicked.connect(self._handle_export_clicked)
        manage_layout.addRow("", export_btn)
        
        import_btn = QPushButton("导入数据")
        import_btn.clicked.connect(self._handle_import_clicked)
        manage_layout.addRow("", import_btn)
        
        clear_btn = QPushButton("清空数据")
        clear_btn.setStyleSheet("color: red;")
        clear_btn.clicked.connect(self._handle_clear_clicked)
        manage_layout.addRow("", clear_btn)
        
        self._main_layout.addWidget(manage_group)
        
        # 添加伸缩项
        self._main_layout.addStretch()

    def _connect_signals(self):
        """连接信号。"""
        super()._connect_signals()
        
        # 数据存储设置
        self._auto_backup_check.stateChanged.connect(self._handle_auto_backup_changed)
        self._backup_interval_spin.valueChanged.connect(self._handle_backup_interval_changed)

    def _load_settings(self):
        """加载设置。"""
        super()._load_settings()
        
        # 数据存储设置
        self._data_dir_edit.setText(self._config_manager.get_data_dir())
        self._auto_backup_check.setChecked(self._config_manager.get("data", "auto_backup", True))
        self._backup_interval_spin.setValue(self._config_manager.get("data", "backup_interval_days", 7))
        
        # 更新UI状态
        self._update_ui_state()

    def _update_ui_state(self):
        """更新UI状态。"""
        auto_backup = self._auto_backup_check.isChecked()
        
        # 备份设置
        self._backup_interval_spin.setEnabled(auto_backup)

    def _handle_browse_clicked(self):
        """处理浏览按钮点击事件。"""
        # 发布选择数据目录事件
        self._event_system.publish("select_data_dir", {
            "callback": self._set_data_dir
        })

    def _set_data_dir(self, dir_path):
        """
        设置数据目录。

        Args:
            dir_path: 目录路径
        """
        if not dir_path:
            return
        
        self._data_dir_edit.setText(dir_path)
        self._config_manager.set_data_dir(dir_path)
        self.settings_changed.emit({"data": {"dir": dir_path}})

    def _handle_auto_backup_changed(self, state):
        """
        处理自动备份变更事件。

        Args:
            state: 状态
        """
        enabled = state == Qt.CheckState.Checked.value
        self._config_manager.set("data", "auto_backup", enabled)
        self.settings_changed.emit({"data": {"auto_backup": enabled}})
        
        # 更新UI状态
        self._update_ui_state()

    def _handle_backup_interval_changed(self, value):
        """
        处理备份间隔变更事件。

        Args:
            value: 值
        """
        self._config_manager.set("data", "backup_interval_days", value)
        self.settings_changed.emit({"data": {"backup_interval_days": value}})

    def _handle_backup_now_clicked(self):
        """处理立即备份按钮点击事件。"""
        # 发布立即备份事件
        self._event_system.publish("backup_data_now")

    def _handle_export_clicked(self):
        """处理导出数据按钮点击事件。"""
        # 发布导出数据事件
        self._event_system.publish("export_data")

    def _handle_import_clicked(self):
        """处理导入数据按钮点击事件。"""
        # 发布导入数据事件
        self._event_system.publish("import_data")

    def _handle_clear_clicked(self):
        """处理清空数据按钮点击事件。"""
        # 发布清空数据事件
        self._event_system.publish("clear_data")

    def save_settings(self):
        """保存设置。"""
        # 所有设置已经在变更时保存，无需额外操作
        pass


class AboutTab(SettingsTab):
    """关于选项卡，显示应用程序信息。"""

    def _init_ui(self):
        """初始化UI。"""
        super()._init_ui()
        
        # 应用信息
        app_layout = QVBoxLayout()
        app_layout.setContentsMargins(0, 0, 0, 0)
        app_layout.setSpacing(10)
        app_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # 应用图标
        app_icon = QLabel()
        icon_pixmap = QPixmap(":/icons/app_icon.png")
        if not icon_pixmap.isNull():
            app_icon.setPixmap(icon_pixmap.scaled(64, 64, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        app_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        app_layout.addWidget(app_icon)
        
        # 应用名称
        app_name = QLabel("ideaSystemXS")
        app_name.setStyleSheet("font-size: 24px; font-weight: bold;")
        app_name.setAlignment(Qt.AlignmentFlag.AlignCenter)
        app_layout.addWidget(app_name)
        
        # 应用版本
        app_version = QLabel("版本 1.0.0")
        app_version.setAlignment(Qt.AlignmentFlag.AlignCenter)
        app_layout.addWidget(app_version)
        
        # 应用描述
        app_desc = QLabel("一个智能的想法管理系统")
        app_desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        app_layout.addWidget(app_desc)
        
        # 分隔线
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        app_layout.addWidget(separator)
        
        # 版权信息
        copyright_info = QLabel("© 2025 ideaSystemXS. 保留所有权利。")
        copyright_info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        app_layout.addWidget(copyright_info)
        
        self._main_layout.addLayout(app_layout)
        self._main_layout.addStretch()


class SettingsWindow(QWidget):
    """设置窗口类，用于配置应用程序设置。"""

    def __init__(
        self,
        parent: Optional[QWidget] = None,
        config_manager: Optional[ConfigManager] = None,
        event_system: Optional[EventSystem] = None,
        theme_manager: Optional[ThemeManager] = None,
    ):
        """
        初始化设置窗口。

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
        
        # 设置窗口属性
        self.setWindowTitle("设置")
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # 设置窗口大小
        self.resize(600, 500)
        
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
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(0)
        
        # 标题栏
        title_layout = QHBoxLayout()
        title_layout.setContentsMargins(15, 15, 15, 15)
        title_layout.setSpacing(10)
        
        title_label = QLabel("设置")
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
        
        # 设置选项卡
        self._tab_widget = QTabWidget()
        self._tab_widget.setDocumentMode(True)
        
        # 添加选项卡
        self._general_tab = GeneralSettingsTab(self._tab_widget, self._config_manager, self._event_system, self._theme_manager)
        self._tab_widget.addTab(self._general_tab, "通用")
        
        self._ai_tab = AISettingsTab(self._tab_widget, self._config_manager, self._event_system, self._theme_manager)
        self._tab_widget.addTab(self._ai_tab, "AI")
        
        self._data_tab = DataSettingsTab(self._tab_widget, self._config_manager, self._event_system, self._theme_manager)
        self._tab_widget.addTab(self._data_tab, "数据")
        
        self._about_tab = AboutTab(self._tab_widget, self._config_manager, self._event_system, self._theme_manager)
        self._tab_widget.addTab(self._about_tab, "关于")
        
        container_layout.addWidget(self._tab_widget)
        
        # 按钮区域
        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(15, 15, 15, 15)
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
        self._save_btn.clicked.connect(self._save_settings)
        
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

    def _connect_signals(self):
        """连接信号。"""
        # 主题变更信号
        self._theme_manager.theme_changed.connect(self._update_theme)
        
        # 设置变更信号
        self._general_tab.settings_changed.connect(self._handle_settings_changed)
        self._ai_tab.settings_changed.connect(self._handle_settings_changed)
        self._data_tab.settings_changed.connect(self._handle_settings_changed)

    def _register_event_handlers(self):
        """注册事件处理器。"""
        # 显示设置窗口事件
        self._event_system.subscribe("show_settings_window", self._handle_show_settings_window)

    def _handle_show_settings_window(self, data=None):
        """
        处理显示设置窗口事件。

        Args:
            data: 事件数据
        """
        # 显示窗口
        self.show_with_animation()
        
        # 激活窗口
        self.activateWindow()
        
        # 如果指定了选项卡，切换到指定选项卡
        if data and "tab" in data:
            tab = data["tab"]
            if tab == "general":
                self._tab_widget.setCurrentIndex(0)
            elif tab == "ai":
                self._tab_widget.setCurrentIndex(1)
            elif tab == "data":
                self._tab_widget.setCurrentIndex(2)
            elif tab == "about":
                self._tab_widget.setCurrentIndex(3)

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

    def _handle_settings_changed(self, settings):
        """
        处理设置变更事件。

        Args:
            settings: 设置
        """
        # 发布配置变更事件
        self._event_system.publish("config_changed", settings)

    def _save_settings(self):
        """保存设置。"""
        # 保存各选项卡的设置
        self._general_tab.save_settings()
        self._ai_tab.save_settings()
        self._data_tab.save_settings()
        
        # 关闭窗口
        self.close()

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
        animation = QPropertyAnimation(self, b"windowOpacity")
        animation.setDuration(300)
        animation.setStartValue(0.0)
        animation.setEndValue(1.0)
        animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        animation.start()

    def mousePressEvent(self, event):
        """
        鼠标按下事件。

        Args:
            event: 鼠标事件
        """
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        """
        鼠标移动事件。

        Args:
            event: 鼠标事件
        """
        if event.buttons() == Qt.MouseButton.LeftButton and hasattr(self, '_drag_position'):
            self.move(event.globalPosition().toPoint() - self._drag_position)
            event.accept()
