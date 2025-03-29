"""
定时提醒系统模块，用于管理定时提醒。
"""
import datetime
import threading
import time
from typing import Callable, Dict, List, Optional, Tuple, Union

from src.ai.ai_service import AIService
from src.business.idea_manager import IdeaManager
from src.core.config_manager import ConfigManager
from src.core.event_system import EventSystem
from src.system_integration.notification_manager import NotificationManager


class ReminderSystem:
    """定时提醒系统类，用于管理定时提醒。"""

    def __init__(
        self,
        config_manager: Optional[ConfigManager] = None,
        event_system: Optional[EventSystem] = None,
        ai_service: Optional[AIService] = None,
        idea_manager: Optional[IdeaManager] = None,
        notification_manager: Optional[NotificationManager] = None,
    ):
        """
        初始化定时提醒系统。

        Args:
            config_manager: 配置管理器实例
            event_system: 事件系统实例
            ai_service: AI服务实例
            idea_manager: 想法管理器实例
            notification_manager: 通知管理器实例
        """
        self._config_manager = config_manager or ConfigManager()
        self._event_system = event_system or EventSystem()
        self._ai_service = ai_service or AIService(self._config_manager, self._event_system)
        self._idea_manager = idea_manager or IdeaManager(self._config_manager, self._event_system)
        self._notification_manager = notification_manager or NotificationManager(self._config_manager, self._event_system)
        
        # 提醒线程
        self._reminder_thread = None
        self._stop_thread = False
        
        # 注册事件处理器
        self._register_event_handlers()
        
        # 启动提醒线程
        self._start_reminder_thread()

    def _register_event_handlers(self):
        """注册事件处理器。"""
        # 添加提醒事件
        self._event_system.subscribe("add_reminder", self._handle_add_reminder)
        
        # 删除提醒事件
        self._event_system.subscribe("delete_reminder", self._handle_delete_reminder)
        
        # 获取提醒事件
        self._event_system.subscribe("get_reminders", self._handle_get_reminders)
        
        # 生成提醒建议事件
        self._event_system.subscribe("generate_reminder_suggestion", self._handle_generate_reminder_suggestion)
        
        # 应用程序退出事件
        self._event_system.subscribe("app_exit", self._handle_app_exit)

    def _handle_add_reminder(self, data):
        """
        处理添加提醒事件。

        Args:
            data: 事件数据，包含idea_id、remind_time、remind_reason和callback字段
        """
        # 获取想法ID
        idea_id = data.get("idea_id", None)
        
        # 获取提醒时间
        remind_time = data.get("remind_time", None)
        
        # 获取提醒原因
        remind_reason = data.get("remind_reason", "")
        
        # 获取回调函数
        callback = data.get("callback", None)
        
        # 如果想法ID或提醒时间为空，不处理
        if idea_id is None or remind_time is None:
            return
        
        # 添加提醒
        success = self.add_reminder(idea_id, remind_time, remind_reason)
        
        # 如果有回调函数，调用回调函数
        if callback:
            callback(success)

    def _handle_delete_reminder(self, data):
        """
        处理删除提醒事件。

        Args:
            data: 事件数据，包含reminder_id和callback字段
        """
        # 获取提醒ID
        reminder_id = data.get("reminder_id", None)
        
        # 获取回调函数
        callback = data.get("callback", None)
        
        # 如果提醒ID为空，不处理
        if reminder_id is None:
            return
        
        # 删除提醒
        success = self.delete_reminder(reminder_id)
        
        # 如果有回调函数，调用回调函数
        if callback:
            callback(success)

    def _handle_get_reminders(self, data):
        """
        处理获取提醒事件。

        Args:
            data: 事件数据，包含idea_id和callback字段
        """
        # 获取想法ID
        idea_id = data.get("idea_id", None)
        
        # 获取回调函数
        callback = data.get("callback", None)
        
        # 获取提醒
        reminders = self.get_reminders(idea_id)
        
        # 如果有回调函数，调用回调函数
        if callback:
            callback(reminders)

    def _handle_generate_reminder_suggestion(self, data):
        """
        处理生成提醒建议事件。

        Args:
            data: 事件数据，包含idea_id和callback字段
        """
        # 获取想法ID
        idea_id = data.get("idea_id", None)
        
        # 获取回调函数
        callback = data.get("callback", None)
        
        # 如果想法ID为空，不处理
        if idea_id is None:
            return
        
        # 获取想法
        idea = self._idea_manager.get_idea(idea_id)
        
        # 如果想法不存在，不处理
        if not idea:
            return
        
        # 生成提醒建议
        suggestion = self.generate_reminder_suggestion(idea["content"])
        
        # 如果有回调函数，调用回调函数
        if callback:
            callback(suggestion)

    def _handle_app_exit(self, data=None):
        """
        处理应用程序退出事件。

        Args:
            data: 事件数据
        """
        # 停止提醒线程
        self._stop_reminder_thread()

    def _start_reminder_thread(self):
        """启动提醒线程。"""
        # 如果线程已经启动，不重复启动
        if self._reminder_thread is not None and self._reminder_thread.is_alive():
            return
        
        # 重置停止标志
        self._stop_thread = False
        
        # 创建线程
        self._reminder_thread = threading.Thread(target=self._reminder_loop, daemon=True)
        
        # 启动线程
        self._reminder_thread.start()

    def _stop_reminder_thread(self):
        """停止提醒线程。"""
        # 设置停止标志
        self._stop_thread = True
        
        # 等待线程结束
        if self._reminder_thread is not None and self._reminder_thread.is_alive():
            self._reminder_thread.join(timeout=1.0)

    def _reminder_loop(self):
        """提醒循环。"""
        while not self._stop_thread:
            try:
                # 检查是否有到期的提醒
                self._check_reminders()
                
                # 休眠一段时间
                time.sleep(60)  # 每分钟检查一次
            except Exception as e:
                # 记录错误
                print(f"提醒循环异常: {str(e)}")
                
                # 休眠一段时间
                time.sleep(60)

    def _check_reminders(self):
        """检查是否有到期的提醒。"""
        # 获取当前时间
        now = datetime.datetime.now()
        
        # 获取所有提醒
        reminders = self.get_reminders()
        
        # 检查每个提醒
        for reminder in reminders:
            # 获取提醒时间
            remind_time_str = reminder.get("remind_time", "")
            
            # 如果提醒时间为空，跳过
            if not remind_time_str:
                continue
            
            try:
                # 解析提醒时间
                remind_time = datetime.datetime.strptime(remind_time_str, "%Y-%m-%d %H:%M:%S")
                
                # 如果提醒时间已到，触发提醒
                if remind_time <= now:
                    # 触发提醒
                    self._trigger_reminder(reminder)
                    
                    # 删除提醒
                    self.delete_reminder(reminder["id"])
            except Exception as e:
                # 记录错误
                print(f"检查提醒异常: {str(e)}")

    def _trigger_reminder(self, reminder):
        """
        触发提醒。

        Args:
            reminder: 提醒信息
        """
        # 获取想法ID
        idea_id = reminder.get("idea_id", None)
        
        # 如果想法ID为空，不处理
        if idea_id is None:
            return
        
        # 获取想法
        idea = self._idea_manager.get_idea(idea_id)
        
        # 如果想法不存在，不处理
        if not idea:
            return
        
        # 获取提醒原因
        remind_reason = reminder.get("remind_reason", "")
        
        # 构建提醒标题
        title = f"想法提醒: {idea.get('title', '')}"
        
        # 构建提醒内容
        content = f"{remind_reason}\n\n{idea.get('content', '')}"
        
        # 发送通知
        self._notification_manager.send_notification(title, content)
        
        # 发布提醒触发事件
        self._event_system.publish("reminder_triggered", {
            "reminder": reminder,
            "idea": idea
        })

    def add_reminder(self, idea_id: int, remind_time: str, remind_reason: str = "") -> bool:
        """
        添加提醒。

        Args:
            idea_id: 想法ID
            remind_time: 提醒时间，格式为YYYY-MM-DD HH:MM:SS
            remind_reason: 提醒原因

        Returns:
            是否添加成功
        """
        # 如果想法ID为空，返回False
        if idea_id is None:
            return False
        
        # 如果提醒时间为空，返回False
        if not remind_time:
            return False
        
        try:
            # 解析提醒时间
            datetime.datetime.strptime(remind_time, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            # 如果提醒时间格式不正确，返回False
            return False
        
        # 添加提醒到数据库
        reminder_id = self._idea_manager.add_reminder(idea_id, remind_time, remind_reason)
        
        # 如果添加失败，返回False
        if reminder_id is None:
            return False
        
        # 发布提醒添加事件
        self._event_system.publish("reminder_added", {
            "id": reminder_id,
            "idea_id": idea_id,
            "remind_time": remind_time,
            "remind_reason": remind_reason
        })
        
        return True

    def delete_reminder(self, reminder_id: int) -> bool:
        """
        删除提醒。

        Args:
            reminder_id: 提醒ID

        Returns:
            是否删除成功
        """
        # 如果提醒ID为空，返回False
        if reminder_id is None:
            return False
        
        # 删除提醒
        success = self._idea_manager.delete_reminder(reminder_id)
        
        # 如果删除成功，发布提醒删除事件
        if success:
            self._event_system.publish("reminder_deleted", {
                "id": reminder_id
            })
        
        return success

    def get_reminders(self, idea_id: Optional[int] = None) -> List[Dict]:
        """
        获取提醒。

        Args:
            idea_id: 想法ID，如果为None，则获取所有提醒

        Returns:
            提醒列表
        """
        # 获取提醒
        reminders = self._idea_manager.get_reminders(idea_id)
        
        return reminders

    def generate_reminder_suggestion(self, content: str) -> Dict:
        """
        生成提醒建议。

        Args:
            content: 想法内容

        Returns:
            提醒建议，包含should_remind、remind_time和remind_reason字段
        """
        # 使用AI服务生成提醒建议
        suggestion = self._ai_service.generate_reminder(content)
        
        return suggestion
