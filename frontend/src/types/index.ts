export interface User {
  id: number
  username: string
  email: string
  avatar_url?: string
  bio?: string
  is_active: boolean
  role: string
  created_at: string
}

export interface LoginRequest {
  username: string
  password: string
}

export interface RegisterRequest {
  username: string
  email: string
  password: string
}

export interface TokenResponse {
  access_token: string
  refresh_token: string
  token_type: string
}

export interface Category {
  id: number
  name: string
  description?: string
  sort_order: number
  created_at: string
}

export interface Tag {
  id: number
  name: string
  created_at: string
}

export interface Article {
  id: number
  title: string
  content: string
  summary?: string
  cover_image?: string
  view_count: number
  like_count: number
  status: string
  is_private: boolean
  author_id: number
  category_id?: number
  published_at?: string
  created_at: string
  updated_at: string
  author?: UserBrief
  category?: Category
  tags: Tag[]
}

export interface ArticleListItem {
  id: number
  title: string
  summary?: string
  cover_image?: string
  view_count: number
  like_count: number
  status: string
  author_id: number
  published_at?: string
  created_at: string
  author?: UserBrief
  category?: Category
  tags: Tag[]
}

export interface UserBrief {
  id: number
  username: string
  avatar_url?: string
}

export interface Comment {
  id: number
  content: string
  article_id: number
  user_id?: number
  parent_id?: number
  is_approved: boolean
  created_at: string
  user?: UserBrief
  replies: Comment[]
}

export interface Subscription {
  id: number
  email: string
  is_active: boolean
  created_at: string
}

export interface ResponseModel<T> {
  code: number
  message: string
  data: T
}

export interface PaginatedData<T> {
  items: T[]
  total: number
  page: number
  size: number
}
