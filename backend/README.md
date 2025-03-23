# GradNote 后端启动文档

本文档介绍了如何设置和运行GradNote错题知识点管理系统的后端服务。

## 环境要求

- Python 3.8+
- PostgreSQL 14+
- Redis（可选，用于缓存）

## 安装步骤

### 1. 克隆代码库

```bash
git clone <repository-url>
cd GradNote-v1/backend
```

### 2. 创建虚拟环境

```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# Linux/MacOS
python -m venv venv
source venv/bin/activate
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

### 4. 配置环境变量

创建`.env`文件，内容如下：

```
# 数据库配置
POSTGRES_SERVER=localhost
POSTGRES_USER=postgres
POSTGRES_PASSWORD=123456
POSTGRES_DB=GradNote
POSTGRES_PORT=5432

# Redis配置（可选）
REDIS_HOST=localhost
REDIS_PORT=6379

# 安全配置
SECRET_KEY=your-secret-key-for-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# LangSmith配置（可选）
LANGSMITH_TRACING=true
LANGSMITH_API_KEY=your-langsmith-api-key

# LLM设置 (OpenAI格式)
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
```

根据您的实际环境修改上述配置。

### 5. 准备PostgreSQL数据库

1. 安装PostgreSQL数据库

2. 创建数据库：
   ```sql
   CREATE DATABASE "GradNote";
   ```

## 运行应用

### 开发模式运行

```bash
# Windows
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Linux/MacOS
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 生产模式运行

```bash
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### 使用Docker运行

```bash
# 构建Docker镜像
docker build -t gradnote-backend .

# 运行容器
docker run -d --name gradnote-backend -p 8000:8000 \
  -e POSTGRES_SERVER=host.docker.internal \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=123456 \
  -e POSTGRES_DB=GradNote \
  -e POSTGRES_PORT=5432 \
  gradnote-backend
```

## API文档

启动应用后，可以通过以下URL访问自动生成的API文档：

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 初始化数据

应用程序启动时会自动执行以下操作：
1. 创建必要的数据库表
2. 创建数据库索引以提高查询性能
3. 添加初始用户（用户名：admin，密码：admin）
4. 添加初始知识点数据

如果需要手动初始化数据库，可以运行以下命令：

```bash
# 创建表
python -m app.db.create_tables

# 创建索引
python -m app.db.create_index

# 初始化数据
python -c "from app.db.session import SessionLocal; from app.db.init_db import init_db; db = SessionLocal(); init_db(db); db.close()"
```

## 主要功能

### 1. 用户认证
- 用户注册和登录
- JWT令牌认证

### 2. 错题管理
- 创建、更新、删除和查询错题
- 支持按科目、难度等筛选错题
- 错题图像上传和处理

### 3. 知识点管理
- 创建、更新、删除和查询知识点
- 支持结构化查询和树形展示
- 知识点自动标记和提取

### 4. 图像处理
- 支持多种格式图像上传（JPG、PNG、PDF等）
- 图像格式自动识别
- 安全的文件处理和存储

### 5. AI辅助功能
- 集成LangChain和LangGraph
- 智能解题辅助
- 知识点自动标记和关联

## 目录结构

```
backend/
├── app/                  # 应用主目录
│   ├── api/              # API路由和模式定义
│   │   ├── deps/         # 依赖项（如认证）
│   │   ├── routes/       # API路由
│   │   └── schemas/      # Pydantic模型
│   ├── core/             # 核心配置
│   ├── db/               # 数据库相关代码
│   ├── models/           # SQLAlchemy模型
│   ├── services/         # 业务逻辑
│   └── ml/               # 机器学习相关代码
│       ├── image_processing/  # 图像处理
│       ├── knowledge_mark/    # 知识点标记
│       └── solving/           # 解题辅助
├── uploads/              # 上传文件存储
├── tests/                # 测试
├── requirements.txt      # 依赖包列表
└── Dockerfile            # Docker配置
```

## 故障排除

### 常见问题

1. **数据库连接失败**：
   - 确认PostgreSQL服务已启动
   - 检查数据库连接信息是否正确
   - 确认用户拥有足够的权限

2. **API认证问题**：
   - 默认用户名/密码：admin/admin
   - 登录接口：`POST /api/v1/auth/login`
   - 大多数API需要认证，请在请求头中添加Token：`Authorization: Bearer <token>`

3. **文件上传问题**：
   - 确保uploads目录存在且有写入权限
   - 文件大小默认限制为10MB
   - 支持的图像格式：JPG、PNG、GIF、PDF

4. **LLM服务连接问题**：
   - 检查API密钥和基础URL配置
   - 确认网络连接正常
   - 查看日志获取详细错误信息

### 日志

应用日志默认输出到控制台。如需更改日志配置，请修改`app/core/config.py`文件。 