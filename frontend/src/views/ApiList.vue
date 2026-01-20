<template>
  <div class="api-list">
    <el-card>
      <template #header>
        <div class="card-header">
          <h2>API项目列表</h2>
          <el-button type="primary" @click="handleAdd">添加项目</el-button>
        </div>
      </template>
      
      <el-table
        v-loading="loading"
        :data="apiProjects"
        style="width: 100%"
        @selection-change="handleSelectionChange"
      >
        <el-table-column type="selection" width="55" />
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="项目名称" min-width="200" />
        <el-table-column prop="description" label="描述" min-width="300" />
        <el-table-column prop="base_url" label="基础URL" min-width="200" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="scope">
            <el-tag :type="scope.row.status === 'active' ? 'success' : 'danger'">
              {{ scope.row.status }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="project_type" label="类型" width="100" />
        <el-table-column prop="created_at" label="创建时间" width="180" />
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="scope">
            <el-button type="primary" link @click="handleView(scope.row)">查看</el-button>
            <el-button type="warning" link @click="handleEdit(scope.row)">编辑</el-button>
            <el-button type="danger" link @click="handleDelete(scope.row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <div class="pagination" v-if="apiProjects.length > 0">
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

// API项目类型定义
interface ApiProject {
  id: number
  name: string
  description: string
  base_url: string
  status: string
  project_type: string
  created_at: string
  // 其他字段根据后端返回的数据添加
}

// 响应数据类型定义
interface ApiResponse<T> {
  status: string
  message: string
  data?: T
}

// 状态管理
const apiProjects = ref<ApiProject[]>([])
const loading = ref(false)
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)
const selectedProjects = ref<ApiProject[]>([])

// 获取API项目列表
const fetchApiProjects = async () => {
  loading.value = true
  try {
    const response = await request.get<ApiProject[]>('/api-projects')
    apiProjects.value = response
    total.value = response.length
  } catch (error) {
    ElMessage.error('获取API项目列表失败')
    console.error('获取API项目列表失败:', error)
  } finally {
    loading.value = false
  }
}

// 页面加载时获取数据
onMounted(() => {
  fetchApiProjects()
})

// 分页处理
const handleSizeChange = (size: number) => {
  pageSize.value = size
  currentPage.value = 1
  fetchApiProjects()
}

const handleCurrentChange = (page: number) => {
  currentPage.value = page
  fetchApiProjects()
}

// 选择处理
const handleSelectionChange = (selection: ApiProject[]) => {
  selectedProjects.value = selection
}

// 操作处理
const handleAdd = () => {
  // 添加项目逻辑
  ElMessage.info('添加项目功能开发中')
}

const handleView = (row: ApiProject) => {
  // 查看项目详情
  ElMessage.info(`查看项目: ${row.name}`)
}

const handleEdit = (row: ApiProject) => {
  // 编辑项目
  ElMessage.info(`编辑项目: ${row.name}`)
}

const handleDelete = (row: ApiProject) => {
  // 删除项目
  ElMessage.info(`删除项目: ${row.name}`)
}
</script>

<style scoped>
.api-list {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}
</style>
