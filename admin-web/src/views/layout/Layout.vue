<script setup>
import { onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '../../store/user'
import { useAppStore } from '../../store/app'
import { countPendingTickets } from '../../api/agent'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()
const appStore = useAppStore()

const searchKeyword = ref('')
const pendingTicketCount = ref(0)
const alertTicketCount = ref(0)

onMounted(async () => {
  try {
    const counts = await countPendingTickets()
    pendingTicketCount.value = counts.pending
    alertTicketCount.value = counts.total
  } catch {
    // 智能体接口暂不可用，忽略
  }
})

function handleSearch() {
  const kw = searchKeyword.value.trim()
  if (!kw) return
  // 根据关键词智能跳转
  if (kw.includes('订单') || kw.includes('order')) { router.push('/orders'); return }
  if (kw.includes('会员') || kw.includes('member')) { router.push('/members'); return }
  if (kw.includes('库存') || kw.includes('食材')) { router.push('/inventory'); return }
  if (kw.includes('菜') || kw.includes('dish')) { router.push('/dishes'); return }
  // 默认跳订单
  router.push('/orders')
}

function handleLogout() {
  userStore.logout()
  router.push('/login')
}

</script>

<template>
  <div class="app">
    <aside class="rail">
      <div class="brand">
        <div class="logo">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M4 3v7a3 3 0 0 0 6 0V3M7 3v18M17 3c-1.7 0-3 2-3 5s1.3 4 3 4v9" /></svg>
        </div>
        <div class="brand-tx"><b>智餐 AI</b><span>一体化运营管理平台</span></div>
      </div>
      <nav class="nav">
        <div class="nav-grp">概览</div>
        <router-link to="/dashboard" class="nav-item" style="--ac: var(--brand)" :class="{ on: route.path === '/dashboard' }">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="7" height="7" rx="1.5" /><rect x="14" y="3" width="7" height="7" rx="1.5" /><rect x="3" y="14" width="7" height="7" rx="1.5" /><rect x="14" y="14" width="7" height="7" rx="1.5" /></svg>
          <span class="lbl">运营总览</span>
        </router-link>

        <div class="nav-grp">经营管理</div>
        <router-link to="/dishes" class="nav-item" style="--ac: var(--brand)" :class="{ on: route.path === '/dishes' }">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round"><path d="M4 3h16v18l-4-2-4 2-4-2-4 2z" /><path d="M8 8h8M8 12h8" /></svg>
          <span class="lbl">菜品管理</span>
        </router-link>
        <router-link to="/orders" class="nav-item" style="--ac: var(--brand)" :class="{ on: route.path === '/orders' }">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round"><path d="M9 3h6l1 3H8z" /><path d="M5 6h14l-1 15H6z" /><path d="M9 11h6" /></svg>
          <span class="lbl">订单管理</span>
        </router-link>
        <router-link to="/tables" class="nav-item" style="--ac: var(--brand)" :class="{ on: route.path === '/tables' }">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="10" r="6" /><path d="M12 16v5M8 21h8" /></svg>
          <span class="lbl">桌台管理</span>
        </router-link>
        <router-link to="/marketing" class="nav-item" style="--ac: var(--brand)" :class="{ on: route.path === '/marketing' }">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round"><path d="M3 9v6l9 4V5z" /><path d="M16 9a3 3 0 0 1 0 6" /></svg>
          <span class="lbl">营销活动</span>
        </router-link>

        <div class="nav-grp">库存采购</div>
        <router-link to="/inventory" class="nav-item" style="--ac: var(--c-stock)" :class="{ on: route.path === '/inventory' }">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round"><path d="M21 8 12 3 3 8v8l9 5 9-5z" /><path d="M3 8l9 5 9-5" /><path d="M12 13v8" /></svg>
          <span class="lbl">库存管理</span>
        </router-link>

        <div class="nav-grp">AI 智能体</div>
        <router-link to="/agents/order" class="nav-item" style="--ac: var(--c-order)" :class="{ on: route.path.startsWith('/agents/order') }">
          <span class="ai-dot"></span><span class="lbl">点餐推荐</span>
        </router-link>
        <router-link to="/agents/stock" class="nav-item" style="--ac: var(--c-stock)" :class="{ on: route.path.startsWith('/agents/stock') }">
          <span class="ai-dot"></span><span class="lbl">库存预测</span>
          <span v-if="pendingTicketCount > 0" class="nav-badge">{{ pendingTicketCount }}</span>
        </router-link>
        <router-link to="/agents/service" class="nav-item" style="--ac: var(--c-svc)" :class="{ on: route.path.startsWith('/agents/service') }">
          <span class="ai-dot"></span><span class="lbl">客服处理</span>
          <span v-if="alertTicketCount > 0" class="nav-badge alert">{{ alertTicketCount }}</span>
        </router-link>
        <router-link to="/agents/analytics" class="nav-item" style="--ac: var(--c-ana)" :class="{ on: route.path.startsWith('/agents/analytics') }">
          <span class="ai-dot"></span><span class="lbl">经营分析</span>
        </router-link>

        <div class="nav-grp">顾客/团队</div>
        <router-link to="/members" class="nav-item" style="--ac: var(--brand)" :class="{ on: route.path === '/members' }">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round"><circle cx="9" cy="8" r="3.5" /><path d="M3 20a6 6 0 0 1 12 0" /><path d="M16 5.5a3 3 0 0 1 0 5M18 14a5 5 0 0 1 3 6" /></svg>
          <span class="lbl">会员管理</span>
        </router-link>
        <router-link to="/staff" class="nav-item" style="--ac: var(--brand)" :class="{ on: route.path === '/staff' }">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="7" r="4" /><path d="M5 21a7 7 0 0 1 14 0" /></svg>
          <span class="lbl">员工管理</span>
        </router-link>

        <div class="nav-grp">系统</div>
        <router-link to="/settings" class="nav-item" style="--ac: var(--brand)" :class="{ on: route.path === '/settings' }">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="3" /><path d="M19 12a7 7 0 0 0-.1-1.4l2-1.5-2-3.4-2.3 1a7 7 0 0 0-2.4-1.4L13.8 2h-3.6l-.4 2.3A7 7 0 0 0 7.4 5.7l-2.3-1-2 3.4 2 1.5A7 7 0 0 0 5 12a7 7 0 0 0 .1 1.4l-2 1.5 2 3.4 2.3-1a7 7 0 0 0 2.4 1.4l.4 2.3h3.6l.4-2.3a7 7 0 0 0 2.4-1.4l2.3 1 2-3.4-2-1.5A7 7 0 0 0 19 12z" /></svg>
          <span class="lbl">系统设置</span>
        </router-link>
      </nav>
      <div class="rail-foot">
        <div class="who">
          <div class="ava">{{ (appStore.storeName || '商')[0] }}</div>
          <div><b>{{ appStore.storeName }}</b><span>{{ userStore.role || '商家管理员' }}</span></div>
          <button class="logout-link" @click="handleLogout">退出</button>
        </div>
      </div>
    </aside>
    <div class="main">
      <header class="topbar">
        <div class="top-title"><b>{{ route.meta.title }}</b><span>{{ route.meta.sub }}</span></div>
        <div class="top-spacer"></div>
        <div class="top-search">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-linecap="round"><circle cx="11" cy="11" r="7" /><path d="m21 21-4.3-4.3" /></svg>
          <input v-model="searchKeyword" placeholder="搜索菜品、订单、会员…" @keyup.enter="handleSearch" />
        </div>
        <button class="icon-btn">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round"><path d="M18 8a6 6 0 0 0-12 0c0 7-3 9-3 9h18s-3-2-3-9" /><path d="M13.5 21a1.8 1.8 0 0 1-3 0" /></svg>
        </button>
      </header>
      <div class="content">
        <div class="view">
          <router-view />
        </div>
      </div>
    </div>
  </div>
</template>
