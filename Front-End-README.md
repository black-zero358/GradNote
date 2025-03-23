
# GradNote前端项目技术文档（优化版）

## 目录

1. [项目概述](#1-项目概述)
2. [技术栈](#2-技术栈)
3. [项目结构](#3-项目结构)
4. [开发环境](#4-开发环境)
5. [组件设计](#5-组件设计)
6. [数据流管理](#6-数据流管理)
7. [路由设计](#7-路由设计)
8. [UI设计与响应式策略](#8-ui设计与响应式策略)
9. [认证与安全](#9-认证与安全)
10. [错误处理](#10-错误处理)
11. [测试策略](#11-测试策略)
12. [性能优化](#12-性能优化)
13. [部署流程](#13-部署流程)
14. [开发规范](#14-开发规范)

## 1. 项目概述

GradNote是一个错题知识点管理系统，通过智能技术帮助学习者分析错题并提取相关知识点。

### 核心功能

- 错题提交与管理
- 自动知识点提取与匹配
- 知识点标记与统计
- 解题过程分析
- 学习数据可视化

> **技术价值**：系统整合了现代前端技术与智能分析，提供流畅的用户体验与精准的学习反馈。

## 2. 技术栈

| 类别 | 技术 | 版本 | 用途 |
|------|------|------|------|
| **核心框架** | React | 18 | UI构建基础库 |
|  | Next.js | 14 (App Router) | SSR, 路由, API |
| **UI与样式** | Tailwind CSS | 3.x | 原子化CSS |
|  | Ant Design | 5.x | 数据可视化组件 |
| **表单与文件** | React Hook Form | 7.x | 表单处理 |
|  | React-Dropzone | 14.x | 文件上传 |
| **状态管理** | React Context | - | 轻量级状态共享 |
|  | Zustand | 4.x | 状态管理 |
| **数据获取** | React Query | 4.x | 服务端状态管理 |
|  | Axios | 1.x | HTTP客户端 |
| **开发工具** | TypeScript | 5.x | 静态类型检查 |

### 技术选择理由

- **Next.js App Router**: 提供更好的SEO支持和性能优化
- **Zustand**: 相比Redux更轻量且简洁，学习曲线平缓
- **React Query**: 简化数据获取和缓存管理，减少模板代码

## 3. 项目结构

```
/
├── app/                      # Next.js App Router
│   ├── layout.tsx            # 根布局组件
│   ├── page.tsx              # 首页
│   ├── (auth)/               # 认证相关路由组
│   ├── (dashboard)/          # 主功能路由组
│   └── api/                  # API路由
├── components/               # 共享组件
│   ├── ui/                   # UI基础组件
│   ├── forms/                # 表单相关组件
│   ├── questions/            # 错题相关组件
│   ├── knowledge/            # 知识点相关组件
│   └── layout/               # 布局组件
├── lib/                      # 工具函数和库
│   ├── api/                  # API集成
│   ├── hooks/                # 自定义Hooks
│   ├── store/                # 状态管理
│   └── utils/                # 工具函数
└── public/                   # 静态资源
```

> **最佳实践**：按功能域而非技术类型组织文件，提高相关代码的内聚性。

## 4. 开发环境

### 快速启动

```bash
# 创建项目
npx create-next-app@latest gradnote --typescript --eslint --tailwind --app

# 安装依赖
npm install antd @ant-design/charts react-hook-form react-dropzone zustand @tanstack/react-query axios
```

### API类型生成

在`package.json`中添加:

```json
"scripts": {
  // ...其他脚本
  "generate-api": "openapi --input http://localhost:8000/openapi.json --output lib/api/generated --client axios"
}
```

> **提示**：首次设置完成后，每当后端API变更时运行`npm run generate-api`更新类型定义。

## 5. 组件设计

### 核心组件架构

![组件架构](https://placeholder-for-component-architecture.png)

### 关键组件示例

#### 错题提交组件

```tsx
// components/questions/QuestionForm.tsx
import { useForm } from 'react-hook-form';
import { useDropzone } from 'react-dropzone';
import { useSubmitQuestion } from '@/lib/hooks/useQuestions';

export function QuestionForm() {
  const { register, handleSubmit } = useForm();
  const { mutate, isLoading } = useSubmitQuestion();
  const { getRootProps, getInputProps } = useDropzone({
    accept: {'image/*': []},
    // ...配置
  });
  
  // 处理逻辑...
  
  return (
    <form onSubmit={handleSubmit(onSubmit)}>
      {/* 表单字段 */}
      <div {...getRootProps()} className="border-2 border-dashed p-4">
        <input {...getInputProps()} />
        <p>拖放题目图片或点击上传</p>
      </div>
      <button type="submit" disabled={isLoading}>
        {isLoading ? '提交中...' : '提交错题'}
      </button>
    </form>
  );
}
```

#### 组件设计原则

- **单一职责**：每个组件专注于特定功能
- **组合优先**：通过组合而非继承扩展功能
- **状态下移**：将状态尽可能保持在低层级组件中
- **声明式设计**：使用hooks封装业务逻辑

### 章节要点

- ✅ 采用组件化设计提高代码复用性
- ✅ 使用自定义hooks分离业务逻辑和UI
- ✅ 组件保持低耦合、高内聚的设计原则

## 6. 数据流管理

### 状态管理

#### Zustand状态存储

```tsx
// lib/store/authStore.ts
import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface AuthState {
  token: string | null;
  user: User | null;
  isAuthenticated: boolean;
  login: (token: string, user: User) => void;
  logout: () => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      token: null,
      user: null,
      isAuthenticated: false,
      login: (token, user) => set({ token, user, isAuthenticated: true }),
      logout: () => set({ token: null, user: null, isAuthenticated: false }),
    }),
    { name: 'auth-storage' }
  )
);
```

### API集成

#### React Query数据获取

```tsx
// lib/hooks/useQuestions.ts
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { QuestionsService } from '@/lib/api/generated';

export function useQuestions(skip = 0, limit = 10) {
  return useQuery(['questions', skip, limit], () => 
    QuestionsService.getQuestions(skip, limit)
  );
}

export function useSubmitQuestion() {
  const queryClient = useQueryClient();
  
  return useMutation(
    (data) => QuestionsService.createQuestion(data),
    {
      onSuccess: () => {
        queryClient.invalidateQueries(['questions']);
      },
    }
  );
}
```

### 数据流向图

![数据流向图](https://placeholder-for-data-flow.png)

> **最佳实践**：使用React Query管理服务端状态，Zustand管理客户端状态，明确分离关注点。

### 章节要点

- ✅ API接口自动生成TypeScript类型，确保类型安全
- ✅ 服务端状态与客户端状态分离管理
- ✅ 缓存策略优化数据加载性能

## 7. 路由设计

### Next.js App Router结构

| 路由路径 | 组件文件 | 功能描述 |
|---------|---------|---------|
| `/` | app/page.tsx | 首页 |
| `/login` | app/(auth)/login/page.tsx | 登录页 |
| `/register` | app/(auth)/register/page.tsx | 注册页 |
| `/questions` | app/(dashboard)/questions/page.tsx | 错题列表 |
| `/questions/[id]` | app/(dashboard)/questions/[id]/page.tsx | 错题详情 |
| `/knowledge` | app/(dashboard)/knowledge/page.tsx | 知识点管理 |

### 布局组件

```tsx
// app/(dashboard)/layout.tsx
import { Sidebar } from '@/components/layout/Sidebar';
import { Header } from '@/components/layout/Header';

export default function DashboardLayout({ children }) {
  return (
    <div className="flex h-screen">
      <Sidebar />
      <div className="flex-1 flex flex-col">
        <Header />
        <main className="flex-1 overflow-y-auto p-4">
          {children}
        </main>
      </div>
    </div>
  );
}
```

> **注意**：路由组结构(`auth`, `dashboard`)用于共享布局而不影响URL路径。

### 章节要点

- ✅ 使用App Router提供更好的布局嵌套和加载状态
- ✅ 采用路由组隔离不同功能区域
- ✅ 页面组件专注于数据获取和展示

## 8. UI设计与响应式策略

### 样式方案

#### Tailwind实用工具类

```css
/* styles/globals.css */
@tailwind base;
@tailwind components;
@tailwind utilities;

@layer components {
  .card {
    @apply bg-white rounded-lg shadow p-4;
  }
  
  .btn-primary {
    @apply px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 
    focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2;
  }
}
```

### 响应式设计

#### 断点配置

```js
// tailwind.config.js
module.exports = {
  theme: {
    extend: {
      screens: {
        'xs': '480px',    // 小型手机
        'sm': '640px',    // 大型手机
        'md': '768px',    // 平板
        'lg': '1024px',   // 笔记本
        'xl': '1280px',   // 桌面
      },
    }
  },
}
```

#### 响应式组件示例

```tsx
// components/layout/ResponsiveSidebar.tsx
'use client';

import { useState } from 'react';
import { useBreakpoint } from '@/lib/hooks/useBreakpoint';

export function ResponsiveSidebar() {
  const [isOpen, setIsOpen] = useState(false);
  const breakpoint = useBreakpoint();
  const isMobile = ['xs', 'sm'].includes(breakpoint);
  
  // 根据断点渲染不同的侧边栏
  return isMobile ? (
    <MobileSidebar isOpen={isOpen} onToggle={() => setIsOpen(!isOpen)} />
  ) : (
    <DesktopSidebar />
  );
}
```

### 移动端优化

- **触摸友好设计**：所有交互元素最小44x44px
- **自适应布局**：从卡片视图到表格视图的响应式转换
- **安全区域适配**：使用`env(safe-area-inset-*)`确保全面屏设备显示正常

> **设计原则**：始终采用移动优先的设计方法，再向上扩展到桌面视图。

### 章节要点

- ✅ Tailwind提供一致的设计系统和原子化CSS
- ✅ 响应式设计确保跨设备良好体验
- ✅ 触摸优化改善移动端用户交互

## 9. 认证与安全

### 认证流程

![认证流程图](https://placeholder-for-auth-flow.png)

### 路由保护

```tsx
// middleware.ts
import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

export function middleware(request: NextRequest) {
  const token = request.cookies.get('auth-token')?.value;
  const isAuthRoute = request.nextUrl.pathname.startsWith('/(auth)');
  const isDashboardRoute = request.nextUrl.pathname.startsWith('/(dashboard)');
  
  // 未登录用户访问仪表盘，重定向到登录页
  if (isDashboardRoute && !token) {
    const loginUrl = new URL('/login', request.url);
    return NextResponse.redirect(loginUrl);
  }
  
  // 已登录用户访问登录/注册页，重定向到仪表盘
  if (isAuthRoute && token) {
    return NextResponse.redirect(new URL('/questions', request.url));
  }
  
  return NextResponse.next();
}
```

### 客户端权限控制

```tsx
// components/AuthGuard.tsx
'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuthStore } from '@/lib/store/authStore';

export function AuthGuard({ children }) {
  const isAuthenticated = useAuthStore(state => state.isAuthenticated);
  const router = useRouter();
  
  useEffect(() => {
    if (!isAuthenticated) {
      router.push('/login');
    }
  }, [isAuthenticated, router]);
  
  return isAuthenticated ? <>{children}</> : <Loading />;
}
```

> **安全提示**：同时在中间件和客户端实现认证检查，确保双重保护。

### 章节要点

- ✅ 完整的认证流程保护敏感数据
- ✅ 使用中间件实现路由级别保护
- ✅ 客户端组件提供额外的权限控制层

## 10. 错误处理

### 错误边界

```tsx
// components/ErrorBoundary.tsx
'use client';

import { Component, ErrorInfo, ReactNode } from 'react';

interface Props {
  fallback: ReactNode;
  children: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

export class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false, error: null };
  }
  
  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }
  
  componentDidCatch(error: Error, errorInfo: ErrorInfo): void {
    console.error('错误边界捕获错误:', error, errorInfo);
    // 错误日志上报
  }
  
  render(): ReactNode {
    if (this.state.hasError) {
      return this.props.fallback;
    }
    
    return this.props.children;
  }
}
```

### API错误处理

```tsx
// lib/hooks/useApiError.ts
import { useState, useCallback } from 'react';
import { AxiosError } from 'axios';

export function useApiError() {
  const [error, setError] = useState(null);
  
  const handleError = useCallback((err) => {
    if (err instanceof AxiosError) {
      // 处理不同类型的API错误
      // ...
    } else {
      setError({ message: '发生未知错误' });
    }
  }, []);
  
  return { error, handleError, clearError: () => setError(null) };
}
```

### 错误处理策略

| 错误类型 | 处理方式 | 用户体验 |
|---------|---------|---------|
| 网络错误 | 自动重试 + 用户通知 | 显示重试按钮 |
| 认证错误 | 重定向到登录页 | 保存当前页面状态 |
| 表单错误 | 内联显示错误信息 | 高亮错误字段 |
| 服务端错误 | 错误边界捕获 | 显示友好错误页面 |

> **最佳实践**：错误消息应当清晰明了，并提供恢复建议。

### 章节要点

- ✅ 全面的错误处理确保良好用户体验
- ✅ 区分不同类型错误并采取相应对策
- ✅ 使用错误边界防止整个应用崩溃

## 11. 测试策略

### 测试配置

```json
// package.json测试配置
{
  "scripts": {
    "test": "jest",
    "test:watch": "jest --watch",
    "test:coverage": "jest --coverage"
  }
}
```

### 测试类型与示例

#### 组件测试

```tsx
// Button.test.tsx
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { Button } from './Button';

describe('Button组件', () => {
  test('渲染按钮文本', () => {
    render(<Button>测试按钮</Button>);
    expect(screen.getByText('测试按钮')).toBeInTheDocument();
  });
  
  test('点击按钮触发onClick事件', async () => {
    const handleClick = jest.fn();
    render(<Button onClick={handleClick}>点击我</Button>);
    
    await userEvent.click(screen.getByText('点击我'));
    expect(handleClick).toHaveBeenCalledTimes(1);
  });
});
```

#### API调用测试

```tsx
// knowledge.test.ts
import { searchKnowledgePoints } from './knowledge';
import apiClient from './client';

jest.mock('./client');

describe('知识点API', () => {
  test('searchKnowledgePoints发送正确的请求', async () => {
    // 测试代码...
  });
});
```

### 测试覆盖目标

| 层级 | 覆盖率目标 | 重点测试内容 |
|------|----------|------------|
| 组件 | 80% | 交互事件、UI状态变化 |
| Hooks | 90% | 业务逻辑、状态变更 |
| 工具函数 | 95% | 边界条件、异常处理 |

> **提示**：优先测试核心业务逻辑和高风险代码路径。

### 章节要点

- ✅ 单元测试确保组件和功能的正确性
- ✅ 模拟API调用测试数据流
- ✅ 覆盖关键业务逻辑和用户交互流程

## 12. 性能优化

### 代码分割

```tsx
// 使用动态导入延迟加载大型组件
import dynamic from 'next/dynamic';

const KnowledgeChart = dynamic(
  () => import('@/components/charts/KnowledgeChart').then(mod => mod.KnowledgeChart),
  { loading: () => <p>加载图表中...</p> }
);
```

### 图像优化

```tsx
import Image from 'next/image';

export function QuestionImage({ src, alt }) {
  return (
    <div className="relative h-48 w-full">
      <Image
        src={src}
        alt={alt}
        fill
        sizes="(max-width: 768px) 100vw, 50vw"
        className="object-contain"
      />
    </div>
  );
}
```

### 缓存策略

```tsx
// 配置React Query缓存
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 60 * 1000, // 1分钟
      cacheTime: 5 * 60 * 1000, // 5分钟
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
});
```

### 性能监控

```tsx
// lib/utils/vitals.ts
const reportWebVitals = (metric) => {
  // 发送性能指标到分析服务
  console.log(metric);
  // ...
};

export default reportWebVitals;
```

> **性能目标**：首屏加载时间(FCP) < 1.2秒，交互延迟(FID) < 100ms。

### 章节要点

- ✅ 懒加载优化初始加载体验
- ✅ 图像优化减少网络负载
- ✅ 缓存策略减少不必要的请求
- ✅ 性能监控及时发现问题

## 13. 部署流程

### 生产构建步骤

```bash
# 生成API类型
npm run generate-api

# 构建生产版本
npm run build

# 启动生产服务器
npm run start
```

### 容器化部署

```dockerfile
# Dockerfile
FROM node:18-alpine AS base

FROM base AS deps
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci

FROM base AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
RUN npm run build

FROM base AS runner
WORKDIR /app
ENV NODE_ENV production
COPY --from=builder /app/public ./public
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static

EXPOSE 3000
CMD ["node", "server.js"]
```

### 环境配置

- 开发环境：`.env.development`
- 测试环境：`.env.test`
- 生产环境：`.env.production`

> **部署检查清单**：确保环境变量、缓存配置、CDN设置和安全头部都已正确配置。

### 章节要点

- ✅ 标准化的构建流程确保一致性
- ✅ 容器化简化部署和扩展
- ✅ 环境变量分离不同环境配置

## 14. 开发规范

### 代码风格

- ESLint + Prettier保持统一风格
- TypeScript严格模式确保类型安全
- 命名约定：
  - 组件：PascalCase
  - 函数/变量：camelCase
  - 常量：UPPER_SNAKE_CASE

### 提交规范

使用约定式提交(Conventional Commits):
```
feat: 添加知识点标记功能
fix: 修复错题列表分页问题
docs: 更新文档
```

### 团队协作流程

![开发流程图](https://placeholder-for-dev-workflow.png)

> **协作提示**：创建新功能时先创建功能分支，完成后提交PR进行代码审查。

### 章节要点

- ✅ 统一的代码和提交规范提高可维护性
- ✅ 明确的分支管理策略简化团队协作
- ✅ 代码审查确保代码质量

---

## 总结

本文档提供了GradNote前端项目的技术架构和实现方案，涵盖了从项目结构到部署的完整开发流程。开发团队应遵循本文档的规范和最佳实践，确保项目的一致性和质量。

### 技术栈亮点

- Next.js 14 App Router提供优化的服务端渲染和路由
- Zustand + React Query实现高效状态管理
- Tailwind CSS实现响应式设计
- TypeScript确保类型安全
