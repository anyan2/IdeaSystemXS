"""
向量嵌入生成模块，用于生成文本的向量嵌入。
"""
from typing import List, Optional, Union

import numpy as np

from ..ai.ai_service import AIService
from ..core.config_manager import ConfigManager
from ..core.event_system import EventSystem


class EmbeddingGenerator:
    """向量嵌入生成器类，用于生成文本的向量嵌入。"""

    def __init__(
        self,
        config_manager: Optional[ConfigManager] = None,
        event_system: Optional[EventSystem] = None,
        ai_service: Optional[AIService] = None,
    ):
        """
        初始化向量嵌入生成器。

        Args:
            config_manager: 配置管理器实例
            event_system: 事件系统实例
            ai_service: AI服务实例
        """
        self._config_manager = config_manager or ConfigManager()
        self._event_system = event_system or EventSystem()
        self._ai_service = ai_service or AIService(self._config_manager, self._event_system)
        
        # 注册事件处理器
        self._register_event_handlers()

    def _register_event_handlers(self):
        """注册事件处理器。"""
        # 生成嵌入向量事件
        self._event_system.subscribe("generate_embedding", self._handle_generate_embedding)

    def _handle_generate_embedding(self, data):
        """
        处理生成嵌入向量事件。

        Args:
            data: 事件数据，包含text和callback字段
        """
        # 获取文本
        text = data.get("text", "")
        
        # 获取回调函数
        callback = data.get("callback", None)
        
        # 生成嵌入向量
        embedding = self.generate_embedding(text)
        
        # 如果有回调函数，调用回调函数
        if callback:
            callback(embedding)

    def generate_embedding(self, text: str) -> Optional[List[float]]:
        """
        生成文本的嵌入向量。

        Args:
            text: 文本

        Returns:
            嵌入向量，如果生成失败则返回None
        """
        # 如果文本为空，返回None
        if not text:
            return None
        
        # 使用AI服务生成嵌入向量
        embedding = self._ai_service.generate_embedding(text)
        
        # 如果AI服务不可用或生成失败，使用备用方法生成
        if embedding is None:
            embedding = self._generate_fallback_embedding(text)
        
        return embedding

    def _generate_fallback_embedding(self, text: str) -> List[float]:
        """
        生成备用嵌入向量，当AI服务不可用时使用。

        Args:
            text: 文本

        Returns:
            备用嵌入向量
        """
        # 简单的词袋模型
        # 注意：这只是一个非常简单的备用方法，不适合生产环境
        
        # 分词
        words = text.lower().split()
        
        # 创建词袋
        word_set = set(words)
        
        # 创建词频向量
        vector = [words.count(word) for word in word_set]
        
        # 归一化
        norm = np.linalg.norm(vector)
        if norm > 0:
            vector = [v / norm for v in vector]
        
        # 填充到固定维度
        embedding_dim = 1536  # OpenAI的text-embedding-ada-002模型维度
        if len(vector) < embedding_dim:
            vector.extend([0.0] * (embedding_dim - len(vector)))
        else:
            vector = vector[:embedding_dim]
        
        return vector

    def calculate_similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """
        计算两个嵌入向量的余弦相似度。

        Args:
            embedding1: 第一个嵌入向量
            embedding2: 第二个嵌入向量

        Returns:
            余弦相似度，范围为[-1, 1]
        """
        # 如果任一嵌入向量为None，返回0
        if embedding1 is None or embedding2 is None:
            return 0.0
        
        # 转换为numpy数组
        vec1 = np.array(embedding1)
        vec2 = np.array(embedding2)
        
        # 计算余弦相似度
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        # 避免除以0
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return dot_product / (norm1 * norm2)

    def batch_generate_embeddings(self, texts: List[str]) -> List[Optional[List[float]]]:
        """
        批量生成文本的嵌入向量。

        Args:
            texts: 文本列表

        Returns:
            嵌入向量列表，对应于输入文本列表
        """
        # 如果文本列表为空，返回空列表
        if not texts:
            return []
        
        # 逐个生成嵌入向量
        embeddings = []
        for text in texts:
            embedding = self.generate_embedding(text)
            embeddings.append(embedding)
        
        return embeddings
