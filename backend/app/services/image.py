import os
from typing import Dict, Optional
import aiofiles
import uuid
from app.llm_services.image_processing import (
    ImageProcessor,
    ImageProcessorError,
    ImageSizeExceededError,
    ImageFormatError,
    ImageReadError,
    ImageProcessingAPIError,
    InvalidBase64Error,
    ImagePathError
)

# 从环境变量获取配置
UPLOAD_DIR = os.getenv("UPLOAD_DIR", "uploads")

def get_image_processor() -> ImageProcessor:
    """
    获取图像处理器实例

    Returns:
        ImageProcessor实例
    """
    return ImageProcessor()

async def save_uploaded_image(file_content: bytes, filename: str) -> str:
    """
    保存上传的图像文件

    Args:
        file_content: 文件内容
        filename: 原始文件名

    Returns:
        保存后的文件路径
    """
    # 确保上传目录存在
    os.makedirs(UPLOAD_DIR, exist_ok=True)

    # 生成唯一文件名
    file_extension = filename.split('.')[-1] if '.' in filename else 'jpg'
    unique_filename = f"{uuid.uuid4()}.{file_extension}"
    file_path = os.path.join(UPLOAD_DIR, unique_filename)

    # 保存文件
    async with aiofiles.open(file_path, 'wb') as f:
        await f.write(file_content)

    return file_path

async def process_question_image(file_content: bytes, filename: str) -> Dict:
    """
    处理题目图像并提取文本

    Args:
        file_content: 文件内容字节数据
        filename: 原始文件名

    Returns:
        包含提取文本和图像URL的字典，或包含错误信息的字典

        成功时返回:
        {
            "status": "success",
            "text": "提取的文本内容",
            "image_url": "保存的图像路径"
        }

        失败时返回:
        {
            "status": "error",
            "message": "错误描述信息",
            "error_code": "错误代码",
            "image_url": None
        }
    """
    try:
        # 保存图像
        image_path = await save_uploaded_image(file_content, filename)

        # 提取文本
        processor = get_image_processor()
        extracted_text = await processor.process_image_bytes(file_content)

        return {
            "status": "success",
            "text": extracted_text,
            "image_url": image_path
        }
    except ImageSizeExceededError as e:
        # 用户友好的错误信息，避免显示详细的技术内容
        size_mb = round(e.file_size / (1024 * 1024), 2)
        max_size_mb = round(e.max_size / (1024 * 1024), 2)
        return {
            "status": "error",
            "message": f"图像太大，无法处理。图像大小: {size_mb}MB，最大允许: {max_size_mb}MB",
            "error_code": "IMAGE_SIZE_EXCEEDED",
            "image_url": None
        }
    except ImageFormatError as e:
        return {
            "status": "error",
            "message": f"不支持的图像格式。{e.message}",
            "error_code": "IMAGE_FORMAT_ERROR",
            "image_url": None
        }
    except InvalidBase64Error as e:
        return {
            "status": "error",
            "message": "图像数据无效，无法解码",
            "error_code": "INVALID_IMAGE_DATA",
            "image_url": None
        }
    except ImagePathError as e:
        return {
            "status": "error",
            "message": f"图像路径无效: {e.reason}",
            "error_code": "INVALID_IMAGE_PATH",
            "image_url": None
        }
    except ImageReadError as e:
        return {
            "status": "error",
            "message": "无法读取图像文件",
            "error_code": "IMAGE_READ_ERROR",
            "image_url": None
        }
    except ImageProcessingAPIError as e:
        return {
            "status": "error",
            "message": "图像处理服务暂时不可用，请稍后再试",
            "error_code": "API_ERROR",
            "image_url": None
        }
    except ImageProcessorError as e:
        return {
            "status": "error",
            "message": f"图像处理失败: {e.message}",
            "error_code": "PROCESSING_ERROR",
            "image_url": None
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"未知错误，请联系管理员",
            "error_code": "UNKNOWN_ERROR",
            "image_url": None
        }

async def process_answer_image(file_content: bytes, filename: str) -> Dict:
    """
    处理答案图像并提取文本

    Args:
        file_content: 文件内容字节数据
        filename: 原始文件名

    Returns:
        包含提取文本和图像URL的字典，或包含错误信息的字典

        成功时返回:
        {
            "status": "success",
            "text": "提取的答案内容",
            "image_url": "保存的图像路径"
        }

        失败时返回:
        {
            "status": "error",
            "message": "错误描述信息",
            "error_code": "错误代码",
            "image_url": None
        }
    """
    try:
        # 保存图像
        image_path = await save_uploaded_image(file_content, filename)

        # 提取文本，使用"answer"模式
        processor = get_image_processor()
        extracted_text = await processor.process_image_bytes(file_content, mode="answer")

        return {
            "status": "success",
            "text": extracted_text,
            "image_url": image_path
        }
    except ImageSizeExceededError as e:
        # 用户友好的错误信息，避免显示详细的技术内容
        size_mb = round(e.file_size / (1024 * 1024), 2)
        max_size_mb = round(e.max_size / (1024 * 1024), 2)
        return {
            "status": "error",
            "message": f"图像太大，无法处理。图像大小: {size_mb}MB，最大允许: {max_size_mb}MB",
            "error_code": "IMAGE_SIZE_EXCEEDED",
            "image_url": None
        }
    except ImageFormatError as e:
        return {
            "status": "error",
            "message": f"不支持的图像格式。{e.message}",
            "error_code": "IMAGE_FORMAT_ERROR",
            "image_url": None
        }
    except InvalidBase64Error as e:
        return {
            "status": "error",
            "message": "图像数据无效，无法解码",
            "error_code": "INVALID_IMAGE_DATA",
            "image_url": None
        }
    except ImagePathError as e:
        return {
            "status": "error",
            "message": f"图像路径无效: {e.reason}",
            "error_code": "INVALID_IMAGE_PATH",
            "image_url": None
        }
    except ImageReadError as e:
        return {
            "status": "error",
            "message": "无法读取图像文件",
            "error_code": "IMAGE_READ_ERROR",
            "image_url": None
        }
    except ImageProcessingAPIError as e:
        return {
            "status": "error",
            "message": "图像处理服务暂时不可用，请稍后再试",
            "error_code": "API_ERROR",
            "image_url": None
        }
    except ImageProcessorError as e:
        return {
            "status": "error",
            "message": f"图像处理失败: {e.message}",
            "error_code": "PROCESSING_ERROR",
            "image_url": None
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"未知错误，请联系管理员",
            "error_code": "UNKNOWN_ERROR",
            "image_url": None
        }