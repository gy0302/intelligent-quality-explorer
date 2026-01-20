import axios from 'axios'
import type { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios'

// 创建axios实例
const request: AxiosInstance = axios.create({
  baseURL: 'http://localhost:8000/api/v1',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
request.interceptors.request.use(
  (config: AxiosRequestConfig) => {
    // 可以在这里添加token等认证信息
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器
request.interceptors.response.use(
  (response: AxiosResponse) => {
    const res = response.data
    return res
  },
  (error) => {
    console.error('API请求错误:', error)
    // 可以在这里统一处理错误
    return Promise.reject(error)
  }
)

export default request