import os
import json
import base64
import logging
import re
from pathlib import Path
from typing import Optional, Tuple, Union, Literal

from langchain_openai import ChatOpenAI
from langchain.schema.messages import HumanMessage, SystemMessage
from langfuse.callback import CallbackHandler

# 从环境变量获取配置
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_API_BASE = os.getenv("OPENAI_API_BASE")
OPENAI_VLM_MODEL = os.getenv("OPENAI_VLM_MODEL", "doubao-1-5-vision-pro-32k-250115")

# 读取不同模式的提示语
VLM_EXTRACT_QUESTION_PROMPT = os.getenv("VLM_EXTRACT_QUESTION_PROMPT", "请提取这张错题图片中的文本内容，包括题目、选项等。保持原始格式，不要遗漏任何文字和符号。")
VLM_EXTRACT_ANSWER_PROMPT = os.getenv("VLM_EXTRACT_ANSWER_PROMPT", "你是一个专业的答案提取助手，任务是从错题图片中准确提取答案部分。如果图片中没有明确的答案，请回复None。请不要提取题目内容，只关注答案部分。")
VLM_EXTRACT_QUESTION_SYSTEM_PROMPT = os.getenv("VLM_EXTRACT_QUESTION_SYSTEM_PROMPT", "你是一个专业的OCR助手，任务是从图片中准确提取文字内容，特别是识别数学公式、物理符号等学科内容。请尽可能保持原始格式，完整输出所有文本内容。")
VLM_EXTRACT_ANSWER_SYSTEM_PROMPT = os.getenv("VLM_EXTRACT_ANSWER_SYSTEM_PROMPT", "你是一个专业的OCR助手，任务是从图片中准确提取文字内容，特别是识别数学公式、物理符号等学科内容。请尽可能保持原始格式，完整输出所有文本内容。")

# 默认的最大图片大小 (20MB)
DEFAULT_MAX_IMAGE_SIZE = 20 * 1024 * 1024

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

# 配置日志
logger = logging.getLogger(__name__)

class ImageProcessorError(Exception):
    """图像处理器异常基类"""
    def __init__(self, message: str = "图像处理错误"):
        self.message = message
        super().__init__(self.message)


class ImageSizeExceededError(ImageProcessorError):
    """图像大小超出限制异常"""
    def __init__(self, file_size: int, max_size: int):
        self.file_size = file_size
        self.max_size = max_size
        super().__init__(f"图片大小({file_size}字节)超过限制({max_size}字节)")


class ImageFormatError(ImageProcessorError):
    """图像格式错误异常"""
    def __init__(self, format_name: str = None):
        message = "不支持的图像格式"
        if format_name:
            message = f"不支持的图像格式: {format_name}"
        super().__init__(message)


class ImagePathError(ImageProcessorError):
    """图像路径错误异常"""
    def __init__(self, path: str, reason: str):
        self.path = path
        self.reason = reason
        super().__init__(f"图像路径无效: {reason}, 路径: {path}")


class ImageReadError(ImageProcessorError):
    """图像读取错误异常"""
    def __init__(self, file_path: str, error: str):
        self.file_path = file_path
        super().__init__(f"读取图片文件时出错: {error}, 文件路径: {file_path}")


class ImageProcessingAPIError(ImageProcessorError):
    """图像处理API错误异常"""
    def __init__(self, api_error: str):
        self.api_error = api_error
        super().__init__(f"图像处理API调用失败: {api_error}")


class InvalidBase64Error(ImageProcessorError):
    """无效的Base64编码异常"""
    def __init__(self):
        super().__init__("提供的字符串不是有效的base64编码")

class ImageProcessor:
    """图像处理类，用于将错题图片转换为文本"""

    def __init__(self,
                 api_key: Optional[str] = None,
                 api_base: Optional[str] = None,
                 model_name: Optional[str] = None,
                 max_image_size: int = DEFAULT_MAX_IMAGE_SIZE,
                 strict_format_check: bool = False):
        """
        初始化图像处理器

        Args:
            api_key: API密钥，默认从环境变量获取
            api_base: API基础URL，默认从环境变量获取
            model_name: VLM模型名称，默认从环境变量获取
            max_image_size: 最大处理图片大小（字节），默认20MB
            strict_format_check: 是否启用严格的图像格式检查，启用后对未知格式将抛出异常
        """
        self.langfuse_handler = CallbackHandler(tags=["VLM"])
        self.vlm = ChatOpenAI(
            api_key=api_key or OPENAI_API_KEY,
            base_url=api_base or OPENAI_API_BASE,
            model_name=model_name or OPENAI_VLM_MODEL,
            callbacks=[self.langfuse_handler]
        )
        self.max_image_size = max_image_size
        self.strict_format_check = strict_format_check

    def _validate_file_path(self, image_path: str) -> str:
        """
        验证文件路径的安全性和有效性

        Args:
            image_path: 图像文件路径

        Returns:
            绝对路径字符串

        Raises:
            ImagePathError: 路径无效或不存在
            ImageSizeExceededError: 图片大小超过限制
            ImageFormatError: 不支持的图像格式
        """
        # 确保路径存在且为文件
        path = Path(image_path).resolve()
        if not path.exists():
            logger.error(f"文件不存在: {image_path}")
            raise ImagePathError(image_path, "文件不存在")
        if not path.is_file():
            logger.error(f"路径不是文件: {image_path}")
            raise ImagePathError(image_path, "路径不是文件")

        # 检查文件大小
        file_size = path.stat().st_size
        if file_size > self.max_image_size:
            logger.error(f"图片大小({file_size}字节)超过限制({self.max_image_size}字节)")
            raise ImageSizeExceededError(
                file_size, self.max_image_size
            )

        # 检查文件扩展名是否为已知图像格式
        ext = path.suffix.lstrip('.').lower()
        if ext not in MIME_TYPES:
            logger.warning(f"未知的图片扩展名: {ext}")
            # 可以选择是否在严格模式下抛出异常
            if getattr(self, 'strict_format_check', False):
                raise ImageFormatError(ext)

        return str(path)

    def _is_valid_base64(self, base64_str: str) -> bool:
        """
        检查字符串是否为有效的base64编码

        Args:
            base64_str: 待检查的base64字符串

        Returns:
            是否为有效的base64编码
        """
        try:
            # 检查字符是否符合base64编码规则 (A-Z, a-z, 0-9, +, /, =)
            if not re.match(r'^[A-Za-z0-9+/]+={0,2}$', base64_str):
                return False

            # 尝试解码
            decoded = base64.b64decode(base64_str)
            return True
        except Exception:
            return False

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

    def _load_and_detect_image(self, image_path: str) -> Tuple[str, bytes]:
        """
        加载图像文件并检测其类型

        Args:
            image_path: 图像文件路径

        Returns:
            Tuple[str, bytes]: (MIME类型, 图像字节数据)

        Raises:
            ImagePathError: 路径无效或不存在
            ImageSizeExceededError: 图片大小超过限制
            ImageFormatError: 不支持的图像格式
            ImageReadError: 文件读取错误
        """
        # 验证文件路径
        validated_path = self._validate_file_path(image_path)

        try:
            # 读取文件
            with open(validated_path, "rb") as image_file:
                image_data = image_file.read()

            # 检测MIME类型
            # 先尝试从扩展名获取
            ext = Path(validated_path).suffix.lstrip('.').lower()
            mime_type = MIME_TYPES.get(ext)

            # 如果扩展名不存在或无法识别，尝试通过魔术字节判断
            if not mime_type:
                mime_type = self._detect_image_type_from_bytes(image_data[:8])

            return mime_type, image_data
        except OSError as e:
            logger.error(f"读取图片文件时出错: {str(e)}")
            raise ImageReadError(validated_path, str(e))

    async def process_image_file(self, image_path: str, mode: Literal["question", "answer"] = "question") -> str:
        """
        处理图像文件并提取文本

        Args:
            image_path: 图像文件路径
            mode: 处理模式，"question"提取题目，"answer"提取答案

        Returns:
            提取的文本内容

        Raises:
            ImagePathError: 路径无效或不存在
            ImageSizeExceededError: 图像大小超出限制
            ImageFormatError: 不支持的图像格式
            ImageReadError: 图像读取错误
            InvalidBase64Error: 图像转换为base64时发生错误
            ImageProcessingAPIError: 图像处理API错误
        """
        try:
            # 加载图像并检测类型
            mime_type, image_data = self._load_and_detect_image(image_path)

            # 编码为base64
            base64_image = base64.b64encode(image_data).decode('utf-8')

            # 异步调用VLM提取文本
            return await self.process_image_base64(base64_image, mime_type, mode)
        except (ImagePathError, ImageSizeExceededError, ImageFormatError, ImageReadError, InvalidBase64Error) as e:
            # 已知的特定异常，直接抛出
            raise
        except Exception as e:
            logger.error(f"处理图像文件时出错: {str(e)}")
            raise ImageProcessingAPIError(str(e))

    async def process_image_base64(self, base64_image: str, mime_type: str = 'image/png', mode: Literal["question", "answer"] = "question") -> str:
        """
        处理base64编码的图像并提取文本

        Args:
            base64_image: base64编码的图像
            mime_type: 图像的MIME类型，默认为'image/png'
            mode: 处理模式，"question"提取题目，"answer"提取答案

        Returns:
            提取的文本内容

        Raises:
            InvalidBase64Error: base64字符串无效
            ImageSizeExceededError: 图像大小超出限制
            ImageProcessingAPIError: 图像处理API错误
        """
        # 验证base64字符串
        if not self._is_valid_base64(base64_image):
            logger.error("提供的字符串不是有效的base64编码")
            raise InvalidBase64Error()

        # 检查图片大小（近似值，base64编码比原始数据大约大1/3）
        approx_size = (len(base64_image) * 3) // 4
        if approx_size > self.max_image_size:
            logger.error(f"解码后图片大小(约{approx_size}字节)超过限制({self.max_image_size}字节)")
            raise ImageSizeExceededError(
                approx_size, self.max_image_size
            )

        try:
            # 根据模式选择适当的提示语
            if mode == "question":
                system_prompt = VLM_EXTRACT_QUESTION_SYSTEM_PROMPT
                user_prompt = VLM_EXTRACT_QUESTION_PROMPT
            else:  # mode == "answer"
                system_prompt = VLM_EXTRACT_ANSWER_SYSTEM_PROMPT
                user_prompt = VLM_EXTRACT_ANSWER_PROMPT

            # 创建消息
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(
                    content=[
                        {
                            "type": "text",
                            "text": user_prompt
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:{mime_type};base64,{base64_image}",
                                "detail": "high"
                            }
                        }
                    ]
                )
            ]

            # 异步调用VLM
            response = await self.vlm.ainvoke(messages)

            # 返回内容
            return response.content
        except Exception as e:
            logger.error(f"处理base64图像时出错: {str(e)}")
            raise ImageProcessingAPIError(str(e))

    async def process_image_bytes(self, image_bytes: bytes, mode: Literal["question", "answer"] = "question") -> str:
        """
        处理图像字节数据并提取文本

        Args:
            image_bytes: 图像的字节数据
            mode: 处理模式，"question"提取题目，"answer"提取答案

        Returns:
            提取的文本内容

        Raises:
            ImageSizeExceededError: 图像大小超出限制
            ImageFormatError: 不支持的图像格式
            InvalidBase64Error: 图像转换为base64时发生错误
            ImageProcessingAPIError: 图像处理API错误
        """
        # 检查图片大小
        if len(image_bytes) > self.max_image_size:
            logger.error(f"图片大小({len(image_bytes)}字节)超过限制({self.max_image_size}字节)")
            raise ImageSizeExceededError(
                len(image_bytes), self.max_image_size
            )

        try:
            # 检测图像类型
            mime_type = self._detect_image_type_from_bytes(image_bytes[:8])

            # 编码图像
            base64_image = base64.b64encode(image_bytes).decode('utf-8')

            # 异步调用VLM提取文本
            return await self.process_image_base64(base64_image, mime_type, mode)
        except (ImageSizeExceededError, InvalidBase64Error) as e:
            # 已知的特定异常，直接抛出
            raise
        except Exception as e:
            logger.error(f"处理图像字节数据时出错: {str(e)}")
            raise ImageProcessingAPIError(str(e))