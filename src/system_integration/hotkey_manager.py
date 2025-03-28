"""
快捷键管理器模块，负责管理全局快捷键。
"""
import threading
from typing import Callable, Dict, Optional

import keyboard

from ..core.config_manager import ConfigManager
from ..core.event_system import EventSystem


class HotkeyManager:
    """快捷键管理器类，负责管理全局快捷键。"""

    _instance = None
    _lock = threading.Lock()

    def __new__(cls, config_manager: Optional[ConfigManager] = None, event_system: Optional[EventSystem] = None):
        """
        实现单例模式。

        Args:
            config_manager: 配置管理器实例
            event_system: 事件系统实例

        Returns:
            HotkeyManager实例
        """
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(HotkeyManager, cls).__new__(cls)
                cls._instance._initialized = False
            return cls._instance

    def __init__(self, config_manager: Optional[ConfigManager] = None, event_system: Optional[EventSystem] = None):
        """
        初始化快捷键管理器。

        Args:
            config_manager: 配置管理器实例
            event_system: 事件系统实例
        """
        if self._initialized:
            return

        self._config_manager = config_manager or ConfigManager()
        self._event_system = event_system or EventSystem()
        self._hotkeys: Dict[str, Callable] = {}
        self._initialized = True

        # 注册事件处理器
        self._event_system.subscribe("config_changed", self._handle_config_changed)

    def _handle_config_changed(self, data=None):
        """
        处理配置更改事件。

        Args:
            data: 事件数据
        """
        if data and "hotkeys" in data:
            # 重新注册快捷键
            self.unregister_all_hotkeys()
            self.register_hotkeys()

    def register_hotkey(self, hotkey: str, callback: Callable) -> bool:
        """
        注册快捷键。

        Args:
            hotkey: 快捷键字符串
            callback: 回调函数

        Returns:
            是否成功注册
        """
        try:
            keyboard.add_hotkey(hotkey, callback, suppress=True)
            self._hotkeys[hotkey] = callback
            return True
        except Exception as e:
            print(f"注册快捷键失败: {e}")
            return False

    def unregister_hotkey(self, hotkey: str) -> bool:
        """
        取消注册快捷键。

        Args:
            hotkey: 快捷键字符串

        Returns:
            是否成功取消注册
        """
        try:
            keyboard.remove_hotkey(hotkey)
            if hotkey in self._hotkeys:
                del self._hotkeys[hotkey]
            return True
        except Exception as e:
            print(f"取消注册快捷键失败: {e}")
            return False

    def unregister_all_hotkeys(self) -> None:
        """取消注册所有快捷键。"""
        for hotkey in list(self._hotkeys.keys()):
            self.unregister_hotkey(hotkey)
        self._hotkeys.clear()

    def register_hotkeys(self) -> None:
        """注册所有配置的快捷键。"""
        # 注册显示输入窗口的快捷键
        show_input_hotkey = self._config_manager.get_show_input_hotkey()
        self.register_hotkey(show_input_hotkey, self._show_input_window)

    def _show_input_window(self) -> None:
        """显示输入窗口。"""
        # 发布显示输入窗口事件
        self._event_system.publish("show_input_window")

    def is_hotkey_registered(self, hotkey: str) -> bool:
        """
        检查快捷键是否已注册。

        Args:
            hotkey: 快捷键字符串

        Returns:
            是否已注册
        """
        return hotkey in self._hotkeys

    def get_registered_hotkeys(self) -> Dict[str, Callable]:
        """
        获取所有已注册的快捷键。

        Returns:
            已注册的快捷键字典
        """
        return self._hotkeys.copy()

    def update_hotkey(self, old_hotkey: str, new_hotkey: str) -> bool:
        """
        更新快捷键。

        Args:
            old_hotkey: 旧快捷键字符串
            new_hotkey: 新快捷键字符串

        Returns:
            是否成功更新
        """
        if old_hotkey not in self._hotkeys:
            return False

        callback = self._hotkeys[old_hotkey]
        if self.unregister_hotkey(old_hotkey) and self.register_hotkey(new_hotkey, callback):
            return True
        return False
