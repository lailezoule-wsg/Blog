import api from './index'
import type { Comment, ResponseModel, PaginatedData } from '../types'

export const commentApi = {
  create(articleId: number, data: { content: string; parent_id?: number }) {
    return api.post<ResponseModel<Comment>>(`/api/articles/${articleId}/comments`, data)
  },

  getList(articleId: number, params: { page?: number; size?: number }) {
    return api.get<ResponseModel<PaginatedData<Comment>>>(`/api/articles/${articleId}/comments`, { params })
  },

  update(articleId: number, commentId: number, data: { content: string }) {
    return api.put<ResponseModel<Comment>>(`/api/articles/${articleId}/comments/${commentId}`, data)
  },

  delete(articleId: number, commentId: number) {
    return api.delete<ResponseModel<null>>(`/api/articles/${articleId}/comments/${commentId}`)
  },

  approve(articleId: number, commentId: number) {
    return api.post<ResponseModel<Comment>>(`/api/articles/${articleId}/comments/${commentId}/approve`)
  },
}
