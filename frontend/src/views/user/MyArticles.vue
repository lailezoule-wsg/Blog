<template>
  <div class="my-articles">
    <el-card>
      <div class="page-header">
        <h2>我的文章</h2>
        <el-button type="primary" @click="$router.push('/article/write')">写文章</el-button>
      </div>

      <div class="filter-bar">
        <el-radio-group v-model="statusFilter" @change="handleFilterChange">
          <el-radio-button value="">全部</el-radio-button>
          <el-radio-button value="draft">草稿</el-radio-button>
          <el-radio-button value="published">已发布</el-radio-button>
        </el-radio-group>
      </div>

      <el-table :data="articles" stripe>
        <el-table-column prop="title" label="标题" min-width="200">
          <template #default="{ row }">
            <span class="title-link" @click="goToArticle(row.id)">{{ row.title }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === 'published' ? 'success' : 'info'" size="small">
              {{ row.status === 'published' ? '已发布' : '草稿' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="view_count" label="浏览" width="80" />
        <el-table-column prop="like_count" label="点赞" width="80" />
        <el-table-column prop="created_at" label="创建时间" width="120">
          <template #default="{ row }">{{ formatDate(row.created_at) }}</template>
        </el-table-column>
        <el-table-column label="操作" width="240">
          <template #default="{ row }">
            <el-button size="small" @click="goToEdit(row.id)">编辑</el-button>
            <el-button
              v-if="row.status === 'draft'"
              size="small"
              type="success"
              @click="handlePublish(row)"
            >发布</el-button>
            <el-button size="small" type="danger" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :total="total"
        :page-sizes="[10, 20, 50]"
        layout="total, sizes, prev, pager, next, jumper"
        class="pagination"
        @size-change="handlePageChange"
        @current-change="handlePageChange"
      />

      <el-empty v-if="!loading && articles.length === 0" description="暂无文章" />
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { articleApi } from '../../api/article'
import { useUserStore } from '../../stores/user'
import type { ArticleListItem } from '../../types'

const router = useRouter()
const userStore = useUserStore()

const articles = ref<ArticleListItem[]>([])
const loading = ref(false)
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)
const statusFilter = ref('')

onMounted(() => {
  fetchArticles()
})

async function fetchArticles() {
  loading.value = true
  try {
    const res = await articleApi.getList({
      page: currentPage.value,
      size: pageSize.value,
      author_id: userStore.user?.id,
      status: statusFilter.value || undefined,
    })
    articles.value = res.data.data.items
    total.value = res.data.data.total
  } catch {
    // error handled by interceptor
  } finally {
    loading.value = false
  }
}

function handleFilterChange() {
  currentPage.value = 1
  fetchArticles()
}

function handlePageChange() {
  fetchArticles()
}

function goToArticle(id: number) {
  router.push(`/article/${id}`)
}

function goToEdit(id: number) {
  router.push(`/article/edit/${id}`)
}

async function handlePublish(row: ArticleListItem) {
  try {
    await articleApi.publish(row.id)
    ElMessage.success('发布成功')
    await fetchArticles()
  } catch {
    // error handled by interceptor
  }
}

async function handleDelete(row: ArticleListItem) {
  await ElMessageBox.confirm(`确定删除文章「${row.title}」？`, '提示', { type: 'warning' })
  try {
    await articleApi.delete(row.id)
    ElMessage.success('删除成功')
    if (articles.value.length === 1 && currentPage.value > 1) {
      currentPage.value--
    }
    await fetchArticles()
  } catch {
    // error handled by interceptor
  }
}

function formatDate(dateStr: string) {
  return new Date(dateStr).toLocaleDateString('zh-CN')
}
</script>

<style scoped>
.my-articles {
  max-width: 1000px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.page-header h2 {
  margin: 0;
}

.filter-bar {
  margin-bottom: 20px;
}

.title-link {
  cursor: pointer;
  color: #409eff;
}

.title-link:hover {
  text-decoration: underline;
}

.pagination {
  margin-top: 20px;
  justify-content: flex-end;
}
</style>
