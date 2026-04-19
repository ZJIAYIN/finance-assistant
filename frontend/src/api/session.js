import request from './request'

export const sessionApi = {
  // 获取会话列表
  getList() {
    return request.get('/sessions')
  },

  // 创建会话
  create(data) {
    return request.post('/sessions', data)
  },

  // 获取会话历史
  getHistory(sessionId) {
    return request.get(`/sessions/${sessionId}/history`)
  },

  // 更新会话名称
  update(sessionId, data) {
    return request.put(`/sessions/${sessionId}`, data)
  },

  // 删除会话
  delete(sessionId) {
    return request.delete(`/sessions/${sessionId}`)
  }
}
