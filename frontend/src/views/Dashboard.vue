<template>
  <div class="dashboard">
    <h2>仪表盘</h2>
    
    <!-- 统计卡片 -->
    <div class="stats-cards">
      <el-card class="stat-card">
        <div class="stat-content">
          <div class="stat-info">
            <div class="stat-value">{{ apiProjectsCount }}</div>
            <div class="stat-label">API项目</div>
          </div>
          <div class="stat-icon">
            <el-icon :size="32"><Document /></el-icon>
          </div>
        </div>
      </el-card>
      
      <el-card class="stat-card">
        <div class="stat-content">
          <div class="stat-info">
            <div class="stat-value">{{ testCasesCount }}</div>
            <div class="stat-label">测试用例</div>
          </div>
          <div class="stat-icon">
            <el-icon :size="32"><Notebook /></el-icon>
          </div>
        </div>
      </el-card>
      
      <el-card class="stat-card">
        <div class="stat-content">
          <div class="stat-info">
            <div class="stat-value">{{ testScriptsCount }}</div>
            <div class="stat-label">测试脚本</div>
          </div>
          <div class="stat-icon">
            <el-icon :size="32"><Cpu /></el-icon>
          </div>
        </div>
      </el-card>
      
      <el-card class="stat-card">
        <div class="stat-content">
          <div class="stat-info">
            <div class="stat-value">{{ successRate }}</div>
            <div class="stat-label">成功率</div>
          </div>
          <div class="stat-icon">
            <el-icon :size="32"><CircleCheck /></el-icon>
          </div>
        </div>
      </el-card>
    </div>
    
    <!-- 最近活动和工作流状态 -->
    <div class="dashboard-content">
      <el-card class="content-card" style="width: 50%;">
        <template #header>
          <div class="card-header">
            <span>最近活动</span>
            <el-button type="text" size="small">查看全部</el-button>
          </div>
        </template>
        
        <el-timeline>
          <el-timeline-item
            v-for="activity in recentActivities"
            :key="activity.id"
            :timestamp="activity.timestamp"
            :icon="activity.icon"
            :type="activity.type"
          >
            {{ activity.content }}
          </el-timeline-item>
        </el-timeline>
      </el-card>
      
      <el-card class="content-card" style="width: 48%;">
        <template #header>
          <div class="card-header">
            <span>工作流状态</span>
            <el-button type="text" size="small">管理工作流</el-button>
          </div>
        </template>
        
        <div class="workflow-status">
          <div
            v-for="workflow in workflows"
            :key="workflow.id"
            class="workflow-item"
          >
            <div class="workflow-info">
              <div class="workflow-name">{{ workflow.name }}</div>
              <div class="workflow-desc">{{ workflow.description }}</div>
            </div>
            <el-progress
              :percentage="workflow.progress"
              :status="workflow.progress === 100 ? 'success' : 'active'"
            ></el-progress>
            <div class="workflow-meta">
              <span class="workflow-status">{{ workflow.status }}</span>
              <span class="workflow-date">{{ workflow.updatedAt }}</span>
            </div>
          </div>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { 
  Document, Notebook, Cpu, CircleCheck, 
  Clock, Plus, Edit, Check, InfoFilled 
} from '@element-plus/icons-vue'
import request from '../utils/request'

// 统计数据
const apiProjectsCount = ref(0)
const testCasesCount = ref(0)
const testScriptsCount = ref(0)
const successRate = ref('0%')

// 最近活动数据
const recentActivities = ref([
  {
    id: 1,
    content: 'API项目 "用户管理系统" 导入成功',
    timestamp: '2024-01-10 15:30',
    icon: Clock,
    type: 'success'
  },
  {
    id: 2,
    content: '测试用例 "登录功能" AI评审完成',
    timestamp: '2024-01-10 14:45',
    icon: InfoFilled,
    type: 'info'
  },
  {
    id: 3,
    content: '测试脚本 "订单创建" 执行失败',
    timestamp: '2024-01-10 13:20',
    icon: Edit,
    type: 'warning'
  },
  {
    id: 4,
    content: '工作流 "用户管理系统测试" 完成',
    timestamp: '2024-01-10 12:15',
    icon: Check,
    type: 'success'
  },
  {
    id: 5,
    content: '测试点 "权限验证" 生成成功',
    timestamp: '2024-01-10 11:00',
    icon: Plus,
    type: 'primary'
  }
])

// 工作流数据
const workflows = ref([
  {
    id: 1,
    name: '用户管理系统测试',
    description: '完整的用户管理系统测试流程',
    progress: 100,
    status: '已完成',
    updatedAt: '2024-01-10 12:15'
  },
  {
    id: 2,
    name: '订单系统测试',
    description: '订单系统核心功能测试',
    progress: 65,
    status: '进行中',
    updatedAt: '2024-01-10 15:00'
  },
  {
    id: 3,
    name: '支付系统测试',
    description: '支付系统安全测试',
    progress: 20,
    status: '待开始',
    updatedAt: '2024-01-10 16:00'
  }
])

// 获取统计数据
const fetchStatistics = async () => {
  try {
    // 获取API项目数量
    const apiProjects = await request.get('/api-projects')
    apiProjectsCount.value = Array.isArray(apiProjects) ? apiProjects.length : 0
    
    // 获取测试用例数量
    const testCases = await request.get('/test-cases/')
    testCasesCount.value = Array.isArray(testCases) ? testCases.length : 0
    
    // 获取测试脚本数量
    const testScripts = await request.get('/test-scripts/')
    testScriptsCount.value = Array.isArray(testScripts) ? testScripts.length : 0
    
    // 获取工作流度量指标
    const workflowMetrics = await request.get('/workflows/metrics', { params: { project_id: 1 } })
    if (workflowMetrics && workflowMetrics.data && workflowMetrics.data.success_rate !== undefined) {
      successRate.value = `${workflowMetrics.data.success_rate}%`
    }
  } catch (error) {
    console.error('获取统计数据失败:', error)
  }
}

// 组件挂载时获取数据
onMounted(() => {
  fetchStatistics()
})
</script>

<style scoped>
.dashboard {
  padding: 20px 0;
}

.stats-cards {
  display: flex;
  gap: 20px;
  margin-bottom: 20px;
  flex-wrap: wrap;
}

.stat-card {
  flex: 1;
  min-width: 200px;
}

.stat-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 32px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 8px;
}

.stat-label {
  font-size: 14px;
  color: #606266;
}

.stat-icon {
  color: #409eff;
}

.dashboard-content {
  display: flex;
  gap: 20px;
  flex-wrap: wrap;
}

.content-card {
  flex: 1;
  min-width: 300px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.workflow-status {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.workflow-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.workflow-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.workflow-name {
  font-weight: 500;
  color: #303133;
}

.workflow-desc {
  font-size: 12px;
  color: #909399;
}

.workflow-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 12px;
  color: #909399;
}

.workflow-status {
  color: #67c23a;
}
</style>
