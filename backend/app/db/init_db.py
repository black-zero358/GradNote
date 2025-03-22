from sqlalchemy.orm import Session
from app.core.config import settings
from app.services.user import create_user, get_user_by_username
from app.api.schemas.user import UserCreate
from app.models.knowledge import KnowledgePoint
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 初始测试用户
FIRST_SUPERUSER = "admin"
FIRST_SUPERUSER_PASSWORD = "admin"
FIRST_SUPERUSER_EMAIL = "admin@example.com"

# 初始知识点数据
INITIAL_KNOWLEDGE_POINTS = [
    {
        "subject": "高等数学",
        "chapter": "微积分",
        "section": "导数",
        "item": "导数的定义",
        "details": "函数y=f(x)在点x0处的导数定义为：f'(x0)=lim(△x→0)[(f(x0+△x)-f(x0))/△x]，表示函数在该点的变化率。"
    },
    {
        "subject": "高等数学",
        "chapter": "微积分",
        "section": "导数",
        "item": "导数的几何意义",
        "details": "导数的几何意义是切线的斜率，表示曲线在该点的瞬时变化率。"
    },
    {
        "subject": "高等数学",
        "chapter": "微积分",
        "section": "积分",
        "item": "定积分的定义",
        "details": "定积分∫[a,b]f(x)dx定义为函数f(x)在区间[a,b]上的黎曼和的极限，表示曲线下的面积。"
    },
    {
        "subject": "线性代数",
        "chapter": "矩阵",
        "section": "矩阵运算",
        "item": "矩阵乘法",
        "details": "矩阵乘法C=AB中，C的元素cij等于矩阵A的第i行与矩阵B的第j列对应元素乘积之和。要求A的列数等于B的行数。"
    },
    {
        "subject": "线性代数",
        "chapter": "矩阵",
        "section": "特征值与特征向量",
        "item": "特征值与特征向量的定义",
        "details": "如果存在非零向量x和标量λ使得Ax=λx，则λ称为矩阵A的特征值，x称为对应于特征值λ的特征向量。"
    }
]

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
    
    # 创建初始知识点数据
    init_knowledge_points(db)

def init_knowledge_points(db: Session) -> None:
    """
    初始化知识点数据
    """
    existing_count = db.query(KnowledgePoint).count()
    if existing_count == 0:
        logger.info("开始添加初始知识点数据...")
        try:
            for kp_data in INITIAL_KNOWLEDGE_POINTS:
                knowledge_point = KnowledgePoint(**kp_data)
                db.add(knowledge_point)
            db.commit()
            logger.info(f"成功添加 {len(INITIAL_KNOWLEDGE_POINTS)} 条初始知识点数据")
        except Exception as e:
            db.rollback()
            logger.error(f"添加初始知识点数据失败: {e}")
    else:
        logger.info(f"数据库中已存在 {existing_count} 条知识点数据，跳过初始化") 