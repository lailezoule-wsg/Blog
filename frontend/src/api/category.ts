import api from './index'
import type { Category, ResponseModel, PaginatedData } from '../types'

export const categoryApi = {
  create(data: Partial<Category>) {
    return api.post<ResponseModel<Category>>('/api/categories', data)
  },

  getList(page = 1, size = 20) {
    return api.get<ResponseModel<PaginatedData<Category>>>('/api/categories', { params: { page, size } })
  },

  update(id: number, data: Partial<Category>) {
    return api.put<ResponseModel<Category>>(`/api/categories/${id}`, data)
  },

  delete(id: number) {
    return api.delete<ResponseModel<null>>(`/api/categories/${id}`)
  },
}
