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
          <div class="cover-section">
            <div v-if="coverPreview" class="cover-preview">
              <img :src="coverPreview" class="cover-img" />
              <el-button type="danger" size="small" circle @click="removeCover">
                <el-icon><Close /></el-icon>
              </el-button>
            </div>
            <el-upload
              :show-file-list="false"
              :auto-upload="false"
              :on-change="handleCoverChange"
              accept="image/jpeg,image/png,image/webp"
            >
              <el-button type="primary" size="small">{{ coverPreview ? '更换封面' : '选择封面图' }}</el-button>
            </el-upload>
          </div>
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
import { API_BASE } from '../../api'
import { categoryApi } from '../../api/category'
import { tagApi } from '../../api/tag'
import type { Category, Tag } from '../../types'
import type { UploadFile } from 'element-plus'
import { Close } from '@element-plus/icons-vue'

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
  is_private: false,
})

const coverFile = ref<File | null>(null)
const coverPreview = ref('')

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
    form.is_private = article.is_private
    if (article.cover_image) {
      coverPreview.value = `${API_BASE}${article.cover_image}`
    }
  } catch {
    // error handled by interceptor
  }
}

function handleCoverChange(uploadFile: UploadFile) {
  const file = uploadFile.raw
  if (!file) return

  const isImage = ['image/jpeg', 'image/png', 'image/webp'].includes(file.type)
  if (!isImage) {
    ElMessage.error('只能上传 JPG/PNG/WebP 格式的图片')
    return
  }
  if (file.size / 1024 / 1024 >= 5) {
    ElMessage.error('图片大小不能超过 5MB')
    return
  }

  coverFile.value = file
  coverPreview.value = URL.createObjectURL(file)
}

function removeCover() {
  coverFile.value = null
  coverPreview.value = ''
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
    const formData = new FormData()
    formData.append('title', form.title)
    formData.append('content', form.content)
    if (form.summary) formData.append('summary', form.summary)
    if (form.category_id) formData.append('category_id', String(form.category_id))
    formData.append('is_private', String(form.is_private))
    form.tag_ids.forEach(id => formData.append('tag_ids', String(id)))
    if (coverFile.value) {
      formData.append('file', coverFile.value)
    }

    let savedArticleId: number
    if (isEdit.value) {
      const res = await articleApi.update(articleId.value, formData)
      savedArticleId = res.data.data.id
    } else {
      const res = await articleApi.create(formData)
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

.cover-section {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.cover-preview {
  position: relative;
  display: inline-block;
  width: 200px;
  height: 120px;
}

.cover-img {
  width: 200px;
  height: 120px;
  object-fit: cover;
  border-radius: 4px;
  border: 1px solid #e4e7ed;
}

.cover-preview .el-button {
  position: absolute;
  top: -8px;
  right: -8px;
}
</style>
