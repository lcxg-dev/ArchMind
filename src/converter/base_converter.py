from abc import ABC, abstractmethod
from src.api_client.base_client import BaseAPIClient

class BaseConverter(ABC):
    """转换器基础抽象类"""
    
    def __init__(self, api_client: BaseAPIClient):
        """
        初始化转换器
        
        Args:
            api_client: API客户端实例
        """
        self.api_client = api_client
    
    @abstractmethod
    def convert(self, source_lang: str, target_lang: str, code: str) -> str:
        """
        转换代码
        
        Args:
            source_lang: 源代码语言
            target_lang: 目标代码语言
            code: 源代码
            
        Returns:
            转换后的代码
            
        Raises:
            ConversionError: 转换失败时抛出
        """
        pass
    
    @abstractmethod
    def validate(self, lang: str, code: str) -> bool:
        """
        验证代码是否有效
        
        Args:
            lang: 代码语言
            code: 代码
            
        Returns:
            代码是否有效的布尔值
        """
        pass
    
    def format_code(self, lang: str, code: str) -> str:
        """
        格式化代码
        
        Args:
            lang: 代码语言
            code: 代码
            
        Returns:
            格式化后的代码
        """
        # 清理字符串
        code = code.strip()
        
        # 处理Markdown代码块标记
        if code.startswith('```'):
            # 找到所有代码块标记的位置
            all_markers = []
            start = 0
            while True:
                marker_pos = code.find('```', start)
                if marker_pos == -1:
                    break
                all_markers.append(marker_pos)
                start = marker_pos + 3
            
            # 如果有偶数个标记，提取中间的内容
            if len(all_markers) >= 2:
                # 从第一个标记结束到第二个标记开始
                code = code[all_markers[0] + 3:all_markers[1]].strip()
                
                # 检查是否包含语言标记（如果有换行符的话）
                first_newline = code.find('\n')
                if first_newline != -1:
                    # 检查第一行是否只有语言名称
                    first_line = code[:first_newline].strip()
                    # 常见的语言名称列表（可以根据需要扩展）
                    common_languages = ['c', 'cpp', 'python', 'java', 'javascript', 'js', 'html', 'css', 'go', 'rust', 'ruby']
                    if first_line.lower() in common_languages:
                        # 移除语言标记行
                        code = code[first_newline:].strip()
            else:
                # 只有一个标记，直接移除
                code = code.replace('```', '').strip()
        
        # 最后再清理一次
        code = code.strip()
        
        return code