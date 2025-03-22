# GradNote 后端启动文档

本文档介绍了如何设置和运行GradNote错题知识点管理系统的后端服务。

## 环境要求

- Python 3.8+
- PostgreSQL 14+（需启用pgvector扩展）
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

# LLM服务配置（可选）
LLM_API_KEY=your-llm-api-key
LLM_MODEL=deepseek-r1-250120
VLM_MODEL=doubao-1-5-vision-pro-32k-250115
EMBEDDING_MODEL=doubao-embedding-large-text-240915

# LangSmith配置（可选）
LANGCHAIN_TRACING_V2=false
LANGCHAIN_API_KEY=your-langsmith-api-key
```

根据您的实际环境修改上述配置。

### 5. 准备PostgreSQL数据库

1. 安装PostgreSQL数据库

2. 创建数据库：
   ```sql
   CREATE DATABASE "GradNote";
   ```

3. 启用pgvector扩展（用于向量检索）：
   ```sql
   \c GradNote
   CREATE EXTENSION IF NOT EXISTS vector;
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

2. **pgvector扩展问题**：
   - 确认已安装pgvector：`CREATE EXTENSION vector;`
   - 如果不需要向量搜索功能，可以忽略相关错误

3. **API认证问题**：
   - 默认用户名/密码：admin/admin
   - 登录接口：`POST /api/v1/auth/login`
   - 大多数API需要认证，请在请求头中添加Token：`Authorization: Bearer <token>`

### 日志

应用日志默认输出到控制台。如需更改日志配置，请修改`app/core/config.py`文件。 