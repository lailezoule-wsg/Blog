<template>
  <div class="admin-categories">
    <el-card>
      <div class="header">
        <h2>分类管理</h2>
        <el-button type="primary" @click="handleAdd">新增分类</el-button>
      </div>

      <el-table :data="categories" stripe>
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="名称" />
        <el-table-column prop="description" label="描述" />
        <el-table-column prop="sort_order" label="排序" width="100" />
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

    <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑分类' : '新增分类'" width="500px">
      <el-form :model="form" label-width="80px">
        <el-form-item label="名称">
          <el-input v-model="form.name" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="form.description" type="textarea" :rows="3" />
        </el-form-item>
        <el-form-item label="排序">
          <el-input-number v-model="form.sort_order" :min="0" />
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
import { categoryApi } from '../../api/category'
import type { Category } from '../../types'

const categories = ref<Category[]>([])
const dialogVisible = ref(false)
const isEdit = ref(false)
const editId = ref(0)
const loading = ref(false)
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)

const form = reactive({
  name: '',
  description: '',
  sort_order: 0,
})

onMounted(() => {
  fetchCategories()
})

async function fetchCategories() {
  try {
    const res = await categoryApi.getList(currentPage.value, pageSize.value)
    const paginatedData = res.data.data
    categories.value = paginatedData.items
    total.value = paginatedData.total
  } catch {
    // error handled by interceptor
  }
}

function handlePageChange() {
  fetchCategories()
}

function handleAdd() {
  isEdit.value = false
  form.name = ''
  form.description = ''
  form.sort_order = 0
  dialogVisible.value = true
}

function handleEdit(row: Category) {
  isEdit.value = true
  editId.value = row.id
  form.name = row.name
  form.description = row.description || ''
  form.sort_order = row.sort_order
  dialogVisible.value = true
}

async function handleSave() {
  if (!form.name.trim()) {
    ElMessage.warning('请输入分类名称')
    return
  }

  loading.value = true
  try {
    if (isEdit.value) {
      await categoryApi.update(editId.value, form)
      ElMessage.success('更新成功')
    } else {
      await categoryApi.create(form)
      ElMessage.success('创建成功')
    }
    dialogVisible.value = false
    await fetchCategories()
  } catch {
    // error handled by interceptor
  } finally {
    loading.value = false
  }
}

async function handleDelete(row: Category) {
  await ElMessageBox.confirm(`确定删除分类 "${row.name}"？`, '提示', { type: 'warning' })
  try {
    await categoryApi.delete(row.id)
    ElMessage.success('删除成功')
    if (categories.value.length === 1 && currentPage.value > 1) {
      currentPage.value--
    }
    await fetchCategories()
  } catch {
    // error handled by interceptor
  }
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
