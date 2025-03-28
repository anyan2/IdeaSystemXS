"""
测试脚本 - 数据库操作测试
"""
import os
import sys
import tempfile
import unittest

# 添加项目根目录到Python路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.data.database_manager import DatabaseManager
from src.data.vector_db_manager import VectorDBManager
from src.core.config_manager import ConfigManager
from src.core.event_system import EventSystem

class TestDatabaseOperations(unittest.TestCase):
    """数据库操作测试类"""
    
    def setUp(self):
        """测试前的准备工作"""
        # 创建临时数据库文件
        self.temp_db_file = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
        self.temp_db_file.close()
        
        # 创建临时向量数据库目录
        self.temp_vector_db_dir = tempfile.mkdtemp()
        
        # 创建配置管理器
        self.config_manager = ConfigManager()
        self.config_manager.set('database', 'path', self.temp_db_file.name)
        self.config_manager.set('vector_database', 'path', self.temp_vector_db_dir)
        
        # 创建事件系统
        self.event_system = EventSystem()
        
        # 创建数据库管理器
        self.db_manager = DatabaseManager(self.config_manager, self.event_system)
        
        # 创建向量数据库管理器
        self.vector_db_manager = VectorDBManager(self.config_manager, self.event_system)
        
        # 初始化数据库
        self.db_manager.initialize_database()
    
    def tearDown(self):
        """测试后的清理工作"""
        # 关闭数据库连接
        self.db_manager.close()
        
        # 删除临时数据库文件
        if os.path.exists(self.temp_db_file.name):
            os.unlink(self.temp_db_file.name)
        
        # 删除临时向量数据库目录
        if os.path.exists(self.temp_vector_db_dir):
            import shutil
            shutil.rmtree(self.temp_vector_db_dir)
    
    def test_idea_crud(self):
        """测试想法的增删改查操作"""
        print("测试想法的增删改查操作...")
        
        # 添加想法
        idea_id = self.db_manager.add_idea("测试想法", "这是一个测试想法的内容")
        self.assertIsNotNone(idea_id, "添加想法失败")
        print(f"添加想法成功，ID: {idea_id}")
        
        # 获取想法
        idea = self.db_manager.get_idea(idea_id)
        self.assertIsNotNone(idea, "获取想法失败")
        self.assertEqual(idea['title'], "测试想法", "想法标题不匹配")
        self.assertEqual(idea['content'], "这是一个测试想法的内容", "想法内容不匹配")
        print("获取想法成功")
        
        # 更新想法
        success = self.db_manager.update_idea(idea_id, title="更新后的标题", content="更新后的内容")
        self.assertTrue(success, "更新想法失败")
        
        # 获取更新后的想法
        updated_idea = self.db_manager.get_idea(idea_id)
        self.assertEqual(updated_idea['title'], "更新后的标题", "更新后的标题不匹配")
        self.assertEqual(updated_idea['content'], "更新后的内容", "更新后的内容不匹配")
        print("更新想法成功")
        
        # 删除想法
        success = self.db_manager.delete_idea(idea_id)
        self.assertTrue(success, "删除想法失败")
        
        # 确认想法已删除
        deleted_idea = self.db_manager.get_idea(idea_id)
        self.assertIsNone(deleted_idea, "想法未被删除")
        print("删除想法成功")
    
    def test_tag_operations(self):
        """测试标签操作"""
        print("测试标签操作...")
        
        # 添加标签
        tag_id = self.db_manager.add_tag("测试标签")
        self.assertIsNotNone(tag_id, "添加标签失败")
        print(f"添加标签成功，ID: {tag_id}")
        
        # 获取标签
        tag = self.db_manager.get_tag(tag_id)
        self.assertIsNotNone(tag, "获取标签失败")
        self.assertEqual(tag['name'], "测试标签", "标签名称不匹配")
        print("获取标签成功")
        
        # 添加想法
        idea_id = self.db_manager.add_idea("测试想法", "这是一个测试想法的内容")
        
        # 关联标签和想法
        success = self.db_manager.add_idea_tag(idea_id, tag_id)
        self.assertTrue(success, "关联标签和想法失败")
        print("关联标签和想法成功")
        
        # 获取想法的标签
        tags = self.db_manager.get_idea_tags(idea_id)
        self.assertEqual(len(tags), 1, "获取想法的标签数量不匹配")
        self.assertEqual(tags[0]['name'], "测试标签", "获取的标签名称不匹配")
        print("获取想法的标签成功")
        
        # 获取标签的想法
        ideas = self.db_manager.get_ideas_by_tag(tag_id)
        self.assertEqual(len(ideas), 1, "获取标签的想法数量不匹配")
        self.assertEqual(ideas[0]['title'], "测试想法", "获取的想法标题不匹配")
        print("获取标签的想法成功")
        
        # 删除标签和想法的关联
        success = self.db_manager.remove_idea_tag(idea_id, tag_id)
        self.assertTrue(success, "删除标签和想法的关联失败")
        
        # 确认关联已删除
        tags = self.db_manager.get_idea_tags(idea_id)
        self.assertEqual(len(tags), 0, "标签和想法的关联未被删除")
        print("删除标签和想法的关联成功")
    
    def test_vector_db(self):
        """测试向量数据库操作"""
        print("测试向量数据库操作...")
        
        # 添加文档
        doc_id = "test_doc_1"
        content = "这是一个测试文档的内容"
        metadata = {"title": "测试文档", "source": "测试"}
        embedding = [0.1, 0.2, 0.3, 0.4, 0.5]  # 简化的嵌入向量
        
        success = self.vector_db_manager.add_document(doc_id, content, metadata, embedding)
        self.assertTrue(success, "添加文档失败")
        print("添加文档成功")
        
        # 获取文档
        doc = self.vector_db_manager.get_document(doc_id)
        self.assertIsNotNone(doc, "获取文档失败")
        self.assertEqual(doc['document'], content, "文档内容不匹配")
        print("获取文档成功")
        
        # 搜索相似文档
        results = self.vector_db_manager.search_similar(embedding, limit=5)
        self.assertGreater(len(results), 0, "搜索相似文档失败")
        self.assertEqual(results[0]['id'], doc_id, "搜索结果不匹配")
        print("搜索相似文档成功")
        
        # 删除文档
        success = self.vector_db_manager.delete_document(doc_id)
        self.assertTrue(success, "删除文档失败")
        
        # 确认文档已删除
        doc = self.vector_db_manager.get_document(doc_id)
        self.assertIsNone(doc, "文档未被删除")
        print("删除文档成功")

if __name__ == "__main__":
    unittest.main()
