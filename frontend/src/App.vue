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
              <div class="assistant-chat">
                <!-- 回答展示区域 - 增大高度，自适应剩余空间 -->
                <div class="chat-messages full-height" ref="chatMessagesRef">
                  <div v-if="messages.length === 0" class="empty-messages">
                    <p>欢迎使用智能助手！请输入您的问题，我将为您提供帮助。</p>
                  </div>
                  <div v-for="(msg, index) in messages" :key="index" :class="['message-item', msg.role]">
                    <div class="message-header">
                      <span class="message-role">{{ msg.role === 'user' ? '您' : 'AI助手' }}</span>
                      <span class="message-time">{{ msg.timestamp }}</span>
                    </div>
                    <div class="message-content">
                      <div v-if="msg.role === 'ai'" class="ai-avatar">🤖</div>
                      <div class="content-text" v-html="msg.content"></div>
                    </div>
                  </div>
                  <div v-if="isLoading" class="loading-message">
                    <div class="loading-spinner"></div>
                    <span>AI助手正在思考中...</span>
                  </div>
                </div>
                
                <!-- 输入区域 - 包含输入框和工具栏，类似trae的布局 -->
                <div class="input-container">
                  <el-input
                    v-model="inputMessage"
                    type="textarea"
                    :rows="2"
                    placeholder="请输入您的问题..."
                    resize="none"
                    @keyup.enter="sendMessage"
                    class="trae-input"
                  />
                  <div class="trae-toolbar">
                    <div class="toolbar-left">
                      <div class="model-selector">
                        <el-select v-model="selectedModel" placeholder="选择模型" size="small">
                          <el-option
                            v-for="model in models"
                            :key="model.value"
                            :label="model.label"
                            :value="model.value"
                          />
                        </el-select>
                      </div>
                    </div>
                    <div class="toolbar-right">
                      <el-button type="text" size="small" @click="clearMessages">
                        <el-icon><Delete /></el-icon> 清空
                      </el-button>
                      <el-button
                        type="primary"
                        @click="sendMessage"
                        :disabled="!inputMessage.trim() || isLoading"
                        size="small"
                      >
                        发送
                      </el-button>
                    </div>
                  </div>
                </div>
              </div>
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
import { ref, onMounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import request from './utils/request'
import { 
  User, ArrowDown, Histogram, Document, Star, 
  RefreshRight, Setting, Collection, Monitor, 
  Tickets, CircleClose, TrendCharts, 
  ArrowLeft, ArrowRight, Delete 
} from '@element-plus/icons-vue'

const router = useRouter()
const activeMenu = ref('dashboard')
// 右侧标签页
const activeTab = ref('assistant')
// 右侧面板折叠状态
const isRightPanelCollapsed = ref(false)

// AI助手相关
interface ChatMessage {
  role: 'user' | 'ai'
  content: string
  timestamp: string
}

// 聊天消息列表
const messages = ref<ChatMessage[]>([])
// 输入消息
const inputMessage = ref('')
// 选中的模型
const selectedModel = ref('qwen3:8b')
// 可用模型列表
const models = ref([
  { value: 'qwen3:8b', label: 'Qwen3:8B' }
])
// 加载状态
const isLoading = ref(false)
// 聊天消息容器引用
const chatMessagesRef = ref<HTMLElement | null>(null)

// 格式化时间
const formatTime = (date: Date) => {
  return date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
}

// 清空消息
const clearMessages = () => {
  messages.value = []
}

// 发送消息
const sendMessage = async () => {
  if (!inputMessage.value.trim() || isLoading.value) return
  
  const question = inputMessage.value.trim()
  const userMessage: ChatMessage = {
    role: 'user',
    content: question,
    timestamp: formatTime(new Date())
  }
  
  messages.value.push(userMessage)
  inputMessage.value = ''
  
  // 滚动到底部
  await nextTick()
  scrollToBottom()
  
  isLoading.value = true
  
  try {
    // 调用AI助手API
    const response = await request.post('/api/v1/ai/assistant/chat', {
      model: selectedModel.value,
      question: question
    })
    
    const aiMessage: ChatMessage = {
      role: 'ai',
      content: response.data.answer || '抱歉，我无法回答这个问题。',
      timestamp: formatTime(new Date())
    }
    
    messages.value.push(aiMessage)
  } catch (error) {
    console.error('AI助手请求失败:', error)
    const errorMessage: ChatMessage = {
      role: 'ai',
      content: '抱歉，AI助手暂时无法响应，请稍后再试。',
      timestamp: formatTime(new Date())
    }
    messages.value.push(errorMessage)
  } finally {
    isLoading.value = false
    // 滚动到底部
    await nextTick()
    scrollToBottom()
  }
}

// 滚动到底部
const scrollToBottom = () => {
  if (chatMessagesRef.value) {
    chatMessagesRef.value.scrollTop = chatMessagesRef.value.scrollHeight
  }
}

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
  padding: 0;
  height: calc(100% - 40px);
  overflow-y: auto;
}

/* AI助手聊天容器 */
.assistant-chat {
  display: flex;
  flex-direction: column;
  height: 100%;
  background-color: #ffffff;
  overflow: hidden; /* 确保整个聊天容器不会出现滚动条 */
}

/* 助手内容区域 */
.assistant-content {
  padding: 0;
  height: 100%;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  background-color: #fafafa; /* 为整个助手内容区域设置灰色背景 */
}

/* 聊天消息区域 */
.chat-messages {
  flex: 1;
  overflow-y: auto; /* 只在聊天消息区域显示滚动条 */
  padding: 15px;
  background-color: transparent; /* 移除消息区域的背景色，使用父容器的灰色背景 */
  max-height: calc(100% - 200px); /* 调整最大高度，确保不会被固定的输入容器遮挡 */
}

/* 自适应高度的聊天消息区域 - 填满剩余空间 */
.chat-messages.full-height {
  flex: 1;
  overflow-y: auto; /* 只在聊天消息区域显示滚动条 */
  min-height: auto;
  max-height: calc(100% - 200px); /* 调整最大高度，确保不会被固定的输入容器遮挡 */
  background-color: transparent; /* 移除消息区域的背景色，使用父容器的灰色背景 */
}

/* 空消息状态 */
.empty-messages {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 200px;
  color: #909399;
  font-size: 14px;
  text-align: center;
}

/* 消息项 */
.message-item {
  margin-bottom: 15px;
  display: flex;
  flex-direction: column;
}

/* 用户消息 */
.message-item.user {
  align-items: flex-end;
}

/* AI消息 */
.message-item.ai {
  align-items: flex-start;
}

/* 消息头部 */
.message-header {
  display: flex;
  align-items: center;
  margin-bottom: 8px;
  font-size: 12px;
}

/* 用户消息头部 */
.message-item.user .message-header {
  flex-direction: row-reverse;
}

/* 角色名称 */
.message-role {
  font-weight: 500;
  margin-right: 8px;
}

.message-item.user .message-role {
  margin-right: 0;
  margin-left: 8px;
  color: #409eff;
}

.message-item.ai .message-role {
  color: #67c23a;
}

/* 消息时间 */
.message-time {
  color: #909399;
  font-size: 11px;
}

/* 消息内容 */
.message-content {
  display: flex;
  align-items: flex-start;
  max-width: 85%;
}

.message-item.user .message-content {
  flex-direction: row-reverse;
}

/* AI头像 */
.ai-avatar {
  font-size: 24px;
  margin-right: 10px;
  margin-top: 2px;
}

/* 消息文本 */
.content-text {
  background-color: #ffffff;
  padding: 12px 16px;
  border-radius: 8px;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
  line-height: 1.6;
  color: #303133;
  word-wrap: break-word;
  white-space: pre-wrap;
}

.message-item.user .content-text {
  background-color: #ecf5ff;
  color: #303133;
}

/* 加载消息 */
.loading-message {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 15px;
  color: #909399;
  font-size: 14px;
}

/* 加载动画 */
.loading-spinner {
  width: 16px;
  height: 16px;
  border: 2px solid #dcdfe6;
  border-top-color: #409eff;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-right: 8px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* 输入容器 - 包含输入框和工具栏，固定在浏览器底部 */
.input-container {
  background-color: #ffffff;
  border-top: 1px solid #e4e7ed;
  display: flex;
  flex-direction: column;
  width: 300px; /* 与右侧面板宽度一致 */
  border-radius: 8px 8px 0 0; /* 底部圆角改为直角 */
  overflow: hidden;
  box-shadow: 0 -2px 10px rgba(0, 0, 0, 0.05);
  position: fixed; /* 固定定位 */
  bottom: 0; /* 底部对齐 */
  right: 0; /* 右侧对齐 */
  z-index: 1000; /* 确保在最上层 */
  max-width: 300px; /* 限制最大宽度 */
  height: auto; /* 自适应高度 */
}

/* 输入框样式 - 类似trae */
.trae-input {
  padding: 10px 15px;
  background-color: #ffffff;
  border: none;
}

.trae-input :deep(.el-textarea__inner) {
  border: 1px solid #e4e7ed;
  border-bottom: none;
  border-radius: 4px 4px 0 0;
  resize: none;
  min-height: 90px; /* 增加高度30px，从60px调整为90px */
  font-size: 14px;
  line-height: 1.5;
  padding: 10px;
  transition: border-color 0.2s;
}

.trae-input :deep(.el-textarea__inner:focus) {
  border-color: #409eff;
  box-shadow: none;
}

.trae-input :deep(.el-textarea__inner:hover) {
  border-color: #66b1ff;
}

/* 工具栏样式 - 类似trae */
.trae-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 15px;
  background-color: #f5f7fa;
  border-top: 1px solid #e4e7ed;
  border-radius: 0 0 4px 4px;
}

/* 工具栏左侧 */
.toolbar-left {
  display: flex;
  align-items: center;
  gap: 8px;
}

/* 工具栏右侧 */
.toolbar-right {
  display: flex;
  align-items: center;
  gap: 8px;
}

/* 模型选择器 */
.model-selector .el-select {
  min-width: 120px;
  font-size: 13px;
}

.model-selector :deep(.el-input__wrapper) {
  box-shadow: none;
  border-radius: 4px;
}

/* 按钮样式 */
.trae-toolbar .el-button {
  font-size: 13px;
  font-weight: normal;
  padding: 4px 12px;
  border-radius: 4px;
}

.trae-toolbar .el-button--primary {
  background-color: #409eff;
  border-color: #409eff;
}

.trae-toolbar .el-button--text {
  color: #606266;
  padding: 4px 8px;
}

.trae-toolbar .el-button--text:hover {
  color: #409eff;
  background-color: rgba(64, 158, 255, 0.1);
}

/* 富文本内容样式 */
.content-text h1, .content-text h2, .content-text h3 {
  margin: 16px 0 8px 0;
  font-weight: 600;
  line-height: 1.4;
}

.content-text h1 { font-size: 20px; }
.content-text h2 { font-size: 18px; }
.content-text h3 { font-size: 16px; }

.content-text p {
  margin: 8px 0;
  line-height: 1.6;
}

.content-text code {
  background-color: #f5f7fa;
  padding: 2px 6px;
  border-radius: 4px;
  font-family: monospace;
  font-size: 13px;
}

.content-text pre {
  background-color: #f5f7fa;
  padding: 12px;
  border-radius: 6px;
  overflow-x: auto;
  font-family: monospace;
  font-size: 13px;
  line-height: 1.5;
  margin: 10px 0;
}

.content-text ul, .content-text ol {
  margin: 8px 0;
  padding-left: 24px;
}

.content-text li {
  margin: 4px 0;
  line-height: 1.6;
}

/* 帮助文档样式 */
.help-content {
  padding: 20px;
}

.help-content h3 {
  margin: 0 0 16px 0;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

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
