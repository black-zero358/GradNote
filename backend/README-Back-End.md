# GradNote 后端服务

## 简介

GradNote是一个错题知识点管理系统，帮助学生高效管理和学习错题。本文档介绍了后端服务的设置、运行和维护方法。

## 目录

- [功能特性](#功能特性)
- [技术栈](#技术栈)
- [环境要求](#环境要求)
- [快速开始](#快速开始)
- [详细配置](#详细配置)
- [API文档](#api文档)
- [项目结构](#项目结构)
- [开发指南](#开发指南)
- [部署指南](#部署指南)
- [故障排除](#故障排除)
- [性能优化](#性能优化)
- [贡献指南](#贡献指南)

## 功能特性

- 用户认证与授权
- 错题管理与分析
- 知识点提取与关联
- 智能解题辅助
- 图像处理与OCR
- 数据统计与可视化

## 技术栈

- **Web框架**: FastAPI
- **数据库**: PostgreSQL 14+
- **缓存**: Redis
- **AI模型**: LangChain, OpenAI
- **图像处理**: PIL, OpenCV
- **认证**: JWT
- **文档**: OpenAPI/Swagger

## 环境要求

### 基础环境
- Python 3.8+
- PostgreSQL 14+
- Redis 6+
- Node.js 16+ (用于前端开发)

### 硬件推荐配置
- CPU: 4核+
- 内存: 8GB+
- 存储: 20GB+
- GPU: 推荐NVIDIA GPU (用于图像处理)

### 操作系统支持
- Linux (推荐Ubuntu 20.04+)
- Windows 10/11
- macOS 10.15+

## 快速开始

### 1. 克隆代码库

```bash
git clone https://github.com/yourusername/GradNote-v1.git
cd GradNote-v1/backend
```

### 2. 创建虚拟环境

```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# Linux/macOS
python -m venv venv
source venv/bin/activate
```

### 3. 安装依赖

```bash
# 基础依赖
pip install -r requirements.txt

# GPU支持（可选）
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

### 4. 环境配置

创建`.env`文件：

```ini
# 数据库配置
POSTGRES_SERVER=localhost
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password
POSTGRES_DB=GradNote
POSTGRES_PORT=5432

# Redis配置
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=

# 安全配置
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# LANGFUSE配置
LANGFUSE_PUBLIC_KEY=your-langfuse-public-key
LANGFUSE_SECRET_KEY=your-langfuse-secret-key

# LLM设置
OPENAI_API_KEY=your-openai-api-key
OPENAI_API_BASE=your-openai-api-base
OPENAI_LLM_MODEL=deepseek-r1-250120
OPENAI_EMBEDDING_MODEL=doubao-embedding-large-text-240915
OPENAI_VLM_MODEL=doubao-1-5-vision-pro-32k-250115

# 服务设置
DEBUG=true
WORKERS=4
API_PORT=8000
API_HOST=0.0.0.0
UPLOAD_DIR=uploads
MAX_UPLOAD_SIZE=10485760  # 10MB
ALLOWED_IMAGE_TYPES=["image/jpeg", "image/png", "image/gif", "application/pdf"]
```

### 5. 初始化数据库

```bash
# 创建数据库
psql -U postgres
CREATE DATABASE "GradNote";
\q

# 初始化表结构和数据
python -m app.db.create_tables
python -m app.db.init_db
```

### 6. 启动服务

```bash
# 开发模式
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 生产模式
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

## 详细配置

### 数据库配置

PostgreSQL配置说明：

```sql
-- 创建数据库
CREATE DATABASE "GradNote";

-- 创建用户（可选）
CREATE USER gradnote WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE "GradNote" TO gradnote;

-- 创建扩展（如果需要）
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
```

### Redis配置

redis.conf关键配置：

```conf
port 6379
bind 127.0.0.1
maxmemory 2gb
maxmemory-policy allkeys-lru
```

### 文件上传配置

支持的文件类型和大小限制：

```python
ALLOWED_IMAGE_TYPES = [
    "image/jpeg",
    "image/png",
    "image/gif",
    "application/pdf"
]

MAX_UPLOAD_SIZE = 10 * 1024 * 1024  # 10MB
```

## API文档

API文档访问地址：

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- OpenAPI JSON: http://localhost:8000/openapi.json

详细API文档请参考：[backend-api.md](backend-api.md)

## 项目结构

```
backend/
├── app/                    # 应用主目录
│   ├── api/               # API相关代码
│   │   ├── routes/       # API路由定义
│   │   ├── schemas/      # 数据模型定义
│   │   └── deps.py       # 依赖注入
│   ├── core/             # 核心配置
│   │   ├── config.py     # 配置管理
│   │   ├── security.py   # 安全相关
│   │   └── logging.py    # 日志配置
│   ├── db/               # 数据库相关
│   │   ├── session.py    # 数据库会话
│   │   └── base.py      # 基础模型
│   ├── models/           # 数据库模型
│   ├── services/         # 业务逻辑
│   ├── llm_services/     # AI服务
│   │   ├── image_processing/  # 图像处理
│   │   ├── knowledge_mark/    # 知识点标记
│   │   └── solving/          # 解题辅助
│   └── main.py           # 应用入口
├── tests/                # 测试代码
│   ├── api/             # API测试
│   ├── services/        # 服务测试
│   └── conftest.py      # 测试配置
├── uploads/             # 上传文件目录
├── alembic/             # 数据库迁移
├── requirements.txt     # 依赖清单
├── Dockerfile          # Docker配置
└── docker-compose.yml  # Docker编排
```

## 开发指南

### 代码规范

- 遵循PEP 8规范
- 使用Black进行代码格式化
- 使用isort管理导入顺序
- 使用flake8进行代码检查

### 提交规范

```bash
<type>(<scope>): <subject>

<body>

<footer>
```

类型(type)：
- feat: 新功能
- fix: 修复
- docs: 文档
- style: 格式
- refactor: 重构
- test: 测试
- chore: 构建


## 部署指南

### Docker部署

```bash
# 构建镜像
docker build -t gradnote-backend .

# 运行容器
docker run -d \
  --name gradnote-backend \
  -p 8000:8000 \
  -e POSTGRES_SERVER=host.docker.internal \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=your_password \
  -e POSTGRES_DB=GradNote \
  gradnote-backend
```

### Docker Compose部署

```yaml
version: '3.8'
services:
  backend:
    build: .
    ports:
      - "8000:8000"
    env_file:
      - .env
    depends_on:
      - db
      - redis

  db:
    image: postgres:14
    environment:
      POSTGRES_DB: GradNote
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: your_password
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:6
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

volumes:
  postgres_data:
  redis_data:
```

## 故障排除

### 常见问题

1. **数据库连接问题**
   - 检查数据库服务是否运行
   - 验证连接信息是否正确
   - 确认防火墙设置

2. **Redis连接问题**
   - 检查Redis服务状态
   - 验证密码配置
   - 检查内存使用情况

3. **文件上传问题**
   - 检查目录权限
   - 验证文件大小限制
   - 确认支持的文件类型

4. **API认证问题**
   - 检查Token格式
   - 验证密钥配置
   - 确认过期时间设置

### 错误码说明

| 错误码 | 描述 | 解决方案 |
|--------|------|----------|
| DB001 | 数据库连接失败 | 检查数据库配置 |
| AUTH001 | 认证失败 | 验证Token |
| FILE001 | 文件上传失败 | 检查文件大小和类型 |
| API001 | API调用失败 | 检查请求参数 |

## 性能优化

### 数据库优化

1. **索引优化**
   ```sql
   CREATE INDEX idx_questions_user_id ON questions(user_id);
   CREATE INDEX idx_knowledge_points_subject ON knowledge_points(subject);
   ```

2. **查询优化**
   ```sql
   -- 使用子查询优化
   EXPLAIN ANALYZE SELECT * FROM questions WHERE user_id IN (SELECT id FROM users WHERE active = true);
   ```

### 缓存策略

1. **Redis缓存配置**
   ```python
   CACHE_TTL = 3600  # 缓存过期时间（秒）
   CACHE_PREFIX = "gradnote:"  # 缓存键前缀
   ```

2. **缓存使用示例**
   ```python
   async def get_cached_data(key: str):
       cached = await redis.get(f"{CACHE_PREFIX}{key}")
       return json.loads(cached) if cached else None
   ```

### 并发处理

1. **异步任务**
   ```python
   from celery import Celery
   
   celery = Celery('tasks', broker='redis://localhost:6379/0')
   
   @celery.task
   def process_image(image_path: str):
       # 处理图片的代码
       pass
   ```

2. **连接池配置**
   ```python
   DATABASE_POOL_SIZE = 20
   DATABASE_POOL_OVERFLOW = 10
   DATABASE_POOL_TIMEOUT = 30
   ```

## 贡献指南

1. Fork项目
2. 创建特性分支
3. 提交更改
4. 推送到分支
5. 创建Pull Request

### 开发流程

1. 领取或创建issue
2. 本地开发和测试
3. 提交代码审查
4. 合并到主分支

### 文档维护

1. 及时更新API文档
2. 编写详细的注释
3. 维护README文档
4. 记录重要的更改