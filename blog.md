# FastAPI 实战项目：个人博客系统（BlogBox）

## 一、项目简介

BlogBox 是一个功能完整的个人博客系统，包含用户认证、文章管理、评论系统、分类标签、全文搜索、图片上传、WebSocket 实时通知等功能。通过这个项目，你将系统性地掌握 FastAPI 的核心知识点。

---

## 二、学习目标与知识点覆盖

| 知识点 | 对应功能 |
|--------|----------|
| 路由与路径操作（GET/POST/PUT/DELETE） | 所有 CRUD 接口 |
| 路径参数、查询参数、请求体 | 文章详情、列表筛选、创建/更新 |
| Pydantic 模型（请求/响应分离） | 所有接口的入参和出参校验 |
| 依赖注入系统（Depends） | 认证校验、权限控制、分页、数据库会话 |
| OAuth2 + JWT 认证 | 用户登录、Token 刷新 |
| 中间件（Middleware） | 请求日志、CORS、响应时间统计 |
| 后台任务（BackgroundTasks） | 文章发布后异步发送邮件通知订阅者 |
| WebSocket | 新评论实时通知 |
| 文件上传（UploadFile） | 文章封面图、头像上传 |
| 异常处理（HTTPException + 自定义异常处理器） | 全局错误响应格式统一 |
| 响应模型（response_model） | 控制返回字段、排除敏感信息 |
| 分页与排序 | 文章列表接口 |
| 数据库会话管理（yield 依赖） | get_db 依赖注入 |
| 子路由（APIRouter） | 按模块拆分路由 |
| 生命周期事件（lifespan） | 应用启动时初始化资源 |

---

## 三、技术栈

| 层级 | 技术 |
|------|------|
| 后端框架 | FastAPI |
| ORM | SQLAlchemy 2.0（async） |
| 数据库迁移 | Alembic |
| 数据库 | SQLite（开发）/ PostgreSQL（生产） |
| 认证 | JWT + OAuth2 Password Bearer |
| 缓存 | Redis（可选） |

---

## 四、数据库设计

### 4.1 用户表 users

| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer, PK | 主键 |
| username | String(50), unique | 用户名 |
| email | String(100), unique | 邮箱 |
| hashed_password | String(255) | 哈希密码 |
| avatar_url | String(255), nullable | 头像路径 |
| bio | Text, nullable | 个人简介 |
| is_active | Boolean | 是否启用 |
| role | String(20) | 角色：user / admin |
| created_at | DateTime | 创建时间 |
| updated_at | DateTime | 更新时间 |

### 4.2 文章表 articles

| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer, PK | 主键 |
| title | String(200) | 文章标题 |
| content | Text | 文章内容（Markdown） |
| summary | String(500), nullable | 文章摘要 |
| cover_image | String(255), nullable | 封面图路径 |
| view_count | Integer | 浏览次数 |
| like_count | Integer | 点赞数 |
| status | String(20) | 状态：draft / published |
| is_private | Boolean | 是否私密 |
| author_id | Integer, FK | 作者 ID |
| category_id | Integer, FK, nullable | 分类 ID |
| published_at | DateTime, nullable | 发布时间 |
| created_at | DateTime | 创建时间 |
| updated_at | DateTime | 更新时间 |

### 4.3 分类表 categories

| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer, PK | 主键 |
| name | String(50) | 分类名称 |
| description | String(200), nullable | 分类描述 |
| sort_order | Integer | 排序权重 |
| created_at | DateTime | 创建时间 |

### 4.4 标签表 tags

| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer, PK | 主键 |
| name | String(30), unique | 标签名称 |
| created_at | DateTime | 创建时间 |

### 4.5 评论表 comments

| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer, PK | 主键 |
| content | Text | 评论内容 |
| article_id | Integer, FK | 所属文章 |
| user_id | Integer, FK, nullable | 评论用户（可为匿名） |
| nickname | String(100) | 匿名用户 |
| parent_id | Integer, FK, nullable | 父评论 ID（支持回复） |
| is_approved | Boolean | 是否审核通过 |
| created_at | DateTime | 创建时间 |



### 4.6 文章-标签关联表 article_tags

| 字段 | 类型 | 说明 |
|------|------|------|
| article_id | Integer, FK | 文章 ID |
| tag_id | Integer, FK | 标签 ID |

### 4.7 点赞表 likes

| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer, PK | 主键 |
| user_id | Integer, FK | 用户 ID |
| article_id | Integer, FK | 文章 ID |
| created_at | DateTime | 创建时间 |

### 4.8 订阅表 subscriptions

| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer, PK | 主键 |
| email | String(100) | 订阅邮箱 |
| is_active | Boolean | 是否有效 |
| created_at | DateTime | 创建时间 |

### 4.9 浏览记录表 view_records

| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer, PK | 主键 |
| user_id | Integer, FK, nullable | 浏览用户（匿名用户为 null） |
| article_id | Integer, FK | 文章 ID |
| ip_address | String(45), nullable | 访客 IP 地址（用于匿名用户去重） |
| created_at | DateTime | 浏览时间 |

> **索引**：`(article_id, created_at)` 用于按文章聚合浏览趋势；`(user_id, created_at)` 用于查询用户阅读历史。
>
> **说明**：`view_count` 字段仍作为文章表的缓存值，每次访问详情接口时同步 +1 并写入本表。趋势统计、去重浏览量、用户阅读历史等场景均从本表聚合查询。

---

## 五、接口设计

### 5.1 用户模块 `/api/users`

| 方法 | 路径 | 说明 | 认证 |
|------|------|------|------|
| POST | /register | 用户注册 | 否 |
| POST | /login | 登录获取 Token | 否 |
| POST | /refresh | 刷新 Token | 是 |
| GET | /me | 获取当前用户信息 | 是 |
| PUT | /me | 更新用户信息 | 是 |
| POST | /me/avatar | 上传头像 | 是 |

#### POST /register — 用户注册

**请求体（JSON）：**

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| username | string | 是 | 用户名，3-50 字符 |
| email | string | 是 | 邮箱，需符合邮箱格式 |
| password | string | 是 | 密码，不少于 8 位 |

```json
{
  "username": "zhangsan",
  "email": "zhangsan@example.com",
  "password": "MyPass1234"
}
```

**成功响应 `201`：**
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "id": 1,
    "username": "zhangsan",
    "email": "zhangsan@example.com",
    "avatar_url": null,
    "bio": null,
    "is_active": true,
    "role": "user",
    "created_at": "2026-07-02T10:00:00",
    "updated_at": "2026-07-02T10:00:00"
  }
}
```

**错误响应 `400`：**
```json
{
  "code": 400,
  "message": "用户名已存在",
  "detail": null
}
```

---

#### POST /login — 登录获取 Token

**请求体（form-data / x-www-form-urlencoded）：**

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| username | string | 是 | 用户名 |
| password | string | 是 | 密码 |

> 采用 OAuth2 Password 模式，Content-Type 为 `application/x-www-form-urlencoded`。

**成功响应 `200`：**
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer"
  }
}
```

**错误响应 `401`：**
```json
{
  "code": 401,
  "message": "用户名或密码错误",
  "detail": null
}
```

---

#### POST /refresh — 刷新 Token

**请求头：** `Authorization: Bearer <access_token>`

**成功响应 `200`：**
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer"
  }
}
```

**错误响应 `401`：**
```json
{
  "code": 401,
  "message": "Token 已过期或无效",
  "detail": null
}
```

---

#### GET /me — 获取当前用户信息

**请求头：** `Authorization: Bearer <access_token>`

**成功响应 `200`：**
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "id": 1,
    "username": "zhangsan",
    "email": "zhangsan@example.com",
    "avatar_url": "/uploads/avatars/1_avatar.jpg",
    "bio": "一个热爱编程的开发者",
    "is_active": true,
    "role": "user",
    "created_at": "2026-07-02T10:00:00",
    "updated_at": "2026-07-02T10:00:00"
  }
}
```

---

#### PUT /me — 更新用户信息

**请求头：** `Authorization: Bearer <access_token>`

**请求体（JSON）：**

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| username | string | 否 | 新用户名，3-50 字符 |
| email | string | 否 | 新邮箱 |
| bio | string | 否 | 个人简介，最长 500 字符 |
| password | string | 否 | 新密码，不少于 8 位 |

```json
{
  "bio": "全栈开发者，专注于 Python 和 FastAPI",
  "email": "newemail@example.com"
}
```

**成功响应 `200`：**
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "id": 1,
    "username": "zhangsan",
    "email": "newemail@example.com",
    "avatar_url": "/uploads/avatars/1_avatar.jpg",
    "bio": "全栈开发者，专注于 Python 和 FastAPI",
    "is_active": true,
    "role": "user",
    "created_at": "2026-07-02T10:00:00",
    "updated_at": "2026-07-02T12:00:00"
  }
}
```

---

#### POST /me/avatar — 上传头像

**请求头：** `Authorization: Bearer <access_token>`，`Content-Type: multipart/form-data`

**请求参数（form-data）：**

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| file | file | 是 | 图片文件，支持 jpg/png/gif，最大 2MB |

**成功响应 `200`：**
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "avatar_url": "/uploads/avatars/1_avatar_1719900000.jpg"
  }
}
```

**错误响应 `400`：**
```json
{
  "code": 400,
  "message": "文件类型不支持，仅允许 jpg/png/gif",
  "detail": null
}
```

### 5.2 文章模块 `/api/articles`

| 方法 | 路径 | 说明 | 认证 |
|------|------|------|------|
| POST | / | 创建文章 | 是 |
| GET | / | 文章列表（分页、排序、筛选、搜索） | 否 |
| GET | /{id} | 文章详情（增加浏览数） | 否 |
| PUT | /{id} | 更新文章 | 是（仅作者） |
| DELETE | /{id} | 删除文章 | 是（仅作者或admin） |
| POST | /{id}/publish | 发布文章（draft → published） | 是（仅作者） |
| POST | /{id}/like | 点赞/取消点赞 | 是 |
| POST | /{id}/tags | 为文章添加标签 | 是 |
| DELETE | /{id}/tags/{tag_id} | 移除文章标签 | 是 |
| GET | /stats | 文章浏览量统计（排行、趋势、总览） | 是（admin） |

#### POST / — 创建文章

**请求头：** `Authorization: Bearer <access_token>`

**请求体（JSON）：**

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| title | string | 是 | 文章标题，最长 200 字符 |
| content | string | 是 | 文章内容（Markdown 格式） |
| summary | string | 否 | 文章摘要，最长 500 字符 |
| cover_image | string | 否 | 封面图路径 |
| category_id | integer | 否 | 分类 ID |
| is_private | boolean | 否 | 是否私密，默认 false |
| tag_ids | array[integer] | 否 | 标签 ID 列表 |

```json
{
  "title": "FastAPI 入门指南",
  "content": "## 简介\n\nFastAPI 是一个现代、高性能的 Python Web 框架...",
  "summary": "本文介绍 FastAPI 的基本概念和快速上手方法",
  "category_id": 1,
  "is_private": false,
  "tag_ids": [1, 3]
}
```

**成功响应 `201`：**
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "id": 1,
    "title": "FastAPI 入门指南",
    "content": "## 简介\n\nFastAPI 是一个现代、高性能的 Python Web 框架...",
    "summary": "本文介绍 FastAPI 的基本概念和快速上手方法",
    "cover_image": null,
    "view_count": 0,
    "like_count": 0,
    "status": "draft",
    "is_private": false,
    "author_id": 1,
    "category_id": 1,
    "published_at": null,
    "created_at": "2026-07-02T10:00:00",
    "updated_at": "2026-07-02T10:00:00",
    "author": {
      "id": 1,
      "username": "zhangsan"
    },
    "category": {
      "id": 1,
      "name": "技术"
    },
    "tags": [
      {"id": 1, "name": "Python"},
      {"id": 3, "name": "FastAPI"}
    ]
  }
}
```

---

#### GET / — 文章列表

**查询参数：**

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| page | integer | 否 | 1 | 页码 |
| size | integer | 否 | 20 | 每页条数，最大 100 |
| sort_by | string | 否 | created_at | 排序字段：created_at / published_at / view_count / like_count |
| order | string | 否 | desc | 排序方向：asc / desc |
| category_id | integer | 否 | - | 按分类 ID 筛选 |
| tag_id | integer | 否 | - | 按标签 ID 筛选 |
| q | string | 否 | - | 关键词搜索（匹配 title、content、summary） |
| status | string | 否 | - | 按状态筛选：draft / published |
| author_id | integer | 否 | - | 按作者 ID 筛选 |

**请求示例：**
```
GET /api/articles?page=1&size=10&sort_by=view_count&order=desc&category_id=1&q=FastAPI
```

**成功响应 `200`：**
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "items": [
      {
        "id": 1,
        "title": "FastAPI 入门指南",
        "summary": "本文介绍 FastAPI 的基本概念和快速上手方法",
        "cover_image": "/uploads/covers/fastapi.jpg",
        "view_count": 320,
        "like_count": 45,
        "status": "published",
        "is_private": false,
        "author_id": 1,
        "category_id": 1,
        "published_at": "2026-07-02T10:00:00",
        "created_at": "2026-07-02T10:00:00",
        "author": {
          "id": 1,
          "username": "zhangsan"
        },
        "category": {
          "id": 1,
          "name": "技术"
        },
        "tags": [
          {"id": 1, "name": "Python"},
          {"id": 3, "name": "FastAPI"}
        ]
      }
    ],
    "total": 56,
    "page": 1,
    "size": 10
  }
}
```

---

#### GET /{id} — 文章详情

**路径参数：**

| 参数 | 类型 | 说明 |
|------|------|------|
| id | integer | 文章 ID |

**请求示例：**
```
GET /api/articles/1
```

> 每次请求该接口，`view_count` 自动 +1。

**成功响应 `200`：**
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "id": 1,
    "title": "FastAPI 入门指南",
    "content": "## 简介\n\nFastAPI 是一个现代、高性能的 Python Web 框架...",
    "summary": "本文介绍 FastAPI 的基本概念和快速上手方法",
    "cover_image": "/uploads/covers/fastapi.jpg",
    "view_count": 321,
    "like_count": 45,
    "status": "published",
    "is_private": false,
    "author_id": 1,
    "category_id": 1,
    "published_at": "2026-07-02T10:00:00",
    "created_at": "2026-07-02T10:00:00",
    "updated_at": "2026-07-02T12:00:00",
    "author": {
      "id": 1,
      "username": "zhangsan",
      "avatar_url": "/uploads/avatars/1_avatar.jpg"
    },
    "category": {
      "id": 1,
      "name": "技术"
    },
    "tags": [
      {"id": 1, "name": "Python"},
      {"id": 3, "name": "FastAPI"}
    ],
    "is_liked": false
  }
}
```

**错误响应 `404`：**
```json
{
  "code": 404,
  "message": "文章不存在",
  "detail": null
}
```

---

#### PUT /{id} — 更新文章

**请求头：** `Authorization: Bearer <access_token>`

**路径参数：**

| 参数 | 类型 | 说明 |
|------|------|------|
| id | integer | 文章 ID |

**请求体（JSON）：**

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| title | string | 否 | 文章标题 |
| content | string | 否 | 文章内容 |
| summary | string | 否 | 文章摘要 |
| cover_image | string | 否 | 封面图路径 |
| category_id | integer | 否 | 分类 ID |
| is_private | boolean | 否 | 是否私密 |

```json
{
  "title": "FastAPI 入门指南（修订版）",
  "summary": "全面介绍 FastAPI 核心特性"
}
```

**成功响应 `200`：**
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "id": 1,
    "title": "FastAPI 入门指南（修订版）",
    "content": "## 简介\n\nFastAPI 是一个现代、高性能的 Python Web 框架...",
    "summary": "全面介绍 FastAPI 核心特性",
    "cover_image": "/uploads/covers/fastapi.jpg",
    "view_count": 321,
    "like_count": 45,
    "status": "draft",
    "is_private": false,
    "author_id": 1,
    "category_id": 1,
    "published_at": null,
    "created_at": "2026-07-02T10:00:00",
    "updated_at": "2026-07-02T14:00:00"
  }
}
```

**错误响应 `403`：**
```json
{
  "code": 403,
  "message": "无权编辑他人文章",
  "detail": null
}
```

---

#### DELETE /{id} — 删除文章

**请求头：** `Authorization: Bearer <access_token>`

**路径参数：**

| 参数 | 类型 | 说明 |
|------|------|------|
| id | integer | 文章 ID |

**成功响应 `200`：**
```json
{
  "code": 200,
  "message": "文章已删除",
  "data": null
}
```

---

#### POST /{id}/publish — 发布文章

**请求头：** `Authorization: Bearer <access_token>`

**路径参数：**

| 参数 | 类型 | 说明 |
|------|------|------|
| id | integer | 文章 ID |

> 将文章状态从 draft 变为 published，并记录 published_at。发布后会触发后台任务通知订阅者。

**成功响应 `200`：**

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "id": 1,
    "title": "FastAPI 入门指南",
    "status": "published",
    "published_at": "2026-07-02T15:00:00"
  }
}
```

**错误响应 `400`：**
```json
{
  "code": 400,
  "message": "文章已发布，不可重复发布",
  "detail": null
}
```

---

#### POST /{id}/like — 点赞/取消点赞

**请求头：** `Authorization: Bearer <access_token>`

**路径参数：**

| 参数 | 类型 | 说明 |
|------|------|------|
| id | integer | 文章 ID |

> Toggle 模式：第一次调用点赞，再次调用取消点赞。

**成功响应 `200`（点赞）：**
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "liked": true,
    "like_count": 46
  }
}
```

**成功响应 `200`（取消点赞）：**
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "liked": false,
    "like_count": 45
  }
}
```

---

#### POST /{id}/tags — 为文章添加标签

**请求头：** `Authorization: Bearer <access_token>`

**路径参数：**

| 参数 | 类型 | 说明 |
|------|------|------|
| id | integer | 文章 ID |

**请求体（JSON）：**

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| tag_ids | array[integer] | 是 | 要添加的标签 ID 列表 |

```json
{
  "tag_ids": [2, 5]
}
```

**成功响应 `200`：**
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "tags": [
      {"id": 1, "name": "Python"},
      {"id": 2, "name": "Web"},
      {"id": 3, "name": "FastAPI"},
      {"id": 5, "name": "教程"}
    ]
  }
}
```

---

#### DELETE /{id}/tags/{tag_id} — 移除文章标签

**请求头：** `Authorization: Bearer <access_token>`

**路径参数：**

| 参数 | 类型 | 说明 |
|------|------|------|
| id | integer | 文章 ID |
| tag_id | integer | 标签 ID |

**成功响应 `200`：**
```json
{
  "code": 200,
  "message": "标签已移除",
  "data": null
}
```

---

#### GET /stats — 文章浏览量统计

**请求头：** `Authorization: Bearer <access_token>`（仅 admin）

> 提供文章浏览量的总览、排行和趋势数据，用于后台数据分析面板。

**查询参数：**

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| type | string | 否 | overview | 统计类型：overview（总览）/ ranking（排行）/ trend（趋势） |
| period | string | 否 | week | 统计周期：day / week / month，仅 trend 类型生效 |
| top | integer | 否 | 10 | 排行数量，仅 ranking 类型生效，最大 50 |

**请求示例（总览）：**
```
GET /api/articles/stats?type=overview
```

**成功响应 `200`（overview）：**
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "total_views": 15230,
    "total_likes": 892,
    "total_articles": 56,
    "avg_views_per_article": 272.0,
    "most_viewed_article": {
      "id": 1,
      "title": "FastAPI 入门指南",
      "view_count": 1024
    },
    "today_views": 128,
    "published_count": 42,
    "draft_count": 14
  }
}
```

**请求示例（排行）：**
```
GET /api/articles/stats?type=ranking&top=5
```

**成功响应 `200`（ranking）：**
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "items": [
      {
        "id": 1,
        "title": "FastAPI 入门指南",
        "view_count": 1024,
        "like_count": 89,
        "author": {
          "id": 1,
          "username": "zhangsan"
        },
        "published_at": "2026-07-02T10:00:00"
      },
      {
        "id": 3,
        "title": "Python 异步编程详解",
        "view_count": 876,
        "like_count": 67,
        "author": {
          "id": 2,
          "username": "lisi"
        },
        "published_at": "2026-07-01T08:00:00"
      }
    ],
    "total": 5
  }
}
```

**请求示例（趋势）：**
```
GET /api/articles/stats?type=trend&period=week
```

**成功响应 `200`（trend）：**
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "period": "week",
    "items": [
      {"date": "2026-06-28", "views": 180, "articles_published": 2},
      {"date": "2026-06-29", "views": 210, "articles_published": 1},
      {"date": "2026-06-30", "views": 195, "articles_published": 3},
      {"date": "2026-07-01", "views": 250, "articles_published": 0},
      {"date": "2026-07-02", "views": 310, "articles_published": 2},
      {"date": "2026-07-03", "views": 128, "articles_published": 1},
      {"date": "2026-07-04", "views": 95, "articles_published": 0}
    ],
    "total_views": 1368,
    "total_published": 9
  }
}
```

**错误响应 `403`：**
```json
{
  "code": 403,
  "message": "无权访问文章统计数据",
  "detail": null
}
```

### 5.3 评论模块 `/api/articles/{article_id}/comments`

| 方法 | 路径 | 说明 | 认证 |
|------|------|------|------|
| POST | / | 发表评论 | 否 |
| GET | / | 文章评论列表（支持分页） | 否 |
| PUT | /{comment_id} | 编辑评论 | 是（仅评论者） |
| DELETE | /{comment_id} | 删除评论 | 是（仅评论者或admin） |
| POST | /{comment_id}/approve | 审核评论 | 是（仅文章作者或admin） |

#### POST / — 发表评论

**路径参数：**

| 参数 | 类型 | 说明 |
|------|------|------|
| article_id | integer | 文章 ID |

**请求体（JSON）：**

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| content | string | 是 | 评论内容 |
| nickname | string | 否 | 匿名评论时的昵称（未登录时必填） |
| parent_id | integer | 否 | 父评论 ID（回复某条评论时传入） |

**请求示例（登录用户评论）：**

请求头：`Authorization: Bearer <access_token>`

```json
{
  "content": "写得很好，学到了！"
}
```

**请求示例（匿名评论）：**

```json
{
  "content": "不错的文章",
  "nickname": "路过的小伙伴"
}
```

**请求示例（回复评论）：**

请求头：`Authorization: Bearer <access_token>`

```json
{
  "content": "感谢补充！",
  "parent_id": 3
}
```

**成功响应 `201`：**
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "id": 10,
    "content": "写得很好，学到了！",
    "article_id": 1,
    "user_id": 1,
    "parent_id": null,
    "is_approved": false,
    "created_at": "2026-07-02T16:00:00",
    "user": {
      "id": 1,
      "username": "zhangsan"
    },
    "parent": null
  }
}
```

**错误响应 `404`：**
```json
{
  "code": 404,
  "message": "文章不存在",
  "detail": null
}
```

---

#### GET / — 文章评论列表

**路径参数：**

| 参数 | 类型 | 说明 |
|------|------|------|
| article_id | integer | 文章 ID |

**查询参数：**

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| page | integer | 否 | 1 | 页码 |
| size | integer | 否 | 20 | 每页条数 |

**请求示例：**
```
GET /api/articles/1/comments?page=1&size=10
```

**成功响应 `200`：**
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "items": [
      {
        "id": 5,
        "content": "写得很好，学到了！",
        "article_id": 1,
        "user_id": 1,
        "parent_id": null,
        "is_approved": true,
        "created_at": "2026-07-02T16:00:00",
        "user": {
          "id": 1,
          "username": "zhangsan"
        },
        "parent": null,
        "replies": [
          {
            "id": 6,
            "content": "感谢支持！",
            "article_id": 1,
            "user_id": 2,
            "parent_id": 5,
            "is_approved": true,
            "created_at": "2026-07-02T16:30:00",
            "user": {
              "id": 2,
              "username": "lisi"
            }
          }
        ]
      }
    ],
    "total": 12,
    "page": 1,
    "size": 10
  }
}
```

---

#### PUT /{comment_id} — 编辑评论

**请求头：** `Authorization: Bearer <access_token>`

**路径参数：**

| 参数 | 类型 | 说明 |
|------|------|------|
| article_id | integer | 文章 ID |
| comment_id | integer | 评论 ID |

**请求体（JSON）：**

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| content | string | 是 | 修改后的评论内容 |

```json
{
  "content": "修改后的评论内容"
}
```

**成功响应 `200`：**
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "id": 5,
    "content": "修改后的评论内容",
    "article_id": 1,
    "user_id": 1,
    "parent_id": null,
    "is_approved": true,
    "created_at": "2026-07-02T16:00:00"
  }
}
```

**错误响应 `403`：**
```json
{
  "code": 403,
  "message": "无权编辑他人评论",
  "detail": null
}
```

---

#### DELETE /{comment_id} — 删除评论

**请求头：** `Authorization: Bearer <access_token>`

**路径参数：**

| 参数 | 类型 | 说明 |
|------|------|------|
| article_id | integer | 文章 ID |
| comment_id | integer | 评论 ID |

**成功响应 `200`：**
```json
{
  "code": 200,
  "message": "评论已删除",
  "data": null
}
```

---

#### POST /{comment_id}/approve — 审核评论

**请求头：** `Authorization: Bearer <access_token>`

**路径参数：**

| 参数 | 类型 | 说明 |
|------|------|------|
| article_id | integer | 文章 ID |
| comment_id | integer | 评论 ID |

> 仅文章作者或 admin 可以审核评论。审核通过后评论才会公开展示。

**成功响应 `200`：**
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "id": 5,
    "content": "写得很好，学到了！",
    "is_approved": true
  }
}
```

**错误响应 `403`：**
```json
{
  "code": 403,
  "message": "无权审核该评论",
  "detail": null
}
```

### 5.4 分类模块 `/api/categories`

| 方法 | 路径 | 说明 | 认证 |
|------|------|------|------|
| POST | / | 创建分类 | 是（admin） |
| GET | / | 分类列表 | 否 |
| PUT | /{id} | 更新分类 | 是（admin） |
| DELETE | /{id} | 删除分类 | 是（admin） |

#### POST / — 创建分类

**请求头：** `Authorization: Bearer <access_token>`

**请求体（JSON）：**

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| name | string | 是 | 分类名称，最长 50 字符 |
| description | string | 否 | 分类描述，最长 200 字符 |
| sort_order | integer | 否 | 排序权重，默认 0 |

```json
{
  "name": "技术",
  "description": "技术类文章",
  "sort_order": 1
}
```

**成功响应 `201`：**
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "id": 1,
    "name": "技术",
    "description": "技术类文章",
    "sort_order": 1,
    "created_at": "2026-07-02T10:00:00"
  }
}
```

**错误响应 `400`：**
```json
{
  "code": 400,
  "message": "分类名称已存在",
  "detail": null
}
```

---

#### GET / — 分类列表

**查询参数：**

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| page | integer | 否 | 1 | 页码 |
| size | integer | 否 | 20 | 每页条数 |

**请求示例：**
```
GET /api/categories?page=1&size=10
```

**成功响应 `200`：**
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "items": [
      {
        "id": 1,
        "name": "技术",
        "description": "技术类文章",
        "sort_order": 1,
        "created_at": "2026-07-02T10:00:00",
        "article_count": 15
      },
      {
        "id": 2,
        "name": "生活",
        "description": "生活随笔",
        "sort_order": 2,
        "created_at": "2026-07-02T10:30:00",
        "article_count": 8
      }
    ],
    "total": 5,
    "page": 1,
    "size": 10
  }
}
```

---

#### PUT /{id} — 更新分类

**请求头：** `Authorization: Bearer <access_token>`

**路径参数：**

| 参数 | 类型 | 说明 |
|------|------|------|
| id | integer | 分类 ID |

**请求体（JSON）：**

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| name | string | 否 | 分类名称 |
| description | string | 否 | 分类描述 |
| sort_order | integer | 否 | 排序权重 |

```json
{
  "name": "编程技术",
  "sort_order": 10
}
```

**成功响应 `200`：**
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "id": 1,
    "name": "编程技术",
    "description": "技术类文章",
    "sort_order": 10,
    "created_at": "2026-07-02T10:00:00"
  }
}
```

---

#### DELETE /{id} — 删除分类

**请求头：** `Authorization: Bearer <access_token>`

**路径参数：**

| 参数 | 类型 | 说明 |
|------|------|------|
| id | integer | 分类 ID |

> 删除分类后，该分类下的文章 category_id 置为 null。

**成功响应 `200`：**
```json
{
  "code": 200,
  "message": "分类已删除",
  "data": null
}
```

---

### 5.5 标签模块 `/api/tags`

| 方法 | 路径 | 说明 | 认证 |
|------|------|------|------|
| POST | / | 创建标签 | 是 |
| GET | / | 标签列表 | 否 |
| PUT | /{id} | 更新标签 | 是（admin） |
| DELETE | /{id} | 删除标签 | 是（admin） |

#### POST / — 创建标签

**请求头：** `Authorization: Bearer <access_token>`

**请求体（JSON）：**

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| name | string | 是 | 标签名称，最长 30 字符，唯一 |

```json
{
  "name": "Python"
}
```

**成功响应 `201`：**
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "id": 1,
    "name": "Python",
    "created_at": "2026-07-02T10:00:00"
  }
}
```

**错误响应 `400`：**
```json
{
  "code": 400,
  "message": "标签名称已存在",
  "detail": null
}
```

---

#### GET / — 标签列表

**查询参数：**

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| page | integer | 否 | 1 | 页码 |
| size | integer | 否 | 20 | 每页条数 |

**请求示例：**
```
GET /api/tags?page=1&size=10
```

**成功响应 `200`：**
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "items": [
      {
        "id": 1,
        "name": "Python",
        "created_at": "2026-07-02T10:00:00",
        "article_count": 20
      },
      {
        "id": 2,
        "name": "FastAPI",
        "created_at": "2026-07-02T10:10:00",
        "article_count": 12
      }
    ],
    "total": 10,
    "page": 1,
    "size": 10
  }
}
```

---

#### PUT /{id} — 更新标签

**请求头：** `Authorization: Bearer <access_token>`

**路径参数：**

| 参数 | 类型 | 说明 |
|------|------|------|
| id | integer | 标签 ID |

**请求体（JSON）：**

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| name | string | 是 | 新标签名称 |

```json
{
  "name": "Python3"
}
```

**成功响应 `200`：**
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "id": 1,
    "name": "Python3",
    "created_at": "2026-07-02T10:00:00"
  }
}
```

---

#### DELETE /{id} — 删除标签

**请求头：** `Authorization: Bearer <access_token>`

**路径参数：**

| 参数 | 类型 | 说明 |
|------|------|------|
| id | integer | 标签 ID |

> 删除标签时，同时删除 article_tags 关联记录。

**成功响应 `200`：**
```json
{
  "code": 200,
  "message": "标签已删除",
  "data": null
}
```

---

### 5.6 订阅模块 `/api/subscriptions`

| 方法 | 路径 | 说明 | 认证 |
|------|------|------|------|
| POST | / | 订阅 | 否 |
| DELETE | /{email} | 取消订阅 | 否 |
| GET | / | 订阅列表 | 是（admin） |

#### POST / — 订阅

**请求体（JSON）：**

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| email | string | 是 | 订阅邮箱，需符合邮箱格式 |

```json
{
  "email": "subscriber@example.com"
}
```

**成功响应 `201`：**
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "id": 1,
    "email": "subscriber@example.com",
    "is_active": true,
    "created_at": "2026-07-02T10:00:00"
  }
}
```

**错误响应 `400`：**
```json
{
  "code": 400,
  "message": "该邮箱已订阅",
  "detail": null
}
```

---

#### DELETE /{email} — 取消订阅

**路径参数：**

| 参数 | 类型 | 说明 |
|------|------|------|
| email | string | 订阅邮箱（URL 编码） |

**请求示例：**
```
DELETE /api/subscriptions/subscriber%40example.com
```

**成功响应 `200`：**
```json
{
  "code": 200,
  "message": "已取消订阅",
  "data": null
}
```

---

#### GET / — 订阅列表

**请求头：** `Authorization: Bearer <access_token>`

**查询参数：**

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| page | integer | 否 | 1 | 页码 |
| size | integer | 否 | 20 | 每页条数 |

**成功响应 `200`：**
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "items": [
      {
        "id": 1,
        "email": "subscriber@example.com",
        "is_active": true,
        "created_at": "2026-07-02T10:00:00"
      }
    ],
    "total": 50,
    "page": 1,
    "size": 20
  }
}
```

**错误响应 `403`：**
```json
{
  "code": 403,
  "message": "无权访问订阅列表",
  "detail": null
}
```

### 5.7 WebSocket `/ws/notifications`

**连接方式：**

客户端通过 WebSocket 协议连接到服务端，可以携带认证 Token：

```
ws://localhost:8000/ws/notifications?token=<access_token>
```

或

```
wss://yourdomain.com/ws/notifications?token=<access_token>
```

#### 消息类型

服务端会推送以下类型的消息：

##### 1. 新评论通知 `new_comment`

当文章有新评论时推送：

```json
{
  "type": "new_comment",
  "data": {
    "article_id": 1,
    "comment_id": 5,
    "commenter": "张三",
    "content": "写得很好！",
    "created_at": "2026-07-02T16:00:00"
  }
}
```

##### 2. 文章发布通知 `article_published`

当订阅的文章发布时推送：

```json
{
  "type": "article_published",
  "data": {
    "article_id": 10,
    "title": "FastAPI 高级用法",
    "author": "李四",
    "published_at": "2026-07-02T17:00:00"
  }
}
```

##### 3. 连接成功确认 `connected`

客户端连接成功后，服务端返回确认消息：

```json
{
  "type": "connected",
  "data": {
    "message": "WebSocket 连接成功",
    "user_id": 1
  }
}
```

#### 客户端示例（JavaScript）

```javascript
const ws = new WebSocket('ws://localhost:8000/ws/notifications?token=YOUR_TOKEN');

ws.onopen = () => {
  console.log('WebSocket 连接已建立');
};

ws.onmessage = (event) => {
  const message = JSON.parse(event.data);
  
  switch (message.type) {
    case 'new_comment':
      console.log(`新评论：${message.data.commenter} - ${message.data.content}`);
      // 显示通知
      break;
    case 'article_published':
      console.log(`新文章：${message.data.title}`);
      // 刷新文章列表
      break;
    case 'connected':
      console.log('连接确认：', message.data.message);
      break;
  }
};

ws.onerror = (error) => {
  console.error('WebSocket 错误：', error);
};

ws.onclose = () => {
  console.log('WebSocket 连接已关闭');
  // 可选：实现重连逻辑
};
```

#### 注意事项

- WebSocket 连接需要有效的 access_token，否则会被拒绝。
- 服务端会维护在线用户列表，只向相关用户推送通知。
- 建议客户端实现断线重连机制。
- 对于大量并发场景，可考虑使用 Redis Pub/Sub 进行分布式消息传递。

---

## 六、业务规则

1. **注册**：用户名 3-50 字符，邮箱格式校验，密码不少于 8 位，使用 bcrypt 哈希。
2. **登录**：OAuth2 Password 模式，access_token 有效期 30 分钟，refresh_token 有效期 7 天。
3. **文章发布**：创建时默认为 draft，调用 publish 接口后变为 published，并记录 published_at。
4. **浏览数**：每次访问文章详情接口，`view_count` 自动 +1，同时写入 `view_records` 表（记录 user_id 或 ip_address）。
5. **点赞**：同一用户对同一文章只能点赞一次，再次调用则取消点赞（toggle）。
6. **评论**：支持匿名评论（user_id 为 null），支持嵌套回复（parent_id）。
7. **权限控制**：
   - 普通用户只能操作自己的资源。
   - admin 角色可以管理所有资源、审核评论。
8. **删除分类**：该分类下的文章 category_id 置为 null，不级联删除。
9. **删除标签**：同时删除 article_tags 关联记录。
10. **头像上传**：限制文件类型（jpg/png/gif），大小不超过 2MB，存储到 `uploads/avatars/`。
11. **封面图上传**：限制文件类型（jpg/png/webp），大小不超过 5MB，存储到 `uploads/covers/`。
12. **后台任务**：文章发布后，异步通知所有订阅者（模拟发送邮件）。
13. **统一错误响应格式**：
    ```json
    {
      "code": 400,
      "message": "错误描述",
      "detail": null
    }
    ```
14. **浏览记录**：`view_records` 表记录每次浏览行为。登录用户以 `user_id` 标识，匿名用户以 `ip_address` 标识。`view_count` 作为缓存值快速读取，趋势统计和去重数据从 `view_records` 聚合。删除文章时级联删除对应的浏览记录。

---

## 七、项目结构

```
blogbox/
├── alembic/                  # 数据库迁移
├── alembic.ini
├── app/
│   ├── __init__.py
│   ├── main.py               # FastAPI 应用入口、lifespan、中间件
│   ├── config.py             # 配置管理（pydantic-settings）
│   ├── database.py           # 数据库引擎和会话
│   ├── dependencies.py       # 公共依赖（get_db, get_current_user, pagination）
│   ├── models/               # SQLAlchemy 模型
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── article.py
│   │   ├── category.py
│   │   ├── tag.py
│   │   ├── comment.py
│   │   ├── subscription.py
│   │   └── view_record.py
│   ├── schemas/              # Pydantic 请求/响应模型
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── article.py
│   │   ├── category.py
│   │   ├── tag.py
│   │   ├── comment.py
│   │   ├── subscription.py
│   │   └── common.py        # 统一响应、分页等通用模型
│   ├── routers/              # 路由模块
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── article.py
│   │   ├── comment.py
│   │   ├── category.py
│   │   ├── tag.py
│   │   ├── subscription.py
│   │   └── ws.py            # WebSocket 路由
│   ├── services/             # 业务逻辑层
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── article.py
│   │   ├── comment.py
│   │   ├── category.py
│   │   └── tag.py
│   ├── tasks/                # 后台任务
│   │   └── notify.py        # 文章发布通知
│   ├── middleware/            # 自定义中间件
│   │   └── logging.py       # 请求日志 + 响应时间
│   └── utils/                # 工具函数
│       ├── security.py       # JWT 生成/校验、密码哈希
│       └── upload.py         # 文件上传处理
├── uploads/
│   ├── avatars/              # 头像存储
│   └── covers/               # 封面图存储
├── tests/                    # 测试目录
│   ├── test_user.py
│   ├── test_article.py
│   └── ...
├── requirements.txt
└── .env
```

---

## 八、开发顺序规划（分 9 个阶段）

### 阶段 1：项目初始化（1-2 天）
- [ ] 创建项目目录结构
- [ ] 配置 `.env` 和 `config.py`（pydantic-settings）
- [ ] 初始化数据库引擎和会话（`database.py`）
- [ ] 初始化 Alembic
- [ ] 创建 `main.py` 基础 FastAPI 应用
- [ ] 配置 CORS 中间件
- [ ] 编写 `requirements.txt`

### 阶段 2：用户模块（2-3 天）
- [ ] 创建 User 模型
- [ ] 编写 User 的 Pydantic schemas
- [ ] 实现密码哈希工具（bcrypt）
- [ ] 实现 JWT 工具（生成/校验 token）
- [ ] 实现注册接口
- [ ] 实现登录接口（OAuth2 Password）
- [ ] 实现 Token 刷新接口
- [ ] 实现获取/更新当前用户信息接口
- [ ] 编写 `get_current_user` 依赖
- [ ] 编写 `get_db` 依赖（yield）
- [ ] 运行 Alembic 迁移
- [ ] 使用 Swagger UI 测试

### 阶段 3：分类 & 标签模块（1-2 天）
- [ ] 创建 Category、Tag 模型
- [ ] 编写对应的 schemas
- [ ] 实现分类 CRUD 接口
- [ ] 实现标签 CRUD 接口
- [ ] 实现 admin 权限校验依赖
- [ ] 测试接口

### 阶段 4：文章模块 - 基础 CRUD（2-3 天）
- [ ] 创建 Article 模型（含与 Category、Tag 的关系）
- [ ] 创建 article_tags 关联表
- [ ] 编写 Article 的 schemas（请求/响应分离）
- [ ] 实现创建文章接口
- [ ] 实现文章详情接口（增加浏览数）
- [ ] 实现更新/删除文章接口
- [ ] 实现发布文章接口（draft → published）
- [ ] 权限校验：仅作者可编辑/删除

### 阶段 5：文章模块 - 高级功能（2-3 天）
- [ ] 实现文章列表接口
- [ ] 实现分页功能（自定义 Pagination 依赖）
- [ ] 实现排序功能（sort_by、order）
- [ ] 实现分类/标签筛选
- [ ] 实现关键词搜索（模糊匹配 title、content、summary）
- [ ] 实现点赞/取消点赞（toggle）
- [ ] 实现文章标签管理（添加/移除）
- [ ] 创建 ViewRecord 模型
- [ ] 文章详情接口写入浏览记录（user_id / ip_address）
- [ ] 实现文章浏览量统计接口（overview / ranking / trend）

### 阶段 6：评论模块（2 天）
- [ ] 创建 Comment 模型（支持嵌套回复）
- [ ] 编写 Comment 的 schemas
- [ ] 实现发表评论接口（支持匿名和回复）
- [ ] 实现评论列表接口（分页）
- [ ] 实现编辑/删除评论接口
- [ ] 实现评论审核接口

### 阶段 7：后台任务 + WebSocket（2 天）
- [ ] 创建 Subscription 模型
- [ ] 实现订阅/取消订阅接口
- [ ] 实现后台任务：文章发布后通知订阅者
- [ ] 实现 WebSocket 连接管理
- [ ] 实现新评论实时推送
- [ ] 实现文章发布实时推送

### 阶段 8：文件上传 + 中间件（1-2 天）
- [ ] 实现头像上传接口
- [ ] 实现文章封面图上传
- [ ] 文件类型和大小校验
- [ ] 编写请求日志中间件（记录请求方法、路径、耗时）
- [ ] 实现全局异常处理器（统一错误响应格式）
- [ ] 实现响应时间统计中间件

### 阶段 9：测试与优化（2-3 天）
- [ ] 编写用户模块单元测试
- [ ] 编写文章模块单元测试
- [ ] 编写评论模块单元测试
- [ ] 使用 pytest + httpx 进行异步测试
- [ ] 性能优化：添加数据库索引
- [ ] 代码重构和文档完善

---

## 九、统一规范

### 9.1 统一响应格式
```json
{
  "code": 200,
  "message": "success",
  "data": { ... }
}
```

### 9.2 分页响应格式
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "items": [...],
    "total": 100,
    "page": 1,
    "size": 20
  }
}
```

### 9.3 错误响应格式
```json
{
  "code": 400,
  "message": "错误描述",
  "detail": null
}
```

---

## 十、学习建议

1. **每个阶段完成后都要测试**：使用 Swagger UI（`/docs`）或 ReDoc（`/redoc`）手动测试接口。
2. **先写模型，再写 schema，最后写路由**：保持清晰的开发顺序。
3. **善用依赖注入**：将通用逻辑（如认证、分页、数据库会话）封装为依赖。
4. **分层架构**：Router → Service → Model，保持职责清晰。
5. **逐步添加测试**：每完成一个模块就编写对应的测试用例。
6. **使用 Git 管理版本**：每个阶段完成后提交一次代码。

---

## 十一、进阶挑战（可选）

完成基础功能后，可以尝试以下进阶功能：

- [ ] 实现文章草稿自动保存（定时任务）
- [ ] 实现阅读量统计图表接口（按日/周/月）
- [ ] 实现 Markdown 渲染接口
- [ ] 实现 RSS 订阅源接口
- [ ] 实现文章导出为 PDF
- [ ] 添加 Redis 缓存热门文章
- [ ] 实现限流（Rate Limiting）中间件
- [ ] 添加操作审计日志
- [ ] 实现 Swagger 文档自定义分组和描述
