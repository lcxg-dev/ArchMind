from src.converter.base_converter import BaseConverter
from src.api_client.base_client import BaseAPIClient

class GeneralConverter(BaseConverter):
    """通用代码转换器实现"""
    
    def __init__(self, api_client: BaseAPIClient):
        """
        初始化通用转换器
        
        Args:
            api_client: API客户端实例
        """
        super().__init__(api_client)
    
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
            Exception: 转换失败时抛出
        """
        # 验证输入
        if not source_lang or not target_lang or not code:
            raise ValueError("源代码语言、目标代码语言和代码内容不能为空")
        
        try:
            # 使用API客户端进行代码转换
            converted_code = self.api_client.code_conversion(source_lang, target_lang, code)
            
            # 格式化转换后的代码
            formatted_code = self.format_code(target_lang, converted_code)
            
            return formatted_code
            
        except Exception as e:
            raise Exception(f"代码转换失败: {str(e)}")
    
    def validate(self, lang: str, code: str) -> bool:
        """
        验证代码是否有效（基本验证）
        
        Args:
            lang: 代码语言
            code: 代码
            
        Returns:
            代码是否有效的布尔值
        """
        # 基本验证：检查代码是否为空
        if not code or not code.strip():
            return False
        
        # 这里可以添加更复杂的验证逻辑，例如语法检查
        # 由于是通用转换器，暂时只做基本验证
        return True