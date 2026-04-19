import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { chatApi } from '../api/chat'
import { sessionApi } from '../api/session'

export const useChatStore = defineStore('chat', () => {
  // State
  const sessions = ref([])
  const currentSessionId = ref(null)
  const messages = ref([])
  const loading = ref(false)

  // Getters
  const currentSession = computed(() => {
    return sessions.value.find(s => s.id === currentSessionId.value)
  })

  // Actions
  const fetchSessions = async () => {
    const res = await sessionApi.getList()
    sessions.value = res
    return res
  }

  const createSession = async (name = '新会话') => {
    const res = await sessionApi.create({ session_name: name })
    sessions.value.unshift(res)
    currentSessionId.value = res.id
    messages.value = []
    return res
  }

  const selectSession = async (sessionId) => {
    currentSessionId.value = sessionId
    messages.value = []

    if (sessionId) {
      const res = await sessionApi.getHistory(sessionId)
      messages.value = res.messages.map(m => ({
        id: m.id,
        role: 'user',
        content: m.user_msg
      })).concat(res.messages.map(m => ({
        id: m.id + '_assistant',
        role: 'assistant',
        content: m.assistant_msg,
        dataDate: m.data_date
      })))

      // 按时间排序
      messages.value.sort((a, b) => a.id - b.id)
    }
  }

  const updateSessionName = async (sessionId, name) => {
    await sessionApi.update(sessionId, { session_name: name })
    const session = sessions.value.find(s => s.id === sessionId)
    if (session) {
      session.session_name = name
    }
  }

  const deleteSession = async (sessionId) => {
    await sessionApi.delete(sessionId)
    sessions.value = sessions.value.filter(s => s.id !== sessionId)
    if (currentSessionId.value === sessionId) {
      currentSessionId.value = null
      messages.value = []
    }
  }

  const sendMessage = async (content) => {
    if (!currentSessionId.value) {
      // 如果没有当前会话，创建一个
      await createSession()
    }

    // 添加用户消息到界面
    const userMessage = {
      id: Date.now(),
      role: 'user',
      content
    }
    messages.value.push(userMessage)

    loading.value = true

    try {
      const res = await chatApi.send({
        session_id: currentSessionId.value,
        message: content
      })

      // 添加AI回复到界面
      messages.value.push({
        id: Date.now() + 1,
        role: 'assistant',
        content: res.answer,
        dataDate: res.data_date,
        retrievedCount: res.retrieved_count
      })

      // 更新会话最新消息数
      const session = sessions.value.find(s => s.id === currentSessionId.value)
      if (session) {
        session.message_count = (session.message_count || 0) + 1
        session.updated_at = new Date().toISOString()
      }

      return res
    } finally {
      loading.value = false
    }
  }

  return {
    sessions,
    currentSessionId,
    messages,
    loading,
    currentSession,
    fetchSessions,
    createSession,
    selectSession,
    updateSessionName,
    deleteSession,
    sendMessage
  }
})
