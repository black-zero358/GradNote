import os
from typing import Dict, Optional
import aiofiles
import uuid
from app.ml.image_processing import ImageProcessor

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
        包含提取文本和图像URL的字典
    """
    try:
        # 保存图像
        image_path = await save_uploaded_image(file_content, filename)
        
        # 提取文本
        processor = get_image_processor()
        extracted_text = processor.process_image_bytes(file_content)
        
        return {
            "status": "success",
            "text": extracted_text,
            "image_url": image_path
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"图像处理失败: {str(e)}",
            "image_url": None
        }