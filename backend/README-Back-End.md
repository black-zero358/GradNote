# GradNote 后端启动文档

本文档介绍了如何设置和运行GradNote错题知识点管理系统的后端服务。

## 目录
- [环境要求](#环境要求)
- [安装步骤](#安装步骤)
- [运行应用](#运行应用)
- [API文档](#api文档)
- [初始化数据](#初始化数据)
- [主要功能](#主要功能)
- [项目结构](#项目结构)
- [故障排除](#故障排除)
- [优化与监控](#优化与监控)

## 环境要求

- Python 3.8+
- PostgreSQL 14+
- Redis（用于缓存和任务队列）

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

# 如果需要GPU支持，还需安装CUDA相关依赖
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
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

# Redis配置
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=

# 安全配置
SECRET_KEY=your-secret-key-for-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# LangSmith配置
LANGSMITH_TRACING=true
LANGSMITH_API_KEY=your-langsmith-api-key
LANGSMITH_PROJECT=gradnote

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
# Windows/Linux/MacOS
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

### 1. 用户认证 (`/api/v1/auth`)
- 用户注册和登录
- JWT令牌认证
- 基于deps.py的依赖注入认证系统

### 2. 错题管理 (`/api/v1/questions`)
- 创建、更新、删除和查询错题
- 支持按科目、难度等筛选错题
- 错题图像上传和处理
- 支持批量操作和分页查询
- 错题知识点关联和标注

### 3. 知识点管理 (`/api/v1/knowledge`)
- 创建、更新、删除和查询知识点
- 支持结构化查询和树形展示
- 知识点自动标记和提取
- 知识点关系图谱构建
- 支持知识点难度评估

### 4. 图像处理 (`/api/v1/image`)
- 支持多种格式图像上传（JPG、PNG、PDF等）
- 图像预处理和优化
- OCR文本识别（通过image_processing模块）
- 安全的文件处理和存储
- 图像压缩和格式转换

### 5. 智能解题 (`/api/v1/solving`)
- 基于LangChain的解题辅助
- 知识点提取和关联
- 题目难度智能评估
- 解题步骤分析和推导
- 相似题目推荐

## 项目结构

### 目录结构

```
backend/
├── app/                  # 应用主目录
│   ├── api/              # API路由和模式定义
│   │   ├── routes/       # API路由
│   │   ├── schemas/      # Pydantic模型
│   │   └── deps.py       # 依赖注入
│   ├── core/             # 核心配置
│   ├── db/               # 数据库相关代码
│   ├── models/           # SQLAlchemy模型
│   ├── services/         # 业务逻辑
│   ├── llm_services/               # 机器学习相关代码
│   │   ├── image_processing/  # 图像处理
│   │   ├── knowledge_mark/    # 知识点标记
│   │   └── solving/           # 解题辅助
│   └── main.py           # 应用入口
├── uploads/              # 上传文件存储
├── tests/                # 测试
├── requirements.txt      # 依赖包列表
└── Dockerfile            # Docker配置
```

### API路由结构

```
api/
├── routes/
│   ├── api.py          # API路由聚合
│   ├── auth.py         # 认证相关路由
│   ├── questions.py    # 错题管理路由
│   ├── knowledge.py    # 知识点管理路由
│   ├── image.py        # 图像处理路由
│   └── solving.py      # 智能解题路由
├── schemas/            # 数据模型定义
└── deps.py            # 依赖注入
```

### 机器学习模块结构

```
llm_services/
├── image_processing/   # 图像处理模块
├── knowledge_mark/     # 知识点标记模块
└── solving/           # 智能解题模块
```

## 故障排除

### 常见问题

1. **数据库连接失败**：
   - 确认PostgreSQL服务已启动
   - 检查数据库连接信息是否正确
   - 确认用户拥有足够的权限
   - 检查防火墙设置是否允许数据库连接
   - 常见错误码及解决方案：
     * `FATAL: password authentication failed` - 检查POSTGRES_PASSWORD
     * `FATAL: database does not exist` - 运行初始化脚本创建数据库

2. **Redis连接问题**：
   - 确认Redis服务正在运行
   - 检查Redis配置信息
   - 验证Redis密码（如果设置）
   - 常见错误：
     * `Connection refused` - Redis服务未启动
     * `AuthenticationError` - Redis密码错误

3. **API认证问题**：
   - 默认管理员账户：
     * 用户名：admin
     * 密码：admin
   - 登录接口：`POST /api/v1/auth/login`
   - Token格式：`Authorization: Bearer <token>`
   - 常见状态码：
     * 401 - 未认证或token过期
     * 403 - 权限不足
     * 422 - 请求数据格式错误

4. **文件上传问题**：
   - 确保uploads目录存在且有写入权限
   - 文件大小限制：10MB
   - 支持的文件类型：
     * 图片：JPG、PNG、GIF
   - 常见错误：
     * 413 - 文件过大
     * 415 - 不支持的文件类型
     * 507 - 存储空间不足

5. **机器学习服务问题**：
   - 确保CUDA正确安装（如果使用GPU）
   - 检查模型文件是否完整
   - 验证OCR服务状态
   - 常见问题：
     * CUDA out of memory - 减小batch_size
     * Model not found - 检查模型路径
     * OCR服务超时 - 增加超时设置

6. **LLM服务连接问题**：
   - 验证API密钥和基础URL
   - 检查网络连接状态
   - 确认模型可用性
   - 常见错误：
     * 429 - 请求频率限制
     * 503 - LLM服务不可用
     * 504 - 请求超时

## 优化与监控

### 日志管理

日志配置位于 `app/core/config.py`，支持以下功能：

```python
# 日志级别设置
LOG_LEVEL = "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL

# 日志输出位置
LOG_FILE = "logs/app.log"

# 日志格式
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# 日志轮转
LOG_ROTATION = "500 MB"
```

### 性能优化

1. **数据库优化**：
   - 使用数据库连接池
   - 优化查询索引
   - 定期VACUUM

2. **缓存策略**：
   - Redis缓存热点数据
   - 图片缓存
   - API响应缓存

3. **并发处理**：
   - 使用异步任务队列
   - 合理设置worker数量
   - 启用协程池

### 监控指标

1. **系统监控**：
   - CPU使用率
   - 内存占用
   - 磁盘I/O
   - 网络流量

2. **应用监控**：
   - API响应时间
   - 请求成功率
   - 并发用户数
   - 错误率统计