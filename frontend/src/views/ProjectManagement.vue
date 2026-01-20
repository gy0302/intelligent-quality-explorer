<template>
  <div class="project-management">
    <el-card>
      <template #header>
        <div class="card-header">
          <h2>产品项目管理</h2>
          <div class="header-buttons">
            <el-button type="primary" @click="handleAdd">新增产品项目</el-button>
            <el-button type="danger" @click="handleBatchDelete" :disabled="selectedProjects.length === 0">批量删除</el-button>
            <el-button type="warning" @click="handleBatchEnable" :disabled="selectedProjects.length === 0">批量启用</el-button>
            <el-button type="warning" @click="handleBatchDisable" :disabled="selectedProjects.length === 0">批量禁用</el-button>
          </div>
        </div>
      </template>
      
      <!-- 查询表单 -->
      <div class="filter-section">
        <el-form :inline="true" :model="filterForm" class="demo-form-inline">
          <el-form-item label="项目名称">
            <el-input v-model="filterForm.name" placeholder="请输入项目名称" width="200" />
          </el-form-item>
          <el-form-item label="项目描述">
            <el-input v-model="filterForm.description" placeholder="请输入项目描述" width="300" />
          </el-form-item>
          <el-form-item label="项目状态">
            <el-select v-model="filterForm.status" placeholder="请选择项目状态" style="width: 200px;">
              <el-option label="全部" :value="null" />
              <el-option label="激活" :value="'active'" />
              <el-option label="禁用" :value="'inactive'" />
            </el-select>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="handleFilter">查询</el-button>
            <el-button @click="handleReset">重置</el-button>
          </el-form-item>
        </el-form>
      </div>
      
      <!-- 项目列表 -->
      <el-table
        v-loading="loading"
        :data="projects"
        style="width: 100%"
        @selection-change="handleSelectionChange"
      >
        <el-table-column type="selection" width="55" />
        <el-table-column prop="id" label="项目ID" width="100" />
        <el-table-column prop="name" label="项目名称" min-width="200" />
        <el-table-column prop="description" label="项目描述" min-width="300" />
        <el-table-column prop="status" label="项目状态" width="120">
          <template #default="scope">
            <el-tag :type="scope.row.status === 'active' ? 'success' : 'danger'">
              {{ scope.row.status === 'active' ? '激活' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="base_url" label="基础URL" min-width="200" />
        <el-table-column prop="project_type" label="项目类型" width="120" />
        <el-table-column prop="created_at" label="创建时间" width="180" />
        <el-table-column prop="updated_at" label="更新时间" width="180" />
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="scope">
            <el-button type="primary" link @click="handleView(scope.row)">查看</el-button>
            <el-button type="warning" link @click="handleEdit(scope.row)">编辑</el-button>
            <el-button 
              :type="scope.row.status === 'active' ? 'danger' : 'success'" 
              link 
              @click="handleToggleStatus(scope.row)"
            >
              {{ scope.row.status === 'active' ? '禁用' : '启用' }}
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
    
    <!-- 新增/编辑产品项目对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="isEditing ? '编辑产品项目' : '新增产品项目'"
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
          <el-input v-model="projectForm.base_url" placeholder="请输入项目基础URL" />
        </el-form-item>
        <el-form-item label="项目类型" prop="project_type">
          <el-select v-model="projectForm.project_type" placeholder="请选择项目类型">
            <el-option label="REST" value="REST" />
            <el-option label="GraphQL" value="GraphQL" />
            <el-option label="gRPC" value="gRPC" />
          </el-select>
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
import request from '../utils/request'

// 项目类型定义
interface Project {
  id: number
  name: string
  description: string
  status: string
  base_url: string
  project_type: string
  created_at: string
  updated_at: string
  // 其他字段根据实际需求添加
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
    { required: true, message: '请输入项目基础URL', trigger: 'blur' },
    { type: 'url', message: '请输入有效的URL', trigger: 'blur' }
  ],
  project_type: [
    { required: true, message: '请选择项目类型', trigger: 'change' }
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
  project_type: 'REST',
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
    total.value = (response as unknown as Project[]).length // 实际项目中应该从后端获取total
  } catch (error) {
    ElMessage.error('获取项目列表失败')
    console.error('获取项目列表失败:', error)
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
  projectForm.project_type = 'REST'
  projectForm.status = 'active'
}

const handleAdd = () => {
  isEditing.value = false
  resetForm()
  dialogVisible.value = true
}

const handleEdit = (row: Project) => {
  isEditing.value = true
  // 填充表单数据
  Object.assign(projectForm, row)
  dialogVisible.value = true
}

const handleSubmit = async () => {
  if (!formRef.value) return
  
  try {
    await formRef.value.validate()
    
    if (isEditing.value) {
      // 更新项目
      await request.put(`/projects/${projectForm.id}`, projectForm)
      ElMessage.success('项目更新成功')
    } else {
      // 新增项目
      await request.post('/projects', projectForm)
      ElMessage.success('项目新增成功')
    }
    
    dialogVisible.value = false
    fetchProjects()
  } catch (error) {
    console.error('提交失败:', error)
  }
}

// 操作处理
const handleView = (row: Project) => {
  ElMessage.info(`查看项目: ${row.name}`)
}

const handleToggleStatus = async (row: Project) => {
  try {
    const newStatus = row.status === 'active' ? 'inactive' : 'active'
    await request.put(`/projects/${row.id}`, { status: newStatus })
    ElMessage.success(`项目${newStatus === 'active' ? '启用' : '禁用'}成功`)
    fetchProjects()
  } catch (error) {
    ElMessage.error(`项目${row.status === 'active' ? '禁用' : '启用'}失败`)
    console.error('切换项目状态失败:', error)
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
    
    // 实际项目中应该使用批量删除API
    for (const project of selectedProjects.value) {
      await request.delete(`/projects/${project.id}`)
    }
    
    ElMessage.success('批量删除成功')
    fetchProjects()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('批量删除失败')
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
    
    // 实际项目中应该使用批量更新API
    for (const project of selectedProjects.value) {
      await request.put(`/projects/${project.id}`, { status: 'active' })
    }
    
    ElMessage.success('批量启用成功')
    fetchProjects()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('批量启用失败')
      console.error('批量启用项目失败:', error)
    }
  }
}

const handleBatchDisable = async () => {
  try {
    await ElMessageBox.confirm(`确定要禁用选中的${selectedProjects.value.length}个项目吗？`, '批量禁用', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    // 实际项目中应该使用批量更新API
    for (const project of selectedProjects.value) {
      await request.put(`/projects/${project.id}`, { status: 'inactive' })
    }
    
    ElMessage.success('批量禁用成功')
    fetchProjects()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('批量禁用失败')
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