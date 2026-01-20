<template>
  <div class="api-list">
    <el-card>
      <template #header>
        <div class="card-header">
          <h2>接口管理</h2>
          <div class="header-buttons">
            <el-button type="primary" @click="handleAdd">添加接口</el-button>
            <el-button type="success" @click="openImportDialog">导入API</el-button>
          </div>
        </div>
      </template>
      
      <el-table
        v-loading="loading"
        :data="apiInterfaces"
        style="width: 100%"
        @selection-change="handleSelectionChange"
      >
        <el-table-column type="selection" width="55" />
        <el-table-column prop="id" label="接口ID" width="80" />
        <el-table-column prop="path" label="接口路径" min-width="200" />
        <el-table-column prop="method" label="请求方法" width="100">
          <template #default="scope">
            <el-tag :type="getMethodType(scope.row.method)">
              {{ scope.row.method }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="name" label="接口名称" min-width="200" />
        <el-table-column prop="description" label="接口描述" min-width="300" />
        <el-table-column prop="project_id" label="所属项目ID" width="120" />
        <el-table-column prop="created_at" label="创建时间" width="180" />
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="scope">
            <el-button type="primary" link @click="handleView(scope.row)">查看</el-button>
            <el-button type="warning" link @click="handleEdit(scope.row)">编辑</el-button>
            <el-button type="danger" link @click="handleDelete(scope.row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <div class="pagination" v-if="apiInterfaces.length > 0">
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
    
    <!-- API导入对话框 -->
    <el-dialog
      v-model="importDialogVisible"
      title="导入API规范"
      width="600px"
    >
      <!-- API导入方式切换 -->
      <el-tabs v-model="importActiveTab" class="import-tabs">
        <el-tab-pane label="上传文件" name="file">
          <el-form ref="fileFormRef" :model="fileForm" label-width="100px">
            <el-form-item label="所属项目">
              <el-select v-model="fileForm.projectId" placeholder="请选择要导入到的项目" filterable>
                <el-option
                  v-for="project in projects"
                  :key="project.id"
                  :label="project.name"
                  :value="project.id"
                />
              </el-select>
            </el-form-item>
            
            <el-form-item label="选择文件">
              <el-upload
                ref="uploadRef"
                v-model:file-list="fileList"
                accept=".json,.yaml,.yml"
                :auto-upload="false"
                :on-change="handleFileChange"
                :show-file-list="true"
                drag
              >
                <el-icon class="el-icon--upload"><Upload /></el-icon>
                <div class="el-upload__text">
                  将文件拖到此处，或<em>点击上传</em>
                </div>
                <template #tip>
                  <div class="el-upload__tip">
                    支持上传 .json, .yaml, .yml 格式的 OpenAPI/Swagger 文件
                  </div>
                </template>
              </el-upload>
            </el-form-item>
          </el-form>
        </el-tab-pane>
        
        <el-tab-pane label="通过URL导入" name="url">
          <el-form ref="urlFormRef" :model="urlForm" label-width="100px">
            <el-form-item label="所属项目">
              <el-select v-model="urlForm.projectId" placeholder="请选择要导入到的项目" filterable>
                <el-option
                  v-for="project in projects"
                  :key="project.id"
                  :label="project.name"
                  :value="project.id"
                />
              </el-select>
            </el-form-item>
            
            <el-form-item label="API URL">
              <el-input v-model="urlForm.apiUrl" placeholder="请输入API规范URL（如：http://example.com/openapi.json）" />
            </el-form-item>
          </el-form>
        </el-tab-pane>
      </el-tabs>
      
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="importDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleImportSubmit" :loading="isImporting">
            <el-icon v-if="isImporting"><Loading /></el-icon>
            导入API
          </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import request from '../utils/request'
import { ElMessage } from 'element-plus'
import { Upload, Loading } from '@element-plus/icons-vue'
import type { FormInstance, UploadInstance } from 'element-plus'

// API接口类型定义
interface ApiInterface {
  id: number
  path: string
  method: string
  name: string
  description: string
  project_id: number
  created_at: string
  // 其他字段根据后端返回的数据添加
}

// 项目类型定义
interface Project {
  id: number
  name: string
  description: string
  status: string
  created_at: string
}

// 响应数据类型定义已移除，直接使用返回的数据类型

// 状态管理
const apiInterfaces = ref<ApiInterface[]>([])
const loading = ref(false)
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)
const selectedInterfaces = ref<ApiInterface[]>([])

// API导入相关状态
const importDialogVisible = ref(false)
const importActiveTab = ref('file')
const isImporting = ref(false)

// 项目列表（用于选择要导入到的项目）
const projects = ref<Project[]>([])

// 文件导入表单
const fileFormRef = ref<FormInstance>()
const fileForm = ref({
  projectId: 0
})

// 文件上传
const uploadRef = ref<UploadInstance>()
const fileList = ref<any[]>([])
const selectedFile = ref<File | null>(null)

// URL导入表单
const urlFormRef = ref<FormInstance>()
const urlForm = ref({
  projectId: 0,
  apiUrl: ''
})

// 获取请求方法对应的标签类型
const getMethodType = (method: string): string => {
  const methodMap: Record<string, string> = {
    GET: 'success',
    POST: 'primary',
    PUT: 'warning',
    DELETE: 'danger',
    PATCH: 'info'
  }
  return methodMap[method] || 'info'
}

// 获取项目列表
const fetchProjects = async () => {
  try {
    const response = await request.get('/projects')
    // 只显示已启动的项目
    projects.value = (response as unknown as Project[]).filter(project => project.status === 'active')
  } catch (error) {
    ElMessage.error('获取项目列表失败')
    console.error('获取项目列表失败:', error)
  }
}

// 获取API接口列表
const fetchApiInterfaces = async () => {
  loading.value = true
  try {
    // 这里需要根据实际情况修改API端点，假设我们有一个active项目，id为1
    // 实际应用中应该从项目选择器获取project_id
    const projectId = 1
    const response = await request.get(`/projects/${projectId}/interfaces`)
    apiInterfaces.value = response as unknown as ApiInterface[]
    total.value = (response as unknown as ApiInterface[]).length
  } catch (error) {
    ElMessage.error('获取API接口列表失败')
    console.error('获取API接口列表失败:', error)
  } finally {
    loading.value = false
  }
}

// 页面加载时获取数据
onMounted(() => {
  fetchApiInterfaces()
  fetchProjects()
})

// 分页处理
const handleSizeChange = (size: number) => {
  pageSize.value = size
  currentPage.value = 1
  fetchApiInterfaces()
}

const handleCurrentChange = (page: number) => {
  currentPage.value = page
  fetchApiInterfaces()
}

// 选择处理
const handleSelectionChange = (selection: ApiInterface[]) => {
  selectedInterfaces.value = selection
}

// 操作处理
const handleAdd = () => {
  // 添加接口逻辑
  ElMessage.info('添加接口功能开发中')
}

const handleView = (row: ApiInterface) => {
  // 查看接口详情
  ElMessage.info(`查看接口: ${row.name}`)
}

const handleEdit = (row: ApiInterface) => {
  // 编辑接口
  ElMessage.info(`编辑接口: ${row.name}`)
}

const handleDelete = (row: ApiInterface) => {
  // 删除接口
  ElMessage.info(`删除接口: ${row.name}`)
}

// API导入相关方法
const openImportDialog = () => {
  // 打开对话框前刷新项目列表
  fetchProjects()
  importDialogVisible.value = true
}

const handleFileChange = (file: any) => {
  selectedFile.value = file.raw
  fileList.value = [file]
}

const handleImportSubmit = async () => {
  if (importActiveTab.value === 'file') {
    // 文件导入
    await handleFileImport()
  } else {
    // URL导入
    await handleUrlImport()
  }
}

// 文件导入
const handleFileImport = async () => {
  if (!fileForm.value.projectId) {
    return ElMessage.warning('请选择所属项目')
  }
  
  if (!selectedFile.value) {
    return ElMessage.warning('请选择文件')
  }
  
  isImporting.value = true
  
  try {
    const formData = new FormData()
    formData.append('file', selectedFile.value)
    
    await request.post(`/projects/${fileForm.value.projectId}/import-spec`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
    
    ElMessage.success('API导入成功')
    importDialogVisible.value = false
    resetImportForms()
    // 刷新接口列表
    fetchApiInterfaces()
  } catch (error) {
    ElMessage.error('API导入失败')
    console.error('API导入失败:', error)
  } finally {
    isImporting.value = false
  }
}

// URL导入
const handleUrlImport = async () => {
  if (!urlForm.value.projectId) {
    return ElMessage.warning('请选择所属项目')
  }
  
  if (!urlForm.value.apiUrl) {
    return ElMessage.warning('请输入API URL')
  }
  
  isImporting.value = true
  
  try {
    await request.post(`/projects/${urlForm.value.projectId}/import-spec-url`, {
      url: urlForm.value.apiUrl
    })
    
    ElMessage.success('API导入成功')
    importDialogVisible.value = false
    resetImportForms()
    // 刷新接口列表
    fetchApiInterfaces()
  } catch (error) {
    ElMessage.error('API导入失败')
    console.error('API导入失败:', error)
  } finally {
    isImporting.value = false
  }
}

// 重置导入表单
const resetImportForms = () => {
  fileFormRef.value?.resetFields()
  urlFormRef.value?.resetFields()
  fileList.value = []
  selectedFile.value = null
  fileForm.value.projectId = 0
  urlForm.value.projectId = 0
  urlForm.value.apiUrl = ''
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

.header-buttons {
  display: flex;
  gap: 10px;
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

.import-tabs {
  margin-top: 20px;
}
</style>
