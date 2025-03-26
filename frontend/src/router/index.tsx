import { createBrowserRouter, Navigate, RouterProvider } from 'react-router-dom';
import { useEffect } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { getCurrentUser } from '../store/slices/authSlice';
import { RootState, AppDispatch } from '../store';

// 导入布局组件
import MainLayout from '../layouts/MainLayout';

// 导入页面组件
import Dashboard from '../pages/Dashboard/Dashboard';
import Login from '../pages/Auth/Login';
import Register from '../pages/Auth/Register';
import NotFound from '../pages/NotFound';

// 导入错题管理相关页面
import QuestionCreate from '../pages/ErrorManage/QuestionCreate';

// 受保护的路由组件
const ProtectedRoute = ({ children }: { children: React.ReactNode }) => {
  const { isAuthenticated, loading } = useSelector((state: RootState) => state.auth);
  const dispatch = useDispatch<AppDispatch>();

  useEffect(() => {
    if (!loading && !isAuthenticated) {
      dispatch(getCurrentUser());
    }
  }, [dispatch, isAuthenticated, loading]);

  if (loading) {
    return <div>加载中...</div>;
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" />;
  }

  return <>{children}</>;
};

// 访客路由组件（仅未登录可访问）
const GuestRoute = ({ children }: { children: React.ReactNode }) => {
  const { isAuthenticated } = useSelector((state: RootState) => state.auth);

  if (isAuthenticated) {
    return <Navigate to="/" />;
  }

  return <>{children}</>;
};

// 路由配置
const router = createBrowserRouter([
  {
    path: '/',
    element: (
      <ProtectedRoute>
        <MainLayout />
      </ProtectedRoute>
    ),
    children: [
      { index: true, element: <Dashboard /> },
      // 错题管理路由
      { path: 'questions/new', element: <QuestionCreate /> },
      // 其他需要认证的路由可以在这里添加
    ]
  },
  {
    path: '/login',
    element: (
      <GuestRoute>
        <Login />
      </GuestRoute>
    )
  },
  {
    path: '/register',
    element: (
      <GuestRoute>
        <Register />
      </GuestRoute>
    )
  },
  {
    path: '*',
    element: <NotFound />
  }
]);

// 路由提供器组件
const AppRouter = () => {
  return <RouterProvider router={router} />;
};

export default AppRouter; 