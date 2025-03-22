import os
import json
import base64
from typing import Optional
from langchain_openai import ChatOpenAI
from langchain.schema.messages import HumanMessage, SystemMessage
from langfuse.callback import CallbackHandler

# 从环境变量获取配置
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_API_BASE = os.getenv("OPENAI_API_BASE")
OPENAI_VLM_MODEL = os.getenv("OPENAI_VLM_MODEL", "doubao-1-5-vision-pro-32k-250115")

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
    
    def _encode_image(self, image_path: str) -> str:
        """
        将图像编码为base64字符串
        
        Args:
            image_path: 图像文件路径
            
        Returns:
            base64编码的图像字符串
        """
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    
    def process_image_file(self, image_path: str) -> str:
        """
        处理图像文件并提取文本
        
        Args:
            image_path: 图像文件路径
            
        Returns:
            提取的文本内容
        """
        # 编码图像
        base64_image = self._encode_image(image_path)
        
        # 调用VLM提取文本
        return self.process_image_base64(base64_image)
    
    def process_image_base64(self, base64_image: str) -> str:
        """
        处理base64编码的图像并提取文本
        
        Args:
            base64_image: base64编码的图像
            
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
                            "url": f"data:image/jpeg;base64,{base64_image}"
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
        # 编码图像
        base64_image = base64.b64encode(image_bytes).decode('utf-8')
        
        # 调用VLM提取文本
        return self.process_image_base64(base64_image) 