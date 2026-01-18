# GradNote API文档

## 目录

- [API概述](#API概述)
- [认证API](#认证API)
- [错题API](#错题API)
- [知识点API](#知识点API)
- [解题API](#解题API)
- [图像处理API](#图像处理API)
- [API响应格式](#API响应格式)
- [状态码说明](#状态码说明)
- [错误处理](#错误处理)

## API概述

GradNote API采用RESTful设计风格，所有API路径均以`/api/v1/`为前缀，支持JSON格式的请求和响应。

- **基础URL**: `http://localhost:8000/api/v1/`
- **认证方式**: JWT令牌认证（Bearer Token）
- **内容类型**: `application/json`

### 请求示例

```bash
curl -X GET "http://localhost:8000/api/v1/questions" \
     -H "Authorization: Bearer {your_access_token}" \
     -H "Content-Type: application/json"
```

## 认证API

### 用户登录

- **URL**: `/auth/login`
- **方法**: `POST`
- **描述**: 用户登录并获取访问令牌
- **认证**: 无需认证
- **请求体**:
  ```json
  {
    "username": "用户名",
    "password": "密码"
  }
  ```
- **响应**:
  ```json
  {
    "access_token": "JWT令牌",
    "token_type": "bearer"
  }
  ```
- **状态码**:
  - `200`: 登录成功
  - `401`: 用户名或密码错误

### 用户注册

- **URL**: `/auth/register`
- **方法**: `POST`
- **描述**: 注册新用户
- **认证**: 无需认证
- **请求体**:
  ```json
  {
    "username": "用户名",
    "email": "邮箱地址",
    "password": "密码"
  }
  ```
- **响应**:
  ```json
  {
    "id": 1,
    "username": "用户名",
    "email": "邮箱地址",
    "created_at": "2023-01-01T12:00:00"
  }
  ```
- **状态码**:
  - `200`: 注册成功
  - `400`: 用户名或邮箱已存在

## 错题API

### 获取错题列表

- **URL**: `/questions`
- **方法**: `GET`
- **描述**: 获取当前用户的错题列表
- **认证**: 需要Bearer Token
- **查询参数**:
  - `skip`: 跳过的记录数（分页用，默认0）
  - `limit`: 返回的记录数（默认100）
- **响应**:
  ```json
  [
    {
      "id": 1,
      "content": "题目内容",
      "subject": "科目",
      "solution": "解答",
      "answer": "答案",
      "image_url": "图片URL",
      "remark": "备注",
      "user_id": 1,
      "created_at": "创建时间"
    }
  ]
  ```
- **状态码**:
  - `200`: 获取成功

### 创建新错题

- **URL**: `/questions`
- **方法**: `POST`
- **描述**: 创建新错题
- **认证**: 需要Bearer Token
- **请求体**:
  ```json
  {
    "content": "题目内容",
    "subject": "科目",
    "solution": "解答",
    "answer": "答案",
    "image_url": "图片URL",
    "remark": "备注"
  }
  ```
- **响应**:
  ```json
  {
    "id": 1,
    "content": "题目内容",
    "subject": "科目",
    "solution": "解答",
    "answer": "答案",
    "image_url": "图片URL",
    "remark": "备注",
    "user_id": 1,
    "created_at": "创建时间"
  }
  ```
- **状态码**:
  - `200`: 创建成功
  - `422`: 参数验证错误

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
    "id": 1,
    "content": "题目内容",
    "subject": "科目",
    "solution": "解答",
    "answer": "答案",
    "image_url": "图片URL",
    "remark": "备注",
    "user_id": 1,
    "created_at": "创建时间"
  }
  ```
- **状态码**:
  - `200`: 获取成功
  - `404`: 错题不存在

### 更新错题

- **URL**: `/questions/{question_id}`
- **方法**: `PUT`
- **描述**: 更新特定错题的信息
- **认证**: 需要Bearer Token
- **路径参数**:
  - `question_id`: 错题ID
- **请求体**:
  ```json
  {
    "content": "更新的题目内容",
    "subject": "更新的科目",
    "solution": "更新的解答",
    "answer": "更新的答案",
    "image_url": "更新的图片URL",
    "remark": "更新的备注"
  }
  ```
- **响应**:
  ```json
  {
    "id": 1,
    "content": "更新的题目内容",
    "subject": "更新的科目",
    "solution": "更新的解答",
    "answer": "更新的答案",
    "image_url": "更新的图片URL",
    "remark": "更新的备注",
    "user_id": 1,
    "created_at": "创建时间"
  }
  ```
- **状态码**:
  - `200`: 更新成功
  - `404`: 错题不存在
  - `422`: 参数验证错误

### 删除错题

- **URL**: `/questions/{question_id}`
- **方法**: `DELETE`
- **描述**: 删除特定错题
- **认证**: 需要Bearer Token
- **路径参数**:
  - `question_id`: 错题ID
- **响应**:
  ```json
  {
    "id": 1,
    "content": "题目内容",
    "subject": "科目",
    "solution": "解答",
    "answer": "答案",
    "image_url": "图片URL",
    "remark": "备注",
    "user_id": 1,
    "created_at": "创建时间"
  }
  ```
- **状态码**:
  - `200`: 删除成功
  - `404`: 错题不存在



## 知识点API

### 按结构查询知识点

- **URL**: `/knowledge/structure`
- **方法**: `GET`
- **描述**: 基于结构化信息（科目、章节、小节）查询知识点
- **认证**: 需要Bearer Token
- **查询参数**:
  - `subject`: 科目（必需）
  - `chapter`: 章节（可选）
  - `section`: 小节（可选）
- **响应**:
  ```json
  [
    {
      "id": 1,
      "subject": "数学",
      "chapter": "高等数学",
      "section": "微分",
      "item": "导数定义",
      "details": "导数的定义与计算方法",
      "mark_count": 5,
      "created_at": "2023-01-01T12:00:00"
    }
  ]
  ```
- **状态码**:
  - `200`: 查询成功
  - `422`: 参数验证错误

### 搜索知识点

- **URL**: `/knowledge/search`
- **方法**: `GET`
- **描述**: 通过关键词搜索知识点
- **认证**: 需要Bearer Token
- **查询参数**:
  - `query`: 搜索关键词
  - `limit`: 返回结果数量限制（默认10）
- **响应**:
  ```json
  [
    {
      "id": 1,
      "subject": "数学",
      "chapter": "高等数学",
      "section": "微分",
      "item": "导数定义",
      "details": "导数的定义与计算方法",
      "mark_count": 5,
      "created_at": "2023-01-01T12:00:00"
    }
  ]
  ```
- **状态码**:
  - `200`: 搜索成功

### 获取热门知识点

- **URL**: `/knowledge/popular`
- **方法**: `GET`
- **描述**: 获取最热门的知识点（根据标记次数）
- **认证**: 需要Bearer Token
- **查询参数**:
  - `limit`: 返回结果数量限制（默认10）
- **响应**:
  ```json
  [
    {
      "id": 1,
      "subject": "数学",
      "chapter": "高等数学",
      "section": "微分",
      "item": "导数定义",
      "details": "导数的定义与计算方法",
      "mark_count": 5,
      "created_at": "2023-01-01T12:00:00"
    }
  ]
  ```
- **状态码**:
  - `200`: 获取成功

### 获取科目列表

- **URL**: `/knowledge/subjects`
- **方法**: `GET`
- **描述**: 获取所有科目
- **认证**: 需要Bearer Token
- **响应**:
  ```json
  [
    "数学",
    "物理",
    "化学"
  ]
  ```
- **状态码**:
  - `200`: 获取成功

### 获取章节列表

- **URL**: `/knowledge/chapters`
- **方法**: `GET`
- **描述**: 获取指定科目的所有章节
- **认证**: 需要Bearer Token
- **查询参数**:
  - `subject`: 科目名称（必需）
- **响应**:
  ```json
  [
    "高等数学",
    "线性代数",
    "概率论"
  ]
  ```
- **状态码**:
  - `200`: 获取成功
  - `422`: 参数验证错误

### 获取小节列表

- **URL**: `/knowledge/sections`
- **方法**: `GET`
- **描述**: 获取指定科目和章节的所有小节
- **认证**: 需要Bearer Token
- **查询参数**:
  - `subject`: 科目名称（必需）
  - `chapter`: 章节名称（必需）
- **响应**:
  ```json
  [
    "微分",
    "积分",
    "级数"
  ]
  ```
- **状态码**:
  - `200`: 获取成功
  - `422`: 参数验证错误

### 获取知识点详情

- **URL**: `/knowledge/{knowledge_point_id}`
- **方法**: `GET`
- **描述**: 获取知识点详情
- **认证**: 需要Bearer Token
- **路径参数**:
  - `knowledge_point_id`: 知识点ID
- **响应**:
  ```json
  {
    "id": 1,
    "subject": "数学",
    "chapter": "高等数学",
    "section": "微分",
    "item": "导数定义",
    "details": "导数的定义与计算方法",
    "mark_count": 5,
    "created_at": "2023-01-01T12:00:00"
  }
  ```
- **状态码**:
  - `200`: 获取成功
  - `404`: 知识点不存在

### 创建知识点

- **URL**: `/knowledge`
- **方法**: `POST`
- **描述**: 创建新知识点
- **认证**: 需要Bearer Token
- **请求体**:
  ```json
  {
    "subject": "数学",
    "chapter": "高等数学",
    "section": "微分",
    "item": "导数定义",
    "details": "导数的定义与计算方法"
  }
  ```
- **响应**:
  ```json
  {
    "id": 1,
    "subject": "数学",
    "chapter": "高等数学",
    "section": "微分",
    "item": "导数定义",
    "details": "导数的定义与计算方法",
    "mark_count": 0,
    "created_at": "2023-01-01T12:00:00"
  }
  ```
- **状态码**:
  - `200`: 创建成功
  - `422`: 参数验证错误

### 标记知识点

- **URL**: `/knowledge/mark/{knowledge_point_id}`
- **方法**: `POST`
- **描述**: 标记知识点（增加标记次数）
- **认证**: 需要Bearer Token
- **路径参数**:
  - `knowledge_point_id`: 知识点ID
- **响应**:
  ```json
  {
    "id": 1,
    "subject": "数学",
    "chapter": "高等数学",
    "section": "微分",
    "item": "导数定义",
    "details": "导数的定义与计算方法",
    "mark_count": 6,
    "created_at": "2023-01-01T12:00:00"
  }
  ```
- **状态码**:
  - `200`: 标记成功
  - `404`: 知识点不存在

### 创建用户标记

- **URL**: `/knowledge/user-mark`
- **方法**: `POST`
- **描述**: 创建用户与知识点的关联标记
- **认证**: 需要Bearer Token
- **请求体**:
  ```json
  {
    "knowledge_point_id": 1,
    "question_id": 2,
    "remark": "这是一个重要知识点"
  }
  ```
- **响应**:
  ```json
  {
    "id": 1,
    "user_id": 1,
    "knowledge_point_id": 1,
    "question_id": 2,
    "remark": "这是一个重要知识点",
    "created_at": "2023-01-01T12:00:00"
  }
  ```
- **状态码**:
  - `200`: 创建成功
  - `404`: 知识点或错题不存在
  - `422`: 参数验证错误

### 确认知识点标记

- **URL**: `/knowledge/mark-confirmed`
- **方法**: `POST`
- **描述**: 处理用户确认的知识点标记，包括已有知识点和新知识点
- **认证**: 需要Bearer Token
- **请求体**:
  ```json
  {
    "question_id": 1,
    "existing_knowledge_point_ids": [1, 2],
    "new_knowledge_points": [
      {
        "subject": "数学",
        "chapter": "高等数学",
        "section": "微分",
        "item": "新知识点",
        "details": "详细说明",
        "is_existing": false
      }
    ]
  }
  ```
- **响应**:
  ```json
  {
    "question_id": 1,
    "marked_knowledge_points": [
      {
        "id": 1,
        "subject": "数学",
        "chapter": "高等数学",
        "section": "微分",
        "item": "导数定义",
        "details": "导数的定义与计算方法",
        "mark_count": 6,
        "created_at": "2023-01-01T12:00:00"
      },
      {
        "id": 3,
        "subject": "数学",
        "chapter": "高等数学",
        "section": "微分",
        "item": "新知识点",
        "details": "详细说明",
        "mark_count": 1,
        "created_at": "2023-10-27T10:00:00"
      }
    ]
  }
  ```
- **状态码**:
  - `200`: 标记成功
  - `422`: 参数验证错误

### 获取用户标记

- **URL**: `/knowledge/user-marks`
- **方法**: `GET`
- **描述**: 获取当前用户的知识点标记
- **认证**: 需要Bearer Token
- **查询参数**:
  - `question_id`: 错题ID（可选，如果提供则筛选特定错题的标记）
- **响应**:
  ```json
  [
    {
      "id": 1,
      "user_id": 1,
      "knowledge_point_id": 1,
      "question_id": 2,
      "remark": "这是一个重要知识点",
      "created_at": "2023-01-01T12:00:00",
      "knowledge_point": {
        "id": 1,
        "subject": "数学",
        "chapter": "高等数学",
        "section": "微分",
        "item": "导数定义",
        "details": "导数的定义与计算方法"
      }
    }
  ]
  ```
- **状态码**:
  - `200`: 获取成功

### 分析题目提取知识点

- **URL**: `/knowledge/analyze-from-question`
- **方法**: `POST`
- **描述**: 分析题目文本，返回可能的知识点类别
- **认证**: 需要Bearer Token
- **请求体**:
  ```json
  {
    "question_text": "某题目文本内容"
  }
  ```
- **响应**:
  ```json
  {
    "categories": [
      {
        "subject": "数学",
        "chapter": "高等数学",
        "section": "微分"
      },
      {
        "subject": "数学",
        "chapter": "高等数学",
        "section": "导数应用"
      }
    ]
  }
  ```
- **状态码**:
  - `200`: 分析成功
  - `422`: 参数验证错误

### 从解题过程提取知识点

- **URL**: `/knowledge/extract-from-solution`
- **方法**: `POST`
- **描述**: 从解题过程中提取使用的知识点，区分"已有知识点"和"新知识点"
- **认证**: 需要Bearer Token
- **请求体**:
  ```json
  {
    "question_text": "题目文本",
    "solution_text": "解题过程文本",
    "existing_knowledge_point_ids": [1, 2, 3]
  }
  ```
- **响应**:
  ```json
  {
    "existing_knowledge_points": [
      {
        "id": 1,
        "subject": "数学",
        "chapter": "高等数学",
        "section": "微分",
        "item": "导数定义",
        "details": "导数的定义与计算方法",
        "mark_count": 5,
        "created_at": "2023-01-01T12:00:00"
      }
    ],
    "new_knowledge_points": [
      {
        "subject": "数学",
        "chapter": "高等数学",
        "section": "微分",
        "item": "链式法则",
        "details": "复合函数求导的链式法则",
        "is_existing": false
      }
    ]
  }
  ```
- **状态码**:
  - `200`: 提取成功
  - `422`: 参数验证错误

## 解题API

### 解答错题

- **URL**: `/solving/{question_id}`
- **方法**: `POST`
- **描述**: 解答错题
- **认证**: 需要Bearer Token
- **路径参数**:
  - `question_id`: 错题ID
- **请求体**:
  ```json
  {
    "knowledge_points": [1, 2, 3]
  }
  ```
- **响应**:
  ```json
  {
    "status": "success",
    "message": "解题成功",
    "data": {
      "question": "题目内容...",
      "solution": "解题步骤详细内容...",
      "knowledge_points": [
        {
          "id": 1,
          "subject": "数学",
          "chapter": "高等数学",
          "section": "微分",
          "item": "导数定义",
          "details": "导数的定义与计算方法"
        }
      ]
    }
  }
  ```
- **状态码**:
  - `200`: 解答成功
  - `404`: 错题不存在
  - `422`: 参数验证错误

## 图像处理API

### 处理错题图像

- **URL**: `/image/process`
- **方法**: `POST`
- **描述**: 处理错题图像并提取文本
- **认证**: 需要Bearer Token
- **请求体**: 表单数据，包含图片文件
  - `file`: 图片文件（multipart/form-data）
- **响应**:
  ```json
  {
    "status": "success",
    "text": "从图像中提取的文本",
    "image_url": "保存的图像URL"
  }
  ```
- **状态码**:
  - `200`: 处理成功
  - `400`: 文件格式不支持
  - `413`: 文件过大
  - `500`: 图像处理失败

### 从图片提取答案

- **URL**: `/image/process-answer`
- **方法**: `POST`
- **描述**: 从错题图像中提取答案文本
- **认证**: 需要Bearer Token
- **请求体**: 表单数据，包含图片文件
  - `file`: 图片文件（multipart/form-data）
- **响应**:
  ```json
  {
    "status": "success",
    "text": "从图像中提取的答案文本",
    "image_url": "保存的图像URL"
  }
  ```
- **状态码**:
  - `200`: 处理成功
  - `400`: 文件格式不支持
  - `413`: 文件过大
  - `500`: 图像处理失败

## API响应格式

### 成功响应

```json
{
  "data": {...},  // 响应数据
  "message": "操作成功"  // 可选
}
```

### 错误响应

```json
{
  "detail": "错误信息",
  "error_code": "ERROR_CODE"  // 可选
}
```

## 状态码说明

- `200 OK`: 请求成功
- `400 Bad Request`: 请求参数有误
- `401 Unauthorized`: 未授权（未登录或Token无效）
- `403 Forbidden`: 无权限访问
- `404 Not Found`: 资源不存在
- `413 Payload Too Large`: 请求体过大（如上传的文件过大）
- `415 Unsupported Media Type`: 不支持的媒体类型
- `422 Unprocessable Entity`: 参数验证失败
- `500 Internal Server Error`: 服务器内部错误
- `503 Service Unavailable`: 服务暂时不可用

## 错误处理

系统使用标准HTTP状态码表示请求处理状态。对于错误情况，API会返回适当的HTTP状态码和详细的错误信息。常见错误处理如下：

### 参数验证错误

```json
{
  "detail": [
    {
      "loc": ["body", "username"],
      "msg": "用户名不能为空",
      "type": "value_error"
    }
  ]
}
```

### 认证错误

```json
{
  "detail": "用户名或密码错误"
}
```

### 资源不存在

```json
{
  "detail": "找不到该错题"
}
```

### 图像处理错误

```json
{
  "detail": "图像处理失败: 图像过大，无法处理",
  "error_code": "IMAGE_SIZE_EXCEEDED"
}
```
