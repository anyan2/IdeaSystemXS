"""
测试脚本 - 全局快捷键功能测试
"""
import sys
import time
from PyQt6.QtWidgets import QApplication

from src.core.app_manager import AppManager
from src.system_integration.hotkey_manager import HotkeyManager

def test_global_hotkey():
    """测试全局快捷键功能"""
    print("开始测试全局快捷键功能...")
    
    # 创建应用程序实例
    app = QApplication(sys.argv)
    
    # 创建应用管理器实例
    app_manager = AppManager()
    
    # 创建快捷键管理器实例
    hotkey_manager = HotkeyManager()
    
    # 注册测试回调函数
    def hotkey_callback():
        print("快捷键被触发!")
    
    # 注册测试快捷键
    print("注册测试快捷键 Ctrl+Alt+T...")
    hotkey_manager.register_hotkey("ctrl+alt+t", hotkey_callback)
    
    print("请在5秒内按下 Ctrl+Alt+T 组合键...")
    
    # 等待5秒
    for i in range(5, 0, -1):
        print(f"{i}...")
        time.sleep(1)
    
    # 注销测试快捷键
    print("注销测试快捷键...")
    hotkey_manager.unregister_hotkey("ctrl+alt+t")
    
    print("全局快捷键功能测试完成")

if __name__ == "__main__":
    test_global_hotkey()
