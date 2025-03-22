from fastapi import APIRouter
from app.api.routes import auth, questions, knowledge

api_router = APIRouter()

# 添加各模块路由
api_router.include_router(auth.router, prefix="/auth", tags=["认证"])
api_router.include_router(questions.router, prefix="/questions", tags=["错题"])
api_router.include_router(knowledge.router, prefix="/knowledge", tags=["知识点"]) 