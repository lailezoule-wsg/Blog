import api from './index'
import type { User, LoginRequest, RegisterRequest, TokenResponse, ResponseModel } from '../types'

export const userApi = {
  register(data: RegisterRequest) {
    return api.post<ResponseModel<User>>('/api/users/register', data)
  },

  login(data: LoginRequest) {
    return api.post<ResponseModel<TokenResponse>>('/api/users/login', data)
  },

  refreshToken(refreshToken: string) {
    return api.post<ResponseModel<TokenResponse>>('/api/users/refresh', { refresh_token: refreshToken })
  },

  getCurrentUser() {
    return api.get<ResponseModel<User>>('/api/users/me')
  },

  updateCurrentUser(data: Partial<User>) {
    return api.put<ResponseModel<User>>('/api/users/me', data)
  },

  uploadAvatar(file: File) {
    const formData = new FormData()
    formData.append('file', file)
    return api.post<ResponseModel<{ avatar_url: string }>>('/api/users/me/avatar', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
  },
}
