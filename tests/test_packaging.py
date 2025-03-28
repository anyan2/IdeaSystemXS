"""
测试脚本 - 打包和安装流程测试
"""
import os
import sys
import unittest
import subprocess
import tempfile
import shutil
import platform

class TestPackagingAndInstallation(unittest.TestCase):
    """打包和安装流程测试类"""
    
    def setUp(self):
        """测试前的准备工作"""
        # 获取项目根目录
        self.project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        
        # 创建临时目录
        self.temp_dir = tempfile.mkdtemp()
        
        # 确定操作系统
        self.is_windows = platform.system() == 'Windows'
    
    def tearDown(self):
        """测试后的清理工作"""
        # 删除临时目录
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_requirements_file(self):
        """测试依赖列表文件"""
        print("测试依赖列表文件...")
        
        # 检查requirements.txt文件是否存在
        requirements_path = os.path.join(self.project_root, 'requirements.txt')
        self.assertTrue(os.path.exists(requirements_path), "requirements.txt文件不存在")
        
        # 检查文件内容
        with open(requirements_path, 'r') as f:
            content = f.read()
        
        # 检查必要的依赖
        required_packages = [
            'PyQt6', 'SQLite3-adapter', 'chromadb', 
            'openai', 'numpy', 'keyboard', 'pyinstaller'
        ]
        
        for package in required_packages:
            self.assertIn(package, content, f"依赖列表中缺少{package}")
        
        print("依赖列表文件测试通过")
    
    def test_setup_scripts(self):
        """测试环境设置脚本"""
        print("测试环境设置脚本...")
        
        # 检查Linux脚本
        linux_script_path = os.path.join(self.project_root, 'setup-env.sh')
        self.assertTrue(os.path.exists(linux_script_path), "setup-env.sh脚本不存在")
        
        # 检查Windows脚本
        windows_script_path = os.path.join(self.project_root, 'setup-env.bat')
        self.assertTrue(os.path.exists(windows_script_path), "setup-env.bat脚本不存在")
        
        # 检查脚本权限（仅Linux）
        if not self.is_windows:
            self.assertTrue(os.access(linux_script_path, os.X_OK), "setup-env.sh脚本没有执行权限")
        
        print("环境设置脚本测试通过")
    
    def test_build_scripts(self):
        """测试打包脚本"""
        print("测试打包脚本...")
        
        # 检查Linux脚本
        linux_script_path = os.path.join(self.project_root, 'build-app.sh')
        self.assertTrue(os.path.exists(linux_script_path), "build-app.sh脚本不存在")
        
        # 检查Windows脚本
        windows_script_path = os.path.join(self.project_root, 'build-app.bat')
        self.assertTrue(os.path.exists(windows_script_path), "build-app.bat脚本不存在")
        
        # 检查脚本权限（仅Linux）
        if not self.is_windows:
            self.assertTrue(os.access(linux_script_path, os.X_OK), "build-app.sh脚本没有执行权限")
        
        print("打包脚本测试通过")
    
    def test_main_script(self):
        """测试主脚本"""
        print("测试主脚本...")
        
        # 检查main.py文件是否存在
        main_script_path = os.path.join(self.project_root, 'src', 'main.py')
        self.assertTrue(os.path.exists(main_script_path), "main.py文件不存在")
        
        # 检查文件内容
        with open(main_script_path, 'r') as f:
            content = f.read()
        
        # 检查必要的导入
        required_imports = [
            'import sys', 'from PyQt6', 'AppManager', 'ConfigManager'
        ]
        
        for imp in required_imports:
            self.assertIn(imp, content, f"main.py中缺少{imp}")
        
        print("主脚本测试通过")
    
    def test_database_handling(self):
        """测试数据库文件处理"""
        print("测试数据库文件处理...")
        
        # 检查打包脚本中的数据库处理
        with open(os.path.join(self.project_root, 'build-app.bat'), 'r') as f:
            windows_content = f.read()
        
        with open(os.path.join(self.project_root, 'build-app.sh'), 'r') as f:
            linux_content = f.read()
        
        # 检查是否创建数据目录
        self.assertIn('mkdir', linux_content.lower(), "Linux打包脚本中缺少创建数据目录的命令")
        self.assertIn('mkdir', windows_content.lower(), "Windows打包脚本中缺少创建数据目录的命令")
        
        # 检查是否包含数据目录
        self.assertIn('dist/ideaSystemXS/data', linux_content, "Linux打包脚本中缺少数据目录")
        self.assertIn('dist\\ideaSystemXS\\data', windows_content, "Windows打包脚本中缺少数据目录")
        
        print("数据库文件处理测试通过")

if __name__ == "__main__":
    unittest.main()
