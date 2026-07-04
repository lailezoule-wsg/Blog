<template>
  <div class="article-edit">
    <el-card>
      <h2>{{ isEdit ? '编辑文章' : '写文章' }}</h2>
      <el-form :model="form" label-width="100px">
        <el-form-item label="标题">
          <el-input v-model="form.title" placeholder="请输入文章标题" />
        </el-form-item>
        <el-form-item label="摘要">
          <el-input v-model="form.summary" type="textarea" :rows="2" placeholder="请输入文章摘要（可选）" />
        </el-form-item>
        <el-form-item label="分类">
          <el-select v-model="form.category_id" placeholder="选择分类" clearable>
            <el-option v-for="cat in categories" :key="cat.id" :label="cat.name" :value="cat.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="标签">
          <el-select v-model="form.tag_ids" multiple placeholder="选择标签">
            <el-option v-for="tag in tags" :key="tag.id" :label="tag.name" :value="tag.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="封面图">
          <el-upload
            :show-file-list="false"
            :before-upload="beforeCoverUpload"
            :http-request="handleCoverUpload"
            accept="image/jpeg,image/png,image/webp"
          >
            <el-image v-if="form.cover_image" :src="form.cover_image" style="width: 200px; height: 120px" fit="cover" />
            <el-button v-else type="primary">上传封面图</el-button>
          </el-upload>
        </el-form-item>
        <el-form-item label="内容">
          <el-input
            v-model="form.content"
            type="textarea"
            :rows="20"
            placeholder="请输入文章内容（支持 Markdown）"
          />
        </el-form-item>
        <el-form-item label="私密">
          <el-switch v-model="form.is_private" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSave" :loading="loading">保存草稿</el-button>
          <el-button type="success" @click="handleSaveAndPublish" :loading="loading">保存并发布</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { articleApi } from '../../api/article'
import { categoryApi } from '../../api/category'
import { tagApi } from '../../api/tag'
import type { Category, Tag } from '../../types'
import type { UploadRequestOptions } from 'element-plus'
import api from '../../api'

const route = useRoute()
const router = useRouter()

const isEdit = computed(() => !!route.params.id)
const articleId = computed(() => Number(route.params.id))

const categories = ref<Category[]>([])
const tags = ref<Tag[]>([])
const loading = ref(false)

const form = reactive({
  title: '',
  content: '',
  summary: '',
  category_id: undefined as number | undefined,
  tag_ids: [] as number[],
  cover_image: '',
  is_private: false,
})

onMounted(async () => {
  await Promise.all([fetchCategories(), fetchTags()])
  if (isEdit.value) {
    await fetchArticle()
  }
})

async function fetchCategories() {
  try {
    const res = await categoryApi.getList()
    categories.value = res.data.data.items
  } catch {
    // error handled by interceptor
  }
}

async function fetchTags() {
  try {
    const res = await tagApi.getList()
    tags.value = res.data.data.items
  } catch {
    // error handled by interceptor
  }
}

async function fetchArticle() {
  try {
    const res = await articleApi.getById(articleId.value)
    const article = res.data.data
    form.title = article.title
    form.content = article.content
    form.summary = article.summary || ''
    form.category_id = article.category_id
    form.tag_ids = article.tags.map((t) => t.id)
    form.cover_image = article.cover_image || ''
    form.is_private = article.is_private
  } catch {
    // error handled by interceptor
  }
}

function beforeCoverUpload(file: File) {
  const isImage = ['image/jpeg', 'image/png', 'image/webp'].includes(file.type)
  const isLt5M = file.size / 1024 / 1024 < 5

  if (!isImage) {
    ElMessage.error('只能上传 JPG/PNG/WebP 格式的图片')
    return false
  }
  if (!isLt5M) {
    ElMessage.error('图片大小不能超过 5MB')
    return false
  }
  return true
}

async function handleCoverUpload(options: UploadRequestOptions) {
  try {
    const formData = new FormData()
    formData.append('file', options.file as File)
    const res = await api.post('/api/articles/cover', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    form.cover_image = res.data.data.cover_image
    ElMessage.success('封面图上传成功')
  } catch {
    // error handled by interceptor
  }
}

async function handleSave() {
  await saveArticle(false)
}

async function handleSaveAndPublish() {
  await saveArticle(true)
}

async function saveArticle(publish: boolean) {
  if (!form.title.trim()) {
    ElMessage.warning('请输入文章标题')
    return
  }
  if (!form.content.trim()) {
    ElMessage.warning('请输入文章内容')
    return
  }

  loading.value = true
  try {
    const data: Record<string, unknown> = {
      title: form.title,
      content: form.content,
      summary: form.summary || undefined,
      category_id: form.category_id,
      is_private: form.is_private,
      cover_image: form.cover_image || undefined,
      tag_ids: form.tag_ids.length > 0 ? form.tag_ids : undefined,
    }

    let savedArticleId: number
    if (isEdit.value) {
      const res = await articleApi.update(articleId.value, data)
      savedArticleId = res.data.data.id
    } else {
      const res = await articleApi.create(data)
      savedArticleId = res.data.data.id
    }

    if (publish) {
      await articleApi.publish(savedArticleId)
      ElMessage.success('发布成功')
    } else {
      ElMessage.success('保存成功')
    }

    router.push(`/article/${savedArticleId}`)
  } catch {
    // error handled by interceptor
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.article-edit {
  max-width: 900px;
  margin: 0 auto;
}
</style>
