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
    
    参数:
    - file: 上传的图像文件
    
    返回:
    - 提取的文本内容和图像URL
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