"""
测试脚本 - AI功能测试
"""
import os
import sys
import unittest
import tempfile

# 添加项目根目录到Python路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.ai.ai_service import AIService
from src.ai.embedding_generator import EmbeddingGenerator
from src.ai.idea_analyzer import IdeaAnalyzer
from src.ai.ideas_summarizer import IdeasSummarizer
from src.ai.reminder_system import ReminderSystem
from src.ai.ai_query_console import AIQueryConsole
from src.core.config_manager import ConfigManager
from src.core.event_system import EventSystem
from src.business.idea_manager import IdeaManager
from src.data.database_manager import DatabaseManager

class TestAIFeatures(unittest.TestCase):
    """AI功能测试类"""
    
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
        
        # 设置AI服务配置（使用离线模式进行测试）
        self.config_manager.set('ai', 'api_key', 'test_key')
        self.config_manager.set('ai', 'api_url', 'https://api.example.com')
        self.config_manager.set('ai', 'offline_mode', 'true')
        
        # 创建事件系统
        self.event_system = EventSystem()
        
        # 创建数据库管理器
        self.db_manager = DatabaseManager(self.config_manager, self.event_system)
        
        # 初始化数据库
        self.db_manager.initialize_database()
        
        # 创建想法管理器
        self.idea_manager = IdeaManager(self.config_manager, self.event_system)
        
        # 创建AI服务
        self.ai_service = AIService(self.config_manager, self.event_system)
        
        # 创建嵌入生成器
        self.embedding_generator = EmbeddingGenerator(self.config_manager, self.event_system, self.ai_service)
        
        # 创建想法分析器
        self.idea_analyzer = IdeaAnalyzer(self.config_manager, self.event_system, self.ai_service, self.embedding_generator, self.idea_manager)
        
        # 创建想法总结器
        self.ideas_summarizer = IdeasSummarizer(self.config_manager, self.event_system, self.ai_service, self.idea_manager)
        
        # 创建提醒系统
        self.reminder_system = ReminderSystem(self.config_manager, self.event_system, self.ai_service, self.idea_manager)
        
        # 创建AI查询控制台
        self.ai_query_console = AIQueryConsole(self.config_manager, self.event_system, self.ai_service, self.idea_manager)
    
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
    
    def test_embedding_generator(self):
        """测试嵌入生成器"""
        print("测试嵌入生成器...")
        
        # 生成嵌入向量
        text = "这是一个测试文本，用于生成嵌入向量"
        embedding = self.embedding_generator.generate_embedding(text)
        
        # 检查嵌入向量
        self.assertIsNotNone(embedding, "嵌入向量生成失败")
        self.assertIsInstance(embedding, list, "嵌入向量类型不正确")
        self.assertGreater(len(embedding), 0, "嵌入向量长度为0")
        print("嵌入向量生成成功")
        
        # 测试相似度计算
        text2 = "这是另一个测试文本，用于计算相似度"
        embedding2 = self.embedding_generator.generate_embedding(text2)
        
        similarity = self.embedding_generator.calculate_similarity(embedding, embedding2)
        self.assertIsInstance(similarity, float, "相似度类型不正确")
        self.assertGreaterEqual(similarity, -1.0, "相似度小于-1.0")
        self.assertLessEqual(similarity, 1.0, "相似度大于1.0")
        print("相似度计算成功")
    
    def test_idea_analyzer(self):
        """测试想法分析器"""
        print("测试想法分析器...")
        
        # 分析想法
        content = "这是一个关于人工智能的想法。我认为人工智能将在未来十年内彻底改变我们的生活方式。"
        analysis_result = self.idea_analyzer.analyze_idea(content)
        
        # 检查分析结果
        self.assertIsNotNone(analysis_result, "想法分析失败")
        self.assertIn('title', analysis_result, "分析结果中没有标题")
        self.assertIn('summary', analysis_result, "分析结果中没有摘要")
        self.assertIn('tags', analysis_result, "分析结果中没有标签")
        print("想法分析成功")
        
        # 添加想法到数据库
        idea_id = self.idea_manager.add_idea("人工智能想法", content)
        
        # 查找相关想法
        related_ideas = self.idea_analyzer.find_related_ideas(content, idea_id)
        self.assertIsInstance(related_ideas, list, "相关想法类型不正确")
        print("查找相关想法成功")
    
    def test_ideas_summarizer(self):
        """测试想法总结器"""
        print("测试想法总结器...")
        
        # 添加多个想法
        ideas = []
        for i in range(5):
            idea_id = self.idea_manager.add_idea(
                f"测试想法 {i+1}",
                f"这是第 {i+1} 个测试想法的内容。这个想法主要关于测试想法总结器功能。"
            )
            idea = self.idea_manager.get_idea(idea_id)
            ideas.append(idea)
        
        # 总结想法
        summary = self.ideas_summarizer.summarize_ideas(ideas)
        
        # 检查总结结果
        self.assertIsNotNone(summary, "想法总结失败")
        self.assertIsInstance(summary, str, "总结类型不正确")
        self.assertGreater(len(summary), 0, "总结长度为0")
        print("想法总结成功")
    
    def test_reminder_system(self):
        """测试提醒系统"""
        print("测试提醒系统...")
        
        # 添加想法
        idea_id = self.idea_manager.add_idea(
            "提醒测试想法",
            "这是一个需要在明天提醒我的想法。"
        )
        
        # 添加提醒
        import datetime
        remind_time = (datetime.datetime.now() + datetime.timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S")
        remind_reason = "测试提醒"
        
        success = self.reminder_system.add_reminder(idea_id, remind_time, remind_reason)
        self.assertTrue(success, "添加提醒失败")
        print("添加提醒成功")
        
        # 获取提醒
        reminders = self.reminder_system.get_reminders(idea_id)
        self.assertGreater(len(reminders), 0, "获取提醒失败")
        self.assertEqual(reminders[0]['idea_id'], idea_id, "提醒的想法ID不匹配")
        self.assertEqual(reminders[0]['remind_reason'], remind_reason, "提醒原因不匹配")
        print("获取提醒成功")
        
        # 删除提醒
        success = self.reminder_system.delete_reminder(reminders[0]['id'])
        self.assertTrue(success, "删除提醒失败")
        
        # 确认提醒已删除
        reminders = self.reminder_system.get_reminders(idea_id)
        self.assertEqual(len(reminders), 0, "提醒未被删除")
        print("删除提醒成功")
    
    def test_ai_query_console(self):
        """测试AI查询控制台"""
        print("测试AI查询控制台...")
        
        # 添加想法
        for i in range(3):
            self.idea_manager.add_idea(
                f"查询测试想法 {i+1}",
                f"这是第 {i+1} 个用于测试AI查询控制台的想法。"
            )
        
        # 查询AI
        query = "总结所有关于测试的想法"
        response = self.ai_query_console.query_ai(query)
        
        # 检查响应
        self.assertIsNotNone(response, "AI查询失败")
        self.assertIsInstance(response, str, "响应类型不正确")
        self.assertGreater(len(response), 0, "响应长度为0")
        print("AI查询成功")
        
        # 获取对话历史
        history = self.ai_query_console.get_conversation_history()
        self.assertGreater(len(history), 0, "获取对话历史失败")
        self.assertEqual(history[-2]['content'], query, "对话历史中的查询不匹配")
        self.assertEqual(history[-1]['content'], response, "对话历史中的响应不匹配")
        print("获取对话历史成功")
        
        # 清空对话历史
        self.ai_query_console.clear_conversation()
        history = self.ai_query_console.get_conversation_history()
        self.assertEqual(len(history), 0, "清空对话历史失败")
        print("清空对话历史成功")

if __name__ == "__main__":
    unittest.main()
