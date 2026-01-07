from src.converter.base_converter import BaseConverter
from src.api_client.base_client import BaseAPIClient
from config.prompt_config import PromptConfig

class PythonConverter(BaseConverter):
    """Python语言代码转换器实现"""
    
    def __init__(self, api_client: BaseAPIClient):
        """
        初始化Python语言转换器
        
        Args:
            api_client: API客户端实例
        """
        super().__init__(api_client)
    
    def convert(self, source_lang: str, target_lang: str, code: str) -> str:
        """
        转换Python语言代码
        
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
            # 针对Python语言转换的特定提示
            python_specific_prompt = """
            请确保：
            1. 完整转换所有函数、类和方法
            2. 正确处理缩进和Python特有的语法结构
            3. 转换列表推导式、生成器、装饰器等Python特性
            4. 处理模块导入和包结构
            5. 保持相同的功能和逻辑
            6. 生成可直接运行的Python代码
            7. 处理异常处理机制
            8. 保持Python的代码风格和最佳实践
            """
            
            # 构建完整提示
            full_prompt = PromptConfig.BASE_PROMPT.format(
                source_lang=source_lang,
                target_lang=target_lang,
                code=code
            ) + "\n" + python_specific_prompt
            
            # 使用API客户端进行代码转换
            converted_code = self.api_client.generate_response(full_prompt)
            
            # 格式化转换后的代码
            formatted_code = self.format_code(target_lang, converted_code)
            
            return formatted_code
            
        except Exception as e:
            raise Exception(f"Python语言代码转换失败: {str(e)}")
    
    def validate(self, lang: str, code: str) -> bool:
        """
        验证Python语言代码是否有效
        
        Args:
            lang: 代码语言
            code: 代码
            
        Returns:
            代码是否有效的布尔值
        """
        # 基本验证
        if not code or not code.strip():
            return False
        
        # Python语言特定验证
        if lang == 'python':
            # 检查是否包含基本的Python结构
            if 'def ' in code or 'class ' in code or 'import ' in code or 'if ' in code:
                return True
        
        return True
