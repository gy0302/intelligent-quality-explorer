<template>
  <div class="test-points">
    <el-card>
      <template #header>
        <div class="card-header">
          <h2>测试点管理</h2>
          <div class="header-buttons">
            <el-button type="primary" @click="handleGenerate">生成测试点</el-button>
            <el-button type="success" @click="handleAdd">添加测试点</el-button>
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
          <el-form-item label="状态">
            <el-select v-model="filterForm.status" placeholder="请选择状态" width="150">
              <el-option label="草稿" value="DRAFT" />
              <el-option label="已审核" value="REVIEWED" />
              <el-option label="已生成用例" value="CASE_GENERATED" />
              <el-option label="已废弃" value="DEPRECATED" />
            </el-select>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="handleFilter">查询</el-button>
            <el-button @click="handleReset">重置</el-button>
          </el-form-item>
        </el-form>
      </div>
      
      <!-- 测试点列表 -->
      <el-table
        v-loading="loading"
        :data="testPoints"
        style="width: 100%"
        @selection-change="handleSelectionChange"
      >
        <el-table-column type="selection" width="55" />
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="module" label="模块" width="120" />
        <el-table-column prop="name" label="测试点名称" min-width="200" />
        <el-table-column prop="test_type" label="测试类型" width="120" />
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
        <el-table-column prop="description" label="描述" min-width="300" />
        <el-table-column prop="created_at" label="创建时间" width="180" />
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="scope">
            <el-button type="primary" link @click="handleView(scope.row)">查看</el-button>
            <el-button type="warning" link @click="handleEdit(scope.row)">编辑</el-button>
            <el-button type="danger" link @click="handleDelete(scope.row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <div class="pagination" v-if="testPoints.length > 0">
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

// 测试点类型定义
interface TestPoint {
  id: number
  api_project_id: number
  api_interface_id: number
  module: string
  name: string
  description: string
  test_type: string
  priority: string
  status: string
  check_points: Record<string, any>
  input_data: Record<string, any>
  expected_result: Record<string, any>
  special_notes: Record<string, any>
  review_comments: Record<string, any>
  created_at: string
  updated_at: string
}

// 筛选表单类型
interface FilterForm {
  projectId: number | ''
  interfaceId: number | ''
  status: string
}

// 状态管理
const testPoints = ref<TestPoint[]>([])
const loading = ref(false)
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)
const selectedTestPoints = ref<TestPoint[]>([])

// 筛选表单
const filterForm = ref<FilterForm>({
  projectId: '',
  interfaceId: '',
  status: ''
})

// 获取测试点列表
const fetchTestPoints = async () => {
  loading.value = true
  try {
    let url = '/test-points'
    
    if (filterForm.value.projectId) {
      url = `/test-points/project/${filterForm.value.projectId}`
    } else if (filterForm.value.interfaceId) {
      url = `/test-points/interface/${filterForm.value.interfaceId}`
    }
    
    const response = await request.get<TestPoint[]>(url)
    testPoints.value = response
    total.value = response.length
  } catch (error) {
    ElMessage.error('获取测试点列表失败')
    console.error('获取测试点列表失败:', error)
  } finally {
    loading.value = false
  }
}

// 页面加载时获取数据
onMounted(() => {
  fetchTestPoints()
})

// 分页处理
const handleSizeChange = (size: number) => {
  pageSize.value = size
  currentPage.value = 1
  fetchTestPoints()
}

const handleCurrentChange = (page: number) => {
  currentPage.value = page
  fetchTestPoints()
}

// 选择处理
const handleSelectionChange = (selection: TestPoint[]) => {
  selectedTestPoints.value = selection
}

// 筛选处理
const handleFilter = () => {
  currentPage.value = 1
  fetchTestPoints()
}

const handleReset = () => {
  filterForm.value = {
    projectId: '',
    interfaceId: '',
    status: ''
  }
  currentPage.value = 1
  fetchTestPoints()
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
    CASE_GENERATED: 'primary',
    DEPRECATED: 'danger'
  }
  return statusMap[status] || 'info'
}

// 操作处理
const handleGenerate = () => {
  // 生成测试点逻辑
  ElMessage.info('生成测试点功能开发中')
}

const handleAdd = () => {
  // 添加测试点逻辑
  ElMessage.info('添加测试点功能开发中')
}

const handleView = (row: TestPoint) => {
  // 查看测试点详情
  ElMessage.info(`查看测试点: ${row.name}`)
}

const handleEdit = (row: TestPoint) => {
  // 编辑测试点
  ElMessage.info(`编辑测试点: ${row.name}`)
}

const handleDelete = (row: TestPoint) => {
  // 删除测试点
  ElMessage.info(`删除测试点: ${row.name}`)
}
</script>

<style scoped>
.test-points {
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
