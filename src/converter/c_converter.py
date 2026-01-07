from src.converter.base_converter import BaseConverter
from src.api_client.base_client import BaseAPIClient
from config.prompt_config import PromptConfig

class CConverter(BaseConverter):
    """C语言代码转换器实现"""
    
    def __init__(self, api_client: BaseAPIClient):
        """
        初始化C语言转换器
        
        Args:
            api_client: API客户端实例
        """
        super().__init__(api_client)
    
    def convert(self, source_lang: str, target_lang: str, code: str) -> str:
        """
        转换C语言代码
        
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
            # 针对C语言转换的特定提示
            c_specific_prompt = """
            请确保：
            1. 完整转换所有函数和数据结构
            2. 正确处理指针和内存管理
            3. 转换宏定义和预处理指令
            4. 保持相同的功能和逻辑
            5. 生成可直接编译运行的代码
            6. 处理所有必要的导入或头文件
            """
            
            # 构建完整提示
            full_prompt = PromptConfig.BASE_PROMPT.format(
                source_lang=source_lang,
                target_lang=target_lang,
                code=code
            ) + "\n" + c_specific_prompt
            
            # 使用API客户端进行代码转换
            converted_code = self.api_client.generate_response(full_prompt)
            
            # 格式化转换后的代码
            formatted_code = self.format_code(target_lang, converted_code)
            
            return formatted_code
            
        except Exception as e:
            raise Exception(f"C语言代码转换失败: {str(e)}")
    
    def validate(self, lang: str, code: str) -> bool:
        """
        验证C语言代码是否有效
        
        Args:
            lang: 代码语言
            code: 代码
            
        Returns:
            代码是否有效的布尔值
        """
        # 基本验证
        if not code or not code.strip():
            return False
        
        # C语言特定验证
        if lang == 'c':
            # 检查是否包含基本的C语言结构
            if '#' in code or 'int ' in code or 'void ' in code:
                return True
        
        return True
