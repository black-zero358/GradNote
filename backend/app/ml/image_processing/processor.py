import os
import json
import base64
from typing import Optional, Tuple
from langchain_openai import ChatOpenAI
from langchain.schema.messages import HumanMessage, SystemMessage
from langfuse.callback import CallbackHandler

# 从环境变量获取配置
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_API_BASE = os.getenv("OPENAI_API_BASE")
OPENAI_VLM_MODEL = os.getenv("OPENAI_VLM_MODEL", "doubao-1-5-vision-pro-32k-250115")

# 图片格式对应的MIME类型
MIME_TYPES = {
    'jpeg': 'image/jpeg',
    'jpg': 'image/jpeg',
    'png': 'image/png',
    'gif': 'image/gif',
    'webp': 'image/webp',
    'bmp': 'image/bmp',
    'tiff': 'image/tiff',
    'tif': 'image/tiff',
}

# 文件魔术字节映射，用于识别图片格式
MAGIC_BYTES = {
    b'\xff\xd8\xff': 'jpeg',          # JPEG
    b'\x89\x50\x4e\x47': 'png',       # PNG
    b'\x47\x49\x46\x38': 'gif',       # GIF
    b'\x52\x49\x46\x46': 'webp',      # WEBP
    b'\x42\x4d': 'bmp',               # BMP
    b'\x49\x49\x2a\x00': 'tiff',      # TIFF
    b'\x4d\x4d\x00\x2a': 'tiff',      # TIFF
}

class ImageProcessor:
    """图像处理类，用于将错题图片转换为文本"""
    
    def __init__(self, api_key: Optional[str] = None, api_base: Optional[str] = None, model_name: Optional[str] = None):
        """
        初始化图像处理器
        
        Args:
            api_key: API密钥，默认从环境变量获取
            api_base: API基础URL，默认从环境变量获取
            model_name: VLM模型名称，默认从环境变量获取
        """
        self.langfuse_handler = CallbackHandler()
        self.vlm = ChatOpenAI(
            api_key=api_key or OPENAI_API_KEY,
            base_url=api_base or OPENAI_API_BASE,
            model_name=model_name or OPENAI_VLM_MODEL,
            callbacks=[self.langfuse_handler]
        )
    
    def _detect_image_type_from_bytes(self, image_bytes: bytes) -> str:
        """
        从图像字节数据检测图像类型
        
        Args:
            image_bytes: 图像字节数据
            
        Returns:
            图像类型的MIME字符串
        """
        # 默认MIME类型
        default_mime = 'image/png'
        
        # 检查魔术字节
        for magic, format_name in MAGIC_BYTES.items():
            if image_bytes.startswith(magic):
                return MIME_TYPES.get(format_name, default_mime)
        
        # 无法识别则返回默认值
        return default_mime
    
    def _detect_image_type(self, image_path: str = None, image_bytes: bytes = None) -> str:
        """
        检测图像类型
        
        Args:
            image_path: 图像文件路径
            image_bytes: 图像字节数据
            
        Returns:
            图像类型的MIME字符串
        """
        # 默认MIME类型
        default_mime = 'image/png'
        
        # 如果提供了文件路径
        if image_path:
            # 先尝试从文件扩展名获取
            _, ext = os.path.splitext(image_path)
            if ext:
                # 去掉点号并转为小写
                ext = ext[1:].lower()
                if ext in MIME_TYPES:
                    return MIME_TYPES[ext]
            
            # 如果扩展名不存在或无法识别，尝试读取文件并检测魔术字节
            try:
                with open(image_path, 'rb') as f:
                    file_start = f.read(8)  # 读取前8个字节用于识别
                    return self._detect_image_type_from_bytes(file_start)
            except Exception:
                pass
        
        # 如果提供了字节数据
        elif image_bytes:
            return self._detect_image_type_from_bytes(image_bytes[:8])
        
        # 无法识别则返回默认值
        return default_mime
    
    def _encode_image(self, image_path: str) -> Tuple[str, str]:
        """
        将图像编码为base64字符串
        
        Args:
            image_path: 图像文件路径
            
        Returns:
            Tuple[str, str]: (MIME类型, base64编码的图像字符串)
        """
        with open(image_path, "rb") as image_file:
            image_data = image_file.read()
            mime_type = self._detect_image_type(image_path=image_path, image_bytes=image_data)
            return mime_type, base64.b64encode(image_data).decode('utf-8')
    
    def process_image_file(self, image_path: str) -> str:
        """
        处理图像文件并提取文本
        
        Args:
            image_path: 图像文件路径
            
        Returns:
            提取的文本内容
        """
        # 编码图像并获取MIME类型
        mime_type, base64_image = self._encode_image(image_path)
        
        # 调用VLM提取文本
        return self.process_image_base64(base64_image, mime_type)
    
    def process_image_base64(self, base64_image: str, mime_type: str = 'image/png') -> str:
        """
        处理base64编码的图像并提取文本
        
        Args:
            base64_image: base64编码的图像
            mime_type: 图像的MIME类型，默认为'image/png'
            
        Returns:
            提取的文本内容
        """
        # 创建消息
        messages = [
            SystemMessage(content="你是一个专业的OCR助手，任务是从图片中准确提取文字内容，特别是识别数学公式、物理符号等学科内容。请尽可能保持原始格式，完整输出所有文本内容。"),
            HumanMessage(
                content=[
                    {
                        "type": "text", 
                        "text": "请提取这张错题图片中的所有文本内容，包括题目、选项等。保持原始格式，不要遗漏任何文字和符号。"
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:{mime_type};base64,{base64_image}"
                        }
                    }
                ]
            )
        ]
        
        # 调用VLM
        response = self.vlm.invoke(messages)
        
        # 返回内容
        return response.content
    
    def process_image_bytes(self, image_bytes: bytes) -> str:
        """
        处理图像字节数据并提取文本
        
        Args:
            image_bytes: 图像的字节数据
            
        Returns:
            提取的文本内容
        """
        # 检测图像类型
        mime_type = self._detect_image_type(image_bytes=image_bytes)
        
        # 编码图像
        base64_image = base64.b64encode(image_bytes).decode('utf-8')
        
        # 调用VLM提取文本
        return self.process_image_base64(base64_image, mime_type) 