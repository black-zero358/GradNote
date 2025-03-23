# GradNote前端项目技术文档

## 1. 项目概述

GradNote是一个错题知识点管理系统，旨在帮助学习者管理错题并自动提取相关知识点。系统通过LLM和VLM技术分析错题内容，提取知识点，并提供数据分析功能，帮助用户了解自己的学习情况。

### 核心功能
- 错题提交与管理
- 自动知识点提取与匹配
- 知识点标记与统计
- 解题过程分析
- 学习情况数据分析

## 2. 技术栈详解

### 核心框架
- **React 18**: UI构建的基础库
- **Next.js 14**: 采用App Router架构，提供服务端渲染、路由、API路由等功能

### UI与样式
- **Tailwind CSS**: 原子化CSS框架，用于构建响应式界面
- **Ant Design**: 用于数据可视化和复杂UI组件

### 表单与文件处理
- **React Hook Form**: 高性能表单处理库
- **React-Dropzone**: 文件上传组件，支持拖放功能

### 状态管理
- **React Context**: 轻量级状态共享
- **Zustand**: 简洁高效的状态管理库

### 数据获取
- **React Query**: 用于服务端状态管理、缓存和同步
- **Axios**: HTTP客户端，与后端API交互

### 开发工具
- **TypeScript**: 静态类型检查
- **openapi-typescript-codegen**: 自动从FastAPI生成TypeScript类型定义

## 3. 项目结构

```
/
├── app/                      # Next.js App Router
│   ├── layout.tsx            # 根布局组件
│   ├── page.tsx              # 首页
│   ├── (auth)/               # 认证相关路由组
│   │   ├── login/
│   │   └── register/
│   ├── (dashboard)/          # 主功能路由组
│   │   ├── layout.tsx        # 仪表盘布局
│   │   ├── questions/        # 错题相关页面
│   │   └── knowledge/        # 知识点相关页面
│   └── api/                  # API路由
├── components/               # 共享组件
│   ├── ui/                   # UI基础组件
│   ├── forms/                # 表单相关组件
│   ├── questions/            # 错题相关组件
│   ├── knowledge/            # 知识点相关组件
│   ├── charts/               # 图表相关组件
│   └── layout/               # 布局组件
├── lib/                      # 工具函数和库
│   ├── api/                  # API集成
│   │   ├── generated/        # 自动生成的API类型和函数
│   │   └── client.ts         # API客户端配置
│   ├── hooks/                # 自定义Hooks
│   ├── store/                # Zustand状态管理
│   └── utils/                # 工具函数
├── public/                   # 静态资源
├── styles/                   # 全局样式
│   └── globals.css           # 全局CSS
├── types/                    # 类型定义
├── next.config.js            # Next.js配置
├── tailwind.config.js        # Tailwind配置
├── tsconfig.json             # TypeScript配置
└── package.json              # 项目依赖和脚本
```

## 4. 开发环境搭建

### 项目初始化
```bash
# 创建Next.js项目
npx create-next-app@latest gradnote --typescript --eslint --tailwind --app

# 安装依赖
npm install antd @ant-design/charts react-hook-form react-dropzone zustand @tanstack/react-query axios
npm install --save-dev openapi-typescript-codegen
```

### 配置OpenAPI生成工具
在`package.json`中添加脚本:
```json
"scripts": {
  "dev": "next dev",
  "build": "next build",
  "start": "next start",
  "lint": "next lint",
  "generate-api": "openapi --input http://localhost:8000/openapi.json --output lib/api/generated --client axios"
}
```

### 配置Tailwind CSS
`tailwind.config.js`:
```javascript
module.exports = {
  content: [
    './app/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}'
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#f0f9ff',
          100: '#e0f2fe',
          // ...其他shade
          600: '#0284c7',
          700: '#0369a1'
        }
      }
    }
  },
  plugins: [],
}
```

## 5. 组件设计

### 核心组件结构

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
    onDrop: files => handleImageDrop(files)
  });
  
  // 处理逻辑...
  
  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
      {/* 表单字段 */}
      <div {...getRootProps()} className="border-2 border-dashed p-4 rounded-md">
        <input {...getInputProps()} />
        <p>拖放题目图片或点击上传</p>
      </div>
      <button type="submit" disabled={isLoading} className="btn-primary">
        {isLoading ? '提交中...' : '提交错题'}
      </button>
    </form>
  );
}
```

#### 知识点展示组件
```tsx
// components/knowledge/KnowledgePointList.tsx
import { KnowledgePoint } from '@/lib/api/generated';

interface KnowledgePointListProps {
  knowledgePoints: KnowledgePoint[];
  onMarkPoint: (pointId: number) => void;
}

export function KnowledgePointList({ knowledgePoints, onMarkPoint }: KnowledgePointListProps) {
  return (
    <div className="space-y-2">
      <h3 className="text-lg font-medium">相关知识点</h3>
      <ul className="divide-y">
        {knowledgePoints.map(point => (
          <li key={point.id} className="py-2">
            <div className="flex justify-between">
              <div>
                <p className="font-medium">{point.item}</p>
                <p className="text-sm text-gray-500">
                  {point.subject} &gt; {point.chapter} &gt; {point.section}
                </p>
                <p>{point.details}</p>
              </div>
              <button 
                onClick={() => onMarkPoint(point.id)}
                className="px-3 py-1 bg-blue-500 text-white rounded"
              >
                标记
              </button>
            </div>
          </li>
        ))}
      </ul>
    </div>
  );
}
```

#### 数据分析图表组件
```tsx
// components/charts/KnowledgeDistribution.tsx
import { Pie } from '@ant-design/charts';
import { useKnowledgeStats } from '@/lib/hooks/useAnalytics';

export function KnowledgeDistribution() {
  const { data, isLoading } = useKnowledgeStats();
  
  if (isLoading) return <div>加载中...</div>;
  
  const config = {
    data: data?.chapters || [],
    angleField: 'count',
    colorField: 'name',
    radius: 0.8,
    label: {
      type: 'outer',
      content: '{name}: {percentage}',
    },
    // 其他配置...
  };
  
  return (
    <div className="bg-white p-4 rounded-lg shadow">
      <h3 className="text-lg font-medium mb-4">知识点分布</h3>
      <Pie {...config} />
    </div>
  );
}
```

## 6. 状态管理

### Zustand状态管理
```typescript
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

### React Query数据获取
```typescript
// lib/hooks/useQuestions.ts
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { QuestionsService, CreateQuestionRequest } from '@/lib/api/generated';

export function useQuestions(skip = 0, limit = 10) {
  return useQuery(['questions', skip, limit], () => 
    QuestionsService.getQuestions(skip, limit)
  );
}

export function useSubmitQuestion() {
  const queryClient = useQueryClient();
  
  return useMutation(
    (data: CreateQuestionRequest) => QuestionsService.createQuestion(data),
    {
      onSuccess: () => {
        queryClient.invalidateQueries(['questions']);
      },
    }
  );
}
```

## 7. API集成

### Axios客户端配置
```typescript
// lib/api/client.ts
import axios from 'axios';
import { useAuthStore } from '@/lib/store/authStore';

const apiClient = axios.create({
  baseURL: '/api/v1',
  headers: {
    'Content-Type': 'application/json',
  },
});

apiClient.interceptors.request.use((config) => {
  const token = useAuthStore.getState().token;
  
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  
  return config;
});

export default apiClient;
```

### API封装示例
```typescript
// lib/api/knowledge.ts
import apiClient from './client';
import { KnowledgePoint } from './generated';

export const searchKnowledgePoints = async (
  subject?: string,
  chapter?: string,
  section?: string,
  item?: string
) => {
  const params = { subject, chapter, section, item };
  const response = await apiClient.get('/knowledge/search', { params });
  return response.data as KnowledgePoint[];
};

export const markKnowledgePoint = async (knowledgePointId: number, questionId: number) => {
  const response = await apiClient.post('/knowledge/user-mark', {
    knowledge_point_id: knowledgePointId,
    question_id: questionId
  });
  return response.data;
};
```

## 8. 路由设计

### App Router页面结构
```tsx
// app/page.tsx - 主页
export default function Home() {
  return (
    <main>
      <h1 className="text-3xl font-bold">GradNote</h1>
      <p>管理你的错题和知识点</p>
      {/* 主页内容 */}
    </main>
  );
}

// app/(dashboard)/questions/page.tsx - 错题列表页
import { QuestionsTable } from '@/components/questions/QuestionsTable';

export default function QuestionsPage() {
  return (
    <div>
      <h1 className="text-2xl font-bold mb-4">错题列表</h1>
      <QuestionsTable />
    </div>
  );
}

// app/(dashboard)/questions/[id]/page.tsx - 错题详情页
import { QuestionDetails } from '@/components/questions/QuestionDetails';

export default function QuestionDetailPage({ params }: { params: { id: string } }) {
  return <QuestionDetails questionId={parseInt(params.id)} />;
}
```

### 布局组件
```tsx
// app/layout.tsx - 根布局
import '@/styles/globals.css';
import { Inter } from 'next/font/google';
import { Providers } from '@/components/Providers';

const inter = Inter({ subsets: ['latin'] });

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="zh-CN">
      <body className={inter.className}>
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}

// app/(dashboard)/layout.tsx - 仪表盘布局
import { Sidebar } from '@/components/layout/Sidebar';
import { Header } from '@/components/layout/Header';

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex h-screen">
      <Sidebar />
      <div className="flex-1 flex flex-col overflow-hidden">
        <Header />
        <main className="flex-1 overflow-y-auto p-4">{children}</main>
      </div>
    </div>
  );
}
```

## 9. 样式方案

### Tailwind与Ant Design集成
```tsx
// components/ui/Button.tsx - Tailwind风格按钮
interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'outline';
  size?: 'sm' | 'md' | 'lg';
}

export function Button({ 
  variant = 'primary', 
  size = 'md', 
  className, 
  children, 
  ...props 
}: ButtonProps) {
  const baseStyles = "font-medium rounded focus:outline-none";
  
  const variantStyles = {
    primary: "bg-primary-600 text-white hover:bg-primary-700",
    secondary: "bg-gray-200 text-gray-800 hover:bg-gray-300",
    outline: "border border-gray-300 text-gray-700 hover:bg-gray-50"
  };
  
  const sizeStyles = {
    sm: "px-2 py-1 text-sm",
    md: "px-4 py-2",
    lg: "px-6 py-3 text-lg"
  };
  
  return (
    <button
      className={`${baseStyles} ${variantStyles[variant]} ${sizeStyles[size]} ${className}`}
      {...props}
    >
      {children}
    </button>
  );
}
```

### 全局样式设置
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
  
  .input-field {
    @apply px-3 py-2 border border-gray-300 rounded-md focus:outline-none
    focus:ring-2 focus:ring-blue-500 focus:border-blue-500;
  }
}
```

## 10. 部署流程

### 生产构建
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
ENV PORT 3000

CMD ["node", "server.js"]
```

### 环境变量配置
创建`.env.local`文件:
```
NEXT_PUBLIC_API_URL=https://api.example.com
NEXT_PUBLIC_SITE_URL=https://example.com
```

## 11. 开发规范

### 代码风格
- 使用ESLint和Prettier保持代码风格一致
- 遵循TypeScript类型安全原则
- 使用函数组件和React Hooks
- 采用命名约定：
  - 组件使用PascalCase
  - 函数和变量使用camelCase
  - 常量使用UPPER_SNAKE_CASE

### 组件设计原则
- 遵循单一职责原则
- 避免过度抽象
- 使用组合而非继承
- 保持组件纯粹，将副作用放在hooks中

### 提交规范
使用约定式提交(Conventional Commits):
```
feat: 添加知识点标记功能
fix: 修复错题列表分页问题
docs: 更新README文档
style: 改进UI样式
refactor: 重构认证逻辑
```

## 12. 性能优化

### 图像优化
使用Next.js的Image组件优化图像:
```tsx
import Image from 'next/image';

export function QuestionImage({ src, alt }: { src: string, alt: string }) {
  return (
    <div className="relative h-48 w-full">
      <Image
        src={src}
        alt={alt}
        fill
        sizes="(max-width: 768px) 100vw, (max-width: 1200px) 50vw, 33vw"
        className="object-contain"
      />
    </div>
  );
}
```

### 代码分割
利用Next.js的动态导入:
```tsx
import dynamic from 'next/dynamic';

const KnowledgeChart = dynamic(
  () => import('@/components/charts/KnowledgeChart').then(mod => mod.KnowledgeChart),
  { 
    loading: () => <p>加载图表中...</p>,
    ssr: false // 客户端渲染复杂图表
  }
);
```

### React查询优化
配置React Query以优化数据获取:
```tsx
// components/Providers.tsx
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';

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

export function Providers({ children }: { children: React.ReactNode }) {
  return (
    <QueryClientProvider client={queryClient}>
      {children}
      {process.env.NODE_ENV === 'development' && <ReactQueryDevtools />}
    </QueryClientProvider>
  );
}
```

## 13. 认证机制与路由保护

### 认证中间件
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
    loginUrl.searchParams.set('from', request.nextUrl.pathname);
    return NextResponse.redirect(loginUrl);
  }
  
  // 已登录用户访问登录/注册页，重定向到仪表盘
  if (isAuthRoute && token) {
    return NextResponse.redirect(new URL('/questions', request.url));
  }
  
  return NextResponse.next();
}

// 指定匹配的路由
export const config = {
  matcher: ['/(dashboard)/:path*', '/(auth)/:path*'],
};
```

### 客户端路由保护
```tsx
// components/AuthGuard.tsx
'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuthStore } from '@/lib/store/authStore';

interface AuthGuardProps {
  children: React.ReactNode;
}

export function AuthGuard({ children }: AuthGuardProps) {
  const isAuthenticated = useAuthStore(state => state.isAuthenticated);
  const router = useRouter();
  
  useEffect(() => {
    if (!isAuthenticated) {
      router.push('/login');
    }
  }, [isAuthenticated, router]);
  
  if (!isAuthenticated) {
    return <div className="flex justify-center items-center h-screen">正在验证身份...</div>;
  }
  
  return <>{children}</>;
}
```

### 布局组件中集成认证保护
```tsx
// app/(dashboard)/layout.tsx - 添加路由保护
import { Sidebar } from '@/components/layout/Sidebar';
import { Header } from '@/components/layout/Header';
import { AuthGuard } from '@/components/AuthGuard';

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  return (
    <AuthGuard>
      <div className="flex h-screen">
        <Sidebar />
        <div className="flex-1 flex flex-col overflow-hidden">
          <Header />
          <main className="flex-1 overflow-y-auto p-4">{children}</main>
        </div>
      </div>
    </AuthGuard>
  );
}
```

## 14. 错误处理

### 错误边界组件
```tsx
// components/ErrorBoundary.tsx
'use client';

import { Component, ErrorInfo, ReactNode } from 'react';

interface ErrorBoundaryProps {
  fallback: ReactNode;
  children: ReactNode;
}

interface ErrorBoundaryState {
  hasError: boolean;
  error: Error | null;
}

export class ErrorBoundary extends Component<ErrorBoundaryProps, ErrorBoundaryState> {
  constructor(props: ErrorBoundaryProps) {
    super(props);
    this.state = { hasError: false, error: null };
  }
  
  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return { hasError: true, error };
  }
  
  componentDidCatch(error: Error, errorInfo: ErrorInfo): void {
    console.error('错误边界捕获到错误:', error, errorInfo);
    // 此处可以添加错误日志上报逻辑
  }
  
  render(): ReactNode {
    if (this.state.hasError) {
      return this.props.fallback;
    }
    
    return this.props.children;
  }
}
```

### 通用错误提示组件
```tsx
// components/ui/ErrorMessage.tsx
interface ErrorMessageProps {
  message: string;
  className?: string;
}

export function ErrorMessage({ message, className = '' }: ErrorMessageProps) {
  if (!message) return null;
  
  return (
    <div className={`bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded text-sm ${className}`}>
      {message}
    </div>
  );
}
```

### API错误处理Hook
```tsx
// lib/hooks/useApiError.ts
import { useState, useCallback } from 'react';
import { AxiosError } from 'axios';

interface ApiError {
  message: string;
  field?: string;
}

export function useApiError() {
  const [error, setError] = useState<ApiError | null>(null);
  
  const handleError = useCallback((err: unknown) => {
    if (err instanceof AxiosError) {
      const responseData = err.response?.data;
      
      if (responseData?.detail) {
        // FastAPI错误格式
        setError({ 
          message: typeof responseData.detail === 'string' 
            ? responseData.detail 
            : '请求失败，请稍后重试' 
        });
      } else if (responseData?.message) {
        // 自定义错误格式
        setError({ 
          message: responseData.message,
          field: responseData.field 
        });
      } else {
        // 默认错误信息
        setError({ message: '网络错误，请检查网络连接' });
      }
    } else if (err instanceof Error) {
      setError({ message: err.message });
    } else {
      setError({ message: '发生未知错误' });
    }
  }, []);
  
  const clearError = useCallback(() => {
    setError(null);
  }, []);
  
  return { error, handleError, clearError };
}
```

### 与React Query集成
```tsx
// lib/hooks/useQuestions.ts - 改进版本
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { QuestionsService, CreateQuestionRequest } from '@/lib/api/generated';
import { useApiError } from './useApiError';

export function useSubmitQuestion() {
  const queryClient = useQueryClient();
  const { handleError } = useApiError();
  
  return useMutation({
    mutationFn: (data: CreateQuestionRequest) => QuestionsService.createQuestion(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['questions'] });
    },
    onError: (error) => {
      handleError(error);
    }
  });
}
```

## 15. 测试策略

### Jest与React Testing Library配置
在`package.json`中添加测试依赖和脚本:
```json
{
  "scripts": {
    "test": "jest",
    "test:watch": "jest --watch",
    "test:coverage": "jest --coverage"
  },
  "devDependencies": {
    "@testing-library/jest-dom": "^6.1.0",
    "@testing-library/react": "^14.0.0",
    "@testing-library/user-event": "^14.0.0",
    "jest": "^29.6.0",
    "jest-environment-jsdom": "^29.6.0",
    "@types/jest": "^29.5.0"
  }
}
```

配置Jest:
```javascript
// jest.config.js
const nextJest = require('next/jest');

const createJestConfig = nextJest({
  dir: './',
});

const customJestConfig = {
  setupFilesAfterEnv: ['<rootDir>/jest.setup.js'],
  testEnvironment: 'jest-environment-jsdom',
  moduleNameMapper: {
    '^@/(.*)$': '<rootDir>/$1',
  },
  collectCoverageFrom: [
    'app/**/*.{js,jsx,ts,tsx}',
    'components/**/*.{js,jsx,ts,tsx}',
    'lib/**/*.{js,jsx,ts,tsx}',
    '!**/*.d.ts',
    '!**/node_modules/**',
  ],
};

module.exports = createJestConfig(customJestConfig);
```

设置Jest:
```javascript
// jest.setup.js
import '@testing-library/jest-dom';
```

### 组件单元测试示例
```tsx
// components/ui/Button.test.tsx
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
  
  test('禁用状态下按钮不可点击', async () => {
    const handleClick = jest.fn();
    render(<Button disabled onClick={handleClick}>禁用按钮</Button>);
    
    await userEvent.click(screen.getByText('禁用按钮'));
    expect(handleClick).not.toHaveBeenCalled();
  });
  
  test('应用正确的样式类', () => {
    const { rerender } = render(<Button variant="primary">主要按钮</Button>);
    expect(screen.getByText('主要按钮')).toHaveClass('bg-primary-600');
    
    rerender(<Button variant="secondary">次要按钮</Button>);
    expect(screen.getByText('次要按钮')).toHaveClass('bg-gray-200');
    
    rerender(<Button variant="outline">轮廓按钮</Button>);
    expect(screen.getByText('轮廓按钮')).toHaveClass('border-gray-300');
  });
});
```

### API调用测试示例
```tsx
// lib/api/knowledge.test.ts
import { searchKnowledgePoints, markKnowledgePoint } from './knowledge';
import apiClient from './client';

// 模拟apiClient
jest.mock('./client', () => ({
  get: jest.fn(),
  post: jest.fn(),
}));

describe('知识点API', () => {
  afterEach(() => {
    jest.clearAllMocks();
  });
  
  test('searchKnowledgePoints发送正确的请求', async () => {
    const mockResponse = { data: [{ id: 1, item: '测试知识点' }] };
    (apiClient.get as jest.Mock).mockResolvedValueOnce(mockResponse);
    
    await searchKnowledgePoints('数学', '函数', '导数');
    
    expect(apiClient.get).toHaveBeenCalledWith('/knowledge/search', {
      params: { subject: '数学', chapter: '函数', section: '导数', item: undefined }
    });
  });
  
  test('markKnowledgePoint发送正确的请求', async () => {
    const mockResponse = { data: { success: true } };
    (apiClient.post as jest.Mock).mockResolvedValueOnce(mockResponse);
    
    await markKnowledgePoint(1, 2);
    
    expect(apiClient.post).toHaveBeenCalledWith('/knowledge/user-mark', {
      knowledge_point_id: 1,
      question_id: 2
    });
  });
});
```

## 16. 性能监控

### Next.js内置性能分析工具
在`next.config.js`中启用分析功能:
```javascript
// next.config.js
const withBundleAnalyzer = require('@next/bundle-analyzer')({
  enabled: process.env.ANALYZE === 'true',
});

/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  // 其他配置...
};

module.exports = withBundleAnalyzer(nextConfig);
```

添加脚本到`package.json`:
```json
"scripts": {
  "analyze": "ANALYZE=true next build",
  "analyze:server": "ANALYZE=true BUNDLE_ANALYZE=server next build",
  "analyze:browser": "ANALYZE=true BUNDLE_ANALYZE=browser next build"
}
```

### Web Vitals监控
```tsx
// lib/utils/vitals.ts
import { CLSMetric, FCPMetric, FIDMetric, LCPMetric, TTFBMetric } from 'web-vitals';

type MetricType = CLSMetric | FCPMetric | FIDMetric | LCPMetric | TTFBMetric;

const reportWebVitals = (metric: MetricType) => {
  // 开发环境下打印到控制台
  if (process.env.NODE_ENV === 'development') {
    console.log(metric);
  }
  
  // 发送到分析服务
  const body = {
    name: metric.name,
    value: metric.value,
    id: metric.id,
    startTime: metric.startTime,
    label: metric.label,
  };
  
  fetch('/api/vitals', {
    method: 'POST',
    body: JSON.stringify(body),
    headers: {
      'Content-Type': 'application/json'
    }
  });
};

export default reportWebVitals;
```

在根布局中添加监控:
```tsx
// app/layout.tsx
import { useReportWebVitals } from 'next/web-vitals';
import reportWebVitals from '@/lib/utils/vitals';

export function RootLayout({ children }: { children: React.ReactNode }) {
  useReportWebVitals(reportWebVitals);
  
  return (
    <html lang="zh-CN">
      <body>
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
```

### 实时监控解决方案
集成Sentry用于错误跟踪和性能监控:

安装Sentry:
```bash
npm install @sentry/nextjs
```

创建Sentry配置文件:
```javascript
// sentry.server.config.js
import * as Sentry from '@sentry/nextjs';

Sentry.init({
  dsn: process.env.SENTRY_DSN,
  tracesSampleRate: 1.0,
  environment: process.env.NODE_ENV
});

// sentry.client.config.js
import * as Sentry from '@sentry/nextjs';

Sentry.init({
  dsn: process.env.SENTRY_DSN,
  tracesSampleRate: 1.0,
  environment: process.env.NODE_ENV
});

// sentry.edge.config.js
import * as Sentry from '@sentry/nextjs';

Sentry.init({
  dsn: process.env.SENTRY_DSN,
  tracesSampleRate: 1.0,
  environment: process.env.NODE_ENV
});
```

修改`next.config.js`以启用Sentry:
```javascript
// next.config.js
const { withSentryConfig } = require('@sentry/nextjs');

/** @type {import('next').NextConfig} */
const nextConfig = {
  // 你的配置...
};

const sentryWebpackPluginOptions = {
  silent: true,
};

module.exports = withSentryConfig(
  nextConfig,
  sentryWebpackPluginOptions
);
```

## 17. 移动端适配

### 响应式设计策略

#### 移动优先设计
基于Tailwind CSS采用移动优先的设计方法:
```tsx
// components/layout/Sidebar.tsx - 响应式侧边栏
'use client';

import { useState } from 'react';
import Link from 'next/link';
import { Menu, X } from 'lucide-react';

export function Sidebar() {
  const [isOpen, setIsOpen] = useState(false);
  
  const toggleSidebar = () => {
    setIsOpen(!isOpen);
  };
  
  return (
    <>
      {/* 移动端菜单按钮 */}
      <button 
        onClick={toggleSidebar}
        className="fixed z-50 bottom-4 right-4 p-3 rounded-full bg-primary-600 text-white shadow-lg md:hidden"
      >
        {isOpen ? <X size={24} /> : <Menu size={24} />}
      </button>
      
      {/* 侧边栏 - 在移动端为抽屉样式，桌面端为固定侧边栏 */}
      <div 
        className={`fixed top-0 left-0 z-40 h-full w-64 bg-white shadow-lg transform transition-transform duration-300 ease-in-out md:relative md:translate-x-0 md:shadow-none
        ${isOpen ? 'translate-x-0' : '-translate-x-full'}`}
      >
        <div className="p-4">
          <h2 className="text-xl font-bold">GradNote</h2>
          <nav className="mt-8">
            <ul className="space-y-2">
              <li>
                <Link href="/questions" 
                  className="block p-2 rounded hover:bg-gray-100"
                  onClick={() => setIsOpen(false)}
                >
                  错题管理
                </Link>
              </li>
              <li>
                <Link href="/knowledge" 
                  className="block p-2 rounded hover:bg-gray-100"
                  onClick={() => setIsOpen(false)}
                >
                  知识点
                </Link>
              </li>
              {/* 其他菜单项 */}
            </ul>
          </nav>
        </div>
      </div>
      
      {/* 移动端侧边栏打开时的遮罩 */}
      {isOpen && (
        <div 
          className="fixed inset-0 bg-black bg-opacity-50 z-30 md:hidden"
          onClick={() => setIsOpen(false)}
        />
      )}
    </>
  );
}
```

#### 自定义断点配置
在`tailwind.config.js`中添加自定义断点:
```javascript
// tailwind.config.js
module.exports = {
  content: [
    './app/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}'
  ],
  theme: {
    extend: {
      screens: {
        'xs': '480px',    // 小型手机
        'sm': '640px',    // 大型手机
        'md': '768px',    // 平板
        'lg': '1024px',   // 小型笔记本
        'xl': '1280px',   // 大型笔记本
        '2xl': '1536px',  // 桌面显示器
      },
      // 其他配置...
    }
  },
  plugins: [],
}
```

#### 响应式表格组件
```tsx
// components/questions/ResponsiveTable.tsx
interface TableColumn {
  title: string;
  dataIndex: string;
  render?: (value: any, record: any) => React.ReactNode;
}

interface ResponsiveTableProps {
  columns: TableColumn[];
  dataSource: any[];
  rowKey: string;
}

export function ResponsiveTable({ columns, dataSource, rowKey }: ResponsiveTableProps) {
  return (
    <>
      {/* 桌面端表格 - 只在md断点以上显示 */}
      <div className="hidden md:block overflow-x-auto">
        <table className="w-full border-collapse">
          <thead>
            <tr className="bg-gray-50 border-b">
              {columns.map((column) => (
                <th key={column.dataIndex} className="px-4 py-2 text-left font-medium text-gray-500">
                  {column.title}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {dataSource.map((record) => (
              <tr key={record[rowKey]} className="border-b hover:bg-gray-50">
                {columns.map((column) => (
                  <td key={`${record[rowKey]}-${column.dataIndex}`} className="px-4 py-3">
                    {column.render
                      ? column.render(record[column.dataIndex], record)
                      : record[column.dataIndex]}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      
      {/* 移动端卡片布局 - 只在小于md断点显示 */}
      <div className="md:hidden space-y-4">
        {dataSource.map((record) => (
          <div key={record[rowKey]} className="bg-white rounded-lg shadow p-4">
            {columns.map((column) => (
              <div key={`${record[rowKey]}-${column.dataIndex}`} className="py-2">
                <div className="text-sm font-medium text-gray-500">{column.title}</div>
                <div>
                  {column.render
                    ? column.render(record[column.dataIndex], record)
                    : record[column.dataIndex]}
                </div>
              </div>
            ))}
          </div>
        ))}
      </div>
    </>
  );
}
```

#### 屏幕尺寸Hook
```tsx
// lib/hooks/useBreakpoint.ts
'use client';

import { useState, useEffect } from 'react';

type Breakpoint = 'xs' | 'sm' | 'md' | 'lg' | 'xl' | '2xl';

const breakpoints = {
  xs: 480,
  sm: 640,
  md: 768,
  lg: 1024,
  xl: 1280,
  '2xl': 1536,
};

export function useBreakpoint(): Breakpoint {
  const [breakpoint, setBreakpoint] = useState<Breakpoint>('xs');
  
  useEffect(() => {
    const handleResize = () => {
      const width = window.innerWidth;
      
      if (width >= breakpoints['2xl']) {
        setBreakpoint('2xl');
      } else if (width >= breakpoints.xl) {
        setBreakpoint('xl');
      } else if (width >= breakpoints.lg) {
        setBreakpoint('lg');
      } else if (width >= breakpoints.md) {
        setBreakpoint('md');
      } else if (width >= breakpoints.sm) {
        setBreakpoint('sm');
      } else {
        setBreakpoint('xs');
      }
    };
    
    // 初始化
    handleResize();
    
    // 监听窗口大小变化
    window.addEventListener('resize', handleResize);
    
    return () => {
      window.removeEventListener('resize', handleResize);
    };
  }, []);
  
  return breakpoint;
}
```

#### 响应式布局应用示例
```tsx
// app/(dashboard)/questions/page.tsx - 响应式布局
import { useBreakpoint } from '@/lib/hooks/useBreakpoint';
import { QuestionsTable } from '@/components/questions/QuestionsTable';
import { QuestionCards } from '@/components/questions/QuestionCards';

export default function QuestionsPage() {
  const breakpoint = useBreakpoint();
  const isMobile = ['xs', 'sm'].includes(breakpoint);
  
  return (
    <div className="space-y-4">
      <div className="flex flex-col sm:flex-row sm:justify-between sm:items-center gap-4">
        <h1 className="text-2xl font-bold">错题列表</h1>
        <div className="flex flex-col xs:flex-row gap-2">
          <button className="btn-primary">添加错题</button>
          <button className="btn-outline">导出数据</button>
        </div>
      </div>
      
      {/* 根据屏幕大小选择不同显示方式 */}
      {isMobile ? <QuestionCards /> : <QuestionsTable />}
    </div>
  );
}
```

### 触摸友好设计
```css
/* styles/globals.css 添加 */
@layer utilities {
  .touch-target {
    @apply min-w-[44px] min-h-[44px]; /* 确保触摸目标至少44px */
  }
  
  .safe-bottom {
    padding-bottom: env(safe-area-inset-bottom);
  }
  
  .safe-top {
    padding-top: env(safe-area-inset-top);
  }
}
```

在组件中应用触摸友好设计:
```tsx
// components/ui/Button.tsx - 改进触摸体验
interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'outline';
  size?: 'sm' | 'md' | 'lg';
  fullWidth?: boolean;
}

export function Button({ 
  variant = 'primary', 
  size = 'md', 
  fullWidth = false,
  className, 
  children, 
  ...props 
}: ButtonProps) {
  // ... 现有代码
  
  // 增加触摸友好类
  const touchClass = size === 'sm' ? 'touch-target' : '';
  const widthClass = fullWidth ? 'w-full' : '';
  
  return (
    <button
      className={`${baseStyles} ${variantStyles[variant]} ${sizeStyles[size]} ${touchClass} ${widthClass} ${className}`}
      {...props}
    >
      {children}
    </button>
  );
}
```

## 18. 结语

本文档详细阐述了GradNote前端项目的技术架构和实现方案，遵循React和Next.js的最佳实践。通过采用现代化的技术栈和架构设计，完善的认证机制、错误处理策略、测试系统、性能监控和移动端适配，项目能够提供高效、安全、响应式的用户体验，同时保持代码的可维护性和扩展性。

开发团队应遵循本文档的规范和建议，确保项目的一致性和质量。随着项目的发展，本文档将根据需要进行更新和完善。