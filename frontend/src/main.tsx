import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { Provider } from 'react-redux'
import { ConfigProvider } from 'antd'
import zhCN from 'antd/lib/locale/zh_CN'
import { store } from './store'
import AppRouter from './router'
import './styles/global.less'

// 去除开发环境的警告
const container = document.getElementById('root') as HTMLElement
const root = createRoot(container)

root.render(
  <StrictMode>
    <Provider store={store}>
      <ConfigProvider 
        locale={zhCN}
        theme={{
          token: {
            colorPrimary: '#7b68ee',
          },
        }}
      >
        <AppRouter />
      </ConfigProvider>
    </Provider>
  </StrictMode>,
)
