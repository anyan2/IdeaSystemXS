"""
配置管理器模块，负责管理应用程序配置。
"""
import os
import json
from pathlib import Path
from typing import Any, Dict, Optional


class ConfigManager:
    """配置管理器类，负责管理应用程序配置。"""

    def __init__(self, config_file: str = "config.json"):
        """
        初始化配置管理器。

        Args:
            config_file: 配置文件名，默认为config.json
        """
        self.config_file = config_file
        self.config_dir = self._get_config_dir()
        self.config_path = os.path.join(self.config_dir, self.config_file)
        self.config = self._load_config()

    def _get_config_dir(self) -> str:
        """
        获取配置文件目录。

        Returns:
            配置文件目录路径
        """
        # 检查是否在开发环境中
        if os.path.exists(os.path.join(os.getcwd(), "src")):
            # 开发环境，使用项目目录下的data文件夹
            config_dir = os.path.join(os.getcwd(), "data")
        else:
            # 生产环境，使用用户数据目录
            if os.name == "nt":  # Windows
                app_data = os.getenv("APPDATA")
                if app_data:
                    config_dir = os.path.join(app_data, "ideaSystemXS")
                else:
                    config_dir = os.path.join(os.path.expanduser("~"), "ideaSystemXS")
            else:  # Linux/Mac
                config_dir = os.path.join(os.path.expanduser("~"), ".ideaSystemXS")

        # 确保目录存在
        os.makedirs(config_dir, exist_ok=True)
        return config_dir

    def _load_config(self) -> Dict[str, Any]:
        """
        加载配置文件。

        Returns:
            配置字典
        """
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                print(f"加载配置文件失败: {e}")
                return self._get_default_config()
        else:
            # 配置文件不存在，创建默认配置
            default_config = self._get_default_config()
            self._save_config(default_config)
            return default_config

    def _get_default_config(self) -> Dict[str, Any]:
        """
        获取默认配置。

        Returns:
            默认配置字典
        """
        return {
            "general": {
                "theme": "light",  # 主题: light, dark
                "language": "zh_CN",  # 语言
                "first_run": True,  # 是否首次运行
            },
            "hotkeys": {
                "show_input": "Ctrl+Alt+I",  # 显示输入窗口的快捷键
                "save_idea": "Ctrl+Enter",  # 保存想法的快捷键
            },
            "database": {
                "sqlite_path": os.path.join(self.config_dir, "ideas.db"),  # SQLite数据库路径
                "vector_db_path": os.path.join(self.config_dir, "vector_db"),  # 向量数据库路径
                "backup_dir": os.path.join(self.config_dir, "backups"),  # 备份目录
                "auto_backup": True,  # 是否自动备份
                "backup_interval_days": 7,  # 备份间隔（天）
            },
            "ai": {
                "enabled": True,  # 是否启用AI功能
                "api_url": "https://api.openai.com/v1",  # API URL
                "api_key": "",  # API密钥
                "model": "gpt-3.5-turbo",  # 模型名称
                "embedding_model": "text-embedding-ada-002",  # 嵌入模型名称
                "max_tokens": 1000,  # 最大令牌数
                "temperature": 0.7,  # 温度
                "offline_mode": False,  # 是否离线模式
            },
            "ui": {
                "font_size": 12,  # 字体大小
                "window_width": 800,  # 窗口宽度
                "window_height": 600,  # 窗口高度
                "opacity": 0.95,  # 窗口透明度
                "blur_effect": True,  # 是否启用毛玻璃效果
                "animation_speed": 300,  # 动画速度（毫秒）
            },
            "reminders": {
                "enabled": True,  # 是否启用提醒功能
                "check_interval_minutes": 30,  # 检查间隔（分钟）
                "notification_sound": True,  # 是否播放提醒声音
            },
        }

    def _save_config(self, config: Optional[Dict[str, Any]] = None) -> None:
        """
        保存配置到文件。

        Args:
            config: 要保存的配置，如果为None则保存当前配置
        """
        if config is None:
            config = self.config

        try:
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=4, ensure_ascii=False)
        except IOError as e:
            print(f"保存配置文件失败: {e}")

    def get(self, section: str, key: str, default: Any = None) -> Any:
        """
        获取配置项。

        Args:
            section: 配置节
            key: 配置键
            default: 默认值

        Returns:
            配置值
        """
        try:
            return self.config[section][key]
        except KeyError:
            return default

    def set(self, section: str, key: str, value: Any) -> None:
        """
        设置配置项。

        Args:
            section: 配置节
            key: 配置键
            value: 配置值
        """
        if section not in self.config:
            self.config[section] = {}
        self.config[section][key] = value
        self._save_config()

    def get_section(self, section: str) -> Dict[str, Any]:
        """
        获取配置节。

        Args:
            section: 配置节

        Returns:
            配置节字典
        """
        return self.config.get(section, {})

    def set_section(self, section: str, values: Dict[str, Any]) -> None:
        """
        设置配置节。

        Args:
            section: 配置节
            values: 配置值字典
        """
        self.config[section] = values
        self._save_config()

    def reset_to_default(self) -> None:
        """重置配置为默认值。"""
        self.config = self._get_default_config()
        self._save_config()

    def get_data_dir(self) -> str:
        """
        获取数据目录。

        Returns:
            数据目录路径
        """
        return self.config_dir

    def get_sqlite_path(self) -> str:
        """
        获取SQLite数据库路径。

        Returns:
            SQLite数据库路径
        """
        return self.get("database", "sqlite_path")

    def get_vector_db_path(self) -> str:
        """
        获取向量数据库路径。

        Returns:
            向量数据库路径
        """
        return self.get("database", "vector_db_path")

    def is_ai_enabled(self) -> bool:
        """
        检查AI功能是否启用。

        Returns:
            AI功能是否启用
        """
        return self.get("ai", "enabled", False)

    def is_offline_mode(self) -> bool:
        """
        检查是否处于离线模式。

        Returns:
            是否处于离线模式
        """
        return self.get("ai", "offline_mode", False)

    def get_api_key(self) -> str:
        """
        获取API密钥。

        Returns:
            API密钥
        """
        return self.get("ai", "api_key", "")

    def get_api_url(self) -> str:
        """
        获取API URL。

        Returns:
            API URL
        """
        return self.get("ai", "api_url", "")

    def get_show_input_hotkey(self) -> str:
        """
        获取显示输入窗口的快捷键。

        Returns:
            快捷键字符串
        """
        return self.get("hotkeys", "show_input", "Ctrl+Alt+I")

    def get_save_idea_hotkey(self) -> str:
        """
        获取保存想法的快捷键。

        Returns:
            快捷键字符串
        """
        return self.get("hotkeys", "save_idea", "Ctrl+Enter")

    def get_theme(self) -> str:
        """
        获取主题。

        Returns:
            主题名称
        """
        return self.get("general", "theme", "light")

    def is_first_run(self) -> bool:
        """
        检查是否首次运行。

        Returns:
            是否首次运行
        """
        return self.get("general", "first_run", True)

    def set_first_run_completed(self) -> None:
        """设置首次运行已完成。"""
        self.set("general", "first_run", False)
