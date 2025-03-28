"""
通知管理器模块，负责管理系统通知。
"""
import os
from typing import Optional

from PyQt6.QtWidgets import QSystemTrayIcon

from ..core.config_manager import ConfigManager
from ..core.event_system import EventSystem


class NotificationManager:
    """通知管理器类，负责管理系统通知。"""

    def __init__(self, config_manager: Optional[ConfigManager] = None, event_system: Optional[EventSystem] = None):
        """
        初始化通知管理器。

        Args:
            config_manager: 配置管理器实例
            event_system: 事件系统实例
        """
        self._config_manager = config_manager or ConfigManager()
        self._event_system = event_system or EventSystem()
        self._system_tray = None
        
        # 注册事件处理器
        self._event_system.subscribe("reminder_triggered", self._handle_reminder_triggered)
        self._event_system.subscribe("idea_processed", self._handle_idea_processed)
        self._event_system.subscribe("ai_task_completed", self._handle_ai_task_completed)
        self._event_system.subscribe("ai_task_failed", self._handle_ai_task_failed)

    def set_system_tray(self, system_tray) -> None:
        """
        设置系统托盘。

        Args:
            system_tray: 系统托盘实例
        """
        self._system_tray = system_tray

    def _handle_reminder_triggered(self, data) -> None:
        """
        处理提醒触发事件。

        Args:
            data: 事件数据
        """
        if not data or "reminder" not in data:
            return
        
        reminder = data["reminder"]
        idea_title = data.get("idea_title", "")
        
        title = "想法提醒"
        message = f"{idea_title}\n{reminder.get('note', '')}"
        
        self.show_notification(title, message)
        
        # 如果启用了提醒声音，播放声音
        if self._config_manager.get("reminders", "notification_sound", True):
            self._play_notification_sound()

    def _handle_idea_processed(self, data) -> None:
        """
        处理想法处理完成事件。

        Args:
            data: 事件数据
        """
        if not data or "idea" not in data:
            return
        
        idea = data["idea"]
        
        title = "想法处理完成"
        message = f"已完成对想法 \"{idea.get('title', '')}\" 的处理"
        
        self.show_notification(title, message)

    def _handle_ai_task_completed(self, data) -> None:
        """
        处理AI任务完成事件。

        Args:
            data: 事件数据
        """
        if not data or "task" not in data:
            return
        
        task = data["task"]
        task_type = task.get("task_type", "")
        
        title = "AI任务完成"
        message = f"已完成{task_type}任务"
        
        self.show_notification(title, message)

    def _handle_ai_task_failed(self, data) -> None:
        """
        处理AI任务失败事件。

        Args:
            data: 事件数据
        """
        if not data or "task" not in data:
            return
        
        task = data["task"]
        task_type = task.get("task_type", "")
        error = task.get("error", "未知错误")
        
        title = "AI任务失败"
        message = f"{task_type}任务失败: {error}"
        
        self.show_notification(title, message, QSystemTrayIcon.MessageIcon.Warning)

    def show_notification(self, title: str, message: str, icon: QSystemTrayIcon.MessageIcon = QSystemTrayIcon.MessageIcon.Information, timeout: int = 5000) -> None:
        """
        显示通知。

        Args:
            title: 通知标题
            message: 通知内容
            icon: 通知图标
            timeout: 超时时间（毫秒）
        """
        if self._system_tray:
            self._system_tray.show_message(title, message, icon, timeout)

    def _play_notification_sound(self) -> None:
        """播放通知声音。"""
        try:
            # 使用系统声音
            if os.name == "nt":  # Windows
                import winsound
                winsound.PlaySound("SystemAsterisk", winsound.SND_ALIAS)
            else:  # Linux/Mac
                os.system("aplay /usr/share/sounds/sound-icons/glass-water-1.wav &>/dev/null &")
        except Exception as e:
            print(f"播放通知声音失败: {e}")
