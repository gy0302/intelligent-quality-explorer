<template>
  <div class="api-import">
    <h2>API导入</h2>
    
    <el-card>
      <template #header>
        <div class="card-header">
          <span>导入API规范</span>
          <el-button type="primary" @click="refreshProjects">刷新项目列表</el-button>
        </div>
      </template>
      
      <!-- API导入方式切换 -->
      <el-tabs v-model="activeTab" class="import-tabs">
        <el-tab-pane label="上传文件" name="file">
          <el-form ref="fileFormRef" :model="fileForm" label-width="100px">
            <el-form-item label="项目名称">
              <el-input v-model="fileForm.projectName" placeholder="请输入API项目名称" />
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
            
            <el-form-item label="描述">
              <el-input
                v-model="fileForm.description"
                type="textarea"
                :rows="3"
                placeholder="请输入API项目描述"
              />
            </el-form-item>
            
            <el-form-item>
              <el-button type="primary" @click="handleFileImport" :loading="isImporting">
                <el-icon v-if="isImporting"><Loading /></el-icon>
                导入API
              </el-button>
              <el-button @click="resetFileForm">重置</el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>
        
        <el-tab-pane label="通过URL导入" name="url">
          <el-form ref="urlFormRef" :model="urlForm" label-width="100px">
            <el-form-item label="项目名称">
              <el-input v-model="urlForm.projectName" placeholder="请输入API项目名称" />
            </el-form-item>
            
            <el-form-item label="API URL">
              <el-input v-model="urlForm.apiUrl" placeholder="请输入API规范URL（如：http://example.com/openapi.json）" />
            </el-form-item>
            
            <el-form-item label="描述">
              <el-input
                v-model="urlForm.description"
                type="textarea"
                :rows="3"
                placeholder="请输入API项目描述"
              />
            </el-form-item>
            
            <el-form-item>
              <el-button type="primary" @click="handleUrlImport" :loading="isImporting">
                <el-icon v-if="isImporting"><Loading /></el-icon>
                导入API
              </el-button>
              <el-button @click="resetUrlForm">重置</el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>
      </el-tabs>
    </el-card>
    
    <!-- API项目列表 -->
    <el-card>
      <template #header>
        <div class="card-header">
          <span>API项目列表</span>
        </div>
      </template>
      
      <el-table :data="apiProjects" stripe style="width: 100%">
        <el-table-column prop="id" label="项目ID" width="80" />
        <el-table-column prop="name" label="项目名称" width="200" />
        <el-table-column prop="description" label="描述" />
        <el-table-column prop="spec_version" label="规范版本" width="120" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="scope">
            <el-tag :type="scope.row.status === 'active' ? 'success' : 'info'">
              {{ scope.row.status === 'active' ? '活跃' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180" />
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="scope">
            <el-button type="primary" size="small" @click="viewProject(scope.row)">
              查看
            </el-button>
            <el-button type="danger" size="small" @click="deleteProject(scope.row.id)">
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Upload, Loading } from '@element-plus/icons-vue'
import type { FormInstance, UploadInstance } from 'element-plus'
import { ElMessage, ElMessageBox } from 'element-plus'

const router = useRouter()

// 导入状态
const isImporting = ref(false)
const activeTab = ref('file')

// 文件导入表单
const fileFormRef = ref<FormInstance>()
const fileForm = reactive({
  projectName: '',
  description: ''
})

// 文件上传
const uploadRef = ref<UploadInstance>()
const fileList = ref<any[]>([])
const selectedFile = ref<File | null>(null)

// URL导入表单
const urlFormRef = ref<FormInstance>()
const urlForm = reactive({
  projectName: '',
  apiUrl: '',
  description: ''
})

// API项目列表
const apiProjects = ref([
  {
    id: 1,
    name: '用户管理系统',
    description: '用户管理系统API',
    spec_version: '3.0.0',
    status: 'active',
    created_at: '2024-01-10 15:30:00'
  },
  {
    id: 2,
    name: '订单系统',
    description: '订单管理系统API',
    spec_version: '2.0.0',
    status: 'active',
    created_at: '2024-01-09 14:20:00'
  },
  {
    id: 3,
    name: '支付系统',
    description: '支付处理系统API',
    spec_version: '3.0.0',
    status: 'active',
    created_at: '2024-01-08 10:15:00'
  }
])

// 文件变更处理
const handleFileChange = (file: any) => {
  selectedFile.value = file.raw
  fileList.value = [file]
}

// 文件导入
const handleFileImport = async () => {
  if (!fileForm.projectName) {
    return ElMessage.warning('请输入项目名称')
  }
  
  if (!selectedFile.value) {
    return ElMessage.warning('请选择文件')
  }
  
  isImporting.value = true
  
  try {
    // 模拟API调用
    await new Promise(resolve => setTimeout(resolve, 1500))
    
    ElMessage.success('API导入成功')
    
    // 重置表单
    resetFileForm()
    refreshProjects()
  } catch (error) {
    ElMessage.error('API导入失败')
  } finally {
    isImporting.value = false
  }
}

// URL导入
const handleUrlImport = async () => {
  if (!urlForm.projectName) {
    return ElMessage.warning('请输入项目名称')
  }
  
  if (!urlForm.apiUrl) {
    return ElMessage.warning('请输入API URL')
  }
  
  isImporting.value = true
  
  try {
    // 模拟API调用
    await new Promise(resolve => setTimeout(resolve, 1500))
    
    ElMessage.success('API导入成功')
    
    // 重置表单
    resetUrlForm()
    refreshProjects()
  } catch (error) {
    ElMessage.error('API导入失败')
  } finally {
    isImporting.value = false
  }
}

// 重置文件表单
const resetFileForm = () => {
  fileFormRef.value?.resetFields()
  fileList.value = []
  selectedFile.value = null
}

// 重置URL表单
const resetUrlForm = () => {
  urlFormRef.value?.resetFields()
}

// 刷新项目列表
const refreshProjects = () => {
  // 模拟API调用获取最新项目列表
  ElMessage.info('项目列表已刷新')
}

// 查看项目详情
const viewProject = (project: any) => {
  router.push(`/api/${project.id}`)
}

// 删除项目
const deleteProject = (projectId: number) => {
  ElMessageBox.confirm('确定要删除这个API项目吗？', '警告', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(() => {
    // 模拟删除API调用
    apiProjects.value = apiProjects.value.filter(project => project.id !== projectId)
    ElMessage.success('项目删除成功')
  }).catch(() => {
    // 取消删除
  })
}

// 页面加载时刷新项目列表
onMounted(() => {
  refreshProjects()
})
</script>

<style scoped>
.api-import {
  padding: 20px 0;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.import-tabs {
  margin-top: 20px;
}

.el-upload {
  margin-bottom: 20px;
}
</style>
