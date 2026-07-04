<template>
  <div class="admin-tags">
    <el-card>
      <div class="header">
        <h2>标签管理</h2>
        <el-button type="primary" @click="handleAdd">新增标签</el-button>
      </div>

      <el-table :data="tags" stripe>
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="名称" />
        <el-table-column prop="created_at" label="创建时间">
          <template #default="{ row }">{{ formatDate(row.created_at) }}</template>
        </el-table-column>
        <el-table-column label="操作" width="200">
          <template #default="{ row }">
            <el-button size="small" @click="handleEdit(row)">编辑</el-button>
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
    </el-card>

    <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑标签' : '新增标签'" width="500px">
      <el-form :model="form" label-width="80px">
        <el-form-item label="名称">
          <el-input v-model="form.name" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSave" :loading="loading">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { tagApi } from '../../api/tag'
import type { Tag } from '../../types'

const tags = ref<Tag[]>([])
const dialogVisible = ref(false)
const isEdit = ref(false)
const editId = ref(0)
const loading = ref(false)
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)

const form = reactive({
  name: '',
})

onMounted(() => {
  fetchTags()
})

async function fetchTags() {
  try {
    const res = await tagApi.getList(currentPage.value, pageSize.value)
    const paginatedData = res.data.data
    tags.value = paginatedData.items
    total.value = paginatedData.total
  } catch {
    // error handled by interceptor
  }
}

function handlePageChange() {
  fetchTags()
}

function handleAdd() {
  isEdit.value = false
  form.name = ''
  dialogVisible.value = true
}

function handleEdit(row: Tag) {
  isEdit.value = true
  editId.value = row.id
  form.name = row.name
  dialogVisible.value = true
}

async function handleSave() {
  if (!form.name.trim()) {
    ElMessage.warning('请输入标签名称')
    return
  }

  loading.value = true
  try {
    if (isEdit.value) {
      await tagApi.update(editId.value, form)
      ElMessage.success('更新成功')
    } else {
      await tagApi.create(form)
      ElMessage.success('创建成功')
    }
    dialogVisible.value = false
    await fetchTags()
  } catch {
    // error handled by interceptor
  } finally {
    loading.value = false
  }
}

async function handleDelete(row: Tag) {
  await ElMessageBox.confirm(`确定删除标签 "${row.name}"？`, '提示', { type: 'warning' })
  try {
    await tagApi.delete(row.id)
    ElMessage.success('删除成功')
    if (tags.value.length === 1 && currentPage.value > 1) {
      currentPage.value--
    }
    await fetchTags()
  } catch {
    // error handled by interceptor
  }
}

function formatDate(dateStr: string) {
  return new Date(dateStr).toLocaleDateString('zh-CN')
}
</script>

<style scoped>
.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.pagination {
  margin-top: 20px;
  justify-content: flex-end;
}
</style>
