<script setup>
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '../../store/user'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

function handleLogout() {
  userStore.logout()
  router.push('/platform/login')
}
</script>

<template>
  <div class="app">
    <aside class="rail">
      <div class="brand">
        <div class="logo">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M4 3v7a3 3 0 0 0 6 0V3M7 3v18M17 3c-1.7 0-3 2-3 5s1.3 4 3 4v9" /></svg>
        </div>
        <div class="brand-tx"><b>智餐 AI</b><span>平台管理中心</span></div>
      </div>
      <nav class="nav">
        <div class="nav-grp">平台管理</div>
        <router-link to="/platform/dashboard" class="nav-item" style="--ac: var(--brand)" :class="{ on: route.path === '/platform/dashboard' }">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="7" height="7" rx="1.5" /><rect x="14" y="3" width="7" height="7" rx="1.5" /><rect x="3" y="14" width="7" height="7" rx="1.5" /><rect x="14" y="14" width="7" height="7" rx="1.5" /></svg>
          <span class="lbl">运营总览</span>
        </router-link>
        <router-link to="/platform/merchants" class="nav-item" style="--ac: var(--brand)" :class="{ on: route.path === '/platform/merchants' }">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round"><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z" /><polyline points="9 22 9 12 15 12 15 22" /></svg>
          <span class="lbl">商户管理</span>
        </router-link>
        <router-link to="/platform/settings" class="nav-item" style="--ac: var(--brand)" :class="{ on: route.path === '/platform/settings' }">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="3" /><path d="M19 12a7 7 0 0 0-.1-1.4l2-1.5-2-3.4-2.3 1a7 7 0 0 0-2.4-1.4L13.8 2h-3.6l-.4 2.3A7 7 0 0 0 7.4 5.7l-2.3-1-2 3.4 2 1.5A7 7 0 0 0 5 12a7 7 0 0 0 .1 1.4l-2 1.5 2 3.4 2.3-1a7 7 0 0 0 2.4 1.4l.4 2.3h3.6l.4-2.3a7 7 0 0 0 2.4-1.4l2.3 1 2-3.4-2-1.5A7 7 0 0 0 19 12z" /></svg>
          <span class="lbl">平台设置</span>
        </router-link>
      </nav>
      <div class="rail-foot">
        <div class="who">
          <div class="ava">管</div>
          <div><b>平台管理员</b><span>SmartDine 智餐</span></div>
          <button class="logout-link" @click="handleLogout">退出</button>
        </div>
      </div>
    </aside>
    <div class="main">
      <header class="topbar">
        <div class="top-title"><b>{{ route.meta.title }}</b><span>{{ route.meta.sub }}</span></div>
      </header>
      <div class="content">
        <div class="view">
          <router-view />
        </div>
      </div>
    </div>
  </div>
</template>
