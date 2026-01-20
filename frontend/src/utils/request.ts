import axios from 'axios'

// 创建axios实例
const request = axios.create({
  baseURL: 'http://localhost:8000/api/v1',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
request.interceptors.request.use(
  (config) => {
    // 从localStorage获取token
    const token = localStorage.getItem('token')
    // 如果有token，添加到请求头
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器
request.interceptors.response.use(
  (response) => {
    return response.data
  },
  (error) => {
    console.error('API请求错误:', error)
    // 处理认证错误
    if (error.response && error.response.status === 401) {
      // 清除token
      localStorage.removeItem('token')
      console.error('认证失败，请重新登录')
      // 由于当前没有登录页面，暂时只打印错误
      // 后续可以添加重定向到登录页面的逻辑
    }
    return Promise.reject(error)
  }
)

export default request