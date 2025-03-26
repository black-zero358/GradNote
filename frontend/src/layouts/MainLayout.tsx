import React, { useState } from 'react';
import { Layout, Menu, Avatar, Dropdown, Button, theme } from 'antd';
import { useDispatch, useSelector } from 'react-redux';
import { Outlet, useNavigate, useLocation } from 'react-router-dom';
import {
  HomeOutlined,
  FileTextOutlined,
  BookOutlined,
  UserOutlined,
  SettingOutlined,
  MenuFoldOutlined,
  MenuUnfoldOutlined,
  LogoutOutlined,
} from '@ant-design/icons';
import { RootState, AppDispatch } from '../store';
import { logout } from '../store/slices/authSlice';
import type { MenuProps } from 'antd';

const { Header, Sider, Content } = Layout;
const { useToken } = theme;

const MainLayout: React.FC = () => {
  const [collapsed, setCollapsed] = useState(false);
  const dispatch = useDispatch<AppDispatch>();
  const navigate = useNavigate();
  const location = useLocation();
  const { token } = useToken();
  const { user } = useSelector((state: RootState) => state.auth);

  // 处理退出登录
  const handleLogout = () => {
    dispatch(logout());
    navigate('/login');
  };

  // 菜单项配置
  const menuItems: MenuProps['items'] = [
    {
      key: '/',
      icon: <HomeOutlined />,
      label: '仪表盘',
    },
    {
      key: 'error',
      icon: <FileTextOutlined />,
      label: '错题管理',
      children: [
        {
          key: '/questions',
          label: '错题列表',
        },
        {
          key: '/questions/new',
          label: '提交错题',
        },
      ],
    },
    {
      key: 'knowledge',
      icon: <BookOutlined />,
      label: '知识点库',
      children: [
        {
          key: '/knowledge',
          label: '知识点列表',
        },
        {
          key: '/knowledge/user-marks',
          label: '我的标记',
        },
      ],
    },
    {
      key: 'settings',
      icon: <SettingOutlined />,
      label: '设置',
    },
  ];

  // 用户菜单
  const userMenuItems: MenuProps['items'] = [
    {
      key: 'profile',
      icon: <UserOutlined />,
      label: '个人资料',
    },
    {
      key: 'logout',
      icon: <LogoutOutlined />,
      label: '退出登录',
    },
  ];

  // 菜单点击处理
  const handleMenuClick = ({ key }: { key: string }) => {
    navigate(key);
  };

  // 用户菜单点击处理
  const handleUserMenuClick = ({ key }: { key: string }) => {
    if (key === 'logout') {
      handleLogout();
    } else if (key === 'profile') {
      navigate('/profile');
    }
  };

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Sider trigger={null} collapsible collapsed={collapsed} theme="light">
        <div className="logo" style={{ padding: '16px', textAlign: 'center' }}>
          <h1 style={{ 
            color: token.colorPrimary, 
            margin: 0, 
            fontSize: collapsed ? '20px' : '24px',
            overflow: 'hidden',
            whiteSpace: 'nowrap'
          }}>
            {collapsed ? 'GN' : 'GradNote'}
          </h1>
        </div>
        <Menu
          theme="light"
          mode="inline"
          defaultSelectedKeys={['/']}
          selectedKeys={[location.pathname]}
          items={menuItems}
          onClick={handleMenuClick}
        />
      </Sider>
      <Layout>
        <Header style={{ 
          padding: '0 16px', 
          background: token.colorBgContainer,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between'
        }}>
          <Button
            type="text"
            icon={collapsed ? <MenuUnfoldOutlined /> : <MenuFoldOutlined />}
            onClick={() => setCollapsed(!collapsed)}
          />
          <Dropdown menu={{ items: userMenuItems, onClick: handleUserMenuClick }} placement="bottomRight">
            <div style={{ cursor: 'pointer' }}>
              <Avatar icon={<UserOutlined />} />
              <span style={{ marginLeft: 8, display: 'inline-block' }}>{user?.username || '用户'}</span>
            </div>
          </Dropdown>
        </Header>
        <Content style={{ 
          margin: '24px 16px', 
          padding: 24, 
          background: token.colorBgContainer,
          borderRadius: token.borderRadius,
          minHeight: 280 
        }}>
          <Outlet />
        </Content>
      </Layout>
    </Layout>
  );
};

export default MainLayout; 