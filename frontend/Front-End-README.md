
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

## 13. 结语

本文档详细阐述了GradNote前端项目的技术架构和实现方案，遵循React和Next.js的最佳实践。通过采用现代化的技术栈和架构设计，项目能够提供高效、响应式的用户体验，同时保持代码的可维护性和扩展性。

开发团队应遵循本文档的规范和建议，确保项目的一致性和质量。随着项目的发展，本文档将根据需要进行更新和完善。
