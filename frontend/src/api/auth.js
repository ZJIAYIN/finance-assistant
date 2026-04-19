import request from './request'

export const authApi = {
  // 注册
  register(data) {
    return request.post('/auth/register', data)
  },

  // 登录
  login(data) {
    return request.post('/auth/login', data)
  },

  // 刷新token
  refresh(data) {
    return request.post('/auth/refresh', data)
  },

  // 获取当前用户信息
  getMe() {
    return request.get('/auth/me')
  }
}
