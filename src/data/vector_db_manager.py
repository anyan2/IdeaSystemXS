"""
向量数据库管理器模块，负责管理ChromaDB向量数据库的连接和操作。
"""
import os
from typing import Any, Dict, List, Optional, Union

import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions

from ..core.config_manager import ConfigManager


class VectorDBManager:
    """向量数据库管理器类，负责管理ChromaDB向量数据库的连接和操作。"""

    _instance = None

    def __new__(cls, config_manager: Optional[ConfigManager] = None):
        """
        实现单例模式。

        Args:
            config_manager: 配置管理器实例

        Returns:
            VectorDBManager实例
        """
        if cls._instance is None:
            cls._instance = super(VectorDBManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, config_manager: Optional[ConfigManager] = None):
        """
        初始化向量数据库管理器。

        Args:
            config_manager: 配置管理器实例
        """
        if self._initialized:
            return

        self._config_manager = config_manager or ConfigManager()
        self._db_path = self._config_manager.get_vector_db_path()
        self._client = None
        self._embedding_function = None
        self._initialized = True

        # 确保数据库目录存在
        os.makedirs(self._db_path, exist_ok=True)

        # 初始化数据库
        self._init_database()

    def _init_database(self) -> None:
        """初始化向量数据库。"""
        # 创建客户端
        self._client = chromadb.PersistentClient(
            path=self._db_path,
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )

        # 设置嵌入函数
        self._set_embedding_function()

        # 确保集合存在
        self._ensure_collections_exist()

    def _set_embedding_function(self) -> None:
        """设置嵌入函数。"""
        # 检查是否启用AI功能
        if self._config_manager.is_ai_enabled() and not self._config_manager.is_offline_mode():
            # 使用OpenAI嵌入函数
            api_key = self._config_manager.get_api_key()
            if api_key:
                self._embedding_function = embedding_functions.OpenAIEmbeddingFunction(
                    api_key=api_key,
                    model_name=self._config_manager.get("ai", "embedding_model", "text-embedding-ada-002")
                )
            else:
                # 如果没有API密钥，使用默认嵌入函数
                self._embedding_function = embedding_functions.DefaultEmbeddingFunction()
        else:
            # 离线模式或AI功能未启用，使用默认嵌入函数
            self._embedding_function = embedding_functions.DefaultEmbeddingFunction()

    def _ensure_collections_exist(self) -> None:
        """确保集合存在。"""
        # 创建想法嵌入集合
        if "ideas_embeddings" not in self.get_collection_names():
            self._client.create_collection(
                name="ideas_embeddings",
                embedding_function=self._embedding_function,
                metadata={"description": "想法嵌入向量集合"}
            )

        # 创建关键词嵌入集合
        if "keywords_embeddings" not in self.get_collection_names():
            self._client.create_collection(
                name="keywords_embeddings",
                embedding_function=self._embedding_function,
                metadata={"description": "关键词嵌入向量集合"}
            )

    def get_client(self) -> chromadb.PersistentClient:
        """
        获取ChromaDB客户端。

        Returns:
            ChromaDB客户端
        """
        if self._client is None:
            self._init_database()
        return self._client

    def get_collection(self, collection_name: str) -> chromadb.Collection:
        """
        获取集合。

        Args:
            collection_name: 集合名称

        Returns:
            集合对象
        """
        return self.get_client().get_collection(
            name=collection_name,
            embedding_function=self._embedding_function
        )

    def get_collection_names(self) -> List[str]:
        """
        获取所有集合名称。

        Returns:
            集合名称列表
        """
        return [collection.name for collection in self.get_client().list_collections()]

    def add_idea_embedding(
        self,
        idea_id: int,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        添加想法嵌入向量。

        Args:
            idea_id: 想法ID
            content: 想法内容
            metadata: 元数据
        """
        collection = self.get_collection("ideas_embeddings")
        
        # 准备元数据
        if metadata is None:
            metadata = {}
        
        metadata["idea_id"] = idea_id
        
        # 添加嵌入向量
        collection.add(
            ids=[str(idea_id)],
            documents=[content],
            metadatas=[metadata]
        )

    def update_idea_embedding(
        self,
        idea_id: int,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        更新想法嵌入向量。

        Args:
            idea_id: 想法ID
            content: 想法内容
            metadata: 元数据
        """
        collection = self.get_collection("ideas_embeddings")
        
        # 准备元数据
        if metadata is None:
            metadata = {}
        
        metadata["idea_id"] = idea_id
        
        # 更新嵌入向量
        collection.update(
            ids=[str(idea_id)],
            documents=[content],
            metadatas=[metadata]
        )

    def delete_idea_embedding(self, idea_id: int) -> None:
        """
        删除想法嵌入向量。

        Args:
            idea_id: 想法ID
        """
        collection = self.get_collection("ideas_embeddings")
        collection.delete(ids=[str(idea_id)])

    def add_keyword_embedding(
        self,
        keyword: str,
        idea_ids: List[int],
        weight: float = 1.0
    ) -> None:
        """
        添加关键词嵌入向量。

        Args:
            keyword: 关键词
            idea_ids: 包含该关键词的想法ID列表
            weight: 权重
        """
        collection = self.get_collection("keywords_embeddings")
        
        # 准备元数据
        metadata = {
            "keyword": keyword,
            "idea_ids": ",".join(map(str, idea_ids)),
            "weight": weight
        }
        
        # 添加嵌入向量
        collection.add(
            ids=[keyword],
            documents=[keyword],
            metadatas=[metadata]
        )

    def update_keyword_embedding(
        self,
        keyword: str,
        idea_ids: List[int],
        weight: float = 1.0
    ) -> None:
        """
        更新关键词嵌入向量。

        Args:
            keyword: 关键词
            idea_ids: 包含该关键词的想法ID列表
            weight: 权重
        """
        collection = self.get_collection("keywords_embeddings")
        
        # 准备元数据
        metadata = {
            "keyword": keyword,
            "idea_ids": ",".join(map(str, idea_ids)),
            "weight": weight
        }
        
        # 更新嵌入向量
        collection.update(
            ids=[keyword],
            documents=[keyword],
            metadatas=[metadata]
        )

    def delete_keyword_embedding(self, keyword: str) -> None:
        """
        删除关键词嵌入向量。

        Args:
            keyword: 关键词
        """
        collection = self.get_collection("keywords_embeddings")
        collection.delete(ids=[keyword])

    def search_similar_ideas(
        self,
        query: str,
        n_results: int = 5,
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        搜索相似想法。

        Args:
            query: 查询文本
            n_results: 返回结果数量
            filter_metadata: 元数据过滤条件

        Returns:
            相似想法列表
        """
        collection = self.get_collection("ideas_embeddings")
        
        # 执行搜索
        results = collection.query(
            query_texts=[query],
            n_results=n_results,
            where=filter_metadata
        )
        
        # 处理结果
        similar_ideas = []
        if results["ids"]:
            for i, idea_id in enumerate(results["ids"][0]):
                similar_ideas.append({
                    "idea_id": int(idea_id),
                    "metadata": results["metadatas"][0][i] if results["metadatas"] else {},
                    "distance": results["distances"][0][i] if results["distances"] else None,
                    "document": results["documents"][0][i] if results["documents"] else None
                })
        
        return similar_ideas

    def search_similar_keywords(
        self,
        query: str,
        n_results: int = 5
    ) -> List[Dict[str, Any]]:
        """
        搜索相似关键词。

        Args:
            query: 查询文本
            n_results: 返回结果数量

        Returns:
            相似关键词列表
        """
        collection = self.get_collection("keywords_embeddings")
        
        # 执行搜索
        results = collection.query(
            query_texts=[query],
            n_results=n_results
        )
        
        # 处理结果
        similar_keywords = []
        if results["ids"]:
            for i, keyword in enumerate(results["ids"][0]):
                metadata = results["metadatas"][0][i] if results["metadatas"] else {}
                idea_ids = []
                if metadata and "idea_ids" in metadata:
                    idea_ids = [int(id_str) for id_str in metadata["idea_ids"].split(",")]
                
                similar_keywords.append({
                    "keyword": keyword,
                    "idea_ids": idea_ids,
                    "weight": metadata.get("weight", 1.0) if metadata else 1.0,
                    "distance": results["distances"][0][i] if results["distances"] else None
                })
        
        return similar_keywords

    def get_idea_embedding(self, idea_id: int) -> Optional[Dict[str, Any]]:
        """
        获取想法嵌入向量。

        Args:
            idea_id: 想法ID

        Returns:
            想法嵌入向量信息
        """
        collection = self.get_collection("ideas_embeddings")
        
        # 获取嵌入向量
        result = collection.get(ids=[str(idea_id)])
        
        if result["ids"]:
            return {
                "idea_id": int(result["ids"][0]),
                "metadata": result["metadatas"][0] if result["metadatas"] else {},
                "document": result["documents"][0] if result["documents"] else None,
                "embedding": result["embeddings"][0] if result["embeddings"] else None
            }
        
        return None

    def get_keyword_embedding(self, keyword: str) -> Optional[Dict[str, Any]]:
        """
        获取关键词嵌入向量。

        Args:
            keyword: 关键词

        Returns:
            关键词嵌入向量信息
        """
        collection = self.get_collection("keywords_embeddings")
        
        # 获取嵌入向量
        result = collection.get(ids=[keyword])
        
        if result["ids"]:
            metadata = result["metadatas"][0] if result["metadatas"] else {}
            idea_ids = []
            if metadata and "idea_ids" in metadata:
                idea_ids = [int(id_str) for id_str in metadata["idea_ids"].split(",")]
            
            return {
                "keyword": result["ids"][0],
                "idea_ids": idea_ids,
                "weight": metadata.get("weight", 1.0) if metadata else 1.0,
                "document": result["documents"][0] if result["documents"] else None,
                "embedding": result["embeddings"][0] if result["embeddings"] else None
            }
        
        return None

    def reset_database(self) -> None:
        """重置向量数据库。"""
        self.get_client().reset()
        self._ensure_collections_exist()

    def get_db_path(self) -> str:
        """
        获取数据库路径。

        Returns:
            数据库路径
        """
        return self._db_path

    def get_db_size(self) -> int:
        """
        获取数据库大小。

        Returns:
            数据库大小（字节）
        """
        total_size = 0
        for dirpath, dirnames, filenames in os.walk(self._db_path):
            for filename in filenames:
                filepath = os.path.join(dirpath, filename)
                total_size += os.path.getsize(filepath)
        return total_size

    def update_embedding_function(self) -> None:
        """更新嵌入函数。"""
        self._set_embedding_function()
        
        # 更新集合的嵌入函数
        for collection_name in self.get_collection_names():
            collection = self.get_client().get_collection(
                name=collection_name,
                embedding_function=self._embedding_function
            )
