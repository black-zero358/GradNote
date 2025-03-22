from sqlalchemy.orm import Session
from app.core.config import settings
from app.services.user import create_user, get_user_by_username
from app.api.schemas.user import UserCreate
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 初始测试用户
FIRST_SUPERUSER = "admin"
FIRST_SUPERUSER_PASSWORD = "admin"
FIRST_SUPERUSER_EMAIL = "admin@example.com"

def init_db(db: Session) -> None:
    """
    初始化数据库
    """
    # 创建初始管理员用户
    user = get_user_by_username(db, FIRST_SUPERUSER)
    if not user:
        user_in = UserCreate(
            username=FIRST_SUPERUSER,
            password=FIRST_SUPERUSER_PASSWORD,
            email=FIRST_SUPERUSER_EMAIL,
        )
        user = create_user(db, user_in)
        logger.info(f"初始用户 {FIRST_SUPERUSER} 创建成功")
    else:
        logger.info(f"用户 {FIRST_SUPERUSER} 已存在") 