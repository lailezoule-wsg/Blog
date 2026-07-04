<template>
  <div class="profile-page">
    <el-card>
      <h2>个人中心</h2>
      <el-form :model="form" label-width="100px">
        <el-form-item label="头像">
          <div class="avatar-section">
            <el-avatar :size="80" :src="userStore.avatarUrl">
              {{ userStore.user?.username?.charAt(0)?.toUpperCase() }}
            </el-avatar>
            <el-upload
              :show-file-list="false"
              :before-upload="beforeAvatarUpload"
              :http-request="handleAvatarUpload"
              accept="image/jpeg,image/png,image/gif"
            >
              <el-button size="small" type="primary">更换头像</el-button>
            </el-upload>
          </div>
        </el-form-item>
        <el-form-item label="用户名">
          <el-input v-model="form.username" disabled />
        </el-form-item>
        <el-form-item label="邮箱">
          <el-input v-model="form.email" />
        </el-form-item>
        <el-form-item label="个人简介">
          <el-input v-model="form.bio" type="textarea" :rows="4" />
        </el-form-item>
        <el-form-item label="修改密码">
          <el-input
            v-model="form.password"
            type="password"
            show-password
            placeholder="留空则不修改，不少于 8 位"
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleUpdate" :loading="loading">保存修改</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { useUserStore } from '../../stores/user'
import { userApi } from '../../api/user'
import type { UploadRequestOptions } from 'element-plus'

const userStore = useUserStore()
const loading = ref(false)

const form = reactive({
  username: '',
  email: '',
  bio: '',
  password: '',
})

onMounted(() => {
  if (userStore.user) {
    form.username = userStore.user.username
    form.email = userStore.user.email
    form.bio = userStore.user.bio || ''
  }
})

function beforeAvatarUpload(file: File) {
  const isImage = ['image/jpeg', 'image/png', 'image/gif'].includes(file.type)
  const isLt2M = file.size / 1024 / 1024 < 2

  if (!isImage) {
    ElMessage.error('只能上传 JPG/PNG/GIF 格式的图片')
    return false
  }
  if (!isLt2M) {
    ElMessage.error('图片大小不能超过 2MB')
    return false
  }
  return true
}

async function handleAvatarUpload(options: UploadRequestOptions) {
  try {
    const res = await userApi.uploadAvatar(options.file as File)
    const avatarUrl = res.data.data.avatar_url
    if (userStore.user) {
      userStore.user.avatar_url = avatarUrl
    }
    ElMessage.success('头像上传成功')
  } catch {
    // error handled by interceptor
  }
}

async function handleUpdate() {
  loading.value = true
  try {
    const payload: Record<string, string> = {
      username: form.username,
      email: form.email,
      bio: form.bio,
    }
    if (form.password) {
      payload.password = form.password
    }
    const res = await userApi.updateCurrentUser(payload)
    userStore.setUser(res.data.data)
    form.password = ''
    ElMessage.success('更新成功')
  } catch {
    // error handled by interceptor
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.profile-page {
  max-width: 600px;
  margin: 0 auto;
}

.avatar-section {
  display: flex;
  align-items: center;
  gap: 20px;
}
</style>
