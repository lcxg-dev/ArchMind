import os
from typing import Dict, Any
from openai import OpenAI
from src.api_client.base_client import BaseAPIClient
from config.prompt_config import PromptConfig

class DeepSeekAPIClient(BaseAPIClient):
    """DeepSeek API客户端实现"""
    
    def __init__(self, api_key: str, api_base: str, model: str):
        """
        初始化DeepSeek API客户端
        
        Args:
            api_key: DeepSeek API密钥
            api_base: DeepSeek API基础URL
            model: 使用的DeepSeek模型名称
        """
        self.client = OpenAI(
            api_key=api_key,
            base_url=api_base
        )
        self.model = model
    
    def generate_response(self, prompt: str) -> str:
        """
        生成API响应
        
        Args:
            prompt: 提示文本
            
        Returns:
            生成的响应文本
            
        Raises:
            Exception: API调用失败时抛出
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是一位专业的代码转换工程师。"},
                    {"role": "user", "content": prompt}
                ],
                stream=False,
                temperature=0.1,
                max_tokens=4096  # 增加token限制，确保能生成完整代码
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            raise Exception(f"API调用失败: {str(e)}")
    
    def code_conversion(self, source_lang: str, target_lang: str, code: str) -> str:
        """
        代码转换功能
        
        Args:
            source_lang: 源代码语言
            target_lang: 目标代码语言
            code: 源代码
            
        Returns:
            转换后的代码
            
        Raises:
            Exception: API调用失败时抛出
        """
        prompt = PromptConfig.BASE_PROMPT.format(
            source_lang=source_lang,
            target_lang=target_lang,
            code=code
        )
        
        return self.generate_response(prompt)