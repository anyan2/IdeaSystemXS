"""
ideaSystemXS 知识库系统 - 主程序入口
"""

import sys
import os
import logging
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt, QCoreApplication



# 添加项目根目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

# 导入核心模块
from core.app_manager import AppManager
from core.config_manager import ConfigManager
from core.event_system import EventSystem

# 设置日志
def setup_logging():
    """设置日志系统"""
    log_dir = os.path.join(os.path.expanduser("~"), "ideaSystemXS", "logs")
    os.makedirs(log_dir, exist_ok=True)
    
    log_file = os.path.join(log_dir, "app.log")
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    
    return logging.getLogger("ideaSystemXS")

def main():
    """主程序入口"""
    # 设置日志
    logger = setup_logging()
    logger.info("启动 ideaSystemXS...")
    
    # 设置高DPI支持
    QCoreApplication.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling, True)
    QCoreApplication.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps, True)
    
    # 创建应用程序实例
    app = QApplication(sys.argv)
    app.setApplicationName("ideaSystemXS")
    app.setApplicationVersion("1.0.0")
    
    # 创建事件系统
    logger.info("初始化事件系统...")
    event_system = EventSystem()
    
    # 创建配置管理器
    logger.info("初始化配置管理器...")
    config_manager = ConfigManager()
    
    # 创建应用管理器
    logger.info("初始化应用管理器...")
    app_manager = AppManager(config_manager, event_system)
    
    # 初始化应用
    logger.info("初始化应用...")
    app_manager.initialize()
    
    # 启动应用
    logger.info("启动应用...")
    app_manager.start()
    
    # 运行应用程序主循环
    exit_code = app.exec()
    
    # 清理资源
    logger.info("应用退出，清理资源...")
    app_manager.cleanup()
    
    logger.info(f"应用退出，退出码: {exit_code}")
    return exit_code

if __name__ == "__main__":
    sys.exit(main())
