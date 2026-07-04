import api from './index'
import type { Article, ArticleListItem, ResponseModel, PaginatedData } from '../types'

export const articleApi = {
  create(data: Partial<Article>) {
    return api.post<ResponseModel<Article>>('/api/articles', data)
  },

  getList(params: {
    page?: number
    size?: number
    sort_by?: string
    order?: string
    category_id?: number
    tag_id?: number
    q?: string
    status?: string
    author_id?: number
  }) {
    return api.get<ResponseModel<PaginatedData<ArticleListItem>>>('/api/articles', { params })
  },

  getById(id: number) {
    return api.get<ResponseModel<Article>>(`/api/articles/${id}`)
  },

  update(id: number, data: Partial<Article>) {
    return api.put<ResponseModel<Article>>(`/api/articles/${id}`, data)
  },

  delete(id: number) {
    return api.delete<ResponseModel<null>>(`/api/articles/${id}`)
  },

  publish(id: number) {
    return api.post<ResponseModel<Article>>(`/api/articles/${id}/publish`)
  },

  toggleLike(id: number) {
    return api.post<ResponseModel<{ liked: boolean }>>(`/api/articles/${id}/like`)
  },

  addTags(id: number, tagIds: number[]) {
    return api.post<ResponseModel<Article>>(`/api/articles/${id}/tags`, { tag_ids: tagIds })
  },

  removeTag(id: number, tagId: number) {
    return api.delete<ResponseModel<null>>(`/api/articles/${id}/tags/${tagId}`)
  },
}
