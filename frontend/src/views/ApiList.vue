<template>
  <div class="api-management">
    <!-- 页面标题 -->
    <div class="page-header">
      <h2>接口管理</h2>
    </div>
    
    <!-- 主内容区域 -->
    <div class="main-content">
      <!-- 左侧面板：项目切换 + 分组管理 -->
      <div class="left-panel">
        <div class="panel-container">
          <!-- 项目选择 -->
          <div class="panel-section">
            <div class="section-header">
              <h3>项目切换</h3>
            </div>
            <div class="section-content">
              <el-select 
                v-model="selectedProjectId" 
                placeholder="请选择项目" 
                filterable
                @change="onProjectChange"
                style="width: 100%; margin-bottom: 10px;"
              >
                <el-option
                  v-for="project in projects"
                  :key="project.id"
                  :label="project.name"
                  :value="project.id"
                />
              </el-select>
            </div>
          </div>
          
          <!-- API分组 -->
          <div class="panel-section">
            <div class="section-header">
              <h3>API分组</h3>
              <div class="header-actions">
                <el-button type="primary" size="small" @click="handleAddGroup" circle>
                  <el-icon><Plus /></el-icon>
                </el-button>
                <el-button type="danger" size="small" @click="handleDeleteGroup" :disabled="!selectedGroup" circle>
                  <el-icon><Delete /></el-icon>
                </el-button>
              </div>
            </div>
            <div class="section-content group-content">
              <el-tree
                :current-node-key="selectedGroup"
                :data="apiGroups"
                :props="groupTreeProps"
                node-key="id"
                default-expand-all
                :indent="16"
                @node-click="handleSelectGroup"
                @node-contextmenu="handleNodeContextMenu"
              >
                <template #default="{ node, data }">
                  <div class="tree-node">
                    <span @click="handleSelectGroup(data)">{{ node.label }}</span>
                    <span class="node-actions">
                      <el-button type="text" size="small" @click.stop="handleRenameGroup(data)">
                        <el-icon><Edit /></el-icon>
                      </el-button>
                    </span>
                  </div>
                </template>
              </el-tree>
              
              <!-- 右键菜单 -->
              <div v-show="contextMenuVisible" :style="contextMenuStyle" class="custom-context-menu">
                <div class="context-menu-item" @click="handleAddChildGroup">
                  <el-icon><Plus /></el-icon> 新增子分组
                </div>
                <div class="context-menu-item" @click="handleEditGroup">
                  <el-icon><Edit /></el-icon> 编辑
                </div>
                <div class="context-menu-divider"></div>
                <div class="context-menu-item" @click="handleDeleteContextGroup">
                  <el-icon><Delete /></el-icon> 删除
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 右侧面板：接口管理 -->
      <div class="right-panel">
        <div class="panel-container">
          <!-- 接口列表标题 -->
          <div class="panel-section">
            <div class="section-header title-header">
              <h3>接口列表</h3>
            </div>
          </div>
          
          <!-- 操作栏 -->
          <div class="panel-section">
            <div class="section-header action-header">
              <div class="header-actions-left">
                <el-button type="primary" @click="handleAddApi">
                  <el-icon><Plus /></el-icon> 新增接口
                </el-button>
                <el-button type="success" @click="openImportDialog">
                  <el-icon><Upload /></el-icon> 导入API
                </el-button>
              </div>
              <div class="header-actions header-actions-right">
                <el-button type="danger" @click="handleBatchDelete" :disabled="selectedInterfaces.length === 0">
                  <el-icon><Delete /></el-icon> 批量删除
                </el-button>
                <el-button type="warning" @click="handleBatchEnable" :disabled="selectedInterfaces.length === 0">
                  <el-icon><CirclePlus /></el-icon> 批量启用
                </el-button>
                <el-button type="warning" @click="handleBatchDisable" :disabled="selectedInterfaces.length === 0">
                  <el-icon><CircleClose /></el-icon> 批量禁用
                </el-button>
                <el-dropdown trigger="click">
                  <el-button type="primary" size="default">
                    列显示设置 <el-icon class="el-icon--right"><ArrowDown /></el-icon>
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
            
            <!-- 搜索栏 -->
            <div class="search-container">
              <el-form :inline="true" :model="searchForm" class="search-form">
                <el-form-item label="接口名称">
                  <el-input 
                    v-model="searchForm.name" 
                    placeholder="输入接口名称搜索" 
                    prefix-icon="Search"
                    style="width: 160px;"
                    @keyup.enter="handleSearch"
                  />
                </el-form-item>
                <el-form-item label="接口路径">
                  <el-input 
                    v-model="searchForm.path" 
                    placeholder="输入接口路径搜索" 
                    prefix-icon="Search"
                    style="width: 160px;"
                    @keyup.enter="handleSearch"
                  />
                </el-form-item>
                <el-form-item label="接口状态">
                  <el-select v-model="searchForm.status" placeholder="全部" style="width: 100px;">
                    <el-option label="全部" :value="''" />
                    <el-option label="启用" :value="'active'" />
                    <el-option label="禁用" :value="'inactive'" />
                  </el-select>
                </el-form-item>
                <el-form-item label="请求方法">
                  <el-select v-model="searchForm.method" placeholder="全部" style="width: 100px;">
                    <el-option label="全部" :value="''" />
                    <el-option label="GET" value="GET" />
                    <el-option label="POST" value="POST" />
                    <el-option label="PUT" value="PUT" />
                    <el-option label="DELETE" value="DELETE" />
                  </el-select>
                </el-form-item>
                <el-form-item>
                  <el-button type="primary" @click="handleSearch">查询</el-button>
                  <el-button @click="handleResetSearch">重置</el-button>
                </el-form-item>
              </el-form>
            </div>
          </div>
          
          <!-- 接口列表 -->
          <div class="panel-section">
            <div class="section-content table-content">
              <el-table
                v-loading="loading"
                :data="apiInterfaces"
                style="width: 100%"
                @selection-change="handleSelectionChange"
                :default-sort="{ prop: 'updated_at', order: 'descending' }"
                stripe
                border
              >
                <el-table-column type="selection" width="55" />
                
                <!-- 动态列，使用配置的宽度 -->
                <el-table-column 
                  :prop="columns[0].prop" 
                  :label="columns[0].label" 
                  :width="columns[0].width" 
                  :min-width="columns[0].minWidth" 
                  sortable 
                  v-if="columns[0].visible" 
                />
                <el-table-column 
                  :prop="columns[1].prop" 
                  :label="columns[1].label" 
                  :width="columns[1].width" 
                  :min-width="columns[1].minWidth" 
                  sortable 
                  v-if="columns[1].visible" 
                />
                <el-table-column 
                  :prop="columns[2].prop" 
                  :label="columns[2].label" 
                  :width="columns[2].width" 
                  :min-width="columns[2].minWidth" 
                  sortable 
                  v-if="columns[2].visible"
                >
                  <template #default="scope">
                    <el-tag :type="getMethodType(scope.row.method)">
                      {{ scope.row.method }}
                    </el-tag>
                  </template>
                </el-table-column>
                <el-table-column 
                  :prop="columns[3].prop" 
                  :label="columns[3].label" 
                  :width="columns[3].width" 
                  :min-width="columns[3].minWidth" 
                  v-if="columns[3].visible" 
                />
                <el-table-column 
                  :prop="columns[4].prop" 
                  :label="columns[4].label" 
                  :width="columns[4].width" 
                  :min-width="columns[4].minWidth" 
                  v-if="columns[4].visible" 
                />
                <el-table-column 
                  :prop="columns[5].prop" 
                  :label="columns[5].label" 
                  :width="columns[5].width" 
                  :min-width="columns[5].minWidth" 
                  sortable 
                  v-if="columns[5].visible"
                >
                  <template #default="scope">
                    <el-tag :type="scope.row.status === 'active' ? 'success' : 'danger'">
                      {{ scope.row.status === 'active' ? '启用' : '禁用' }}
                    </el-tag>
                  </template>
                </el-table-column>
                <el-table-column 
                  :prop="columns[6].prop" 
                  :label="columns[6].label" 
                  :width="columns[6].width" 
                  :min-width="columns[6].minWidth" 
                  sortable 
                  v-if="columns[6].visible"
                >
                  <template #default="scope">
                    <el-tag :type="getTestStatusType(scope.row.test_status)">
                      {{ getTestStatusText(scope.row.test_status) }}
                    </el-tag>
                  </template>
                </el-table-column>
                <el-table-column 
                  :prop="columns[7].prop" 
                  :label="columns[7].label" 
                  :width="columns[7].width" 
                  :min-width="columns[7].minWidth" 
                  v-if="columns[7].visible" 
                />
                <el-table-column 
                  :prop="columns[8].prop" 
                  :label="columns[8].label" 
                  :width="columns[8].width" 
                  :min-width="columns[8].minWidth" 
                  v-if="columns[8].visible" 
                />
                <el-table-column 
                  :prop="columns[9].prop" 
                  :label="columns[9].label" 
                  :width="columns[9].width" 
                  :min-width="columns[9].minWidth" 
                  sortable 
                  v-if="columns[9].visible" 
                >
                  <template #default="scope">
                    {{ formatDate(scope.row.updated_at) }}
                  </template>
                </el-table-column>
                <el-table-column 
                  :prop="columns[10].prop" 
                  :label="columns[10].label" 
                  :width="columns[10].width" 
                  :min-width="columns[10].minWidth" 
                  v-if="columns[10].visible"
                >
                  <template #default="scope">
                    <el-tag 
                      v-for="(tag, index) in (scope.row.tags || [])" 
                      :key="index"
                      size="small"
                      style="margin-right: 5px;"
                    >
                      {{ tag }}
                    </el-tag>
                  </template>
                </el-table-column>
                
                <!-- 操作列 -->
                <el-table-column label="操作" width="240" fixed="right">
                  <template #default="scope">
                    <el-button type="primary" link @click="handleView(scope.row)">详情</el-button>
                    <el-button type="warning" link @click="handleEdit(scope.row)">编辑</el-button>
                    <el-button 
                      :type="scope.row.status === 'active' ? 'danger' : 'success'" 
                      link 
                      @click="handleToggleStatus(scope.row)"
                    >
                      {{ scope.row.status === 'active' ? '禁用' : '启用' }}
                    </el-button>
                    <el-button type="success" link @click="handleTest(scope.row)" :disabled="scope.row.status !== 'active'">
                      测试
                    </el-button>
                    <el-button type="danger" link @click="handleDelete(scope.row)">
                      删除
                    </el-button>
                  </template>
                </el-table-column>
              </el-table>
              
              <!-- 分页 -->
              <div class="pagination-container" v-if="apiInterfaces.length > 0">
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
            </div>
          </div>
        </div>
      </div>
    </div>
    
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
            <el-form-item label="所属项目" required>
              <el-select v-model="fileForm.projectId" placeholder="请选择要导入到的项目" filterable>
                <el-option
                  v-for="project in projects"
                  :key="project.id"
                  :label="project.name"
                  :value="project.id"
                />
              </el-select>
            </el-form-item>
            
            <el-form-item label="所属分组">
              <el-select v-model="fileForm.groupId" placeholder="请选择要导入到的分组" filterable>
                <el-option
                  v-for="group in apiGroups"
                  :key="group.id"
                  :label="group.name"
                  :value="group.id"
                />
              </el-select>
            </el-form-item>
            
            <el-form-item label="选择文件" required>
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
            <el-form-item label="所属项目" required>
              <el-select v-model="urlForm.projectId" placeholder="请选择要导入到的项目" filterable>
                <el-option
                  v-for="project in projects"
                  :key="project.id"
                  :label="project.name"
                  :value="project.id"
                />
              </el-select>
            </el-form-item>
            
            <el-form-item label="所属分组">
              <el-select v-model="urlForm.groupId" placeholder="请选择要导入到的分组" filterable>
                <el-option
                  v-for="group in apiGroups"
                  :key="group.id"
                  :label="group.name"
                  :value="group.id"
                />
              </el-select>
            </el-form-item>
            
            <el-form-item label="API URL" required>
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
    
    <!-- API详情对话框 -->
    <el-dialog
      v-model="detailDialogVisible"
      title="接口详情"
      width="800px"
    >
      <div v-if="selectedInterface" class="api-detail">
        <el-descriptions title="基本信息" :column="2" border>
          <el-descriptions-item label="接口ID">{{ selectedInterface.id }}</el-descriptions-item>
          <el-descriptions-item label="接口名称">{{ selectedInterface.name }}</el-descriptions-item>
          <el-descriptions-item label="请求方法">{{ selectedInterface.method }}</el-descriptions-item>
          <el-descriptions-item label="接口路径">{{ selectedInterface.path }}</el-descriptions-item>
          <el-descriptions-item label="协议">{{ selectedInterface.protocol }}</el-descriptions-item>
          <el-descriptions-item label="状态">{{ selectedInterface.status === 'active' ? '启用' : '禁用' }}</el-descriptions-item>
          <el-descriptions-item label="所属分组">{{ selectedInterface.group_name }}</el-descriptions-item>
          <el-descriptions-item label="所属项目">{{ selectedInterface.project_name }}</el-descriptions-item>
          <el-descriptions-item label="创建时间" :span="2">{{ formatDate(selectedInterface.created_at) }}</el-descriptions-item>
          <el-descriptions-item label="更新时间" :span="2">{{ formatDate(selectedInterface.updated_at) }}</el-descriptions-item>
        </el-descriptions>
        
        <el-divider />
        
        <h3>请求信息</h3>
        <el-collapse v-model="activeDetailTab">
          <el-collapse-item title="请求参数" name="params">
            <pre v-if="selectedInterface.request_params">{{ JSON.stringify(selectedInterface.request_params, null, 2) }}</pre>
            <p v-else>无请求参数</p>
          </el-collapse-item>
          <el-collapse-item title="请求体" name="body">
            <pre v-if="selectedInterface.request_body">{{ JSON.stringify(selectedInterface.request_body, null, 2) }}</pre>
            <p v-else>无请求体</p>
          </el-collapse-item>
          <el-collapse-item title="请求头" name="headers">
            <pre v-if="selectedInterface.request_headers">{{ JSON.stringify(selectedInterface.request_headers, null, 2) }}</pre>
            <p v-else>无请求头</p>
          </el-collapse-item>
        </el-collapse>
        
        <el-divider />
        
        <h3>响应信息</h3>
        <el-collapse v-model="activeDetailTab">
          <el-collapse-item title="响应状态码" name="response_codes">
            <pre v-if="selectedInterface.response_codes">{{ JSON.stringify(selectedInterface.response_codes, null, 2) }}</pre>
            <p v-else>无响应状态码</p>
          </el-collapse-item>
          <el-collapse-item title="响应体" name="response_body">
            <pre v-if="selectedInterface.response_body">{{ JSON.stringify(selectedInterface.response_body, null, 2) }}</pre>
            <p v-else>无响应体</p>
          </el-collapse-item>
          <el-collapse-item title="响应头" name="response_headers">
            <pre v-if="selectedInterface.response_headers">{{ JSON.stringify(selectedInterface.response_headers, null, 2) }}</pre>
            <p v-else>无响应头</p>
          </el-collapse-item>
        </el-collapse>
      </div>
      
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="detailDialogVisible = false">关闭</el-button>
        </span>
      </template>
    </el-dialog>
    
    <!-- API新增/编辑对话框 -->
    <el-dialog
      v-model="apiDialogVisible"
      :title="apiDialogTitle"
      width="1000px"
      top="2vh"
      :close-on-click-modal="false"
      :close-on-press-escape="false"
    >
      <el-tabs v-model="activeApiTab" class="api-tabs">
        <!-- 基础信息页签 -->
        <el-tab-pane label="基础信息" name="basic">
          <el-form ref="apiFormRef" :model="apiForm" label-width="90px">
            <el-form-item label="接口ID" :disabled="isEditingApi" v-if="isEditingApi">
              <el-input v-model="apiForm.id" :disabled="true" placeholder="系统自动生成" />
            </el-form-item>
            
            <el-form-item label="接口名称" required>
              <el-input v-model="apiForm.name" placeholder="请输入接口名称" />
            </el-form-item>
            
            <el-form-item label="接口路径" required>
              <el-input v-model="apiForm.path" placeholder="请输入接口路径，如：/api/v1/users" />
            </el-form-item>
            
            <el-form-item label="协议" required>
              <el-select v-model="apiForm.protocol" placeholder="请选择协议">
                <el-option label="HTTP" value="HTTP" />
                <el-option label="HTTPS" value="HTTPS" />
              </el-select>
            </el-form-item>
            
            <el-form-item label="请求方法" required>
              <el-select v-model="apiForm.method" placeholder="请选择请求方法">
                <el-option label="GET" value="GET" />
                <el-option label="POST" value="POST" />
                <el-option label="PUT" value="PUT" />
                <el-option label="DELETE" value="DELETE" />
                <el-option label="PATCH" value="PATCH" />
                <el-option label="HEAD" value="HEAD" />
                <el-option label="OPTIONS" value="OPTIONS" />
              </el-select>
            </el-form-item>
            
            <el-form-item label="所属分组" required>
              <el-select v-model="apiForm.group_id" placeholder="请选择所属分组">
                <el-option
                  v-for="group in apiGroups"
                  :key="group.id"
                  :label="group.name"
                  :value="group.id"
                />
              </el-select>
            </el-form-item>
            
            <el-form-item label="所属项目" required>
              <el-select v-model="apiForm.project_id" placeholder="请选择所属项目">
                <el-option
                  v-for="project in projects"
                  :key="project.id"
                  :label="project.name"
                  :value="project.id"
                />
              </el-select>
            </el-form-item>
            
            <el-form-item label="接口责任人">
              <el-input v-model="apiForm.owner" placeholder="请输入接口责任人" />
            </el-form-item>
            
            <el-form-item label="接口状态" required>
              <el-select v-model="apiForm.status" placeholder="请选择接口状态">
                <el-option label="开发中" value="development" />
                <el-option label="测试中" value="testing" />
                <el-option label="已上线" value="active" />
                <el-option label="已废弃" value="deprecated" />
              </el-select>
            </el-form-item>
            
            <el-form-item label="接口标签">
              <el-select v-model="apiForm.tags" multiple placeholder="请选择或输入接口标签">
                <el-option
                  v-for="tag in apiTags"
                  :key="tag"
                  :label="tag"
                  :value="tag"
                />
              </el-select>
            </el-form-item>
            
            <el-form-item label="版本号">
              <el-input v-model="apiForm.version" placeholder="请输入版本号" />
            </el-form-item>
            
            <el-form-item label="备注">
              <el-input v-model="apiForm.description" type="textarea" rows="3" placeholder="请输入备注信息" />
            </el-form-item>
          </el-form>
        </el-tab-pane>
        
        <!-- 请求信息页签 -->
        <el-tab-pane label="请求信息" name="request">
          <el-form :model="apiForm.request_info" label-width="90px">
            <el-form-item label="请求参数">
              <el-tabs v-model="activeRequestTab">
                <el-tab-pane label="Query参数" name="query">
                  <el-input
                    v-model="apiForm.request_info.query_params"
                    type="textarea"
                    rows="6"
                    placeholder="请输入Query参数（JSON格式）"
                    monaco-editor
                  />
                </el-tab-pane>
                <el-tab-pane label="Path参数" name="path">
                  <el-input
                    v-model="apiForm.request_info.path_params"
                    type="textarea"
                    rows="6"
                    placeholder="请输入Path参数（JSON格式）"
                    monaco-editor
                  />
                </el-tab-pane>
                <el-tab-pane label="Body参数" name="body">
                  <el-input
                    v-model="apiForm.request_info.body_params"
                    type="textarea"
                    rows="6"
                    placeholder="请输入Body参数（JSON格式）"
                    monaco-editor
                  />
                </el-tab-pane>
              </el-tabs>
            </el-form-item>
            
            <el-form-item label="请求头">
              <el-input
                v-model="apiForm.request_info.headers"
                type="textarea"
                rows="6"
                placeholder="请输入请求头（JSON格式）"
                monaco-editor
              />
            </el-form-item>
            
            <el-form-item label="认证信息">
              <el-select v-model="apiForm.request_info.auth_type" placeholder="请选择认证类型">
                <el-option label="无" value="none" />
                <el-option label="Basic认证" value="basic" />
                <el-option label="Bearer认证" value="bearer" />
                <el-option label="API Key" value="api_key" />
              </el-select>
              <el-input
                v-if="apiForm.request_info.auth_type !== 'none'"
                v-model="apiForm.request_info.auth_info"
                type="textarea"
                rows="3"
                placeholder="请输入认证信息（JSON格式）"
                monaco-editor
                style="margin-top: 10px;"
              />
            </el-form-item>
          </el-form>
        </el-tab-pane>
        
        <!-- 响应信息页签 -->
        <el-tab-pane label="响应信息" name="response">
          <el-form :model="apiForm.response_info" label-width="90px">
            <el-form-item label="响应状态码">
              <el-input
                v-model="apiForm.response_info.status_codes"
                type="textarea"
                rows="6"
                placeholder="请输入响应状态码（JSON格式）"
                monaco-editor
              />
            </el-form-item>
            
            <el-form-item label="响应体">
              <el-input
                v-model="apiForm.response_info.body"
                type="textarea"
                rows="6"
                placeholder="请输入响应体（JSON格式）"
                monaco-editor
              />
            </el-form-item>
            
            <el-form-item label="响应头">
              <el-input
                v-model="apiForm.response_info.headers"
                type="textarea"
                rows="6"
                placeholder="请输入响应头（JSON格式）"
                monaco-editor
              />
            </el-form-item>
            
            <el-form-item label="响应示例">
              <el-tabs v-model="activeResponseTab">
                <el-tab-pane label="正常响应" name="success">
                  <el-input
                    v-model="apiForm.response_info.success_example"
                    type="textarea"
                    rows="8"
                    placeholder="请输入正常响应示例（JSON格式）"
                    monaco-editor
                  />
                </el-tab-pane>
                <el-tab-pane label="异常响应" name="error">
                  <el-input
                    v-model="apiForm.response_info.error_example"
                    type="textarea"
                    rows="8"
                    placeholder="请输入异常响应示例（JSON格式）"
                    monaco-editor
                  />
                </el-tab-pane>
              </el-tabs>
            </el-form-item>
          </el-form>
        </el-tab-pane>
      </el-tabs>
      
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="apiDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleApiSubmit" :loading="isApiLoading">
            <el-icon v-if="isApiLoading"><Loading /></el-icon>
            保存接口
          </el-button>
        </span>
      </template>
    </el-dialog>
    
    <!-- API测试对话框 -->
    <el-dialog
      v-model="testDialogVisible"
      title="接口测试"
      width="800px"
    >
      <div v-if="selectedInterface" class="api-test">
        <el-form ref="testFormRef" :model="testForm" label-width="100px">
          <el-form-item label="测试环境">
            <el-select v-model="testForm.environment" placeholder="请选择测试环境">
              <el-option label="开发环境" value="development" />
              <el-option label="测试环境" value="testing" />
              <el-option label="生产环境" value="production" />
            </el-select>
          </el-form-item>
          
          <el-divider />
          
          <h4>请求参数</h4>
          <el-form-item label="路径参数">
            <el-input v-model="testForm.pathParams" type="textarea" rows="3" placeholder="请输入路径参数（JSON格式）" />
          </el-form-item>
          
          <el-form-item label="查询参数">
            <el-input v-model="testForm.queryParams" type="textarea" rows="3" placeholder="请输入查询参数（JSON格式）" />
          </el-form-item>
          
          <el-form-item label="请求头">
            <el-input v-model="testForm.headers" type="textarea" rows="3" placeholder="请输入请求头（JSON格式）" />
          </el-form-item>
          
          <el-form-item label="请求体">
            <el-input v-model="testForm.body" type="textarea" rows="5" placeholder="请输入请求体（JSON格式）" />
          </el-form-item>
        </el-form>
        
        <el-divider />
        
        <h4>测试结果</h4>
        <div v-if="testResult" class="test-result">
          <el-descriptions :column="1" border>
            <el-descriptions-item label="响应状态码">{{ testResult.status_code }}</el-descriptions-item>
            <el-descriptions-item label="响应时间">{{ testResult.response_time }}ms</el-descriptions-item>
            <el-descriptions-item label="响应头"><pre>{{ JSON.stringify(testResult.headers, null, 2) }}</pre></el-descriptions-item>
            <el-descriptions-item label="响应体"><pre>{{ JSON.stringify(testResult.body, null, 2) }}</pre></el-descriptions-item>
          </el-descriptions>
        </div>
        <div v-else class="test-result-empty">
          <p>点击测试按钮开始测试</p>
        </div>
      </div>
      
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="testDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleRunTest" :loading="isTesting">
            <el-icon v-if="isTesting"><Loading /></el-icon>
            测试
          </el-button>
        </span>
      </template>
    </el-dialog>
    
    <!-- 分组管理对话框 -->
    <el-dialog
      v-model="groupDialogVisible"
      :title="groupDialogTitle"
      width="600px"
      center
      :before-close="() => groupDialogVisible = false"
    >
      <div class="group-dialog-content">
        <el-form 
          ref="groupFormRef" 
          :model="groupForm" 
          label-width="120px"
          label-position="right"
          :style="{ 'margin-bottom': '20px' }"
        >
          <el-form-item label="分组名称" required>
            <el-input 
              v-model="groupForm.name" 
              placeholder="请输入分组名称" 
              clearable
              style="width: 100%"
            />
          </el-form-item>
          
          <el-form-item label="上级分组">
            <el-select 
              v-model="groupForm.parent_id" 
              placeholder="选择上级分组"
              clearable
              style="width: 100%"
            >
              <el-option label="无（创建为一级分组）" :value="null" />
              <el-option
                v-for="group in flattenedGroups"
                :key="group.id"
                :label="group.name"
                :value="group.id"
                :disabled="getGroupLevel(group) >= 8 || group.id === editingGroupId"
              />
            </el-select>
            <div class="form-hint" style="margin-top: 8px; color: #606266; font-size: 13px;">
              <el-icon><InfoFilled /></el-icon> 
              {{ groupForm.parent_id ? '将创建为子分组' : '将创建为一级分组' }}
              <span v-if="groupForm.parent_id">，当前父分组层级：{{ getGroupLevel(flattenedGroups.find(g => g.id === groupForm.parent_id)) }}</span>
              ，最多支持8级分组
            </div>
          </el-form-item>
          
          <el-form-item label="分组描述">
            <el-input 
              v-model="groupForm.description" 
              type="textarea" 
              rows="4" 
              placeholder="请输入分组描述" 
              resize="vertical"
              style="width: 100%"
            />
          </el-form-item>
        </el-form>
      </div>
      
      <template #footer>
        <div class="dialog-footer" style="display: flex; justify-content: center; gap: 12px;">
          <el-button size="default" @click="groupDialogVisible = false">
            取消
          </el-button>
          <el-button 
            type="primary" 
            size="default" 
            @click="handleGroupSubmit" 
            :loading="isGroupLoading"
            style="min-width: 100px"
          >
            <el-icon v-if="isGroupLoading"><Loading /></el-icon>
            {{ groupDialogTitle.includes('新增') ? '新增' : '保存' }}
          </el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch, onBeforeUnmount } from 'vue'
import request from '../utils/request'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Upload, Loading, Plus, Delete, Edit, ArrowDown, CirclePlus, CircleClose, InfoFilled
} from '@element-plus/icons-vue'
import type { FormInstance, UploadInstance } from 'element-plus'

// API接口类型定义
interface ApiInterface {
  id: number
  name: string
  method: string
  path: string
  protocol: string
  status: string
  group_name: string
  project_name: string
  created_at: string
  updated_at: string
  tags?: string[]
  test_status?: 'pass' | 'warning' | 'fail' | ''  // 测试状态：通过、警告、失败、空
  request_params?: any
  request_body?: any
  request_headers?: any
  response_codes?: any
  response_body?: any
  response_headers?: any
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

// API分组类型定义
interface ApiGroup {
  id: number
  name: string
  parent_id?: number | null
  description?: string
  children?: ApiGroup[]
}

// 状态管理
const apiInterfaces = ref<ApiInterface[]>([])
const loading = ref(false)
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)
const selectedInterfaces = ref<ApiInterface[]>([])

// 产品项目选择
const projects = ref<Project[]>([])
const selectedProjectId = ref<number | null>(null)

// API分组
const apiGroups = ref<ApiGroup[]>([])
const selectedGroup = ref<number | null>(null)
const groupTreeProps = {
  children: 'children',
  label: 'name'
}

// 监听apiGroups变化，更新扁平化分组列表
watch(apiGroups, (newGroups) => {
  flattenedGroups.value = flattenGroups(newGroups)
}, { deep: true })

// 右键菜单相关
const contextMenuVisible = ref(false)
const contextMenuStyle = ref({})
const contextMenuRef = ref<HTMLElement | null>(null)
const currentContextGroup = ref<ApiGroup | null>(null)

// 处理节点右键菜单
const handleNodeContextMenu = (event: MouseEvent, data: ApiGroup) => {
  event.preventDefault()
  event.stopPropagation()
  
  // 保存当前右键点击的分组
  currentContextGroup.value = data
  selectedGroup.value = data.id
  
  // 计算菜单位置
  const x = event.clientX
  const y = event.clientY
  
  contextMenuStyle.value = {
    position: 'fixed',
    left: `${x}px`,
    top: `${y}px`,
    zIndex: '9999'
  }
  
  // 显示右键菜单
  contextMenuVisible.value = true
  
  // 添加点击事件监听器，点击其他区域关闭菜单
  document.addEventListener('click', handleCloseContextMenu)
}

// 关闭右键菜单
const handleCloseContextMenu = () => {
  contextMenuVisible.value = false
  document.removeEventListener('click', handleCloseContextMenu)
}

// 组件卸载时清理事件监听器
onBeforeUnmount(() => {
  contextMenuVisible.value = false
  document.removeEventListener('click', handleCloseContextMenu)
})

// 新增子分组
const handleAddChildGroup = () => {
  if (!currentContextGroup.value) return
  
  // 打开分组对话框，设置父分组ID为当前右键点击的分组ID
  groupDialogTitle.value = '新增子分组'
  groupForm.value = {
    name: '',
    parent_id: currentContextGroup.value.id,
    description: ''
  }
  editingGroupId.value = null
  groupDialogVisible.value = true
  
  // 关闭右键菜单
  handleCloseContextMenu()
}

// 编辑分组
const handleEditGroup = () => {
  if (!currentContextGroup.value) return
  
  // 调用现有的编辑分组函数
  handleRenameGroup(currentContextGroup.value)
  
  // 关闭右键菜单
  handleCloseContextMenu()
}

// 删除分组
const handleDeleteContextGroup = () => {
  if (!currentContextGroup.value) return
  
  // 调用现有的删除分组函数
  handleDeleteGroup()
  
  // 关闭右键菜单
  handleCloseContextMenu()
}

// 搜索表单
const searchForm = ref({
  name: '',
  path: '',
  status: '',
  method: ''
})

// 动态列配置，调整接口ID字段宽度
const columns = ref([
  { prop: 'id', label: '接口ID', visible: true, width: 100 },
  { prop: 'name', label: '接口名称', visible: true, minWidth: 220 },
  { prop: 'method', label: '请求方法', visible: true, width: 110 },
  { prop: 'path', label: '接口路径', visible: true, minWidth: 250 },
  { prop: 'protocol', label: '协议', visible: true, width: 80 },
  { prop: 'status', label: '状态', visible: true, width: 100 },
  { prop: 'test_status', label: '测试状态', visible: true, width: 120 },
  { prop: 'group_name', label: '所属分组', visible: true, width: 130 },
  { prop: 'project_name', label: '所属项目', visible: true, width: 150 },
  { prop: 'updated_at', label: '更新时间', visible: true, width: 180 },
  { prop: 'tags', label: '标签', visible: true, minWidth: 140 }
])

// API新增/编辑相关状态
const apiDialogVisible = ref(false)
const apiDialogTitle = ref('新增接口')
const isEditingApi = ref(false)
const isApiLoading = ref(false)
const activeApiTab = ref('basic')
const activeRequestTab = ref('query')
const activeResponseTab = ref('success')

// API标签
const apiTags = ref(['用户', '订单', '商品', '支付', '查询', '创建', '更新', '删除'])

// API表单数据
const apiFormRef = ref<FormInstance>()
const apiForm = ref({
  id: 0,
  name: '',
  path: '',
  protocol: 'HTTP',
  method: 'GET',
  group_id: 0,
  project_id: 0,
  owner: '',
  status: 'active',
  tags: [] as string[],
  version: '',
  description: '',
  request_info: {
    query_params: '',
    path_params: '',
    body_params: '',
    headers: '',
    auth_type: 'none',
    auth_info: ''
  },
  response_info: {
    status_codes: '',
    body: '',
    headers: '',
    success_example: '',
    error_example: ''
  }
})

// API导入相关状态
const importDialogVisible = ref(false)
const importActiveTab = ref('file')
const isImporting = ref(false)

// 文件导入表单
const fileFormRef = ref<FormInstance>()
const fileForm = ref({
  projectId: 0,
  groupId: 0
})

// 文件上传
const uploadRef = ref<UploadInstance>()
const fileList = ref<any[]>([])
const selectedFile = ref<File | null>(null)

// URL导入表单
const urlFormRef = ref<FormInstance>()
const urlForm = ref({
  projectId: 0,
  groupId: 0,
  apiUrl: ''
})

// API详情对话框
const detailDialogVisible = ref(false)
const selectedInterface = ref<ApiInterface | null>(null)
const activeDetailTab = ref('params')

// API测试对话框
const testDialogVisible = ref(false)
const testFormRef = ref<FormInstance>()
const testForm = ref({
  environment: 'development',
  pathParams: '',
  queryParams: '',
  headers: '',
  body: ''
})
const isTesting = ref(false)
const testResult = ref<any>(null)

// 分组管理对话框
const groupDialogVisible = ref(false)
const groupFormRef = ref<FormInstance>()
const groupDialogTitle = ref('新增API分组')
const isGroupLoading = ref(false)
const editingGroupId = ref<number | null>(null)
const groupForm = ref({
  name: '',
  parent_id: null as number | null,
  description: ''
})

// 计算属性：扁平分组列表，用于选择上级分组
const flattenedGroups = ref<ApiGroup[]>([])

// 方法：扁平化分组树
const flattenGroups = (groups: ApiGroup[]): ApiGroup[] => {
  let result: ApiGroup[] = []
  groups.forEach(group => {
    result.push(group)
    if (group.children && group.children.length > 0) {
      result = result.concat(flattenGroups(group.children))
    }
  })
  return result
}

// 方法：获取分组层级
const getGroupLevel = (group: ApiGroup | undefined): number => {
  if (!group) return 0
  if (!group.parent_id) return 1
  
  let level = 1
  let currentGroup = group
  while (currentGroup.parent_id) {
    const parentGroup = flattenedGroups.value.find(g => g.id === currentGroup.parent_id)
    if (!parentGroup) break
    level++
    currentGroup = parentGroup
  }
  return level
}

// 监听分组数据变化，更新扁平列表
watch(() => apiGroups.value, (newGroups) => {
  flattenedGroups.value = flattenGroups(newGroups)
}, { deep: true })

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

// 获取测试状态对应的标签类型
const getTestStatusType = (status: string | undefined): string => {
  const statusMap: Record<string, string> = {
    pass: 'success',
    warning: 'warning',
    fail: 'danger'
  }
  return statusMap[status || ''] || 'info'
}

// 获取测试状态文本
const getTestStatusText = (status: string | undefined): string => {
  const statusMap: Record<string, string> = {
    pass: '通过',
    warning: '警告',
    fail: '失败'
  }
  return statusMap[status || ''] || ''
}

// 格式化时间为用户友好的格式
const formatDate = (dateString: string): string => {
  if (!dateString) return ''
  
  const date = new Date(dateString)
  // 检查日期是否有效
  if (isNaN(date.getTime())) return ''
  
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  const hours = String(date.getHours()).padStart(2, '0')
  const minutes = String(date.getMinutes()).padStart(2, '0')
  const seconds = String(date.getSeconds()).padStart(2, '0')
  
  return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`
}

// 获取项目列表
const fetchProjects = async () => {
  try {
    const response = await request.get('/projects')
    // 只显示已启动的项目
    projects.value = (response as unknown as Project[]).filter(project => project.status === 'active')
    // 如果没有选择项目，默认选择第一个项目
    if (projects.value.length > 0 && !selectedProjectId.value) {
      selectedProjectId.value = projects.value[0].id
      // 获取默认项目的分组树
      await fetchApiGroups(selectedProjectId.value)
      // 获取默认项目的接口列表
      await fetchApiInterfaces()
    }
  } catch (error) {
    ElMessage.error('获取项目列表失败')
    console.error('获取项目列表失败:', error)
  }
}

// 获取API分组树
const fetchApiGroups = async (projectId: number | null) => {
  if (!projectId) return;
  try {
    console.log(`请求API分组，项目ID: ${projectId}`)
    const response = await request.get(`/projects/${projectId}/groups`)
    console.log('API分组响应:', response)
    
    // 处理响应，确保数据格式正确
    const groups = response as unknown as ApiGroup[]
    apiGroups.value = groups
    console.log('处理后的API分组:', apiGroups.value)
  } catch (error: any) {
    console.error('获取API分组树失败:', error)
    if (error.response) {
      console.error('响应状态:', error.response.status)
      console.error('响应数据:', error.response.data)
    } else if (error.request) {
      console.error('请求发出但未收到响应:', error.request)
    } else {
      console.error('请求配置错误:', error.message)
    }
    ElMessage.error('获取API分组树失败')
  }
}

// 获取API接口列表
const fetchApiInterfaces = async () => {
  loading.value = true
  try {
    // 如果没有选择项目，显示空列表
    if (!selectedProjectId.value) {
      apiInterfaces.value = []
      total.value = 0
      return
    }
    
    // 构建查询参数，只包含有值的参数
    const params: any = {
      skip: (currentPage.value - 1) * pageSize.value,
      limit: pageSize.value
    }
    
    // 只在selectedGroup.value不为null时添加group_id参数
    if (selectedGroup.value !== null) {
      params.group_id = selectedGroup.value
    }
    
    if (searchForm.value.name) {
      params.name = searchForm.value.name
    }
    
    if (searchForm.value.path) {
      params.path = searchForm.value.path
    }
    
    if (searchForm.value.status) {
      params.status = searchForm.value.status
    }
    
    if (searchForm.value.method) {
      params.method = searchForm.value.method
    }
    
    const response = await request.get('/projects/' + selectedProjectId.value + '/interfaces', { params })
    const result = response as unknown as { total: number; items: ApiInterface[] }
    apiInterfaces.value = result.items
    total.value = result.total
  } catch (error) {
    ElMessage.error('获取API接口列表失败')
    console.error('获取API接口列表失败:', error)
    // 发生错误时显示空列表，不显示样例数据
    apiInterfaces.value = []
    total.value = 0
  } finally {
    loading.value = false
  }
}

// 页面加载时获取数据
onMounted(async () => {
  await fetchProjects()
  await fetchApiInterfaces()
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

// 项目切换处理
const onProjectChange = () => {
  if (selectedProjectId.value) {
    fetchApiGroups(selectedProjectId.value)
    fetchApiInterfaces()
  }
}

// 分组选择处理
const handleSelectGroup = (group: ApiGroup) => {
  selectedGroup.value = group.id
  fetchApiInterfaces()
}

// 分组管理
const handleAddGroup = () => {
  if (!selectedProjectId.value) {
    return ElMessage.warning('请先选择产品项目')
  }
  
  // 重置表单
  groupDialogTitle.value = '新增API分组'
  groupForm.value = {
    name: '',
    parent_id: selectedGroup.value === null ? null : selectedGroup.value,
    description: ''
  }
  editingGroupId.value = null
  groupDialogVisible.value = true
}

const handleDeleteGroup = async () => {
  if (selectedGroup.value === null) {
    return ElMessage.warning('请先选择要删除的分组')
  }
  
  ElMessageBox.confirm('确定要删除该API分组吗？', '删除确认', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    try {
      await request.delete(`/groups/${selectedGroup.value}`)
      ElMessage.success('API分组删除成功')
      // 刷新分组树
      fetchApiGroups(selectedProjectId.value)
      // 重置选中的分组
      selectedGroup.value = null
      // 刷新接口列表
      fetchApiInterfaces()
    } catch (error) {
      ElMessage.error('删除API分组失败')
      console.error('删除API分组失败:', error)
    }
  }).catch(() => {
    // 用户取消操作
  })
}

const handleRenameGroup = (group: ApiGroup) => {
  groupDialogTitle.value = '编辑API分组'
  groupForm.value = {
    name: group.name,
    parent_id: group.parent_id || null,
    description: group.description || ''
  }
  editingGroupId.value = group.id
  groupDialogVisible.value = true
}

// 分组表单提交
const handleGroupSubmit = async () => {
  if (!selectedProjectId.value) {
    return ElMessage.warning('请先选择产品项目')
  }
  
  if (!groupForm.value.name.trim()) {
    return ElMessage.warning('分组名称不能为空')
  }
  
  // 检查层级限制
  if (groupForm.value.parent_id) {
    const parentGroup = flattenedGroups.value.find(g => g.id === groupForm.value.parent_id)
    if (parentGroup && getGroupLevel(parentGroup) >= 8) {
      return ElMessage.warning('分组层级不能超过8级')
    }
  }
  
  isGroupLoading.value = true
  
  try {
    if (editingGroupId.value) {
      // 编辑分组
      await request.put(`/groups/${editingGroupId.value}`, {
        name: groupForm.value.name.trim(),
        parent_id: groupForm.value.parent_id,
        description: groupForm.value.description
      })
      ElMessage.success('API分组编辑成功')
    } else {
      // 新增分组
      await request.post(`/projects/${selectedProjectId.value}/groups`, {
        name: groupForm.value.name.trim(),
        parent_id: groupForm.value.parent_id,
        description: groupForm.value.description
      })
      ElMessage.success('API分组创建成功')
    }
    
    // 刷新分组树
    fetchApiGroups(selectedProjectId.value)
    // 关闭对话框
    groupDialogVisible.value = false
  } catch (error) {
    ElMessage.error(editingGroupId.value ? '编辑API分组失败' : '创建API分组失败')
    console.error('处理API分组失败:', error)
  } finally {
    isGroupLoading.value = false
  }
}

// 搜索处理
const handleSearch = () => {
  currentPage.value = 1
  fetchApiInterfaces()
}

const handleResetSearch = () => {
  searchForm.value.name = ''
  searchForm.value.path = ''
  searchForm.value.status = ''
  searchForm.value.method = ''
  fetchApiInterfaces()
}

// 操作处理
const handleAddApi = () => {
  if (!selectedProjectId.value) {
    return ElMessage.warning('请先选择产品项目')
  }
  
  // 重置表单
  apiDialogTitle.value = '新增接口'
  isEditingApi.value = false
  apiForm.value = {
    id: 0,
    name: '',
    path: '',
    protocol: 'HTTP',
    method: 'GET',
    group_id: selectedGroup.value || 0,
    project_id: selectedProjectId.value,
    owner: '',
    status: 'active',
    tags: [] as string[],
    version: '',
    description: '',
    request_info: {
      query_params: '',
      path_params: '',
      body_params: '',
      headers: '',
      auth_type: 'none',
      auth_info: ''
    },
    response_info: {
      status_codes: '',
      body: '',
      headers: '',
      success_example: '',
      error_example: ''
    }
  }
  apiDialogVisible.value = true
}

const handleView = (row: ApiInterface) => {
  // 查看接口详情
  selectedInterface.value = row
  detailDialogVisible.value = true
}

const handleEdit = (row: ApiInterface) => {
  // 编辑接口
  apiDialogTitle.value = '编辑接口'
  isEditingApi.value = true
  
  // 将接口数据填充到表单
  apiForm.value = {
    id: row.id,
    name: row.name,
    path: row.path,
    protocol: row.protocol,
    method: row.method,
    group_id: row.group_id || 0,
    project_id: selectedProjectId.value || 0,
    owner: row.owner || '',
    status: row.status,
    tags: row.tags || [],
    version: row.version || '',
    description: row.description || '',
    request_info: {
      query_params: JSON.stringify(row.request_params || {}, null, 2),
      path_params: '',
      body_params: JSON.stringify(row.request_body || {}, null, 2),
      headers: JSON.stringify(row.request_headers || {}, null, 2),
      auth_type: 'none',
      auth_info: ''
    },
    response_info: {
      status_codes: JSON.stringify(row.response_codes || {}, null, 2),
      body: JSON.stringify(row.response_body || {}, null, 2),
      headers: JSON.stringify(row.response_headers || {}, null, 2),
      success_example: '',
      error_example: ''
    }
  }
  apiDialogVisible.value = true
}

// API表单提交
const handleApiSubmit = async () => {
  if (!apiFormRef.value) return
  
  try {
    await apiFormRef.value.validate()
    
    isApiLoading.value = true
    
    // 处理表单数据，将JSON字符串转换为对象
    const submitData = {
      ...apiForm.value,
      request_info: {
        query_params: apiForm.value.request_info.query_params ? JSON.parse(apiForm.value.request_info.query_params) : {},
        path_params: apiForm.value.request_info.path_params ? JSON.parse(apiForm.value.request_info.path_params) : {},
        body_params: apiForm.value.request_info.body_params ? JSON.parse(apiForm.value.request_info.body_params) : {},
        headers: apiForm.value.request_info.headers ? JSON.parse(apiForm.value.request_info.headers) : {},
        auth_type: apiForm.value.request_info.auth_type,
        auth_info: apiForm.value.request_info.auth_info ? JSON.parse(apiForm.value.request_info.auth_info) : {}
      },
      response_info: {
        status_codes: apiForm.value.response_info.status_codes ? JSON.parse(apiForm.value.response_info.status_codes) : {},
        body: apiForm.value.response_info.body ? JSON.parse(apiForm.value.response_info.body) : {},
        headers: apiForm.value.response_info.headers ? JSON.parse(apiForm.value.response_info.headers) : {},
        success_example: apiForm.value.response_info.success_example ? JSON.parse(apiForm.value.response_info.success_example) : {},
        error_example: apiForm.value.response_info.error_example ? JSON.parse(apiForm.value.response_info.error_example) : {}
      }
    }
    
    if (isEditingApi.value) {
      // 编辑接口
      await request.put(`/interfaces/${apiForm.value.id}`, submitData)
      ElMessage.success(`接口 "${apiForm.value.name}" 编辑成功`)
    } else {
      // 新增接口
      await request.post('/interfaces', submitData)
      ElMessage.success(`接口 "${apiForm.value.name}" 新增成功`)
    }
    
    // 关闭对话框
    apiDialogVisible.value = false
    // 刷新接口列表
    fetchApiInterfaces()
  } catch (error: any) {
    console.error('处理接口失败:', error)
    if (error.response?.data?.detail) {
      ElMessage.error(error.response.data.detail)
    } else if (error.name === 'SyntaxError') {
      ElMessage.error('JSON格式错误，请检查输入的JSON数据')
    } else {
      ElMessage.error(`${isEditingApi.value ? '编辑' : '新增'}接口失败`)
    }
  } finally {
    isApiLoading.value = false
  }
}

const handleDelete = async (row: ApiInterface) => {
  // 删除接口
  if (row.status === 'active') {
    return ElMessage.warning('启用状态的接口不支持删除，请先禁用')
  }
  
  ElMessageBox.confirm(`确定要删除接口 "${row.name}" 吗？`, '删除确认', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    try {
      await request.delete(`/interfaces/${row.id}`)
      ElMessage.success(`接口 "${row.name}" 删除成功`)
      // 刷新接口列表
      fetchApiInterfaces()
    } catch (error) {
      ElMessage.error(`删除接口 "${row.name}" 失败`)
      console.error('删除接口失败:', error)
    }
  }).catch(() => {
    // 用户取消操作
  })
}

const handleToggleStatus = async (row: ApiInterface) => {
  // 切换接口状态
  const newStatus = row.status === 'active' ? 'inactive' : 'active'
  const statusText = newStatus === 'active' ? '启用' : '禁用'
  
  try {
    await request.put(`/interfaces/${row.id}`, {
      status: newStatus
    })
    ElMessage.success(`接口 "${row.name}" ${statusText}成功`)
    // 刷新接口列表
    fetchApiInterfaces()
  } catch (error) {
    ElMessage.error(`接口 "${row.name}" ${statusText}失败`)
    console.error(`切换接口状态失败:`, error)
  }
}

const handleTest = (row: ApiInterface) => {
  // 测试接口
  selectedInterface.value = row
  testDialogVisible.value = true
}

// 批量操作
const handleBatchDelete = async () => {
  if (selectedInterfaces.value.length === 0) {
    return ElMessage.warning('请选择要删除的接口')
  }
  
  ElMessageBox.confirm(`确定要删除选中的 ${selectedInterfaces.value.length} 个接口吗？`, '删除确认', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    try {
      const interfaceIds = selectedInterfaces.value.map(item => item.id)
      await request.delete('/interfaces/batch', {
        params: { interface_ids: interfaceIds }
      })
      ElMessage.success('批量删除成功')
      // 刷新接口列表
      fetchApiInterfaces()
      // 清空选中项
      selectedInterfaces.value = []
    } catch (error) {
      ElMessage.error('批量删除失败')
      console.error('批量删除失败:', error)
    }
  }).catch(() => {
    // 用户取消操作
  })
}

const handleBatchEnable = async () => {
  if (selectedInterfaces.value.length === 0) {
    return ElMessage.warning('请选择要启用的接口')
  }
  
  try {
    const interfaceIds = selectedInterfaces.value.map(item => item.id)
    await request.put('/interfaces/batch/status', {
      interface_ids: interfaceIds,
      status: 'active'
    })
    ElMessage.success('批量启用成功')
    // 刷新接口列表
    fetchApiInterfaces()
    // 清空选中项
    selectedInterfaces.value = []
  } catch (error) {
    ElMessage.error('批量启用失败')
    console.error('批量启用失败:', error)
  }
}

const handleBatchDisable = async () => {
  if (selectedInterfaces.value.length === 0) {
    return ElMessage.warning('请选择要禁用的接口')
  }
  
  try {
    const interfaceIds = selectedInterfaces.value.map(item => item.id)
    await request.put('/interfaces/batch/status', {
      interface_ids: interfaceIds,
      status: 'inactive'
    })
    ElMessage.success('批量禁用成功')
    // 刷新接口列表
    fetchApiInterfaces()
    // 清空选中项
    selectedInterfaces.value = []
  } catch (error) {
    ElMessage.error('批量禁用失败')
    console.error('批量禁用失败:', error)
  }
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
    if (fileForm.value.groupId) {
      formData.append('group_id', fileForm.value.groupId.toString())
    }
    
    const response = await request.post(`/projects/${fileForm.value.projectId}/import-spec`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
    
    // 处理导入结果
    handleImportResult(response)
  } catch (error: any) {
    handleImportError(error)
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
    const params: any = {
      url: urlForm.value.apiUrl
    }
    if (urlForm.value.groupId) {
      params.group_id = urlForm.value.groupId
    }
    
    const response = await request.post(`/projects/${urlForm.value.projectId}/import-spec-url`, params)
    
    // 处理导入结果
    handleImportResult(response)
  } catch (error: any) {
    handleImportError(error)
  } finally {
    isImporting.value = false
  }
}

// 处理导入结果
const handleImportResult = (response: any) => {
  const result = response as any
  
  if (result.success) {
    ElMessage.success(`${result.success_count || 0} 个API导入成功`)
    
    // 显示导入失败的详细列表
    if (result.failed_count && result.failed_count > 0) {
      showImportFailedDialog(result.failed_list || [])
    }
    
    importDialogVisible.value = false
    resetImportForms()
    // 刷新接口列表
    fetchApiInterfaces()
  } else {
    // 导入失败
    if (result.failed_list && result.failed_list.length > 0) {
      showImportFailedDialog(result.failed_list)
    } else {
      ElMessage.error(result.message || 'API导入失败')
    }
  }
}

// 处理导入错误
const handleImportError = (error: any) => {
  console.error('API导入失败:', error)
  
  // 尝试从错误响应中获取详细信息
  if (error.response && error.response.data) {
    const errorData = error.response.data
    if (errorData.failed_list && errorData.failed_list.length > 0) {
      showImportFailedDialog(errorData.failed_list)
      return
    }
  }
  
  // 默认错误提示
  ElMessage.error('API导入失败，请检查文件格式或网络连接')
}

// 显示导入失败对话框
const showImportFailedDialog = (failedList: any[]) => {
  ElMessageBox.alert(
    `<div style="max-height: 400px; overflow-y: auto;">
      <h4>导入失败列表 (共 ${failedList.length} 个)</h4>
      <table style="width: 100%; border-collapse: collapse; margin-top: 10px;">
        <thead>
          <tr style="background-color: #f5f7fa;">
            <th style="padding: 8px; border: 1px solid #ebeef5;">API名称</th>
            <th style="padding: 8px; border: 1px solid #ebeef5;">失败原因</th>
          </tr>
        </thead>
        <tbody>
          ${failedList.map(item => `
            <tr>
              <td style="padding: 8px; border: 1px solid #ebeef5;">${item.name || item.path || '未知API'}</td>
              <td style="padding: 8px; border: 1px solid #ebeef5; color: #f56c6c;">${item.reason || '未知原因'}</td>
            </tr>
          `).join('')}
        </tbody>
      </table>
    </div>`,
    'API导入结果',
    {
      dangerouslyUseHTMLString: true,
      confirmButtonText: '确定',
      type: 'warning'
    }
  )
}

// 重置导入表单
const resetImportForms = () => {
  fileFormRef.value?.resetFields()
  urlFormRef.value?.resetFields()
  fileList.value = []
  selectedFile.value = null
  fileForm.value.projectId = 0
  fileForm.value.groupId = 0
  urlForm.value.projectId = 0
  urlForm.value.groupId = 0
  urlForm.value.apiUrl = ''
}

// 运行测试
const handleRunTest = async () => {
  isTesting.value = true
  try {
    // 模拟测试结果
    testResult.value = {
      status_code: 200,
      response_time: 150,
      headers: {
        'Content-Type': 'application/json',
        'Server': 'nginx'
      },
      body: {
        code: 0,
        message: 'success',
        data: {
          id: 1,
          name: 'test'
        }
      }
    }
    ElMessage.success('测试完成')
  } catch (error) {
    ElMessage.error('测试失败')
    console.error('测试失败:', error)
  } finally {
    isTesting.value = false
  }
}
</script>

<style scoped>
/* 全局样式 */
.api-management {
  padding: 20px;
  background-color: #f5f7fa;
  min-height: 100vh;
  font-size: 14px;
  color: #303133;
}

/* 页面标题 */
.page-header {
  margin-bottom: 20px;
}

.page-header h2 {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
  color: #303133;
}

/* 主内容区域 */
.main-content {
  display: flex;
  gap: 20px;
  height: calc(100vh - 100px);
  overflow: hidden;
}

/* 左侧面板 */
.left-panel {
  width: 280px;
  flex-shrink: 0;
  overflow: hidden;
}

/* 右侧面板 */
.right-panel {
  flex: 1;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

/* 面板容器 */
.panel-container {
  background-color: #ffffff;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  height: 100%;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

/* 面板区块 */
.panel-section {
  padding: 0;
  border-bottom: 1px solid #ebeef5;
}

.panel-section:last-child {
  border-bottom: none;
  flex: 1;
  overflow: hidden;
}

/* 区块头部 */
.section-header {
  padding: 15px 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  background-color: #fafafa;
  border-bottom: 1px solid #ebeef5;
}

.section-header h3 {
  margin: 0;
  font-size: 14px;
  font-weight: 600;
  color: #303133;
}

/* 右侧面板操作栏头部 */
.action-header {
  background-color: #ffffff;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 20px;
}

/* 标题头部样式 */
.title-header {
  background-color: #ffffff;
  padding: 12px 20px;
  border-bottom: 1px solid #ebeef5;
}

.title-header h3 {
  margin: 0;
  font-size: 14px;
  font-weight: 600;
  color: #303133;
}

/* 头部操作按钮 */
.header-actions {
  display: flex;
  gap: 5px;
}

.header-actions-left {
  display: flex;
  gap: 5px;
  flex: 1;
}

.header-actions-right {
  display: flex;
  gap: 5px;
  flex-shrink: 0;
}

/* 区块内容 */
.section-content {
  padding: 15px 20px;
}

/* 分组内容区域 */
.group-content {
  padding: 0;
  height: calc(100vh - 240px);
  overflow-y: auto;
}

/* 表格内容区域 */
.table-content {
  padding: 0;
  height: calc(100vh - 280px);
  overflow-y: auto;
}

/* 搜索容器 */
.search-container {
  padding: 15px 20px;
  background-color: #ffffff;
  border-bottom: 1px solid #ebeef5;
}

.search-form {
  margin: 0;
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
  justify-content: flex-start;
}

/* 调整el-form-item的样式，设置适当的margin */
.search-form :deep(.el-form-item) {
  margin-right: 0;
  margin-bottom: 10px;
  margin-left: 0;
  margin-top: 0;
  display: flex;
  align-items: center;
}

/* 调整el-form-item__label的样式 */
.search-form :deep(.el-form-item__label) {
  margin-right: 8px;
  font-weight: 500;
  color: #303133;
  font-size: 14px;
  white-space: nowrap;
}

/* 调整el-form-item__content的样式 */
.search-form :deep(.el-form-item__content) {
  margin-left: 0;
  flex: 0 0 auto;
}

/* 分页容器 */
.pagination-container {
  padding: 15px 20px;
  background-color: #ffffff;
  border-top: 1px solid #ebeef5;
  display: flex;
  justify-content: flex-end;
}

/* 分组树样式 */
.group-content .el-tree {
  padding: 10px 20px;
}

.tree-node {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
  padding: 4px 0;
}

.node-actions {
  visibility: hidden;
  display: flex;
  gap: 5px;
}

.tree-node:hover .node-actions {
  visibility: visible;
}

/* 表格样式 */
.table-content .el-table {
  margin: 0;
  border-radius: 0;
  font-size: 13px;
  width: 100%;
  min-width: 1000px;
}

/* 表头样式优化，降低高度 */
.table-content .el-table__header-wrapper {
  background-color: #fafafa;
  overflow: hidden;
  white-space: nowrap;
}

.table-content .el-table th {
  padding: 8px 12px;
  height: 40px;
  line-height: 24px;
  font-size: 12px;
  font-weight: 500;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  box-sizing: border-box;
}

/* 表格内容行样式 */
.table-content .el-table td {
  padding: 10px 12px;
  height: 48px;
  line-height: 24px;
  font-size: 13px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

/* 表格容器样式优化 */
.table-content {
  padding: 0;
  height: calc(100vh - 320px);
  overflow-y: auto;
  overflow-x: auto;
}

/* 优化表格滚动条 */
.table-content::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

.table-content::-webkit-scrollbar-track {
  background: #f1f1f1;
}

.table-content::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 4px;
}

.table-content::-webkit-scrollbar-thumb:hover {
  background: #a1a1a1;
}

/* 按钮样式 */
.el-button {
  font-size: 12px;
}

/* 表单样式 */
.el-form-item {
  margin: 0;
}

/* 下拉菜单样式 */
.el-dropdown-menu {
  font-size: 12px;
}

/* 自定义右键菜单样式 */
.custom-context-menu {
  position: fixed;
  z-index: 9999;
  background-color: #fff;
  border: 1px solid #e4e7ed;
  border-radius: 4px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  padding: 4px 0;
  min-width: 180px;
  list-style: none;
  margin: 0;
  outline: none;
}

.context-menu-item {
  display: flex;
  align-items: center;
  padding: 8px 16px;
  cursor: pointer;
  font-size: 14px;
  transition: background-color 0.2s;
  color: #303133;
}

.context-menu-item:hover {
  background-color: #f5f7fa;
  color: #409eff;
}

.context-menu-item .el-icon {
  margin-right: 8px;
  font-size: 14px;
}

.context-menu-divider {
  height: 1px;
  margin: 4px 0;
  background-color: #e4e7ed;
}

.context-menu-item.disabled {
  color: #c0c4cc;
  cursor: not-allowed;
}

.context-menu-item.disabled:hover {
  background-color: #fff;
  color: #c0c4cc;
}

/* 滚动条样式 */
::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}

::-webkit-scrollbar-track {
  background: #f1f1f1;
}

::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

::-webkit-scrollbar-thumb:hover {
  background: #a1a1a1;
}

/* 导入相关样式 */
.import-tabs {
  margin-top: 20px;
}

/* 详情和测试样式 */
.api-detail,
.api-test {
  padding: 10px 0;
}

.test-result {
  background-color: #f5f7fa;
  padding: 10px;
  border-radius: 4px;
  margin-top: 10px;
}

.test-result-empty {
  text-align: center;
  color: #909399;
  padding: 20px;
  background-color: #f5f7fa;
  border-radius: 4px;
  margin-top: 10px;
}

/* API新增/编辑对话框样式 */
.api-tabs {
  margin-bottom: 10px;
  width: 100%;
}

/* 表单容器样式 */
:deep(.el-form) {
  width: 100%;
  max-width: 950px;
  margin: 0 auto;
}

/* 表单样式优化 */
:deep(.el-form-item) {
  margin-bottom: 15px;
  padding: 0 5px;
}

:deep(.el-form-item__label) {
  font-weight: 500;
  color: #303133;
  width: 90px;
}

:deep(.el-form-item__content) {
  margin-left: 90px;
}

:deep(.el-input__wrapper) {
  border-radius: 4px;
  width: 100%;
  height: 36px;
}

:deep(.el-select__wrapper) {
  border-radius: 4px;
  width: 100%;
  height: 36px;
}

/* 页签内容样式 */
:deep(.el-tab-pane__content) {
  padding: 10px 0;
}

/* 标签页样式 */
:deep(.el-tabs__nav-wrap) {
  margin-bottom: 15px;
  padding: 0 5px;
}

/* 多行文本输入样式 */
:deep(.el-textarea__inner) {
  border-radius: 4px;
  resize: vertical;
  min-height: 80px;
  max-height: 120px;
}

/* 对话框内容区域样式 */
:deep(.el-dialog__body) {
  height: auto;
  max-height: 75vh;
  overflow: hidden;
  padding: 15px;
}

/* 页签面板样式 */
:deep(.el-tabs__content) {
  width: 100%;
  height: auto;
  overflow: hidden;
}

/* 标签页容器样式 */
:deep(.el-tabs) {
  height: 100%;
  display: flex;
  flex-direction: column;
}

/* 标签页内容区域样式 */
:deep(.el-tabs__content) {
  flex: 1;
  overflow: hidden;
}

/* 标签页样式 */
:deep(.el-tab-pane) {
  width: 100%;
  height: 100%;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

/* 页签内内容区域样式 */
:deep(.el-tab-pane__wrapper) {
  flex: 1;
  overflow: auto;
}
</style>
