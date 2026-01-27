from datetime import datetime, timedelta
from typing import Optional, Union, Any
import secrets
from jose import jwt
from passlib.context import CryptContext
from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_access_token(subject: Union[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    创建JWT访问令牌
    """
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    验证密码
    bcrypt 限制密码最大长度为 72 字节，需要截断
    """
    # bcrypt 有 72 字节限制，截断密码
    truncated_password = plain_password.encode('utf-8')[:72].decode('utf-8', errors='ignore')
    return pwd_context.verify(truncated_password, hashed_password)

def get_password_hash(password: str) -> str:
    """
    获取密码哈希
    bcrypt 限制密码最大长度为 72 字节，需要截断
    """
    # bcrypt 有 72 字节限制，截断密码
    truncated_password = password.encode('utf-8')[:72].decode('utf-8', errors='ignore')
    return pwd_context.hash(truncated_password)

def generate_secure_password(length: int = 16) -> str:
    """
    生成安全的随机密码
    
    Args:
        length: 密码长度，默认16位
        
    Returns:
        生成的随机密码字符串
        
    密码包含：
    - 大写字母 (A-Z)
    - 小写字母 (a-z) 
    - 数字 (0-9)
    - 特殊符号 (!@#$%^&*)
    - 排除易混淆字符 (0, O, l, 1, I)
    """
    # 定义字符集，排除易混淆字符
    uppercase = 'ABCDEFGHJKLMNPQRSTUVWXYZ'  # 排除I和O
    lowercase = 'abcdefghjkmnpqrstuvwxyz'  # 排除l和o
    digits = '23456789'  # 排除0和1
    special_chars = '!@#$%^&*'
    
    # 确保密码至少包含每种类型的字符
    password_chars = [
        secrets.choice(uppercase),
        secrets.choice(lowercase), 
        secrets.choice(digits),
        secrets.choice(special_chars)
    ]
    
    # 填充剩余长度
    all_chars = uppercase + lowercase + digits + special_chars
    for _ in range(length - 4):
        password_chars.append(secrets.choice(all_chars))
    
    # 随机打乱字符顺序
    secrets.SystemRandom().shuffle(password_chars)
    
    password = ''.join(password_chars)
    
    # 验证生成的密码强度
    if validate_password_strength(password):
        return password
    else:
        # 递归重新生成（理论上很少发生）
        return generate_secure_password(length)

def validate_password_strength(password: str) -> bool:
    """
    验证密码强度是否符合要求
    
    Args:
        password: 待验证的密码
        
    Returns:
        True如果密码符合强度要求，否则False
    """
    if len(password) < 12:
        return False
        
    has_upper = any(c.isupper() for c in password)
    has_lower = any(c.islower() for c in password)
    has_digit = any(c.isdigit() for c in password)
    has_special = any(c in '!@#$%^&*' for c in password)
    
    return all([has_upper, has_lower, has_digit, has_special]) 