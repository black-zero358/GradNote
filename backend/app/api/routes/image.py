import shutil
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_active_user
from app.api.schemas.image import ImageProcessingResponse
from app.models.user import User
from app.services import image as image_service
from typing import Optional

router = APIRouter()

@router.post("/process", response_model=ImageProcessingResponse)
async def process_image(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    处理错题图像并提取文本
    
    此API仅进行图像处理并返回结果，不会在数据库中创建错题。
    常用于：
    1. 预览图像识别结果
    2. 获取图像文本后由前端进行进一步处理
    3. 作为其他API的基础服务（如/questions/from-image调用了此服务）
    
    处理流程:
    1. 上传并保存图片到服务器
    2. 使用图像处理服务提取文本内容
    3. 返回提取的文本和保存的图片URL
    
    参数:
    - file: 要处理的图像文件
    
    返回:
    - status: 处理状态 (success/error)
    - text: 从图像中提取的文本
    - image_url: 保存后的图像URL
    - message: 错误信息（仅当status为error时）
    """
    # 检查文件类型
    if not file.content_type.startswith('image/'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="仅支持图像文件"
        )
    
    # 读取文件内容
    file_content = await file.read()
    
    # 处理图像
    result = await image_service.process_question_image(file_content, file.filename)
    
    if result["status"] == "error":
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=result["message"]
        )
    
    return result 