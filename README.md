# GradNote - 错题知识点管理系统

<div align="center">
  <img src="https://s2.loli.net/2025/04/09/ETjvxPNdeqMQLgZ.png" alt="GradNote Logo" style="display:none;">

  ![GitHub](https://img.shields.io/github/license/black-zero358/GradNote)
  ![Python](https://img.shields.io/badge/python-3.13-blue.svg)
  ![FastAPI](https://img.shields.io/badge/FastAPI-0.115.11+-green.svg)
  ![PostgreSQL](https://img.shields.io/badge/PostgreSQL-17.4-blue.svg)
</div>

## 📚 项目概述

GradNote是一个基于FastAPI和大型语言模型(LLM)的错题知识点管理系统，帮助学生和教师高效管理、分析和利用错题资源。系统自动从错题中提取知识点，构建知识图谱，并提供智能化的学习建议。

### 🎯 核心目标

- 🔍 **智能错题分析**：利用LLM自动分析错题并提取关键知识点
- 🧠 **知识点网络构建**：形成结构化知识体系，揭示知识点间关联
- 📊 **学习弱点识别**：检测学习中的薄弱环节，提供针对性建议
- 📈 **学习进度追踪**：监控学习进度，实现个性化学习

## ✨ 功能特点

- **错题管理**
  - 支持多种格式错题录入（文本、图片）
  - 智能分类与标签系统
  - 全文检索功能

- **知识点提取**
  - 基于LangChain的知识点自动提取
  - 知识点关联性分析
  - 知识体系可视化

- **学习辅助**
  - 个性化复习计划生成
  - 难点攻克建议
  - 学习资源智能推荐

- **系统监控**
  - LangFuse提供的LLM性能监控
  - 用户行为分析
  - 系统使用统计

## 🛠️ 技术架构

### 核心技术栈

- **后端框架**：[FastAPI](https://fastapi.tiangolo.com/) - 高性能异步API框架
- **数据库**：[PostgreSQL](https://www.postgresql.org/) - 开源关系型数据库
- **LLM集成**：
  - [LangChain](https://python.langchain.com/) - LLM应用开发框架
  - [LangGraph](https://python.langchain.com/docs/langgraph) - 基于LangChain的智能流程编排
- **监控分析**：[LangFuse](https://langfuse.com/) - LLM应用监控平台

### 系统架构图

```
GradNote
│
├── backend/                 # 后端服务
│   ├── app/                 # 应用主目录
│   │   ├── api/             # API路由模块
│   │   │   ├── v1/          # API v1版本
│   │   │   └── deps.py      # API依赖项
│   │   │
│   │   ├── core/            # 核心配置
│   │   │   ├── config.py    # 配置管理
│   │   │   └── security.py  # 安全配置
│   │   │
│   │   ├── db/              # 数据库模块
│   │   │   ├── base.py      # 数据库基类
│   │   │   └── session.py   # 会话管理
│   │   │
│   │   ├── llm_services/    # LLM服务
│   │   │   ├── chains/      # LangChain链
│   │   │   ├── graphs/      # LangGraph图
│   │   │   ├── prompts/     # 提示模板
│   │   │   └── monitoring/  # LangFuse监控
│   │   │
│   │   ├── models/          # 数据模型
│   │   │   ├── domain/      # 领域模型
│   │   │   └── schemas/     # Pydantic模式
│   │   │
│   │   ├── services/        # 业务服务
│   │   │   ├── problem_service.py    # 错题服务
│   │   │   └── knowledge_service.py  # 知识点服务
│   │   │
│   │   └── main.py          # 应用入口
│   │
│   ├── requirements.txt     # 依赖
│   ├── uploads/             # 上传的图片
│   └── .env.example         # 环境变量示例
│
└── README.md                # 项目说明
```

## 🚀 快速开始

### 前提条件

- Python 3.13+
- PostgreSQL 17+
- OpenAI API密钥（或其他兼容LLM的API）

### 安装步骤

1. **克隆仓库**

```bash
git clone https://github.com/black-zero358/GradNote.git
cd GradNote
```

2. **设置Python虚拟环境**

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/MacOS
source venv/bin/activate
```

3. **安装依赖**

```bash
pip install -r backend/requirements.txt
```

4. **配置环境变量**

```bash
cp .env.example .env
# 编辑.env文件，配置必要参数
```

5. **初始化数据库**

todo...

6. **启动应用**

```bash
uvicorn app.main:app --reload
```

应用将在 http://localhost:8000 运行

## 📚 API文档

启动应用后，访问以下地址查看API文档:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 💡 使用指南

### 错题管理

#### 创建新错题

```python
import requests

response = requests.post(
    "http://localhost:8000/api/v1/problems/",
    json={
        "title": "求解方程 2x + 3 = 7",
        "content": "求解方程 2x + 3 = 7，其中x为未知数",
        "subject": "数学",
        "difficulty": "简单"
    }
)
print(response.json())
```

#### 查询错题

```python
response = requests.get(
    "http://localhost:8000/api/v1/problems/",
    params={"subject": "数学", "limit": 10}
)
print(response.json())
```

### 知识点操作

#### 提取知识点

```python
response = requests.post(
    "http://localhost:8000/api/v1/knowledge/extract",
    json={"problem_id": 1}
)
print(response.json())
```

## 🔧 开发指南

### 项目结构

- **API路由** (`app/api/`): 处理HTTP请求的路由定义
- **数据模型** (`app/models/`): SQLAlchemy和Pydantic模型
- **业务服务** (`app/services/`): 核心业务逻辑
- **LLM服务** (`app/llm_services/`): LLM相关功能实现

### LLM链设计

我们使用LangChain和LangGraph构建LLM应用，设计原则:

1. **模块化**: 每个链和图都有明确的单一职责
2. **可配置**: 通过环境变量和配置文件灵活配置
3. **可监控**: 集成LangFuse实现全链路监控
4. **可扩展**: 支持多种LLM后端

示例LangChain链:

```python
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI

# 知识点提取链
knowledge_template = """
请从以下题目中提取关键知识点:
题目: {problem_content}
输出格式: 以JSON数组形式返回提取的知识点
"""

prompt = PromptTemplate(
    input_variables=["problem_content"],
    template=knowledge_template
)

llm = ChatOpenAI(temperature=0)
knowledge_chain = LLMChain(llm=llm, prompt=prompt)
```

### 数据库设计

主要实体关系:

- **Problem**: 错题信息
- **KnowledgePoint**: 知识点
- **ProblemKnowledge**: 错题与知识点的多对多关系
- **User**: 用户信息
- **UserProblemRecord**: 用户错题记录

## 📊 监控与性能

我们使用LangFuse进行LLM应用监控:

```python
from langfuse.callback import CallbackHandler

handler = CallbackHandler(
    public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
    secret_key=os.getenv("LANGFUSE_SECRET_KEY")
)

llm = ChatOpenAI(
    callbacks=[handler]
)
```

## 🤝 贡献指南

1. Fork项目仓库
2. 创建特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建Pull Request

## 📝 许可证

本项目采用AGPL-3.0 license - 详见 [LICENSE](LICENSE) 文件


