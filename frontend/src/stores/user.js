import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authApi } from '../api/auth'

export const useUserStore = defineStore('user', () => {
  // State
  const token = ref(localStorage.getItem('token') || '')
  const userInfo = ref(null)

  // Getters
  const isLoggedIn = computed(() => !!token.value)

  // Actions
  const setToken = (newToken) => {
    token.value = newToken
    localStorage.setItem('token', newToken)
  }

  const clearToken = () => {
    token.value = ''
    userInfo.value = null
    localStorage.removeItem('token')
  }

  const login = async (credentials) => {
    const res = await authApi.login(credentials)
    setToken(res.access_token)
    return res
  }

  const register = async (data) => {
    return await authApi.register(data)
  }

  const logout = () => {
    clearToken()
  }

  const fetchUserInfo = async () => {
    try {
      const res = await authApi.getMe()
      userInfo.value = res
      return res
    } catch (error) {
      clearToken()
      throw error
    }
  }

  return {
    token,
    userInfo,
    isLoggedIn,
    login,
    register,
    logout,
    fetchUserInfo
  }
})
