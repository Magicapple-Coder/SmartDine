import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '../store/user'

const routes = [
  // ========== 平台管理端路由（V2.0 新增） ==========
  {
    path: '/platform/login',
    name: 'platform-login',
    component: () => import('../views/platform/Login.vue'),
  },
  {
    path: '/platform',
    component: () => import('../views/platform/Layout.vue'),
    redirect: '/platform/dashboard',
    meta: { requiresPlatform: true },
    children: [
      {
        path: 'dashboard',
        name: 'platform-dashboard',
        component: () => import('../views/platform/Dashboard.vue'),
        meta: { title: '平台运营总览', sub: '多商户平台数据概览' },
      },
      {
        path: 'merchants',
        name: 'platform-merchants',
        component: () => import('../views/platform/Merchants.vue'),
        meta: { title: '商户管理', sub: '入驻审核·状态管理' },
      },
      {
        path: 'settings',
        name: 'platform-settings',
        component: () => import('../views/platform/Settings.vue'),
        meta: { title: '平台设置', sub: '管理员账号与平台参数' },
      },
    ],
  },

  // ========== 商户管理端路由（原 V1.0 路由，路径保持不变） ==========
  { path: '/login', name: 'login', component: () => import('../views/Login.vue') },
  {
    path: '/',
    component: () => import('../views/layout/Layout.vue'),
    redirect: '/dashboard',
    children: [
      { path: 'dashboard', name: 'dashboard', component: () => import('../views/Dashboard.vue'), meta: { title: '运营总览', sub: '实时掌握门店经营动态' } },
      { path: 'dishes', name: 'dishes', component: () => import('../views/Dish.vue'), meta: { title: '菜品管理', sub: '新增·编辑·上下架菜品' } },
      { path: 'orders', name: 'orders', component: () => import('../views/Order.vue'), meta: { title: '订单管理', sub: '堂食·外卖订单跟踪' } },
      { path: 'tables', name: 'tables', component: () => import('../views/Table.vue'), meta: { title: '桌台管理', sub: '座位状态与预订' } },
      { path: 'marketing', name: 'marketing', component: () => import('../views/Marketing.vue'), meta: { title: '营销活动', sub: '优惠券·套餐·促销' } },
      { path: 'inventory', name: 'inventory', component: () => import('../views/Inventory.vue'), meta: { title: '库存管理', sub: '食材·出入库·供应商' } },
      { path: 'members', name: 'members', component: () => import('../views/Member.vue'), meta: { title: '会员管理', sub: '档案·等级·积分' } },
      { path: 'staff', name: 'staff', component: () => import('../views/Staff.vue'), meta: { title: '员工管理', sub: '账号·角色·排班' } },
      { path: 'settings', name: 'settings', component: () => import('../views/Settings.vue'), meta: { title: '系统设置', sub: '门店信息管理' } },
      { path: 'agents/order', name: 'agent-order', component: () => import('../views/agents/OrderAgent.vue'), meta: { title: '点餐推荐智能体', sub: '智能搭配·库存感知' } },
      { path: 'agents/stock', name: 'agent-stock', component: () => import('../views/agents/StockAgent.vue'), meta: { title: '库存预测智能体', sub: '需求预测·采购建议' } },
      { path: 'agents/service', name: 'agent-service', component: () => import('../views/agents/ServiceAgent.vue'), meta: { title: '客服处理智能体', sub: '自动分类·智能回复' } },
      { path: 'agents/analytics', name: 'agent-analytics', component: () => import('../views/agents/AnalyticsAgent.vue'), meta: { title: '经营分析智能体', sub: '数据洞察·优化建议' } },
    ],
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

// V2.0 登录态权限守卫：区分平台端和商户端
router.beforeEach((to) => {
  const userStore = useUserStore()

  // 平台端守卫
  if (to.meta.requiresPlatform && !userStore.isPlatformAdmin) {
    return '/platform/login'
  }
  if (to.path === '/platform/login' && userStore.isPlatformAdmin) {
    return '/platform/dashboard'
  }

  // 商户端守卫
  if (to.path !== '/login' && !to.path.startsWith('/platform') && !userStore.isLoggedIn) {
    return '/login'
  }
  if (to.path === '/login' && userStore.isLoggedIn) {
    return '/dashboard'
  }

  return true
})

export default router
