<template>
  <div class="test-cases">
    <el-card>
      <template #header>
        <div class="card-header">
          <h2>测试用例管理</h2>
          <div class="header-buttons">
            <el-button type="primary" @click="handleGenerate">生成测试用例</el-button>
            <el-button type="success" @click="handleAdd">添加测试用例</el-button>
            <el-button type="danger" @click="handleBatchDelete" :disabled="selectedTestCases.length === 0">批量删除</el-button>
          </div>
        </div>
      </template>
      
      <!-- 筛选条件 -->
      <div class="filter-section">
        <el-form :inline="true" :model="filterForm" class="demo-form-inline">
          <el-form-item label="项目ID">
            <el-input v-model="filterForm.projectId" placeholder="请输入项目ID" width="200" />
          </el-form-item>
          <el-form-item label="接口ID">
            <el-input v-model="filterForm.interfaceId" placeholder="请输入接口ID" width="200" />
          </el-form-item>
          <el-form-item label="测试点ID">
            <el-input v-model="filterForm.testPointId" placeholder="请输入测试点ID" width="200" />
          </el-form-item>
          <el-form-item label="状态">
            <el-select v-model="filterForm.status" placeholder="请选择状态" width="150">
              <el-option label="草稿" value="DRAFT" />
              <el-option label="已审核" value="REVIEWED" />
              <el-option label="已执行" value="EXECUTED" />
              <el-option label="已废弃" value="DEPRECATED" />
            </el-select>
          </el-form-item>
          <el-form-item label="优先级">
            <el-select v-model="filterForm.priority" placeholder="请选择优先级" width="150">
              <el-option label="高" value="HIGH" />
              <el-option label="中" value="MEDIUM" />
              <el-option label="低" value="LOW" />
            </el-select>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="handleFilter">查询</el-button>
            <el-button @click="handleReset">重置</el-button>
          </el-form-item>
        </el-form>
      </div>
      
      <!-- 测试用例列表 -->
      <el-table
        v-loading="loading"
        :data="testCases"
        style="width: 100%"
        @selection-change="handleSelectionChange"
      >
        <el-table-column type="selection" width="55" />
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="case_name" label="用例名称" min-width="200" />
        <el-table-column prop="description" label="描述" min-width="300" />
        <el-table-column prop="priority" label="优先级" width="100">
          <template #default="scope">
            <el-tag :type="getPriorityType(scope.row.priority)">
              {{ scope.row.priority }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="120">
          <template #default="scope">
            <el-tag :type="getStatusType(scope.row.status)">
              {{ scope.row.status }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="execution_status" label="执行状态" width="120">
          <template #default="scope">
            <el-tag :type="getExecutionStatusType(scope.row.execution_status)">
              {{ scope.row.execution_status || '未执行' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="test_point_id" label="测试点ID" width="120" />
        <el-table-column prop="created_at" label="创建时间" width="180" />
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="scope">
            <el-button type="primary" link @click="handleView(scope.row)">查看</el-button>
            <el-button type="warning" link @click="handleEdit(scope.row)">编辑</el-button>
            <el-button type="danger" link @click="handleDelete(scope.row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <div class="pagination" v-if="testCases.length > 0">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          :total="total"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import request from '../utils/request'
import { ElMessage } from 'element-plus'

// 测试用例类型定义
interface TestCase {
  id: number
  test_point_id: number
  case_name: string
  description: string
  steps: Record<string, any>
  input_data: Record<string, any>
  expected_result: Record<string, any>
  priority: string
  status: string
  execution_status: string
  review_comments: Record<string, any>
  is_active: boolean
  created_at: string
  updated_at: string
}

// 筛选表单类型
interface FilterForm {
  projectId: number | ''
  interfaceId: number | ''
  testPointId: number | ''
  status: string
  priority: string
}

// 状态管理
const testCases = ref<TestCase[]>([])
const loading = ref(false)
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)
const selectedTestCases = ref<TestCase[]>([])

// 筛选表单
const filterForm = ref<FilterForm>({
  projectId: '',
  interfaceId: '',
  testPointId: '',
  status: '',
  priority: ''
})

// 获取测试用例列表
const fetchTestCases = async () => {
  loading.value = true
  try {
    const params: any = {
      skip: (currentPage.value - 1) * pageSize.value,
      limit: pageSize.value
    }
    
    // 添加筛选条件
    if (filterForm.value.projectId) {
      params.project_id = filterForm.value.projectId
    }
    if (filterForm.value.interfaceId) {
      params.interface_id = filterForm.value.interfaceId
    }
    if (filterForm.value.testPointId) {
      params.test_point_id = filterForm.value.testPointId
    }
    if (filterForm.value.status) {
      params.status = filterForm.value.status
    }
    if (filterForm.value.priority) {
      params.priority = filterForm.value.priority
    }
    
    const response = await request.get<TestCase[]>('/test-cases', { params })
    testCases.value = response
    total.value = response.length
  } catch (error) {
    ElMessage.error('获取测试用例列表失败')
    console.error('获取测试用例列表失败:', error)
  } finally {
    loading.value = false
  }
}

// 页面加载时获取数据
onMounted(() => {
  fetchTestCases()
})

// 分页处理
const handleSizeChange = (size: number) => {
  pageSize.value = size
  currentPage.value = 1
  fetchTestCases()
}

const handleCurrentChange = (page: number) => {
  currentPage.value = page
  fetchTestCases()
}

// 选择处理
const handleSelectionChange = (selection: TestCase[]) => {
  selectedTestCases.value = selection
}

// 筛选处理
const handleFilter = () => {
  currentPage.value = 1
  fetchTestCases()
}

const handleReset = () => {
  filterForm.value = {
    projectId: '',
    interfaceId: '',
    testPointId: '',
    status: '',
    priority: ''
  }
  currentPage.value = 1
  fetchTestCases()
}

// 获取优先级对应的标签类型
const getPriorityType = (priority: string): string => {
  const priorityMap: Record<string, string> = {
    HIGH: 'danger',
    MEDIUM: 'warning',
    LOW: 'success'
  }
  return priorityMap[priority] || 'info'
}

// 获取状态对应的标签类型
const getStatusType = (status: string): string => {
  const statusMap: Record<string, string> = {
    DRAFT: 'info',
    REVIEWED: 'success',
    EXECUTED: 'primary',
    DEPRECATED: 'danger'
  }
  return statusMap[status] || 'info'
}

// 获取执行状态对应的标签类型
const getExecutionStatusType = (executionStatus: string | undefined): string => {
  if (!executionStatus) return 'info'
  
  const statusMap: Record<string, string> = {
    PASSED: 'success',
    FAILED: 'danger',
    SKIPPED: 'warning',
    BLOCKED: 'info'
  }
  return statusMap[executionStatus] || 'info'
}

// 操作处理
const handleGenerate = () => {
  // 生成测试用例逻辑
  ElMessage.info('生成测试用例功能开发中')
}

const handleAdd = () => {
  // 添加测试用例逻辑
  ElMessage.info('添加测试用例功能开发中')
}

const handleView = (row: TestCase) => {
  // 查看测试用例详情
  ElMessage.info(`查看测试用例: ${row.case_name}`)
}

const handleEdit = (row: TestCase) => {
  // 编辑测试用例
  ElMessage.info(`编辑测试用例: ${row.case_name}`)
}

const handleDelete = (row: TestCase) => {
  // 删除测试用例
  ElMessage.info(`删除测试用例: ${row.case_name}`)
}

const handleBatchDelete = () => {
  // 批量删除测试用例
  ElMessage.info(`批量删除 ${selectedTestCases.value.length} 个测试用例`)
}
</script>

<style scoped>
.test-cases {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-buttons {
  display: flex;
  gap: 10px;
}

.filter-section {
  margin-bottom: 20px;
  padding: 15px;
  background-color: #f5f7fa;
  border-radius: 4px;
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}
</style>
