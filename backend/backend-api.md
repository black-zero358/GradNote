# GradNote API 技术文档

## API基础信息

- **基础URL**: `/api/v1`
- **API版本**: v1
- **内容类型**: application/json（除非特别说明，如文件上传等）
- **认证方式**: Bearer Token（JWT）
- **OpenAPI文档**: `/openapi.json`
- **Swagger UI**: `/docs`
- **ReDoc**: `/redoc`

## 目录

1. [认证API](#认证API)
2. [错题API](#错题API)
3. [知识点API](#知识点API)
4. [解题API](#解题API)
5. [图像处理API](#图像处理API)

## 认证API

### 用户登录

- **URL**: `/auth/login`
- **方法**: `POST`
- **描述**: 使用用户名和密码进行登录
- **请求体**:
  ```json
  {
    "username": "string",
    "password": "string"
  }
  ```
- **响应**:
  ```json
  {
    "access_token": "string",
    "token_type": "bearer"
  }
  ```
- **状态码**:
  - `200`: 登录成功
  - `401`: 用户名或密码错误
  - `422`: 请求参数验证错误

### 用户注册

- **URL**: `/auth/register`
- **方法**: `POST`
- **描述**: 注册新用户
- **请求体**:
  ```json
  {
    "username": "string",
    "email": "string", // 可选
    "password": "string"
  }
  ```
- **响应**:
  ```json
  {
    "id": "integer",
    "username": "string",
    "email": "string",
    "created_at": "datetime"
  }
  ```
- **状态码**:
  - `200`: 注册成功
  - `400`: 用户名或邮箱已存在
  - `422`: 请求参数验证错误

## 错题API

### 创建错题

- **URL**: `/questions/`
- **方法**: `POST`
- **描述**: 创建新的错题记录
- **认证**: 需要Bearer Token
- **请求体**:
  ```json
  {
    "content": "string",
    "subject": "string", // 可选
    "solution": "string", // 可选
    "remarks": "string",  // 可选
    "image_url": "string" // 可选
  }
  ```
- **响应**:
  ```json
  {
    "id": "integer",
    "user_id": "integer",
    "content": "string",
    "subject": "string",
    "solution": "string",
    "remarks": "string",
    "image_url": "string",
    "created_at": "datetime"
  }
  ```
- **状态码**:
  - `200`: 创建成功
  - `422`: 请求参数验证错误

### 获取错题列表

- **URL**: `/questions/`
- **方法**: `GET`
- **描述**: 获取当前用户的错题列表
- **认证**: 需要Bearer Token
- **查询参数**:
  - `skip`: 跳过的记录数（默认: 0）
  - `limit`: 返回的最大记录数（默认: 100）
- **响应**:
  ```json
  [
    {
      "id": "integer",
      "user_id": "integer",
      "content": "string",
      "subject": "string",
      "solution": "string",
      "remarks": "string",
      "image_url": "string",
      "created_at": "datetime"
    }
  ]
  ```
- **状态码**:
  - `200`: 获取成功
  - `422`: 请求参数验证错误

### 获取错题详情

- **URL**: `/questions/{question_id}`
- **方法**: `GET`
- **描述**: 获取特定错题的详细信息
- **认证**: 需要Bearer Token
- **路径参数**:
  - `question_id`: 错题ID
- **响应**:
  ```json
  {
    "id": "integer",
    "user_id": "integer",
    "content": "string",
    "subject": "string",
    "solution": "string",
    "remarks": "string",
    "image_url": "string",
    "created_at": "datetime"
  }
  ```
- **状态码**:
  - `200`: 获取成功
  - `404`: 错题不存在
  - `422`: 请求参数验证错误

### 更新错题

- **URL**: `/questions/{question_id}`
- **方法**: `PUT`
- **描述**: 更新错题信息
- **认证**: 需要Bearer Token
- **路径参数**:
  - `question_id`: 错题ID
- **请求体**:
  ```json
  {
    "content": "string", // 可选
    "solution": "string", // 可选
    "remarks": "string", // 可选
    "image_url": "string" // 可选
  }
  ```
- **响应**:
  ```json
  {
    "id": "integer",
    "user_id": "integer",
    "content": "string",
    "subject": "string",
    "solution": "string",
    "remarks": "string",
    "image_url": "string",
    "created_at": "datetime"
  }
  ```
- **状态码**:
  - `200`: 更新成功
  - `404`: 错题不存在
  - `422`: 请求参数验证错误

### 删除错题

- **URL**: `/questions/{question_id}`
- **方法**: `DELETE`
- **描述**: 删除指定的错题
- **认证**: 需要Bearer Token
- **路径参数**:
  - `question_id`: 错题ID
- **响应**:
  ```json
  {
    "id": "integer",
    "user_id": "integer",
    "content": "string",
    "subject": "string",
    "solution": "string",
    "remarks": "string",
    "image_url": "string",
    "created_at": "datetime"
  }
  ```
- **状态码**:
  - `200`: 删除成功
  - `404`: 错题不存在
  - `422`: 请求参数验证错误

### 通过图片创建错题

- **URL**: `/questions/from-image`
- **方法**: `POST`
- **描述**: 上传图片并从中提取内容创建错题
- **认证**: 需要Bearer Token
- **请求体**: 
  - 表单数据（multipart/form-data）:
    - `file`: 图片文件
- **响应**:
  ```json
  {
    "status": "string",
    "data": {
      "id": "integer",
      "user_id": "integer",
      "content": "string",
      "subject": "string",
      "solution": "string",
      "remarks": "string",
      "image_url": "string",
      "created_at": "datetime"
    },
    "message": "string"
  }
  ```
- **状态码**:
  - `200`: 创建成功
  - `400`: 文件类型错误
  - `422`: 请求参数验证错误
  - `500`: 图像处理错误

## 知识点API

### 根据结构查询知识点

- **URL**: `/knowledge/structure`
- **方法**: `GET`
- **描述**: 基于结构化信息（科目、章节、小节）查询知识点
- **查询参数**:
  - `subject`: 科目（必需）
  - `chapter`: 章节（可选）
  - `section`: 小节（可选）
- **响应**:
  ```json
  [
    {
      "id": "integer",
      "subject": "string",
      "chapter": "string",
      "section": "string",
      "item": "string",
      "details": "string",
      "mark_count": "integer",
      "created_at": "datetime"
    }
  ]
  ```
- **状态码**:
  - `200`: 查询成功
  - `422`: 请求参数验证错误

### 搜索知识点

- **URL**: `/knowledge/search`
- **方法**: `GET`
- **描述**: 按条件搜索知识点
- **查询参数**:
  - `subject`: 科目（可选）
  - `chapter`: 章节（可选）
  - `section`: 小节（可选）
  - `item`: 知识点名称，支持模糊搜索（可选）
  - `sort_by`: 排序字段，如"mark_count"或"created_at"（可选）
  - `skip`: 跳过的记录数（默认: 0）
  - `limit`: 返回的最大记录数（默认: 100）
- **响应**:
  ```json
  [
    {
      "id": "integer",
      "subject": "string",
      "chapter": "string",
      "section": "string",
      "item": "string",
      "details": "string",
      "mark_count": "integer",
      "created_at": "datetime"
    }
  ]
  ```
- **状态码**:
  - `200`: 搜索成功
  - `422`: 请求参数验证错误

### 获取热门知识点

- **URL**: `/knowledge/popular`
- **方法**: `GET`
- **描述**: 获取最热门的知识点（根据标记次数）
- **查询参数**:
  - `limit`: 返回的记录数（默认: 10）
- **响应**:
  ```json
  [
    {
      "id": "integer",
      "subject": "string",
      "chapter": "string",
      "section": "string",
      "item": "string",
      "details": "string",
      "mark_count": "integer",
      "created_at": "datetime"
    }
  ]
  ```
- **状态码**:
  - `200`: 获取成功
  - `422`: 请求参数验证错误

### 获取所有科目

- **URL**: `/knowledge/subjects`
- **方法**: `GET`
- **描述**: 获取所有科目列表
- **响应**:
  ```json
  [
    "string"
  ]
  ```
- **状态码**:
  - `200`: 获取成功

### 获取指定科目的章节

- **URL**: `/knowledge/chapters`
- **方法**: `GET`
- **描述**: 获取指定科目的所有章节
- **查询参数**:
  - `subject`: 科目名称（必需）
- **响应**:
  ```json
  [
    "string"
  ]
  ```
- **状态码**:
  - `200`: 获取成功
  - `422`: 请求参数验证错误

### 获取指定章节的小节

- **URL**: `/knowledge/sections`
- **方法**: `GET`
- **描述**: 获取指定科目和章节的所有小节
- **查询参数**:
  - `subject`: 科目名称（必需）
  - `chapter`: 章节名称（必需）
- **响应**:
  ```json
  [
    "string"
  ]
  ```
- **状态码**:
  - `200`: 获取成功
  - `422`: 请求参数验证错误

### 获取知识点详情

- **URL**: `/knowledge/{knowledge_point_id}`
- **方法**: `GET`
- **描述**: 根据ID获取知识点详情
- **路径参数**:
  - `knowledge_point_id`: 知识点ID
- **响应**:
  ```json
  {
    "id": "integer",
    "subject": "string",
    "chapter": "string",
    "section": "string",
    "item": "string",
    "details": "string",
    "mark_count": "integer",
    "created_at": "datetime"
  }
  ```
- **状态码**:
  - `200`: 获取成功
  - `404`: 知识点不存在
  - `422`: 请求参数验证错误

### 标记知识点

- **URL**: `/knowledge/mark/{knowledge_point_id}`
- **方法**: `POST`
- **描述**: 增加知识点标记次数
- **认证**: 需要Bearer Token
- **路径参数**:
  - `knowledge_point_id`: 知识点ID
- **响应**:
  ```json
  {
    "id": "integer",
    "subject": "string",
    "chapter": "string",
    "section": "string",
    "item": "string",
    "details": "string",
    "mark_count": "integer",
    "created_at": "datetime"
  }
  ```
- **状态码**:
  - `200`: 标记成功
  - `404`: 知识点不存在
  - `422`: 请求参数验证错误

### 创建用户知识点标记

- **URL**: `/knowledge/user-mark`
- **方法**: `POST`
- **描述**: 创建用户知识点标记记录
- **认证**: 需要Bearer Token
- **请求体**:
  ```json
  {
    "knowledge_point_id": "integer",
    "question_id": "integer"
  }
  ```
- **响应**:
  ```json
  {
    "id": "integer",
    "user_id": "integer",
    "knowledge_point_id": "integer",
    "question_id": "integer",
    "marked_at": "datetime"
  }
  ```
- **状态码**:
  - `201`: 创建成功
  - `404`: 知识点不存在
  - `422`: 请求参数验证错误

### 获取用户标记列表

- **URL**: `/knowledge/user-marks`
- **方法**: `GET`
- **描述**: 获取当前用户的所有标记
- **认证**: 需要Bearer Token
- **响应**:
  ```json
  [
    {
      "id": "integer",
      "user_id": "integer",
      "knowledge_point_id": "integer",
      "question_id": "integer",
      "marked_at": "datetime"
    }
  ]
  ```
- **状态码**:
  - `200`: 获取成功

### 创建知识点

- **URL**: `/knowledge/`
- **方法**: `POST`
- **描述**: 创建新的知识点
- **认证**: 需要Bearer Token
- **请求体**:
  ```json
  {
    "subject": "string",
    "chapter": "string",
    "section": "string",
    "item": "string",
    "details": "string" // 可选
  }
  ```
- **响应**:
  ```json
  {
    "id": "integer",
    "subject": "string",
    "chapter": "string",
    "section": "string",
    "item": "string",
    "details": "string",
    "mark_count": "integer",
    "created_at": "datetime"
  }
  ```
- **状态码**:
  - `201`: 创建成功
  - `422`: 请求参数验证错误

## 解题API

### 解答错题

- **URL**: `/solving/{question_id}`
- **方法**: `POST`
- **描述**: 解答指定的错题
- **认证**: 需要Bearer Token
- **路径参数**:
  - `question_id`: 错题ID
- **响应**:
  ```json
  {
    "status": "string",
    "message": "string",
    "data": {
      "question": "string",
      "solution": "string",
      "review_passed": "boolean",
      "review_reason": "string",
      "knowledge_points": [
        {
          "id": "integer",
          "subject": "string",
          "chapter": "string",
          "section": "string",
          "item": "string",
          "details": "string",
          "mark_count": "integer",
          "created_at": "datetime"
        }
      ],
      "new_knowledge_points": [
        {
          "id": "integer",
          "subject": "string",
          "chapter": "string",
          "section": "string",
          "item": "string",
          "details": "string",
          "mark_count": "integer",
          "created_at": "datetime"
        }
      ]
    }
  }
  ```
- **状态码**:
  - `200`: 解答成功
  - `404`: 错题不存在
  - `422`: 请求参数验证错误

### 从错题提取知识点

- **URL**: `/solving/extract/{question_id}`
- **方法**: `POST`
- **描述**: 从错题中提取知识点
- **认证**: 需要Bearer Token
- **路径参数**:
  - `question_id`: 错题ID
- **响应**:
  ```json
  {
    "status": "string",
    "subject_info": {
      "subject": "string",
      "chapter": "string",
      "section": "string"
    },
    "knowledge_points": [
      {
        "id": "integer",
        "subject": "string",
        "chapter": "string",
        "section": "string",
        "item": "string",
        "details": "string",
        "mark_count": "integer",
        "created_at": "datetime"
      }
    ],
    "is_complete": "boolean",
    "evaluation": {
      "key": "value"
    }
  }
  ```
- **状态码**:
  - `200`: 提取成功
  - `404`: 错题不存在
  - `422`: 请求参数验证错误

## 图像处理API

### 处理图像

- **URL**: `/image/process`
- **方法**: `POST`
- **描述**: 处理错题图像并提取文本
- **认证**: 需要Bearer Token
- **请求体**:
  - 表单数据（multipart/form-data）:
    - `file`: 图片文件
- **响应**:
  ```json
  {
    "status": "string",
    "text": "string",
    "image_url": "string",
    "message": "string",
    "error_code": "string"
  }
  ```
- **状态码**:
  - `200`: 处理成功
  - `400`: 文件类型错误
  - `422`: 请求参数验证错误
  - `500`: 图像处理错误

**错误代码说明**:
- `IMAGE_SIZE_EXCEEDED`: 图像过大
- `IMAGE_FORMAT_ERROR`: 不支持的图像格式
- `INVALID_IMAGE_DATA`: 无效的图像数据
- `INVALID_IMAGE_PATH`: 图像路径无效
- `IMAGE_READ_ERROR`: 图像读取错误
- `API_ERROR`: 图像处理API错误
- `PROCESSING_ERROR`: 图像处理失败
- `UNKNOWN_ERROR`: 未知错误
