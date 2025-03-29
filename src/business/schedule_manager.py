"""
定时任务管理器模块，管理定时提醒和任务。
"""
import datetime
import threading
import time
from typing import Callable, Dict, List, Optional

import schedule

from src.core.config_manager import ConfigManager
from src.core.event_system import EventSystem
from src.data.database_manager import DatabaseManager


class ScheduleManager:
    """定时任务管理器类，管理定时提醒和任务。"""

    _instance = None
    _lock = threading.Lock()

    def __new__(cls, config_manager: Optional[ConfigManager] = None, event_system: Optional[EventSystem] = None, database_manager: Optional[DatabaseManager] = None):
        """
        实现单例模式。

        Args:
            config_manager: 配置管理器实例
            event_system: 事件系统实例
            database_manager: 数据库管理器实例

        Returns:
            ScheduleManager实例
        """
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(ScheduleManager, cls).__new__(cls)
                cls._instance._initialized = False
            return cls._instance

    def __init__(self, config_manager: Optional[ConfigManager] = None, event_system: Optional[EventSystem] = None, database_manager: Optional[DatabaseManager] = None):
        """
        初始化定时任务管理器。

        Args:
            config_manager: 配置管理器实例
            event_system: 事件系统实例
            database_manager: 数据库管理器实例
        """
        if self._initialized:
            return

        self._config_manager = config_manager or ConfigManager()
        self._event_system = event_system or EventSystem()
        self._database_manager = database_manager or DatabaseManager(self._config_manager)
        self._scheduler = schedule.Scheduler()
        self._running = False
        self._thread = None
        self._initialized = True

        # 注册事件处理器
        self._event_system.subscribe("app_exit", self._handle_app_exit)
        self._event_system.subscribe("reminder_added", self._handle_reminder_added)
        self._event_system.subscribe("reminder_updated", self._handle_reminder_updated)
        self._event_system.subscribe("reminder_deleted", self._handle_reminder_deleted)

    def _handle_app_exit(self, data=None):
        """
        处理应用程序退出事件。

        Args:
            data: 事件数据
        """
        self.stop()

    def _handle_reminder_added(self, data):
        """
        处理提醒添加事件。

        Args:
            data: 事件数据
        """
        if not data or "reminder" not in data:
            return

        reminder = data["reminder"]
        self._schedule_reminder(reminder)

    def _handle_reminder_updated(self, data):
        """
        处理提醒更新事件。

        Args:
            data: 事件数据
        """
        if not data or "reminder" not in data or "original" not in data:
            return

        reminder = data["reminder"]
        original = data["original"]

        # 如果提醒时间或完成状态发生变化，重新调度
        if (reminder["reminder_time"] != original["reminder_time"] or
                reminder["is_completed"] != original["is_completed"]):
            # 取消原有任务
            self._cancel_reminder(original)
            # 如果未完成，调度新任务
            if not reminder["is_completed"]:
                self._schedule_reminder(reminder)

    def _handle_reminder_deleted(self, data):
        """
        处理提醒删除事件。

        Args:
            data: 事件数据
        """
        if not data or "reminder" not in data:
            return

        reminder = data["reminder"]
        self._cancel_reminder(reminder)

    def _schedule_reminder(self, reminder):
        """
        调度提醒任务。

        Args:
            reminder: 提醒字典
        """
        reminder_id = reminder["id"]
        reminder_time = reminder["reminder_time"]
        
        # 如果提醒时间已过或已完成，不调度
        if (isinstance(reminder_time, str) and reminder_time <= datetime.datetime.now().isoformat()) or reminder["is_completed"]:
            return

        # 转换提醒时间为datetime对象
        if isinstance(reminder_time, str):
            try:
                reminder_time = datetime.datetime.fromisoformat(reminder_time)
            except ValueError:
                print(f"无效的提醒时间格式: {reminder_time}")
                return

        # 如果提醒时间已过，不调度
        if reminder_time <= datetime.datetime.now():
            return

        # 创建任务
        job_tag = f"reminder_{reminder_id}"
        
        # 取消同名任务
        self._scheduler.clear(job_tag)
        
        # 调度任务
        self._scheduler.every().day.at(reminder_time.strftime("%H:%M")).do(
            self._trigger_reminder, reminder_id=reminder_id
        ).tag(job_tag)

    def _cancel_reminder(self, reminder):
        """
        取消提醒任务。

        Args:
            reminder: 提醒字典
        """
        reminder_id = reminder["id"]
        job_tag = f"reminder_{reminder_id}"
        self._scheduler.clear(job_tag)

    def _trigger_reminder(self, reminder_id):
        """
        触发提醒。

        Args:
            reminder_id: 提醒ID

        Returns:
            是否继续调度
        """
        # 获取提醒信息
        self._database_manager.execute(
            """
            SELECT r.*, i.title as idea_title FROM Reminders r
            JOIN Ideas i ON r.idea_id = i.id
            WHERE r.id = ?
            """,
            (reminder_id,)
        )
        reminder = self._database_manager.fetchone()
        
        if not reminder:
            return schedule.CancelJob  # 提醒不存在，取消任务
        
        if reminder["is_completed"]:
            return schedule.CancelJob  # 提醒已完成，取消任务
        
        # 发布提醒触发事件
        self._event_system.publish("reminder_triggered", {"reminder": reminder, "idea_title": reminder["idea_title"]})
        
        # 更新提醒状态为已完成
        self._database_manager.execute(
            "UPDATE Reminders SET is_completed = 1 WHERE id = ?",
            (reminder_id,)
        )
        self._database_manager.commit()
        
        return schedule.CancelJob  # 任务完成，取消调度

    def start(self):
        """启动定时任务管理器。"""
        if self._running:
            return

        self._running = True
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

        # 加载所有未完成的提醒
        self._load_reminders()

    def stop(self):
        """停止定时任务管理器。"""
        self._running = False
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=1.0)

    def _run(self):
        """运行定时任务管理器。"""
        while self._running:
            self._scheduler.run_pending()
            time.sleep(1)

    def _load_reminders(self):
        """加载所有未完成的提醒。"""
        # 清除所有任务
        self._scheduler.clear()

        # 获取所有未完成的提醒
        self._database_manager.execute(
            """
            SELECT * FROM Reminders
            WHERE is_completed = 0
            ORDER BY reminder_time
            """
        )
        reminders = self._database_manager.fetchall()

        # 调度所有提醒
        for reminder in reminders:
            self._schedule_reminder(reminder)

    def schedule_task(self, task_func: Callable, interval: int, unit: str = "minutes", task_id: Optional[str] = None):
        """
        调度定时任务。

        Args:
            task_func: 任务函数
            interval: 时间间隔
            unit: 时间单位，可选值：seconds, minutes, hours, days, weeks
            task_id: 任务ID，用于取消任务

        Returns:
            任务ID
        """
        if task_id is None:
            task_id = f"task_{id(task_func)}"

        # 取消同名任务
        self._scheduler.clear(task_id)

        # 调度任务
        job = None
        if unit == "seconds":
            job = self._scheduler.every(interval).seconds.do(task_func)
        elif unit == "minutes":
            job = self._scheduler.every(interval).minutes.do(task_func)
        elif unit == "hours":
            job = self._scheduler.every(interval).hours.do(task_func)
        elif unit == "days":
            job = self._scheduler.every(interval).days.do(task_func)
        elif unit == "weeks":
            job = self._scheduler.every(interval).weeks.do(task_func)
        else:
            raise ValueError(f"无效的时间单位: {unit}")

        job.tag(task_id)
        return task_id

    def cancel_task(self, task_id: str):
        """
        取消定时任务。

        Args:
            task_id: 任务ID
        """
        self._scheduler.clear(task_id)

    def get_pending_tasks(self) -> List[Dict]:
        """
        获取待执行的任务。

        Returns:
            任务字典列表
        """
        tasks = []
        for job in self._scheduler.jobs:
            tasks.append({
                "task_id": job.tags[0] if job.tags else None,
                "next_run": job.next_run,
                "interval": job.interval,
                "unit": job.unit
            })
        return tasks

    def check_due_reminders(self):
        """检查到期提醒。"""
        # 获取所有到期但未完成的提醒
        self._database_manager.execute(
            """
            SELECT r.*, i.title as idea_title FROM Reminders r
            JOIN Ideas i ON r.idea_id = i.id
            WHERE r.reminder_time <= CURRENT_TIMESTAMP AND r.is_completed = 0
            ORDER BY r.reminder_time
            """
        )
        due_reminders = self._database_manager.fetchall()

        # 触发所有到期提醒
        for reminder in due_reminders:
            # 发布提醒触发事件
            self._event_system.publish("reminder_triggered", {"reminder": reminder, "idea_title": reminder["idea_title"]})
            
            # 更新提醒状态为已完成
            self._database_manager.execute(
                "UPDATE Reminders SET is_completed = 1 WHERE id = ?",
                (reminder["id"],)
            )
            self._database_manager.commit()

    def schedule_ai_tasks(self):
        """调度AI任务检查。"""
        # 如果AI功能已启用且不处于离线模式，调度AI任务检查
        if self._config_manager.is_ai_enabled() and not self._config_manager.is_offline_mode():
            check_interval = self._config_manager.get("ai", "check_interval_minutes", 15)
            self.schedule_task(self._check_ai_tasks, check_interval, "minutes", "ai_tasks_check")

    def _check_ai_tasks(self):
        """检查AI任务。"""
        # 发布AI任务检查事件
        self._event_system.publish("check_ai_tasks")
