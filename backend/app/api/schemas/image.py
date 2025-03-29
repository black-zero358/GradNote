from pydantic import BaseModel
from typing import Optional

class ImageProcessingResponse(BaseModel):
    """图像处理响应模型"""
    status: str
    text: Optional[str] = None
    image_url: Optional[str] = None
    message: Optional[str] = None
    error_code: Optional[str] = None 