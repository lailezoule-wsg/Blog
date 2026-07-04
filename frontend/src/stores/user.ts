import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { User } from '../types'
import { userApi } from '../api/user'
import { API_BASE } from '../api'

export const useUserStore = defineStore('user', () => {
  const user = ref<User | null>(null)
  const token = ref<string>(localStorage.getItem('token') || '')
  const refreshToken = ref<string>(localStorage.getItem('refreshToken') || '')

  const isLoggedIn = computed(() => !!token.value)
  const isAdmin = computed(() => user.value?.role === 'admin')
  const avatarUrl = computed(() =>
    user.value?.avatar_url ? `${API_BASE}${user.value.avatar_url}` : ''
  )

  function setTokens(accessToken: string, refresh: string) {
    token.value = accessToken
    refreshToken.value = refresh
    localStorage.setItem('token', accessToken)
    localStorage.setItem('refreshToken', refresh)
  }

  function setUser(userData: User) {
    user.value = userData
  }

  function logout() {
    user.value = null
    token.value = ''
    refreshToken.value = ''
    localStorage.removeItem('token')
    localStorage.removeItem('refreshToken')
  }

  async function fetchCurrentUser() {
    try {
      const res = await userApi.getCurrentUser()
      user.value = res.data.data
    } catch {
      logout()
    }
  }

  return {
    user,
    token,
    refreshToken,
    isLoggedIn,
    isAdmin,
    avatarUrl,
    setTokens,
    setUser,
    logout,
    fetchCurrentUser,
  }
})
