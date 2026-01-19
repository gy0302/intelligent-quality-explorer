<template>
  <div class="app-container">
    <header class="app-header">
      <div class="header-left">
        <h1>AQES-Test</h1>
      </div>
      <div class="header-right">
        <el-dropdown>
          <span class="el-dropdown-link">
            <el-icon><User /></el-icon>
            管理员
            <el-icon class="el-icon--right"><ArrowDown /></el-icon>
          </span>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item>个人中心</el-dropdown-item>
              <el-dropdown-item>系统设置</el-dropdown-item>
              <el-dropdown-item divided>退出登录</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </header>
    
    <div class="app-main">
      <aside class="sidebar">
        <el-menu
          :default-active="activeMenu"
          class="sidebar-menu"
          mode="vertical"
          @select="handleMenuSelect"
        >
          <el-menu-item index="dashboard">
            <el-icon><Histogram /></el-icon>
            <span>仪表盘</span>
          </el-menu-item>
          
          <el-sub-menu index="api-management">
            <template #title>
              <el-icon><Document /></el-icon>
              <span>API管理</span>
            </template>
            <el-menu-item index="api-import">API导入</el-menu-item>
            <el-menu-item index="api-list">API列表</el-menu-item>
          </el-sub-menu>
          
          <el-sub-menu index="ai-review">
            <template #title>
              <el-icon><Star /></el-icon>
              <span>AI评审</span>
            </template>
            <el-menu-item index="api-review">API评审</el-menu-item>
            <el-menu-item index="test-point-review">测试点评审</el-menu-item>
            <el-menu-item index="test-case-review">测试用例评审</el-menu-item>
            <el-menu-item index="test-script-review">测试脚本评审</el-menu-item>
          </el-sub-menu>
          
          <el-sub-menu index="test-design">
            <template #title>
              <el-icon><Notebook /></el-icon>
              <span>测试设计</span>
            </template>
            <el-menu-item index="test-points">测试点管理</el-menu-item>
            <el-menu-item index="test-cases">测试用例管理</el-menu-item>
            <el-menu-item index="test-scripts">测试脚本管理</el-menu-item>
          </el-sub-menu>
          
          <el-sub-menu index="test-execution">
            <template #title>
              <el-icon><VideoPlay /></el-icon>
              <span>测试执行</span>
            </template>
            <el-menu-item index="execute-tests">执行测试</el-menu-item>
            <el-menu-item index="execution-history">执行历史</el-menu-item>
          </el-sub-menu>
          
          <el-sub-menu index="test-report">
            <template #title>
              <el-icon><DocumentCopy /></el-icon>
              <span>测试报告</span>
            </template>
            <el-menu-item index="reports">报告列表</el-menu-item>
            <el-menu-item index="report-detail">报告详情</el-menu-item>
          </el-sub-menu>
          
          <el-sub-menu index="workflow">
            <template #title>
              <el-icon><RefreshRight /></el-icon>
              <span>工作流管理</span>
            </template>
            <el-menu-item index="workflow-list">工作流列表</el-menu-item>
            <el-menu-item index="workflow-detail">工作流详情</el-menu-item>
          </el-sub-menu>
          
          <el-sub-menu index="config-center">
            <template #title>
              <el-icon><Setting /></el-icon>
              <span>配置中心</span>
            </template>
            <el-menu-item index="config-categories">配置分类</el-menu-item>
            <el-menu-item index="config-items">配置项管理</el-menu-item>
          </el-sub-menu>
        </el-menu>
      </aside>
      
      <main class="content">
        <router-view></router-view>
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { 
  User, ArrowDown, Histogram, Document, Star, 
  Notebook, VideoPlay, DocumentCopy, RefreshRight, Setting 
} from '@element-plus/icons-vue'

const router = useRouter()
const activeMenu = ref('dashboard')

const handleMenuSelect = (index: string) => {
  activeMenu.value = index
  // 根据菜单索引跳转到对应路由
  switch (index) {
    case 'dashboard':
      router.push('/dashboard')
      break
    case 'api-import':
      router.push('/api/import')
      break
    case 'api-list':
      router.push('/api/list')
      break
    case 'test-points':
      router.push('/test-points')
      break
    case 'test-cases':
      router.push('/test-cases')
      break
    case 'test-scripts':
      router.push('/test-scripts')
      break
    case 'execute-tests':
      router.push('/test-execution/execute')
      break
    case 'execution-history':
      router.push('/test-execution/history')
      break
    case 'reports':
      router.push('/reports')
      break
    case 'config-categories':
      router.push('/config/categories')
      break
    case 'config-items':
      router.push('/config/items')
      break
    case 'workflow-list':
      router.push('/workflow')
      break
    default:
      break
  }
}

onMounted(() => {
  // 初始化时根据当前路由设置活动菜单
  const currentPath = router.currentRoute.value.path
  if (currentPath === '/dashboard') {
    activeMenu.value = 'dashboard'
  } else if (currentPath.startsWith('/api')) {
    activeMenu.value = 'api-management'
  } else if (currentPath.startsWith('/test-points')) {
    activeMenu.value = 'test-points'
  }
  // 其他路由的处理...
})
</script>

<style scoped>
.app-container {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  background-color: #f5f7fa;
}

.app-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 60px;
  padding: 0 20px;
  background-color: #ffffff;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  z-index: 100;
}

.header-left h1 {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
  color: #303133;
}

.header-right {
  display: flex;
  align-items: center;
}

.el-dropdown-link {
  display: flex;
  align-items: center;
  cursor: pointer;
  color: #606266;
}

.app-main {
  display: flex;
  flex: 1;
  overflow: hidden;
}

.sidebar {
  width: 220px;
  background-color: #ffffff;
  border-right: 1px solid #e4e7ed;
  overflow-y: auto;
}

.sidebar-menu {
  height: 100%;
  border-right: none;
}

.content {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
}
</style>
