import api from './index'
import type { Subscription, ResponseModel, PaginatedData } from '../types'

export const subscriptionApi = {
  subscribe(email: string) {
    return api.post<ResponseModel<Subscription>>('/api/subscriptions', { email })
  },

  unsubscribe(email: string) {
    return api.delete<ResponseModel<null>>(`/api/subscriptions/${email}`)
  },

  getList(page = 1, size = 20) {
    return api.get<ResponseModel<PaginatedData<Subscription>>>('/api/subscriptions', { params: { page, size } })
  },
}
