"""
AI服务模块，提供AI相关功能。
"""
import json
import os
import time
from typing import Any, Dict, List, Optional, Tuple, Union

import requests
from requests.exceptions import RequestException

from src.core.config_manager import ConfigManager
from src.core.event_system import EventSystem


class AIService:
    """AI服务类，提供AI API调用功能。"""

    def __init__(
        self,
        config_manager: Optional[ConfigManager] = None,
        event_system: Optional[EventSystem] = None,
    ):
        """
        初始化AI服务。

        Args:
            config_manager: 配置管理器实例
            event_system: 事件系统实例
        """
        self._config_manager = config_manager or ConfigManager()
        self._event_system = event_system or EventSystem()
        
        # 注册事件处理器
        self._register_event_handlers()

    def _register_event_handlers(self):
        """注册事件处理器。"""
        # 测试AI API连接事件
        self._event_system.subscribe("test_ai_api", self._handle_test_api)

    def _handle_test_api(self, data=None):
        """
        处理测试AI API连接事件。

        Args:
            data: 事件数据
        """
        # 测试API连接
        success, message = self.test_api_connection()
        
        # 发布测试结果事件
        self._event_system.publish("test_ai_api_result", {
            "success": success,
            "message": message
        })

    def is_available(self) -> bool:
        """
        检查AI服务是否可用。

        Returns:
            是否可用
        """
        # 如果AI功能未启用或处于离线模式，返回False
        if not self._config_manager.is_ai_enabled() or self._config_manager.is_offline_mode():
            return False
        
        # 检查API URL和API密钥是否已配置
        api_url = self._config_manager.get("ai", "api_url", "")
        api_key = self._config_manager.get("ai", "api_key", "")
        
        return bool(api_url and api_key)

    def test_api_connection(self) -> Tuple[bool, str]:
        """
        测试API连接。

        Returns:
            (成功标志, 消息)
        """
        # 如果AI功能未启用或处于离线模式，返回False
        if not self._config_manager.is_ai_enabled():
            return False, "AI功能未启用"
        
        if self._config_manager.is_offline_mode():
            return False, "系统处于离线模式"
        
        # 检查API URL和API密钥是否已配置
        api_url = self._config_manager.get("ai", "api_url", "")
        api_key = self._config_manager.get("ai", "api_key", "")
        
        if not api_url:
            return False, "API URL未配置"
        
        if not api_key:
            return False, "API密钥未配置"
        
        # 构建请求URL
        url = f"{api_url.rstrip('/')}/chat/completions"
        
        # 构建请求头
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        
        # 构建请求数据
        data = {
            "model": self._config_manager.get("ai", "model", "gpt-3.5-turbo"),
            "messages": [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Hello, this is a test message. Please respond with 'Test successful'."}
            ],
            "max_tokens": 50
        }
        
        try:
            # 发送请求
            response = requests.post(url, headers=headers, json=data, timeout=10)
            
            # 检查响应状态码
            if response.status_code == 200:
                # 解析响应数据
                response_data = response.json()
                
                # 检查响应内容
                if "choices" in response_data and len(response_data["choices"]) > 0:
                    content = response_data["choices"][0].get("message", {}).get("content", "")
                    if "test successful" in content.lower():
                        return True, "API连接测试成功"
                    else:
                        return False, f"API响应内容异常: {content}"
                else:
                    return False, f"API响应格式异常: {response_data}"
            else:
                return False, f"API请求失败，状态码: {response.status_code}, 响应: {response.text}"
        except RequestException as e:
            return False, f"API请求异常: {str(e)}"
        except Exception as e:
            return False, f"未知错误: {str(e)}"

    def generate_embedding(self, text: str) -> Optional[List[float]]:
        """
        生成文本嵌入向量。

        Args:
            text: 文本

        Returns:
            嵌入向量，如果生成失败则返回None
        """
        # 如果AI服务不可用，返回None
        if not self.is_available():
            return None
        
        # 构建请求URL
        api_url = self._config_manager.get("ai", "api_url", "")
        url = f"{api_url.rstrip('/')}/embeddings"
        
        # 构建请求头
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self._config_manager.get('ai', 'api_key', '')}"
        }
        
        # 构建请求数据
        data = {
            "model": "text-embedding-ada-002",
            "input": text
        }
        
        try:
            # 发送请求
            response = requests.post(url, headers=headers, json=data, timeout=10)
            
            # 检查响应状态码
            if response.status_code == 200:
                # 解析响应数据
                response_data = response.json()
                
                # 检查响应内容
                if "data" in response_data and len(response_data["data"]) > 0:
                    embedding = response_data["data"][0].get("embedding", None)
                    return embedding
            
            # 记录错误
            print(f"生成嵌入向量失败，状态码: {response.status_code}, 响应: {response.text}")
            return None
        except Exception as e:
            # 记录错误
            print(f"生成嵌入向量异常: {str(e)}")
            return None

    def analyze_idea(self, idea_text: str) -> Dict[str, Any]:
        """
        分析想法，提取标签、主题和摘要。

        Args:
            idea_text: 想法文本

        Returns:
            分析结果，包含标签、主题和摘要
        """
        # 如果AI服务不可用，返回空结果
        if not self.is_available():
            return {
                "tags": [],
                "title": "",
                "summary": ""
            }
        
        # 构建请求URL
        api_url = self._config_manager.get("ai", "api_url", "")
        url = f"{api_url.rstrip('/')}/chat/completions"
        
        # 构建请求头
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self._config_manager.get('ai', 'api_key', '')}"
        }
        
        # 构建提示
        prompt = f"""
        请分析以下想法文本，提取关键信息：

        {idea_text}

        请提供以下信息：
        1. 标签：提取3-5个关键词作为标签，每个标签不超过10个字符
        2. 标题：生成一个简短的标题，不超过20个字符
        3. 摘要：生成一个简短的摘要，不超过100个字符

        请以JSON格式返回结果，格式如下：
        {{
            "tags": ["标签1", "标签2", "标签3"],
            "title": "标题",
            "summary": "摘要"
        }}
        """
        
        # 构建请求数据
        data = {
            "model": self._config_manager.get("ai", "model", "gpt-3.5-turbo"),
            "messages": [
                {"role": "system", "content": "你是一个专业的文本分析助手，擅长提取文本的关键信息。"},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.3,
            "max_tokens": 500
        }
        
        try:
            # 发送请求
            response = requests.post(url, headers=headers, json=data, timeout=30)
            
            # 检查响应状态码
            if response.status_code == 200:
                # 解析响应数据
                response_data = response.json()
                
                # 检查响应内容
                if "choices" in response_data and len(response_data["choices"]) > 0:
                    content = response_data["choices"][0].get("message", {}).get("content", "")
                    
                    # 提取JSON部分
                    try:
                        # 尝试直接解析
                        result = json.loads(content)
                    except json.JSONDecodeError:
                        # 如果直接解析失败，尝试提取JSON部分
                        import re
                        json_match = re.search(r'({[\s\S]*})', content)
                        if json_match:
                            try:
                                result = json.loads(json_match.group(1))
                            except json.JSONDecodeError:
                                # 如果仍然失败，返回默认结果
                                return {
                                    "tags": [],
                                    "title": "",
                                    "summary": ""
                                }
                        else:
                            # 如果没有找到JSON部分，返回默认结果
                            return {
                                "tags": [],
                                "title": "",
                                "summary": ""
                            }
                    
                    # 验证结果格式
                    if not isinstance(result, dict):
                        return {
                            "tags": [],
                            "title": "",
                            "summary": ""
                        }
                    
                    # 提取结果
                    tags = result.get("tags", [])
                    title = result.get("title", "")
                    summary = result.get("summary", "")
                    
                    # 验证结果类型
                    if not isinstance(tags, list):
                        tags = []
                    
                    if not isinstance(title, str):
                        title = ""
                    
                    if not isinstance(summary, str):
                        summary = ""
                    
                    return {
                        "tags": tags,
                        "title": title,
                        "summary": summary
                    }
            
            # 记录错误
            print(f"分析想法失败，状态码: {response.status_code}, 响应: {response.text}")
            return {
                "tags": [],
                "title": "",
                "summary": ""
            }
        except Exception as e:
            # 记录错误
            print(f"分析想法异常: {str(e)}")
            return {
                "tags": [],
                "title": "",
                "summary": ""
            }

    def find_related_ideas(self, idea_text: str, idea_id: Optional[int] = None, limit: int = 5) -> List[Dict[str, Any]]:
        """
        查找与给定想法相关的其他想法。

        Args:
            idea_text: 想法文本
            idea_id: 想法ID，用于排除自身
            limit: 返回结果数量限制

        Returns:
            相关想法列表
        """
        # 如果AI服务不可用，返回空列表
        if not self.is_available():
            return []
        
        # 生成嵌入向量
        embedding = self.generate_embedding(idea_text)
        if not embedding:
            return []
        
        # 发布查询向量数据库事件
        self._event_system.publish("query_vector_db", {
            "embedding": embedding,
            "exclude_id": idea_id,
            "limit": limit,
            "callback": lambda results: self._event_system.publish("related_ideas_found", {
                "idea_id": idea_id,
                "results": results
            })
        })
        
        # 返回空列表，实际结果将通过事件异步返回
        return []

    def summarize_ideas(self, ideas: List[Dict[str, Any]]) -> str:
        """
        总结多个想法。

        Args:
            ideas: 想法列表，每个想法包含id、title、content等字段

        Returns:
            总结文本
        """
        # 如果AI服务不可用或想法列表为空，返回空字符串
        if not self.is_available() or not ideas:
            return ""
        
        # 构建请求URL
        api_url = self._config_manager.get("ai", "api_url", "")
        url = f"{api_url.rstrip('/')}/chat/completions"
        
        # 构建请求头
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self._config_manager.get('ai', 'api_key', '')}"
        }
        
        # 构建想法文本
        ideas_text = ""
        for i, idea in enumerate(ideas):
            ideas_text += f"想法{i+1}：{idea.get('title', '')}\n"
            ideas_text += f"{idea.get('content', '')}\n\n"
        
        # 构建提示
        prompt = f"""
        请总结以下想法，找出共同主题、关联点和可能的行动建议：

        {ideas_text}

        请提供：
        1. 共同主题：这些想法的共同点是什么？
        2. 关键见解：从这些想法中可以得出哪些重要见解？
        3. 行动建议：基于这些想法，有哪些可能的行动建议？

        请以连贯的段落形式回答，不要使用标题或编号。
        """
        
        # 构建请求数据
        data = {
            "model": self._config_manager.get("ai", "model", "gpt-3.5-turbo"),
            "messages": [
                {"role": "system", "content": "你是一个专业的思想分析师，擅长总结和关联不同的想法。"},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.5,
            "max_tokens": 1000
        }
        
        try:
            # 发送请求
            response = requests.post(url, headers=headers, json=data, timeout=30)
            
            # 检查响应状态码
            if response.status_code == 200:
                # 解析响应数据
                response_data = response.json()
                
                # 检查响应内容
                if "choices" in response_data and len(response_data["choices"]) > 0:
                    content = response_data["choices"][0].get("message", {}).get("content", "")
                    return content.strip()
            
            # 记录错误
            print(f"总结想法失败，状态码: {response.status_code}, 响应: {response.text}")
            return ""
        except Exception as e:
            # 记录错误
            print(f"总结想法异常: {str(e)}")
            return ""

    def generate_reminder(self, idea_text: str) -> Dict[str, Any]:
        """
        为想法生成提醒建议。

        Args:
            idea_text: 想法文本

        Returns:
            提醒建议，包含是否需要提醒、提醒时间和提醒原因
        """
        # 如果AI服务不可用，返回默认结果
        if not self.is_available():
            return {
                "should_remind": False,
                "remind_time": None,
                "remind_reason": ""
            }
        
        # 构建请求URL
        api_url = self._config_manager.get("ai", "api_url", "")
        url = f"{api_url.rstrip('/')}/chat/completions"
        
        # 构建请求头
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self._config_manager.get('ai', 'api_key', '')}"
        }
        
        # 获取当前时间
        current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        
        # 构建提示
        prompt = f"""
        请分析以下想法文本，判断是否需要设置提醒：

        {idea_text}

        当前时间：{current_time}

        请判断这个想法是否包含需要在未来某个时间点提醒用户的内容。如果需要提醒，请指定提醒时间和原因。

        请以JSON格式返回结果，格式如下：
        {{
            "should_remind": true或false,
            "remind_time": "YYYY-MM-DD HH:MM:SS"（如果should_remind为true，则提供提醒时间，否则为null）,
            "remind_reason": "提醒原因"（如果should_remind为true，则提供提醒原因，否则为空字符串）
        }}
        """
        
        # 构建请求数据
        data = {
            "model": self._config_manager.get("ai", "model", "gpt-3.5-turbo"),
            "messages": [
                {"role": "system", "content": "你是一个专业的个人助理，擅长分析文本并设置合适的提醒。"},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.3,
            "max_tokens": 500
        }
        
        try:
            # 发送请求
            response = requests.post(url, headers=headers, json=data, timeout=30)
            
            # 检查响应状态码
            if response.status_code == 200:
                # 解析响应数据
                response_data = response.json()
                
                # 检查响应内容
                if "choices" in response_data and len(response_data["choices"]) > 0:
                    content = response_data["choices"][0].get("message", {}).get("content", "")
                    
                    # 提取JSON部分
                    try:
                        # 尝试直接解析
                        result = json.loads(content)
                    except json.JSONDecodeError:
                        # 如果直接解析失败，尝试提取JSON部分
                        import re
                        json_match = re.search(r'({[\s\S]*})', content)
                        if json_match:
                            try:
                                result = json.loads(json_match.group(1))
                            except json.JSONDecodeError:
                                # 如果仍然失败，返回默认结果
                                return {
                                    "should_remind": False,
                                    "remind_time": None,
                                    "remind_reason": ""
                                }
                        else:
                            # 如果没有找到JSON部分，返回默认结果
                            return {
                                "should_remind": False,
                                "remind_time": None,
                                "remind_reason": ""
                            }
                    
                    # 验证结果格式
                    if not isinstance(result, dict):
                        return {
                            "should_remind": False,
                            "remind_time": None,
                            "remind_reason": ""
                        }
                    
                    # 提取结果
                    should_remind = result.get("should_remind", False)
                    remind_time = result.get("remind_time", None)
                    remind_reason = result.get("remind_reason", "")
                    
                    # 验证结果类型
                    if not isinstance(should_remind, bool):
                        should_remind = False
                    
                    if not isinstance(remind_time, str) and remind_time is not None:
                        remind_time = None
                    
                    if not isinstance(remind_reason, str):
                        remind_reason = ""
                    
                    return {
                        "should_remind": should_remind,
                        "remind_time": remind_time,
                        "remind_reason": remind_reason
                    }
            
            # 记录错误
            print(f"生成提醒建议失败，状态码: {response.status_code}, 响应: {response.text}")
            return {
                "should_remind": False,
                "remind_time": None,
                "remind_reason": ""
            }
        except Exception as e:
            # 记录错误
            print(f"生成提醒建议异常: {str(e)}")
            return {
                "should_remind": False,
                "remind_time": None,
                "remind_reason": ""
            }

    def ask_ai(self, query: str, context: Optional[List[Dict[str, Any]]] = None) -> str:
        """
        向AI提问。

        Args:
            query: 问题
            context: 上下文，包含相关想法的列表

        Returns:
            AI回答
        """
        # 如果AI服务不可用，返回错误消息
        if not self.is_available():
            return "AI服务不可用，请检查设置。"
        
        # 构建请求URL
        api_url = self._config_manager.get("ai", "api_url", "")
        url = f"{api_url.rstrip('/')}/chat/completions"
        
        # 构建请求头
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self._config_manager.get('ai', 'api_key', '')}"
        }
        
        # 构建上下文文本
        context_text = ""
        if context:
            context_text = "以下是一些相关的想法，可能对回答有帮助：\n\n"
            for i, idea in enumerate(context):
                context_text += f"想法{i+1}：{idea.get('title', '')}\n"
                context_text += f"{idea.get('content', '')}\n\n"
        
        # 构建提示
        prompt = f"""
        {context_text}
        
        用户问题：{query}
        
        请根据上述信息回答用户的问题。如果无法根据提供的信息回答，请诚实地说明。
        """
        
        # 构建请求数据
        data = {
            "model": self._config_manager.get("ai", "model", "gpt-3.5-turbo"),
            "messages": [
                {"role": "system", "content": "你是一个智能助手，可以帮助用户回答关于他们想法的问题。"},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 1000
        }
        
        try:
            # 发送请求
            response = requests.post(url, headers=headers, json=data, timeout=30)
            
            # 检查响应状态码
            if response.status_code == 200:
                # 解析响应数据
                response_data = response.json()
                
                # 检查响应内容
                if "choices" in response_data and len(response_data["choices"]) > 0:
                    content = response_data["choices"][0].get("message", {}).get("content", "")
                    return content.strip()
            
            # 记录错误
            print(f"AI问答失败，状态码: {response.status_code}, 响应: {response.text}")
            return "AI服务请求失败，请稍后再试。"
        except Exception as e:
            # 记录错误
            print(f"AI问答异常: {str(e)}")
            return f"AI服务异常: {str(e)}"
