from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv
from fastapi.staticfiles import StaticFiles
import logging

from app.api.routes.api import api_router
from app.core.config import settings
from app.db.create_tables import create_tables
from app.db.init_db import init_db
from app.db.create_index import create_indexes
from app.db.session import SessionLocal
from app.db.reset_sequence import reset_all_sequences

# 加载环境变量
load_dotenv()

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 创建FastAPI应用
app = FastAPI(
    title="GradNote API",
    description="错题知识点管理系统API",
    version="0.1.0"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 配置静态文件服务
UPLOAD_DIR = os.getenv("UPLOAD_DIR", "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

# 添加API路由
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.on_event("startup")
async def startup_db_client():
    """应用启动时创建数据库表并初始化数据"""
    # 仅在显式启用时运行数据库初始化
    run_db_init = os.getenv("RUN_DB_INIT", "false").lower() == "true"
    
    if run_db_init:
        try:
            logger.info("正在初始化数据库...")
            # 创建所有表
            create_tables()
            
            # 创建数据库索引
            create_indexes()
            
            # 初始化数据库数据
            db = SessionLocal()
            init_db(db)
            # 重置序列
            reset_all_sequences()
            db.close()
            logger.info("数据库初始化完成")
        except Exception as e:
            logger.error(f"数据库初始化失败: {e}")
    else:
        logger.info("跳过数据库初始化 (设置 RUN_DB_INIT=true 以启用)")

@app.get("/")
async def root():
    return {"message": "欢迎使用GradNote API"}

@app.get("/health")
async def health_check():
    return {"status": "i guess it's healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True) 