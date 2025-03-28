"""
事件系统模块，实现基于发布-订阅模式的事件系统。
"""
from typing import Any, Callable, Dict, List, Set


class EventSystem:
    """事件系统类，实现基于发布-订阅模式的事件系统。"""

    def __init__(self):
        """初始化事件系统。"""
        self._subscribers: Dict[str, List[Callable]] = {}
        self._event_history: Dict[str, Any] = {}
        self._max_history_size = 100

    def subscribe(self, event_type: str, callback: Callable) -> None:
        """
        订阅事件。

        Args:
            event_type: 事件类型
            callback: 回调函数
        """
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(callback)

    def unsubscribe(self, event_type: str, callback: Callable) -> None:
        """
        取消订阅事件。

        Args:
            event_type: 事件类型
            callback: 回调函数
        """
        if event_type in self._subscribers and callback in self._subscribers[event_type]:
            self._subscribers[event_type].remove(callback)
            if not self._subscribers[event_type]:
                del self._subscribers[event_type]

    def publish(self, event_type: str, data: Any = None) -> None:
        """
        发布事件。

        Args:
            event_type: 事件类型
            data: 事件数据
        """
        # 记录事件历史
        self._event_history[event_type] = data
        if len(self._event_history) > self._max_history_size:
            # 移除最旧的事件
            oldest_event = next(iter(self._event_history))
            del self._event_history[oldest_event]

        # 通知订阅者
        if event_type in self._subscribers:
            for callback in self._subscribers[event_type]:
                try:
                    callback(data)
                except Exception as e:
                    print(f"事件处理错误: {e}")

    def get_last_event_data(self, event_type: str) -> Any:
        """
        获取最近一次事件的数据。

        Args:
            event_type: 事件类型

        Returns:
            事件数据
        """
        return self._event_history.get(event_type)

    def get_all_event_types(self) -> Set[str]:
        """
        获取所有事件类型。

        Returns:
            事件类型集合
        """
        return set(self._subscribers.keys()) | set(self._event_history.keys())

    def clear_history(self) -> None:
        """清除事件历史。"""
        self._event_history.clear()

    def has_subscribers(self, event_type: str) -> bool:
        """
        检查事件是否有订阅者。

        Args:
            event_type: 事件类型

        Returns:
            是否有订阅者
        """
        return event_type in self._subscribers and bool(self._subscribers[event_type])
