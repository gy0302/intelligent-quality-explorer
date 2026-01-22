<template>
  <div class="project-management">
    <el-card>
      <template #header>
        <div class="card-header">
          <h2>产品项目管理</h2>
          <div class="header-buttons">
            <el-button type="primary" @click="handleAdd">新增项目</el-button>
            <el-button type="danger" @click="handleBatchDelete" :disabled="selectedProjects.length === 0">批量删除</el-button>
            <el-button type="warning" @click="handleBatchEnable" :disabled="selectedProjects.length === 0">批量启用</el-button>
            <el-button type="warning" @click="handleBatchDisable" :disabled="selectedProjects.length === 0">批量禁用</el-button>
            <el-dropdown trigger="click">
              <el-button type="primary" size="default">
                列显示设置 <el-icon class="el-icon--right"><arrow-down /></el-icon>
              </el-button>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item v-for="column in columns" :key="column.prop">
                    <el-checkbox v-model="column.visible">{{ column.label }}</el-checkbox>
                  </el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </div>
        </div>
      </template>
      
      <!-- 查询表单 -->
      <div class="filter-section">
        <el-form :inline="true" :model="filterForm" class="demo-form-inline" style="display: flex; align-items: center; gap: 5px;">
          <el-form-item label="项目名称" style="margin-right: 5px; margin-bottom: 0;">
            <el-input v-model="filterForm.name" placeholder="请输入项目名称" style="width: 160px;" />
          </el-form-item>
          <el-form-item label="项目描述" style="margin-right: 5px; margin-bottom: 0;">
            <el-input v-model="filterForm.description" placeholder="请输入项目描述" style="width: 200px;" />
          </el-form-item>
          <el-form-item label="项目状态" style="margin-right: 5px; margin-bottom: 0;">
            <el-select v-model="filterForm.status" placeholder="请选择项目状态" style="width: 110px;">
              <el-option label="全部" :value="null" />
              <el-option label="激活" :value="'active'" />
              <el-option label="禁用" :value="'inactive'" />
            </el-select>
          </el-form-item>
          <el-form-item style="margin-bottom: 0;">
            <el-button type="primary" @click="handleFilter" size="small">查询</el-button>
            <el-button @click="handleReset" size="small" style="margin-left: 5px;">重置</el-button>
          </el-form-item>
        </el-form>
      </div>
      
      <!-- 项目列表 -->
      <el-table
        v-loading="loading"
        :data="projects"
        style="width: 100%"
        @selection-change="handleSelectionChange"
        :default-sort="{ prop: 'updated_at', order: 'descending' }"
      >
        <el-table-column type="selection" width="55" />
        <el-table-column prop="id" label="项目ID" width="100" sortable v-if="columns[0].visible" />
        <el-table-column prop="name" label="项目名称" min-width="200" sortable v-if="columns[1].visible" />
        <el-table-column prop="description" label="项目描述" min-width="300" show-overflow-tooltip v-if="columns[2].visible" />
        <el-table-column prop="status" label="项目状态" width="120" sortable v-if="columns[3].visible">
          <template #default="scope">
            <el-tag :type="scope.row.status === 'active' ? 'success' : 'danger'">
              {{ scope.row.status === 'active' ? '激活' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="base_url" label="基础URL" min-width="200" show-overflow-tooltip v-if="columns[4].visible" />

        <el-table-column prop="created_at" label="创建时间" width="180" sortable v-if="columns[5].visible">
          <template #default="scope">
            {{ formatDate(scope.row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column prop="updated_at" label="更新时间" width="180" sortable v-if="columns[6].visible">
          <template #default="scope">
            {{ formatDate(scope.row.updated_at) }}
          </template>
        </el-table-column>
        <el-table-column prop="created_by" label="创建人" width="120" show-overflow-tooltip v-if="columns[7].visible" />
        <el-table-column prop="updated_by" label="更新人" width="120" show-overflow-tooltip v-if="columns[8].visible" />
        <el-table-column label="操作" width="240" fixed="right">
          <template #default="scope">
            <el-button type="primary" link @click="handleView(scope.row)">详情</el-button>
            <el-button type="warning" link @click="handleEdit(scope.row)">编辑</el-button>
            <el-button 
              :type="scope.row.status === 'active' ? 'danger' : 'success'" 
              link 
              @click="handleToggleStatus(scope.row)"
              :disabled="scope.row.id === 1"
            >
              {{ scope.row.status === 'active' ? '禁用' : '启用' }}
            </el-button>
            <el-button 
              type="danger" 
              link 
              @click="handleDelete(scope.row)"
              :disabled="scope.row.id === 1"
            >
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <!-- 分页器 -->
      <div class="pagination" v-if="projects.length > 0">
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
    
    <!-- 新增/编辑项目对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="isEditing ? '编辑项目' : '新增项目'"
      width="500px"
    >
      <el-form :model="projectForm" :rules="formRules" ref="formRef" label-width="100px">
        <el-form-item label="项目ID" prop="id" v-if="isEditing">
          <el-input v-model="projectForm.id" readonly />
        </el-form-item>
        <el-form-item label="项目名称" prop="name">
          <el-input v-model="projectForm.name" placeholder="请输入项目名称" />
        </el-form-item>
        <el-form-item label="项目描述" prop="description">
          <el-input v-model="projectForm.description" type="textarea" rows="3" placeholder="请输入项目描述" />
        </el-form-item>
        <el-form-item label="基础URL" prop="base_url">
          <el-input v-model="projectForm.base_url" placeholder="请输入项目基础URL，例如：https://api.example.com/v1" />
        </el-form-item>

        <el-form-item label="项目状态" prop="status">
          <el-select v-model="projectForm.status" placeholder="请选择项目状态">
            <el-option label="激活" value="active" />
            <el-option label="禁用" value="inactive" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleSubmit">确定</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { ArrowDown } from '@element-plus/icons-vue'
import request from '../utils/request'

// 格式化时间函数
const formatDate = (dateString: string) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  })
}

// 项目类型定义
interface Project {
  id: number
  name: string
  description: string
  status: string
  base_url: string
  created_at: string
  updated_at: string
  created_by?: string
  updated_by?: string
}

// 表格列配置
interface TableColumn {
  prop: string
  label: string
  visible: boolean
}

// 筛选表单类型
interface FilterForm {
  name: string
  description: string
  status: string | null
}

// 表单验证规则
const formRules = {
  name: [
    { required: true, message: '请输入项目名称', trigger: 'blur' },
    { min: 2, max: 50, message: '项目名称长度在 2 到 50 个字符', trigger: 'blur' }
  ],
  description: [
    { max: 200, message: '项目描述长度不超过 200 个字符', trigger: 'blur' }
  ],
  base_url: [
    { required: false, message: '请输入项目基础URL', trigger: 'blur' },
    { pattern: /^(http|https):\/\/.+$/i, message: '请输入有效的URL，必须以http://或https://开头', trigger: 'blur', validator: (rule: any, value: any, callback: any) => {
        if (!value) {
          callback()
          return
        }
        // 使用正则表达式验证URL格式
        const urlPattern = /^(http|https):\/\/.+$/i
        if (urlPattern.test(value)) {
          callback()
        } else {
          callback(new Error('请输入有效的URL，必须以http://或https://开头'))
        }
      }}
  ],
  status: [
    { required: true, message: '请选择项目状态', trigger: 'change' }
  ]
}

// 状态管理
const projects = ref<Project[]>([])
const loading = ref(false)
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)
const selectedProjects = ref<Project[]>([])
const dialogVisible = ref(false)
const isEditing = ref(false)
const formRef = ref()

// 表格列配置
const columns = ref<TableColumn[]>([
  { prop: 'id', label: '项目ID', visible: true },
  { prop: 'name', label: '项目名称', visible: true },
  { prop: 'description', label: '项目描述', visible: true },
  { prop: 'status', label: '项目状态', visible: true },
  { prop: 'base_url', label: '基础URL', visible: true },
  { prop: 'created_at', label: '创建时间', visible: true },
  { prop: 'updated_at', label: '更新时间', visible: true },
  { prop: 'created_by', label: '创建人', visible: true },
  { prop: 'updated_by', label: '更新人', visible: true }
])

// 筛选表单
const filterForm = reactive<FilterForm>({
  name: '',
  description: '',
  status: null
})

// 项目表单
const projectForm = reactive({
  id: 0,
  name: '',
  description: '',
  base_url: '',
  status: 'active'
})

// 获取项目列表
const fetchProjects = async () => {
  loading.value = true
  try {
    const params: any = {
      skip: (currentPage.value - 1) * pageSize.value,
      limit: pageSize.value
    }
    
    // 添加筛选条件
    if (filterForm.name) {
      params.name = filterForm.name
    }
    if (filterForm.description) {
      params.description = filterForm.description
    }
    if (filterForm.status !== null) {
      params.status = filterForm.status
    }
    
    const response = await request.get('/projects', { params })
    projects.value = response as unknown as Project[]
    total.value = projects.value.length
  } catch (error: any) {
    ElMessage.error(`获取项目列表失败: ${error.response?.data?.detail || error.message || '网络错误'}`)
    console.error('获取项目列表失败:', error)
    projects.value = []
    total.value = 0
  } finally {
    loading.value = false
  }
}

// 页面加载时获取数据
onMounted(() => {
  fetchProjects()
})

// 分页处理
const handleSizeChange = (size: number) => {
  pageSize.value = size
  currentPage.value = 1
  fetchProjects()
}

const handleCurrentChange = (page: number) => {
  currentPage.value = page
  fetchProjects()
}

// 选择处理
const handleSelectionChange = (selection: Project[]) => {
  selectedProjects.value = selection
}

// 筛选处理
const handleFilter = () => {
  currentPage.value = 1
  fetchProjects()
}

const handleReset = () => {
  filterForm.name = ''
  filterForm.description = ''
  filterForm.status = null
  currentPage.value = 1
  fetchProjects()
}

// 对话框处理
const resetForm = () => {
  if (formRef.value) {
    formRef.value.resetFields()
  }
  projectForm.id = 0
  projectForm.name = ''
  projectForm.description = ''
  projectForm.base_url = ''
  projectForm.status = 'active'
}

const handleAdd = () => {
  isEditing.value = false
  resetForm()
  dialogVisible.value = true
}

const handleEdit = (row: Project) => {
  isEditing.value = true
  Object.assign(projectForm, row)
  dialogVisible.value = true
}

const handleSubmit = async () => {
  if (!formRef.value) return
  
  try {
    await formRef.value.validate()
    
    if (isEditing.value) {
      await request.put(`/projects/${projectForm.id}`, projectForm)
      ElMessage.success('项目更新成功')
    } else {
      await request.post('/projects', projectForm)
      ElMessage.success('项目新增成功')
    }
    
    dialogVisible.value = false
    fetchProjects()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(`提交失败: ${error.response?.data?.detail || error.message || '操作失败'}`)
      console.error('提交失败:', error)
    }
  }
}

// 操作处理
const handleView = (row: Project) => {
  ElMessage.info(`查看项目: ${row.name}`)
}

const handleToggleStatus = async (row: Project) => {
  if (row.id === 1 && row.status === 'active') {
    ElMessage.warning('默认项目不可禁用')
    return
  }
  
  try {
    const newStatus = row.status === 'active' ? 'inactive' : 'active'
    await request.put(`/projects/${row.id}/status`, { status: newStatus })
    ElMessage.success(`项目${newStatus === 'active' ? '启用' : '禁用'}成功`)
    fetchProjects()
  } catch (error: any) {
    ElMessage.error(`项目${row.status === 'active' ? '禁用' : '启用'}失败: ${error.response?.data?.detail || '操作失败'}`)
    console.error('切换项目状态失败:', error)
  }
}

const handleDelete = async (row: Project) => {
  if (row.id === 1) {
    ElMessage.warning('默认项目不可删除')
    return
  }
  
  try {
    await ElMessageBox.confirm(`确定要删除项目「${row.name}」吗？`, '删除项目', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    await request.delete(`/projects/${row.id}`)
    ElMessage.success('项目删除成功')
    fetchProjects()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(`项目删除失败: ${error.response?.data?.detail || '操作失败'}`)
      console.error('删除项目失败:', error)
    }
  }
}

// 批量操作
const handleBatchDelete = async () => {
  try {
    await ElMessageBox.confirm(`确定要删除选中的${selectedProjects.value.length}个项目吗？`, '批量删除', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    const projectIds = selectedProjects.value.map(project => project.id)
    await request.delete('/projects/batch', { data: { project_ids: projectIds } })
    
    ElMessage.success('批量删除成功')
    fetchProjects()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(`批量删除失败: ${error.response?.data?.detail || '操作失败'}`)
      console.error('批量删除项目失败:', error)
    }
  }
}

const handleBatchEnable = async () => {
  try {
    await ElMessageBox.confirm(`确定要启用选中的${selectedProjects.value.length}个项目吗？`, '批量启用', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    const projectIds = selectedProjects.value.map(project => project.id)
    await request.put('/projects/batch/status', { project_ids: projectIds, status: 'active' })
    
    ElMessage.success('批量启用成功')
    fetchProjects()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(`批量启用失败: ${error.response?.data?.detail || '操作失败'}`)
      console.error('批量启用项目失败:', error)
    }
  }
}

const handleBatchDisable = async () => {
  try {
    const hasDefaultProject = selectedProjects.value.some(project => project.id === 1)
    if (hasDefaultProject) {
      ElMessage.warning('默认项目不可禁用')
      return
    }
    
    await ElMessageBox.confirm(`确定要禁用选中的${selectedProjects.value.length}个项目吗？`, '批量禁用', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    const projectIds = selectedProjects.value.map(project => project.id)
    await request.put('/projects/batch/status', { project_ids: projectIds, status: 'inactive' })
    
    ElMessage.success('批量禁用成功')
    fetchProjects()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(`批量禁用失败: ${error.response?.data?.detail || '操作失败'}`)
      console.error('批量禁用项目失败:', error)
    }
  }
}
</script>

<style scoped>
.project-management {
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