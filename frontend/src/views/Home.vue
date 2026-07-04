<template>
  <div class="home-page">
    <div class="search-bar">
      <el-input
        v-model="searchQuery"
        placeholder="搜索文章..."
        prefix-icon="Search"
        size="large"
        clearable
        @keyup.enter="handleSearch"
        @clear="handleSearch"
      />
    </div>

    <div class="article-list">
      <el-card v-for="article in articles" :key="article.id" class="article-card" @click="goToArticle(article.id)">
        <div class="article-content">
          <div class="article-info">
            <h3 class="article-title">{{ article.title }}</h3>
            <p class="article-summary">{{ article.summary || '暂无摘要' }}</p>
            <div class="article-meta">
              <span class="author">{{ article.author?.username }}</span>
              <span class="date">{{ formatDate(article.created_at) }}</span>
              <span class="views"><el-icon><View /></el-icon> {{ article.view_count }}</span>
              <span class="likes"><el-icon><Star /></el-icon> {{ article.like_count }}</span>
              <el-tag v-if="article.category" size="small">{{ article.category.name }}</el-tag>
              <el-tag v-for="tag in article.tags" :key="tag.id" size="small" type="info">{{ tag.name }}</el-tag>
            </div>
          </div>
          <el-image
            v-if="article.cover_image"
            :src="`${API_BASE}${article.cover_image}`"
            class="article-cover"
            fit="cover"
          />
        </div>
      </el-card>
    </div>

    <div class="pagination" v-if="total > pageSize">
      <el-pagination
        v-model:current-page="currentPage"
        :page-size="pageSize"
        :total="total"
        layout="prev, pager, next"
        @current-change="fetchArticles"
      />
    </div>

    <el-empty v-if="!loading && articles.length === 0" description="暂无文章" />

    <div class="subscribe-section">
      <h3>订阅博客更新</h3>
      <p>输入邮箱，第一时间获取新文章通知</p>
      <div class="subscribe-form">
        <el-input
          v-model="subscribeEmail"
          placeholder="请输入邮箱地址"
          size="large"
          clearable
          style="width: 300px"
          @keyup.enter="handleSubscribe"
        />
        <el-button type="primary" size="large" :loading="subscribing" @click="handleSubscribe">
          订阅
        </el-button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { View, Star } from '@element-plus/icons-vue'
import { articleApi } from '../api/article'
import { API_BASE } from '../api'
import { subscriptionApi } from '../api/subscription'
import { ElMessage } from 'element-plus'
import type { ArticleListItem } from '../types'

const router = useRouter()
const articles = ref<ArticleListItem[]>([])
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(20)
const searchQuery = ref('')
const loading = ref(false)

onMounted(() => {
  fetchArticles()
})

async function fetchArticles() {
  loading.value = true
  try {
    const res = await articleApi.getList({
      page: currentPage.value,
      size: pageSize.value,
      q: searchQuery.value || undefined,
      status: 'published',
    })
    articles.value = res.data.data.items
    total.value = res.data.data.total
  } catch {
    // error handled by interceptor
  } finally {
    loading.value = false
  }
}

function handleSearch() {
  currentPage.value = 1
  fetchArticles()
}

function goToArticle(id: number) {
  router.push(`/article/${id}`)
}

function formatDate(dateStr: string) {
  return new Date(dateStr).toLocaleDateString('zh-CN')
}

const subscribeEmail = ref('')
const subscribing = ref(false)

async function handleSubscribe() {
  const email = subscribeEmail.value.trim()
  if (!email) {
    ElMessage.warning('请输入邮箱地址')
    return
  }
  const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/
  if (!emailRegex.test(email)) {
    ElMessage.warning('请输入有效的邮箱地址')
    return
  }
  subscribing.value = true
  try {
    await subscriptionApi.subscribe(email)
    ElMessage.success('订阅成功')
    subscribeEmail.value = ''
  } catch {
    // error handled by interceptor
  } finally {
    subscribing.value = false
  }
}
</script>

<style scoped>
.home-page {
  max-width: 900px;
  margin: 0 auto;
}

.search-bar {
  margin-bottom: 24px;
}

.article-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.article-card {
  cursor: pointer;
  transition: box-shadow 0.3s;
}

.article-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.12);
}

.article-content {
  display: flex;
  gap: 20px;
}

.article-info {
  flex: 1;
}

.article-title {
  margin: 0 0 8px 0;
  font-size: 20px;
  color: #333;
}

.article-summary {
  margin: 0 0 12px 0;
  color: #666;
  font-size: 14px;
  line-height: 1.6;
}

.article-meta {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 13px;
  color: #999;
}

.article-meta .el-icon {
  margin-right: 2px;
}

.article-cover {
  width: 160px;
  height: 100px;
  border-radius: 8px;
  flex-shrink: 0;
}

.pagination {
  margin-top: 24px;
  display: flex;
  justify-content: center;
}

.subscribe-section {
  margin-top: 48px;
  padding: 32px;
  background: #f8f9fa;
  border-radius: 8px;
  text-align: center;
}

.subscribe-section h3 {
  margin: 0 0 8px 0;
  font-size: 20px;
  color: #333;
}

.subscribe-section p {
  margin: 0 0 20px 0;
  color: #666;
  font-size: 14px;
}

.subscribe-form {
  display: flex;
  justify-content: center;
  gap: 12px;
}
</style>
