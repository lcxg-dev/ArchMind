from abc import ABC, abstractmethod

class BaseAPIClient(ABC):
    """API客户端基础抽象类"""
    
    @abstractmethod
    def __init__(self, api_key: str, api_base: str, model: str):
        """
        初始化API客户端
        
        Args:
            api_key: API密钥
            api_base: API基础URL
            model: 使用的模型名称
        """
        pass
    
    @abstractmethod
    def generate_response(self, prompt: str) -> str:
        """
        生成API响应
        
        Args:
            prompt: 提示文本
            
        Returns:
            生成的响应文本
            
        Raises:
            APIError: API调用失败时抛出
        """
        pass
    
    @abstractmethod
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
            APIError: API调用失败时抛出
        """
        pass