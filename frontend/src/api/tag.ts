import api from './index'
import type { Tag, ResponseModel, PaginatedData } from '../types'

export const tagApi = {
  create(data: Partial<Tag>) {
    return api.post<ResponseModel<Tag>>('/api/tags', data)
  },

  getList(page = 1, size = 20) {
    return api.get<ResponseModel<PaginatedData<Tag>>>('/api/tags', { params: { page, size } })
  },

  update(id: number, data: Partial<Tag>) {
    return api.put<ResponseModel<Tag>>(`/api/tags/${id}`, data)
  },

  delete(id: number) {
    return api.delete<ResponseModel<null>>(`/api/tags/${id}`)
  },
}
