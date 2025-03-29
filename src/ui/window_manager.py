"""
窗口管理器模块，负责管理应用程序的窗口。
"""
from typing import Optional, Dict

from PyQt6.QtWidgets import QApplication, QMessageBox, QFileDialog

from src.core.config_manager import ConfigManager
from src.core.event_system import EventSystem
from src.ui.main_window import MainWindow
from src.ui.input_window import InputWindow
from src.ui.settings_window import SettingsWindow
from src.business.idea_manager import IdeaManager
from src.business.tag_manager import TagManager


class WindowManager:
    """窗口管理器类，负责管理应用程序的窗口。"""

    _instance = None

    def __new__(cls, config_manager=None, event_system=None):
        """
        实现单例模式，确保只创建一个实例。

        Args:
            config_manager: 配置管理器实例
            event_system: 事件系统实例

        Returns:
            WindowManager 实例
        """
        if cls._instance is None:
            cls._instance = super(WindowManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, config_manager: Optional[ConfigManager] = None, event_system: Optional[EventSystem] = None):
        """
        初始化窗口管理器。

        Args:
            config_manager: 配置管理器实例
            event_system: 事件系统实例
        """
        if self._initialized:
            return

        self._config_manager = config_manager or ConfigManager()
        self._event_system = event_system or EventSystem()
        
        # 窗口实例
        self._main_window = None
        self._input_window = None
        self._settings_window = None
        self._dialog_cache = {}
        
        # 初始化业务逻辑组件
        self._idea_manager = IdeaManager(self._config_manager, self._event_system)
        self._tag_manager = TagManager(self._config_manager, self._event_system)
        
        # 注册事件处理器
        self._register_event_handlers()
        
        self._initialized = True

    def _register_event_handlers(self):
        """注册事件处理器。"""
        # 窗口显示事件
        self._event_system.subscribe("show_main_window", self._handle_show_main_window)
        self._event_system.subscribe("show_input_window", self._handle_show_input_window)
        self._event_system.subscribe("show_settings_window", self._handle_show_settings_window)
        
        # 对话框事件
        self._event_system.subscribe("confirm_delete_idea", self._handle_confirm_delete_idea)
        self._event_system.subscribe("confirm_delete_tag", self._handle_confirm_delete_tag)
        
        # 文件对话框事件
        self._event_system.subscribe("select_data_dir", self._handle_select_data_dir)
        self._event_system.subscribe("export_data", self._handle_export_data)
        self._event_system.subscribe("import_data", self._handle_import_data)
        
        # 应用程序事件
        self._event_system.subscribe("app_exit", self._handle_app_exit)

    def _handle_show_main_window(self, data=None):
        """
        处理显示主窗口事件。

        Args:
            data: 事件数据
        """
        if self._main_window is None:
            self._main_window = MainWindow(
                config_manager=self._config_manager,
                event_system=self._event_system
            )
        
        if data and 'page' in data:
            page_index = data['page']
            self._main_window._sidebar.set_current_page(page_index)
        
        self._main_window.show_with_animation()
        self._main_window.activateWindow()
        self._main_window.raise_()

    def _handle_show_input_window(self, data=None):
        """
        处理显示输入窗口事件。

        Args:
            data: 事件数据
        """
        if self._input_window is None:
            self._input_window = InputWindow(
                config_manager=self._config_manager,
                event_system=self._event_system,
                idea_manager=self._idea_manager
            )
        
        self._input_window.show_with_animation()
        self._input_window.activateWindow()
        self._input_window.raise_()

    def _handle_show_settings_window(self, data=None):
        """
        处理显示设置窗口事件。

        Args:
            data: 事件数据
        """
        if self._settings_window is None:
            self._settings_window = SettingsWindow(
                config_manager=self._config_manager,
                event_system=self._event_system
            )
        
        self._settings_window.show_with_animation()
        self._settings_window.activateWindow()
        self._settings_window.raise_()

    def _handle_confirm_delete_idea(self, data):
        """
        处理确认删除想法事件。

        Args:
            data: 事件数据，包含 idea_id
        """
        idea_id = data.get('idea_id')
        if idea_id is None:
            return
        
        # 获取想法信息
        idea = self._idea_manager.get_idea(idea_id)
        if not idea:
            return
        
        # 显示确认对话框
        msg_box = QMessageBox()
        msg_box.setWindowTitle("确认删除")
        msg_box.setText(f"确定要删除想法 '{idea['title']}' 吗？")
        msg_box.setInformativeText("此操作不可撤销！")
        msg_box.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        msg_box.setDefaultButton(QMessageBox.StandardButton.No)
        
        ret = msg_box.exec()
        
        if ret == QMessageBox.StandardButton.Yes:
            # 删除想法
            self._idea_manager.delete_idea(idea_id)

    def _handle_confirm_delete_tag(self, data):
        """
        处理确认删除标签事件。

        Args:
            data: 事件数据，包含 tag
        """
        tag = data.get('tag')
        if not tag:
            return
        
        # 显示确认对话框
        msg_box = QMessageBox()
        msg_box.setWindowTitle("确认删除")
        msg_box.setText(f"确定要删除标签 '{tag}' 吗？")
        msg_box.setInformativeText("此操作不可撤销！")
        msg_box.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        msg_box.setDefaultButton(QMessageBox.StandardButton.No)
        
        ret = msg_box.exec()
        
        if ret == QMessageBox.StandardButton.Yes:
            # 删除标签
            self._tag_manager.delete_tag(tag)

    def _handle_select_data_dir(self, data):
        """
        处理选择数据目录事件。

        Args:
            data: 事件数据，包含 callback
        """
        callback = data.get('callback')
        if not callback:
            return
        
        # 打开目录选择对话框
        dir_path = QFileDialog.getExistingDirectory(
            None,
            "选择数据目录",
            self._config_manager.get_data_dir(),
            QFileDialog.Option.ShowDirsOnly
        )
        
        if dir_path:
            callback(dir_path)

    def _handle_export_data(self, data=None):
        """
        处理导出数据事件。

        Args:
            data: 事件数据
        """
        # 打开文件保存对话框
        file_path, _ = QFileDialog.getSaveFileName(
            None,
            "导出数据",
            "",
            "ZIP 文件 (*.zip)"
        )
        
        if file_path:
            # 确保文件扩展名为 .zip
            if not file_path.endswith('.zip'):
                file_path += '.zip'
            
            # 发布导出数据任务事件
            self._event_system.publish("export_data_task", {
                "file_path": file_path
            })

    def _handle_import_data(self, data=None):
        """
        处理导入数据事件。

        Args:
            data: 事件数据
        """
        # 打开文件选择对话框
        file_path, _ = QFileDialog.getOpenFileName(
            None,
            "导入数据",
            "",
            "ZIP 文件 (*.zip)"
        )
        
        if file_path:
            # 显示确认对话框
            msg_box = QMessageBox()
            msg_box.setWindowTitle("确认导入")
            msg_box.setText("导入数据将覆盖当前的数据，确定要继续吗？")
            msg_box.setInformativeText("建议在导入前备份当前数据！")
            msg_box.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            msg_box.setDefaultButton(QMessageBox.StandardButton.No)
            
            ret = msg_box.exec()
            
            if ret == QMessageBox.StandardButton.Yes:
                # 发布导入数据任务事件
                self._event_system.publish("import_data_task", {
                    "file_path": file_path
                })

    def _handle_app_exit(self, data=None):
        """
        处理应用程序退出事件。

        Args:
            data: 事件数据
        """
        # 关闭所有窗口
        if self._main_window:
            self._main_window.close()
        
        if self._input_window:
            self._input_window.close()
        
        if self._settings_window:
            self._settings_window.close()

    def show_main_window(self, page_index=None):
        """
        显示主窗口。

        Args:
            page_index: 页面索引
        """
        data = None
        if page_index is not None:
            data = {'page': page_index}
        
        self._event_system.publish("show_main_window", data)

    def show_input_window(self):
        """显示输入窗口。"""
        self._event_system.publish("show_input_window")

    def show_settings_window(self, tab=None):
        """
        显示设置窗口。

        Args:
            tab: 选项卡名称
        """
        data = None
        if tab:
            data = {'tab': tab}
        
        self._event_system.publish("show_settings_window", data)

    def show_message_box(self, title, text, info_text=None, buttons=QMessageBox.StandardButton.Ok, default_button=QMessageBox.StandardButton.Ok):
        """
        显示消息对话框。

        Args:
            title: 标题
            text: 文本
            info_text: 详细信息
            buttons: 按钮
            default_button: 默认按钮

        Returns:
            按钮结果
        """
        msg_box = QMessageBox()
        msg_box.setWindowTitle(title)
        msg_box.setText(text)
        
        if info_text:
            msg_box.setInformativeText(info_text)
        
        msg_box.setStandardButtons(buttons)
        msg_box.setDefaultButton(default_button)
        
        return msg_box.exec()

    def show_file_dialog(self, dialog_type, title, directory="", filter=""):
        """
        显示文件对话框。

        Args:
            dialog_type: 对话框类型，save 或 open
            title: 标题
            directory: 目录
            filter: 过滤器

        Returns:
            文件路径
        """
        if dialog_type == "save":
            file_path, _ = QFileDialog.getSaveFileName(None, title, directory, filter)
        else:  # open
            file_path, _ = QFileDialog.getOpenFileName(None, title, directory, filter)
        
        return file_path

    def show_directory_dialog(self, title, directory=""):
        """
        显示目录对话框。

        Args:
            title: 标题
            directory: 目录

        Returns:
            目录路径
        """
        return QFileDialog.getExistingDirectory(None, title, directory, QFileDialog.Option.ShowDirsOnly)

    def close_all_windows(self):
        """关闭所有窗口。"""
        if self._main_window:
            self._main_window.close()
        
        if self._input_window:
            self._input_window.close()
        
        if self._settings_window:
            self._settings_window.close()
