from app.models.user import User
from app.models.question import WrongQuestion
from app.models.knowledge import KnowledgePoint, QuestionKnowledgeRelation, UserMark

# 方便导入所有模型
__all__ = [
    "User",
    "WrongQuestion",
    "KnowledgePoint",
    "QuestionKnowledgeRelation",
    "UserMark"
] 