"""
测试脚本 - UI界面和交互测试
"""
import os
import sys
import unittest
from PyQt6.QtWidgets import QApplication
from PyQt6.QtTest import QTest
from PyQt6.QtCore import Qt

# 添加项目根目录到Python路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.ui.main_window import MainWindow
from src.ui.input_window import InputWindow
from src.ui.settings_window import SettingsWindow
from src.core.app_manager import AppManager
from src.core.config_manager import ConfigManager
from src.core.event_system import EventSystem

class TestUIInteraction(unittest.TestCase):
    """UI界面和交互测试类"""
    
    @classmethod
    def setUpClass(cls):
        """测试类初始化"""
        # 创建QApplication实例
        cls.app = QApplication(sys.argv)
        
        # 创建配置管理器
        cls.config_manager = ConfigManager()
        
        # 创建事件系统
        cls.event_system = EventSystem()
        
        # 创建应用管理器
        cls.app_manager = AppManager(cls.config_manager, cls.event_system)
    
    def setUp(self):
        """每个测试前的准备工作"""
        pass
    
    def tearDown(self):
        """每个测试后的清理工作"""
        pass
    
    def test_main_window(self):
        """测试主窗口"""
        print("测试主窗口...")
        
        # 创建主窗口
        main_window = MainWindow(self.app_manager, self.config_manager, self.event_system)
        
        # 检查窗口标题
        self.assertEqual(main_window.windowTitle(), "ideaSystemXS", "主窗口标题不正确")
        
        # 检查窗口是否可见
        main_window.show()
        self.assertTrue(main_window.isVisible(), "主窗口未显示")
        
        # 检查主要组件是否存在
        self.assertIsNotNone(main_window.central_widget, "中央部件不存在")
        
        # 关闭窗口
        main_window.close()
        print("主窗口测试完成")
    
    def test_input_window(self):
        """测试输入窗口"""
        print("测试输入窗口...")
        
        # 创建输入窗口
        input_window = InputWindow(self.app_manager, self.config_manager, self.event_system)
        
        # 检查窗口标题
        self.assertEqual(input_window.windowTitle(), "记录想法", "输入窗口标题不正确")
        
        # 检查窗口是否可见
        input_window.show()
        self.assertTrue(input_window.isVisible(), "输入窗口未显示")
        
        # 测试输入文本
        test_text = "这是一个测试想法"
        input_window.idea_text_edit.setPlainText(test_text)
        self.assertEqual(input_window.idea_text_edit.toPlainText(), test_text, "文本输入不正确")
        
        # 关闭窗口
        input_window.close()
        print("输入窗口测试完成")
    
    def test_settings_window(self):
        """测试设置窗口"""
        print("测试设置窗口...")
        
        # 创建设置窗口
        settings_window = SettingsWindow(self.app_manager, self.config_manager, self.event_system)
        
        # 检查窗口标题
        self.assertEqual(settings_window.windowTitle(), "设置", "设置窗口标题不正确")
        
        # 检查窗口是否可见
        settings_window.show()
        self.assertTrue(settings_window.isVisible(), "设置窗口未显示")
        
        # 检查主要组件是否存在
        self.assertIsNotNone(settings_window.tab_widget, "标签部件不存在")
        
        # 关闭窗口
        settings_window.close()
        print("设置窗口测试完成")
    
    def test_theme_switching(self):
        """测试主题切换"""
        print("测试主题切换...")
        
        # 创建主窗口
        main_window = MainWindow(self.app_manager, self.config_manager, self.event_system)
        main_window.show()
        
        # 获取当前主题
        current_theme = self.config_manager.get('ui', 'theme', 'light')
        
        # 切换主题
        new_theme = 'dark' if current_theme == 'light' else 'light'
        self.event_system.publish('theme_changed', {'theme': new_theme})
        
        # 检查主题是否已切换
        self.assertEqual(self.config_manager.get('ui', 'theme'), new_theme, "主题未切换")
        
        # 关闭窗口
        main_window.close()
        print("主题切换测试完成")

if __name__ == "__main__":
    unittest.main()
