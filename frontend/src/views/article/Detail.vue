<template>
  <div class="article-detail" v-if="article">
    <el-card>
      <div class="article-header">
        <h1>{{ article.title }}</h1>
        <div class="article-meta">
          <span class="author">{{ article.author?.username }}</span>
          <span class="date">{{ formatDate(article.published_at || article.created_at) }}</span>
          <span class="views"><el-icon><View /></el-icon> {{ article.view_count }}</span>
          <span class="likes"><el-icon><Star /></el-icon> {{ article.like_count }}</span>
          <el-tag v-if="article.category" size="small">{{ article.category.name }}</el-tag>
          <el-tag v-for="tag in article.tags" :key="tag.id" size="small" type="info">{{ tag.name }}</el-tag>
        </div>
        <div class="article-actions" v-if="canEdit">
          <el-button type="primary" @click="$router.push(`/article/edit/${article.id}`)">编辑</el-button>
          <el-button type="success" v-if="article.status === 'draft'" @click="handlePublish">发布</el-button>
          <el-button type="danger" @click="handleDelete">删除</el-button>
        </div>
      </div>

      <el-image v-if="article.cover_image" :src="article.cover_image" class="cover-image" fit="cover" />

      <div class="article-body" v-html="renderMarkdown(article.content)"></div>

      <div class="article-footer">
        <el-button
          :type="liked ? 'primary' : 'default'"
          @click="handleLike"
          :disabled="!userStore.isLoggedIn"
        >
          <el-icon><Star /></el-icon>
          {{ liked ? '已点赞' : '点赞' }} ({{ article.like_count }})
        </el-button>
      </div>
    </el-card>

    <el-card class="comments-section">
      <h3>评论 ({{ comments.length }})</h3>

      <div class="comment-form" v-if="userStore.isLoggedIn">
        <el-input
          v-model="commentContent"
          type="textarea"
          :rows="3"
          placeholder="写下你的评论..."
        />
        <el-button type="primary" @click="handleComment" :loading="commentLoading" style="margin-top: 12px">
          发表评论
        </el-button>
      </div>
      <div v-else class="login-hint">
        <router-link to="/login">登录</router-link> 后发表评论
      </div>

      <div class="comment-list">
        <div v-for="comment in comments" :key="comment.id" class="comment-item">
          <div class="comment-header">
            <el-avatar :size="32">{{ comment.user?.username?.charAt(0)?.toUpperCase() }}</el-avatar>
            <div class="comment-info">
              <span class="comment-author">{{ comment.user?.username || '匿名用户' }}</span>
              <span class="comment-date">{{ formatDate(comment.created_at) }}</span>
            </div>
            <div class="comment-actions" v-if="isCommentOwner(comment) || canDeleteComment(comment) || canApproveComment()">
              <el-button size="small" text @click="startEdit(comment)" v-if="isCommentOwner(comment)">编辑</el-button>
              <el-button size="small" text @click="handleApprove(comment)" v-if="canApproveComment() && !comment.is_approved">审核</el-button>
              <el-button size="small" text type="danger" @click="handleDeleteComment(comment)" v-if="canDeleteComment(comment)">删除</el-button>
            </div>
          </div>
          <div class="comment-content" v-if="editingId !== comment.id">{{ comment.content }}</div>
          <div v-else class="comment-edit">
            <el-input v-model="editContent" type="textarea" :rows="3" />
            <div class="comment-edit-actions">
              <el-button size="small" @click="cancelEdit">取消</el-button>
              <el-button size="small" type="primary" @click="saveEdit(comment.id)" :loading="editLoading">保存</el-button>
            </div>
          </div>

          <div class="comment-replies" v-if="comment.replies && comment.replies.length > 0">
            <div v-for="reply in comment.replies" :key="reply.id" class="comment-item reply">
              <div class="comment-header">
                <el-avatar :size="28">{{ reply.user?.username?.charAt(0)?.toUpperCase() }}</el-avatar>
                <div class="comment-info">
                  <span class="comment-author">{{ reply.user?.username || '匿名用户' }}</span>
                  <span class="comment-date">{{ formatDate(reply.created_at) }}</span>
                </div>
                <div class="comment-actions" v-if="isCommentOwner(reply) || canDeleteComment(reply)">
                  <el-button size="small" text @click="startEdit(reply)" v-if="isCommentOwner(reply)">编辑</el-button>
                  <el-button size="small" text type="danger" @click="handleDeleteComment(reply)" v-if="canDeleteComment(reply)">删除</el-button>
                </div>
              </div>
              <div class="comment-content" v-if="editingId !== reply.id">{{ reply.content }}</div>
              <div v-else class="comment-edit">
                <el-input v-model="editContent" type="textarea" :rows="3" />
                <div class="comment-edit-actions">
                  <el-button size="small" @click="cancelEdit">取消</el-button>
                  <el-button size="small" type="primary" @click="saveEdit(reply.id)" :loading="editLoading">保存</el-button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <el-empty v-if="comments.length === 0" description="暂无评论" />
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { View, Star } from '@element-plus/icons-vue'
import { useUserStore } from '../../stores/user'
import { articleApi } from '../../api/article'
import { commentApi } from '../../api/comment'
import type { Article, Comment } from '../../types'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

const article = ref<Article | null>(null)
const comments = ref<Comment[]>([])
const commentContent = ref('')
const commentLoading = ref(false)
const liked = ref(false)
const editingId = ref<number | null>(null)
const editContent = ref('')
const editLoading = ref(false)

const articleId = computed(() => Number(route.params.id))

const canEdit = computed(() => {
  if (!userStore.isLoggedIn) return false
  if (userStore.isAdmin) return true
  return article.value?.author_id === userStore.user?.id
})

function isCommentOwner(comment: Comment) {
  return !!userStore.isLoggedIn && comment.user_id === userStore.user?.id
}

function canDeleteComment(comment: Comment) {
  if (!userStore.isLoggedIn) return false
  if (userStore.isAdmin) return true
  return comment.user_id === userStore.user?.id
}

function canApproveComment() {
  if (!userStore.isLoggedIn) return false
  if (userStore.isAdmin) return true
  return article.value?.author_id === userStore.user?.id
}

onMounted(async () => {
  await fetchArticle()
  await fetchComments()
})

async function fetchArticle() {
  try {
    const res = await articleApi.getById(articleId.value)
    article.value = res.data.data
  } catch {
    // error handled by interceptor
  }
}

async function fetchComments() {
  try {
    const res = await commentApi.getList(articleId.value, { page: 1, size: 100 })
    comments.value = res.data.data.items
  } catch {
    // error handled by interceptor
  }
}

async function handleComment() {
  if (!commentContent.value.trim()) {
    ElMessage.warning('请输入评论内容')
    return
  }
  commentLoading.value = true
  try {
    await commentApi.create(articleId.value, { content: commentContent.value })
    commentContent.value = ''
    await fetchComments()
    ElMessage.success('评论成功')
  } catch {
    // error handled by interceptor
  } finally {
    commentLoading.value = false
  }
}

async function handleDeleteComment(comment: Comment) {
  await ElMessageBox.confirm('确定删除此评论？', '提示', { type: 'warning' })
  try {
    await commentApi.delete(articleId.value, comment.id)
    await fetchComments()
    ElMessage.success('删除成功')
  } catch {
    // error handled by interceptor
  }
}

async function handleApprove(comment: Comment) {
  try {
    await commentApi.approve(articleId.value, comment.id)
    await fetchComments()
    ElMessage.success('审核通过')
  } catch {
    // error handled by interceptor
  }
}

function startEdit(comment: Comment) {
  editingId.value = comment.id
  editContent.value = comment.content
}

function cancelEdit() {
  editingId.value = null
  editContent.value = ''
}

async function saveEdit(commentId: number) {
  if (!editContent.value.trim()) {
    ElMessage.warning('评论内容不能为空')
    return
  }
  editLoading.value = true
  try {
    await commentApi.update(articleId.value, commentId, { content: editContent.value })
    editingId.value = null
    editContent.value = ''
    await fetchComments()
    ElMessage.success('修改成功')
  } catch {
    // error handled by interceptor
  } finally {
    editLoading.value = false
  }
}

async function handleLike() {
  try {
    const res = await articleApi.toggleLike(articleId.value)
    liked.value = res.data.data.liked
    if (article.value) {
      article.value.like_count += liked.value ? 1 : -1
    }
  } catch {
    // error handled by interceptor
  }
}

async function handlePublish() {
  await ElMessageBox.confirm('确定发布此文章？', '提示', { type: 'info' })
  try {
    await articleApi.publish(articleId.value)
    await fetchArticle()
    ElMessage.success('发布成功')
  } catch {
    // error handled by interceptor
  }
}

async function handleDelete() {
  await ElMessageBox.confirm('确定删除此文章？此操作不可恢复', '警告', { type: 'warning' })
  try {
    await articleApi.delete(articleId.value)
    ElMessage.success('删除成功')
    router.push('/')
  } catch {
    // error handled by interceptor
  }
}

function renderMarkdown(content: string) {
  return content.replace(/\n/g, '<br>')
}

function formatDate(dateStr: string) {
  return new Date(dateStr).toLocaleDateString('zh-CN')
}
</script>

<style scoped>
.article-detail {
  max-width: 900px;
  margin: 0 auto;
}

.article-header h1 {
  font-size: 28px;
  margin-bottom: 12px;
}

.article-meta {
  display: flex;
  align-items: center;
  gap: 12px;
  color: #999;
  font-size: 14px;
  margin-bottom: 16px;
}

.article-actions {
  margin-top: 16px;
}

.cover-image {
  width: 100%;
  max-height: 400px;
  border-radius: 8px;
  margin-bottom: 24px;
}

.article-body {
  line-height: 1.8;
  font-size: 16px;
  color: #333;
}

.article-footer {
  margin-top: 32px;
  padding-top: 24px;
  border-top: 1px solid #eee;
}

.comments-section {
  margin-top: 24px;
}

.comment-form {
  margin-bottom: 24px;
}

.login-hint {
  margin-bottom: 24px;
  color: #999;
}

.comment-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.comment-item {
  padding: 16px;
  background: #f9f9f9;
  border-radius: 8px;
}

.comment-item.reply {
  margin-left: 40px;
  background: #f0f0f0;
}

.comment-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 8px;
}

.comment-info {
  display: flex;
  flex-direction: column;
}

.comment-author {
  font-weight: 500;
  color: #333;
}

.comment-date {
  font-size: 12px;
  color: #999;
}

.comment-actions {
  margin-left: auto;
}

.comment-content {
  line-height: 1.6;
  color: #555;
}

.comment-edit {
  margin-top: 4px;
}

.comment-edit-actions {
  margin-top: 8px;
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}

.comment-replies {
  margin-top: 12px;
}
</style>
