import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'

// 路由配置
const routes: RouteRecordRaw[] = [
  {
    path: '/',
    redirect: '/dashboard'
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: () => import('../views/Dashboard.vue'),
    meta: { title: '仪表盘' }
  },
  {
    path: '/api/import',
    name: 'ApiImport',
    component: () => import('../views/ApiImport.vue'),
    meta: { title: 'API导入' }
  },
  {
    path: '/api/list',
    name: 'ApiList',
    component: () => import('../views/ApiList.vue'),
    meta: { title: 'API列表' }
  },
  {
    path: '/test-points',
    name: 'TestPoints',
    component: () => import('../views/TestPoints.vue'),
    meta: { title: '测试点管理' }
  },
  {
    path: '/test-cases',
    name: 'TestCases',
    component: () => import('../views/TestCases.vue'),
    meta: { title: '测试用例管理' }
  },
  {
    path: '/test-scripts',
    name: 'TestScripts',
    component: () => import('../views/TestScripts.vue'),
    meta: { title: '测试脚本管理' }
  },
  {
    path: '/test-execution/execute',
    name: 'ExecuteTests',
    component: () => import('../views/ExecuteTests.vue'),
    meta: { title: '执行测试' }
  },
  {
    path: '/test-execution/history',
    name: 'ExecutionHistory',
    component: () => import('../views/ExecutionHistory.vue'),
    meta: { title: '执行历史' }
  },
  {
    path: '/reports',
    name: 'Reports',
    component: () => import('../views/Reports.vue'),
    meta: { title: '报告列表' }
  },
  {
    path: '/workflow',
    name: 'Workflow',
    component: () => import('../views/Workflow.vue'),
    meta: { title: '工作流管理' }
  },
  {
    path: '/config/categories',
    name: 'ConfigCategories',
    component: () => import('../views/ConfigCategories.vue'),
    meta: { title: '配置分类' }
  },
  {
    path: '/config/items',
    name: 'ConfigItems',
    component: () => import('../views/ConfigItems.vue'),
    meta: { title: '配置项管理' }
  }
]

// 创建路由器
const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由前置守卫，设置页面标题
router.beforeEach((to, _from, next) => {
  if (to.meta.title) {
    document.title = `${to.meta.title} - AQES-Test`
  }
  next()
})

export default router
