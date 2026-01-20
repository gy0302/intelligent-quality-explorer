<template>
  <div class="app-container">
    <header class="app-header">
      <div class="header-left">
        <el-icon class="app-logo"><Star /></el-icon>
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
          <!-- 仪表盘 -->
          <el-menu-item index="dashboard">
            <el-icon><Histogram /></el-icon>
            <span>仪表盘</span>
          </el-menu-item>
          
          <!-- 项目管理 -->
          <el-menu-item index="project-management">
            <el-icon><Collection /></el-icon>
            <span>项目管理</span>
          </el-menu-item>
          
          <!-- 工作流管理 -->
          <el-sub-menu index="workflow-management">
            <template #title>
              <el-icon><RefreshRight /></el-icon>
              <span>工作流管理</span>
            </template>
            <el-menu-item index="node-management">节点管理</el-menu-item>
            <el-menu-item index="process-design">流程设计</el-menu-item>
            <el-menu-item index="task-management">任务管理</el-menu-item>
          </el-sub-menu>
          
          <!-- 接口测试 -->
          <el-sub-menu index="api-test">
            <template #title>
              <el-icon><Document /></el-icon>
              <span>接口测试</span>
            </template>
            <el-menu-item index="api-list">接口管理</el-menu-item>
            <el-sub-menu index="test-design">
              <template #title>
                <span>测试设计</span>
              </template>
              <el-menu-item index="test-points">测试点</el-menu-item>
              <el-menu-item index="test-cases">测试用例</el-menu-item>
              <el-menu-item index="scene-cases">场景用例</el-menu-item>
            </el-sub-menu>
          </el-sub-menu>
          
          <!-- UI测试 -->
          <el-sub-menu index="ui-test">
            <template #title>
              <el-icon><Monitor /></el-icon>
              <span>UI测试</span>
            </template>
            <el-menu-item index="ui-test-placeholder">待完善</el-menu-item>
          </el-sub-menu>
          
          <!-- 测试计划 -->
          <el-menu-item index="test-plan">
            <el-icon><Tickets /></el-icon>
            <span>测试计划</span>
          </el-menu-item>
          
          <!-- 测试报告 -->
          <el-sub-menu index="test-report">
            <template #title>
              <el-icon><Document /></el-icon>
              <span>测试报告</span>
            </template>
            <el-menu-item index="reports">报告列表</el-menu-item>
            <el-menu-item index="report-analysis">报告分析</el-menu-item>
          </el-sub-menu>
          
          <!-- AI管理 -->
          <el-sub-menu index="ai-management">
            <template #title>
              <el-icon><Star /></el-icon>
              <span>AI管理</span>
            </template>
            <el-menu-item index="model-management">模型管理</el-menu-item>
            <el-menu-item index="prompt-management">提示词管理</el-menu-item>
            <el-menu-item index="review-management">评审管理</el-menu-item>
            <el-menu-item index="knowledge-base">知识库管理</el-menu-item>
          </el-sub-menu>
          
          <!-- 缺陷管理 -->
          <el-sub-menu index="defect-management">
            <template #title>
              <el-icon><CircleClose /></el-icon>
              <span>缺陷管理</span>
            </template>
            <el-menu-item index="defect-placeholder">待完善</el-menu-item>
          </el-sub-menu>
          
          <!-- 度量管理 -->
          <el-sub-menu index="metrics-management">
            <template #title>
              <el-icon><TrendCharts /></el-icon>
              <span>度量管理</span>
            </template>
            <el-menu-item index="metrics-placeholder">待完善</el-menu-item>
          </el-sub-menu>
          
          <!-- 公共配置 -->
          <el-sub-menu index="public-config">
            <template #title>
              <el-icon><Setting /></el-icon>
              <span>公共配置</span>
            </template>
            <el-menu-item index="environment-config">环境配置</el-menu-item>
            <el-menu-item index="employee-management">员工管理</el-menu-item>
            <el-menu-item index="role-management">角色管理</el-menu-item>
            <el-menu-item index="notification-management">通知管理</el-menu-item>
            <el-menu-item index="log-management">日志管理</el-menu-item>
          </el-sub-menu>
        </el-menu>
      </aside>
      
      <!-- 中间内容区域 -->
      <main class="content">
        <router-view></router-view>
      </main>
      
      <!-- 右侧面板折叠按钮 -->
      <div class="right-panel-toggle" @click="toggleRightPanel">
        <el-icon v-if="isRightPanelCollapsed"><ArrowRight /></el-icon>
        <el-icon v-else><ArrowLeft /></el-icon>
      </div>
      
      <!-- 右侧门户区域 -->
      <aside :class="['right-sidebar', { 'collapsed': isRightPanelCollapsed }]">
        <el-tabs v-model="activeTab" class="right-tabs">
          <!-- 智能助手 -->
          <el-tab-pane label="智能助手" name="assistant">
            <div class="assistant-content">
              <h3>智能助手</h3>
              <p>智能助手功能正在开发中...</p>
            </div>
          </el-tab-pane>
          
          <!-- 帮助文档 -->
          <el-tab-pane label="帮助文档" name="help">
            <div class="help-content">
              <h3>帮助文档</h3>
              <p>帮助文档正在完善中...</p>
            </div>
          </el-tab-pane>
          

        </el-tabs>
      </aside>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { 
  User, ArrowDown, Histogram, Document, Star, 
  RefreshRight, Setting, Collection, Monitor, 
  Tickets, CircleClose, TrendCharts, 
  ArrowLeft, ArrowRight 
} from '@element-plus/icons-vue'

const router = useRouter()
const activeMenu = ref('dashboard')
// 右侧标签页
const activeTab = ref('assistant')
// 右侧面板折叠状态
const isRightPanelCollapsed = ref(false)

// 右侧面板折叠/展开方法
const toggleRightPanel = () => {
  isRightPanelCollapsed.value = !isRightPanelCollapsed.value
}

const handleMenuSelect = (index: string) => {
  activeMenu.value = index
  // 根据菜单索引跳转到对应路由
  switch (index) {
    case 'dashboard':
      router.push('/dashboard')
      break
    case 'project-management':
      router.push('/projects')
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
    case 'execute-tests':
      router.push('/test-execution/execute')
      break
    case 'execution-history':
      router.push('/test-execution/history')
      break
    case 'reports':
      router.push('/reports')
      break
    case 'report-analysis':
      router.push('/reports/analysis')
      break
    case 'test-plan':
      router.push('/test-plan')
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
      // 暂时不处理的菜单，后续可以添加路由
      console.log(`Menu index ${index} not implemented yet`)
      break
  }
}

onMounted(() => {
  // 初始化时根据当前路由设置活动菜单
  const currentPath = router.currentRoute.value.path
  if (currentPath === '/dashboard') {
    activeMenu.value = 'dashboard'
  } else if (currentPath.startsWith('/projects')) {
    activeMenu.value = 'project-management'
  } else if (currentPath.startsWith('/api/list')) {
    activeMenu.value = 'api-test'
  } else if (currentPath.startsWith('/test-points')) {
    activeMenu.value = 'test-points'
  } else if (currentPath.startsWith('/test-cases')) {
    activeMenu.value = 'test-cases'
  } else if (currentPath.startsWith('/test-scripts')) {
    activeMenu.value = 'test-scripts'
  } else if (currentPath.startsWith('/test-execution')) {
    activeMenu.value = 'api-test'
  } else if (currentPath.startsWith('/reports')) {
    activeMenu.value = 'test-report'
  } else if (currentPath.startsWith('/workflow')) {
    activeMenu.value = 'workflow-management'
  } else if (currentPath.startsWith('/config')) {
    activeMenu.value = 'public-config'
  }
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

.header-left {
  display: flex;
  align-items: center;
}

.app-logo {
  font-size: 24px;
  color: #409eff;
  margin-right: 12px;
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

/* 左侧导航栏 */
.sidebar {
  width: 220px;
  background-color: #ffffff;
  border-right: 1px solid #e4e7ed;
  overflow-y: auto;
  flex-shrink: 0;
}

.sidebar-menu {
  height: 100%;
  border-right: none;
}

/* 中间内容区域 */
.content {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
  background-color: #f5f7fa;
  transition: margin 0.3s ease;
}

/* 右侧门户区域 */
.right-sidebar {
  width: 300px;
  background-color: #ffffff;
  border-left: 1px solid #e4e7ed;
  overflow-y: auto;
  flex-shrink: 0;
  transition: width 0.3s ease;
}

/* 右侧门户区域折叠状态 */
.right-sidebar.collapsed {
  width: 0;
  overflow: hidden;
}

/* 右侧面板折叠按钮 */
.right-panel-toggle {
  width: 20px;
  background-color: #ffffff;
  border: 1px solid #e4e7ed;
  border-left: none;
  border-right: none;
  cursor: pointer;
  display: flex;
  justify-content: center;
  align-items: center;
  color: #606266;
  transition: all 0.3s ease;
  flex-shrink: 0;
}

.right-panel-toggle:hover {
  background-color: #f5f7fa;
  color: #409eff;
}



/* 右侧标签页 */
.right-tabs {
  height: 100%;
  display: flex;
  flex-direction: column;
}

/* 右侧标签页 - 标签栏样式优化 */
.right-tabs :deep(.el-tabs__nav-wrap) {
  justify-content: center;
  background-color: #f5f7fa;
  border-bottom: 1px solid #e4e7ed;
}

.right-tabs :deep(.el-tabs__item) {
  margin: 0 10px;
  padding: 0 20px;
  color: #606266;
  font-weight: 500;
}

.right-tabs :deep(.el-tabs__item.is-active) {
  color: #409eff;
}

.right-tabs :deep(.el-tabs__active-bar) {
  background-color: #409eff;
}

/* 右侧标签页内容 */
.assistant-content,
.help-content {
  padding: 20px;
  height: calc(100% - 40px);
  overflow-y: auto;
}

.assistant-content h3,
.help-content h3 {
  margin: 0 0 16px 0;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.assistant-content p,
.help-content p {
  margin: 0;
  color: #606266;
  line-height: 1.6;
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .right-sidebar {
    width: 250px;
  }
}

@media (max-width: 1024px) {
  .right-sidebar {
    display: none;
  }
}
</style>
