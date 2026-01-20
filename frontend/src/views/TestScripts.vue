<template>
  <div class="test-scripts">
    <el-card>
      <template #header>
        <div class="card-header">
          <h2>测试脚本管理</h2>
          <div class="header-buttons">
            <el-button type="primary" @click="handleGenerate">生成测试脚本</el-button>
            <el-button type="success" @click="handleAdd">添加测试脚本</el-button>
            <el-button type="danger" @click="handleBatchDelete" :disabled="selectedTestScripts.length === 0">批量删除</el-button>
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
          <el-form-item label="测试用例ID">
            <el-input v-model="filterForm.testCaseId" placeholder="请输入测试用例ID" width="200" />
          </el-form-item>
          <el-form-item label="脚本类型">
            <el-select v-model="filterForm.scriptType" placeholder="请选择脚本类型" width="150">
              <el-option label="自动化" value="AUTOMATED" />
              <el-option label="手动" value="MANUAL" />
              <el-option label="混合" value="HYBRID" />
            </el-select>
          </el-form-item>
          <el-form-item label="状态">
            <el-select v-model="filterForm.status" placeholder="请选择状态" width="150">
              <el-option label="草稿" value="DRAFT" />
              <el-option label="已审核" value="REVIEWED" />
              <el-option label="已执行" value="EXECUTED" />
              <el-option label="已废弃" value="DEPRECATED" />
            </el-select>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="handleFilter">查询</el-button>
            <el-button @click="handleReset">重置</el-button>
          </el-form-item>
        </el-form>
      </div>
      
      <!-- 测试脚本列表 -->
      <el-table
        v-loading="loading"
        :data="testScripts"
        style="width: 100%"
        @selection-change="handleSelectionChange"
      >
        <el-table-column type="selection" width="55" />
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="test_case_id" label="测试用例ID" width="120" />
        <el-table-column prop="script_type" label="脚本类型" width="120">
          <template #default="scope">
            <el-tag :type="getScriptType(scope.row.script_type)">
              {{ scope.row.script_type }}
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
        <el-table-column prop="created_at" label="创建时间" width="180" />
        <el-table-column prop="updated_at" label="更新时间" width="180" />
        <el-table-column label="操作" width="250" fixed="right">
          <template #default="scope">
            <el-button type="primary" link @click="handleView(scope.row)">查看</el-button>
            <el-button type="info" link @click="handleViewData(scope.row)">查看测试数据</el-button>
            <el-button type="warning" link @click="handleEdit(scope.row)">编辑</el-button>
            <el-button type="danger" link @click="handleDelete(scope.row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <div class="pagination" v-if="testScripts.length > 0">
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

// 测试脚本类型定义
interface TestScript {
  id: number
  test_case_id: number
  script_type: string
  script_content: string
  status: string
  review_comments: Record<string, any>
  created_at: string
  updated_at: string
  test_data: any[]
}

// 筛选表单类型
interface FilterForm {
  projectId: number | ''
  interfaceId: number | ''
  testCaseId: number | ''
  scriptType: string
  status: string
}

// 状态管理
const testScripts = ref<TestScript[]>([])
const loading = ref(false)
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)
const selectedTestScripts = ref<TestScript[]>([])

// 筛选表单
const filterForm = ref<FilterForm>({
  projectId: '',
  interfaceId: '',
  testCaseId: '',
  scriptType: '',
  status: ''
})

// 获取测试脚本列表
const fetchTestScripts = async () => {
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
    if (filterForm.value.testCaseId) {
      params.test_case_id = filterForm.value.testCaseId
    }
    
    const response = await request.get<TestScript[]>('/test-scripts', { params })
    testScripts.value = response
    total.value = response.length
  } catch (error) {
    ElMessage.error('获取测试脚本列表失败')
    console.error('获取测试脚本列表失败:', error)
  } finally {
    loading.value = false
  }
}

// 页面加载时获取数据
onMounted(() => {
  fetchTestScripts()
})

// 分页处理
const handleSizeChange = (size: number) => {
  pageSize.value = size
  currentPage.value = 1
  fetchTestScripts()
}

const handleCurrentChange = (page: number) => {
  currentPage.value = page
  fetchTestScripts()
}

// 选择处理
const handleSelectionChange = (selection: TestScript[]) => {
  selectedTestScripts.value = selection
}

// 筛选处理
const handleFilter = () => {
  currentPage.value = 1
  fetchTestScripts()
}

const handleReset = () => {
  filterForm.value = {
    projectId: '',
    interfaceId: '',
    testCaseId: '',
    scriptType: '',
    status: ''
  }
  currentPage.value = 1
  fetchTestScripts()
}

// 获取脚本类型对应的标签类型
const getScriptType = (scriptType: string): string => {
  const typeMap: Record<string, string> = {
    AUTOMATED: 'primary',
    MANUAL: 'info',
    HYBRID: 'warning'
  }
  return typeMap[scriptType] || 'info'
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

// 操作处理
const handleGenerate = () => {
  // 生成测试脚本逻辑
  ElMessage.info('生成测试脚本功能开发中')
}

const handleAdd = () => {
  // 添加测试脚本逻辑
  ElMessage.info('添加测试脚本功能开发中')
}

const handleView = (row: TestScript) => {
  // 查看测试脚本详情
  ElMessage.info(`查看测试脚本: ${row.id}`)
}

const handleViewData = (row: TestScript) => {
  // 查看测试数据
  ElMessage.info(`查看测试脚本 ${row.id} 的测试数据`)
}

const handleEdit = (row: TestScript) => {
  // 编辑测试脚本
  ElMessage.info(`编辑测试脚本: ${row.id}`)
}

const handleDelete = (row: TestScript) => {
  // 删除测试脚本
  ElMessage.info(`删除测试脚本: ${row.id}`)
}

const handleBatchDelete = () => {
  // 批量删除测试脚本
  ElMessage.info(`批量删除 ${selectedTestScripts.value.length} 个测试脚本`)
}
</script>

<style scoped>
.test-scripts {
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
