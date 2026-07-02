<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '../store/user'

const router = useRouter()
const userStore = useUserStore()
const loading = ref(false)
const errorMsg = ref('')
const form = reactive({ account: '', password: '' })

async function handleLogin() {
  if (!form.account || !form.password || loading.value) return
  loading.value = true
  errorMsg.value = ''
  try {
    await userStore.login(form.account, form.password)
    router.push('/dashboard')
  } catch (err) {
    errorMsg.value = err.response?.data?.message || '登录失败，请检查账号密码'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="login-page">
    <div class="login-card">
      <div class="logo" style="width: 44px; height: 44px; border-radius: 12px">
        <svg viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M4 3v7a3 3 0 0 0 6 0V3M7 3v18M17 3c-1.7 0-3 2-3 5s1.3 4 3 4v9" /></svg>
      </div>
      <h1>智餐 AI · 管理端</h1>
      <div class="sub">一体化运营管理平台</div>

      <div v-if="errorMsg" class="login-err">{{ errorMsg }}</div>

      <form @submit.prevent="handleLogin">
        <div class="field">
          <label>账号</label>
          <input v-model="form.account" type="text" placeholder="商家账号" autocomplete="username" />
        </div>
        <div class="field">
          <label>密码</label>
          <input v-model="form.password" type="password" placeholder="密码" autocomplete="current-password" />
        </div>
        <button type="submit" class="btn primary" :disabled="loading">{{ loading ? '登录中…' : '登录' }}</button>
      </form>
    </div>
  </div>
</template>
