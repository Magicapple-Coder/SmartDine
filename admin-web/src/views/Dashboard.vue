<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { listOrders } from '../api/order'
import { listIngredients } from '../api/inventory'
import { countPendingTickets, getAgentStatus, listAgentLogs } from '../api/agent'
import { formatMoney } from '../utils'
import { useAppStore } from '../store/app'
import LoadingBlock from '../components/LoadingBlock.vue'

const router = useRouter()
const appStore = useAppStore()
const pageLoading = ref(true)

const todayOrderCount = ref(0)
const todayRevenue = ref(0)
const yesterdayRevenue = ref(0)
const pendingCookCount = ref(0)
const lowStock = ref([])
const weekBars = ref([])
const agentStatus = ref(null)
const agentLogs = ref([])
const pendingTicketCount = ref(0)
const autoSolveRate = ref(76)

const todayLabel = computed(() =>
  new Date().toLocaleDateString('zh-CN', { year: 'numeric', month: 'long', day: 'numeric', weekday: 'long' }),
)

const revenueTrend = computed(() => {
  if (!yesterdayRevenue.value) return { pct: 0, up: true }
  const pct = Math.round(((todayRevenue.value - yesterdayRevenue.value) / yesterdayRevenue.value) * 100)
  return { pct: Math.abs(pct), up: pct >= 0 }
})

const orderTrend = computed(() => {
  // Simplified: compare with average of past 6 days
  const pastDays = weekBars.value.slice(0, 6)
  if (!pastDays.length) return { pct: 0, up: true }
  const avg = pastDays.reduce((s, b) => s + b.orders, 0) / pastDays.length
  if (avg === 0) return { pct: 0, up: true }
  const pct = Math.round(((todayOrderCount.value - avg) / avg) * 100)
  return { pct: Math.abs(pct), up: pct >= 0 }
})

const avgOrderValue = computed(() => {
  if (!todayOrderCount.value) return 0
  return Math.round(todayRevenue.value / todayOrderCount.value)
})

function isSameDay(a, b) {
  return a.toDateString() === b.toDateString()
}

async function loadData() {
  pageLoading.value = true
  try {
    const [orders, lowStockList, status, logs, ticketCounts] = await Promise.all([
      listOrders(),
      listIngredients(true),
      getAgentStatus(),
      listAgentLogs(),
      countPendingTickets(),
    ])
    agentStatus.value = status
    agentLogs.value = logs
    pendingTicketCount.value = ticketCounts.pending
    if (ticketCounts.total > 0) {
      autoSolveRate.value = Math.round((ticketCounts.auto / ticketCounts.total) * 100)
    }

    const now = new Date()
    const yesterday = new Date(now)
    yesterday.setDate(yesterday.getDate() - 1)

    const todays = orders.filter((o) => isSameDay(new Date(o.created_at), now))
    const yesterdays = orders.filter((o) => isSameDay(new Date(o.created_at), yesterday))

    todayOrderCount.value = todays.length
    todayRevenue.value = todays.reduce((sum, o) => sum + Number(o.amount || 0), 0)
    yesterdayRevenue.value = yesterdays.reduce((sum, o) => sum + Number(o.amount || 0), 0)
    pendingCookCount.value = orders.filter((o) => o.cook_status === 0).length
    lowStock.value = lowStockList

    // 7-day chart data
    const days = [...Array(7)].map((_, i) => {
      const d = new Date(now)
      d.setDate(d.getDate() - (6 - i))
      return d
    })
    weekBars.value = days.map((d) => {
      const dayOrders = orders.filter((o) => isSameDay(new Date(o.created_at), d))
      const amount = dayOrders.reduce((sum, o) => sum + Number(o.amount || 0), 0)
      const dayNames = ['周日', '周一', '周二', '周三', '周四', '周五', '周六']
      return { label: dayNames[d.getDay()], amount, orders: dayOrders.length }
    })
  } finally {
    pageLoading.value = false
  }
}

const maxBar = computed(() => Math.max(1, ...weekBars.value.map((b) => b.amount)))

const quickActions = [
  { label: '新增菜品', sub: '录入菜单信息', path: '/dishes', tint: 'var(--brand-soft)', color: 'var(--brand-d)', icon: 'M12 5v14M5 12h14' },
  { label: '录入库存', sub: '食材入库登记', path: '/inventory', tint: 'var(--t-stock)', color: '#8A5A0C', icon: 'M21 8 12 3 3 8v8l9 5 9-5zM3 8l9 5 9-5' },
  { label: '创建活动', sub: '优惠券与套餐', path: '/marketing', tint: 'var(--t-order)', color: '#534AB7', icon: 'M3 9v6l9 4V5z' },
  { label: '查看订单', sub: '实时订单流水', path: '/orders', tint: 'var(--t-svc)', color: '#0F6E56', icon: 'M5 6h14l-1 15H6zM9 11h6' },
]

onMounted(loadData)
</script>

<template>
  <div>
    <div class="v-intro">
      <div>
        <div class="eyebrow">{{ todayLabel }}</div>
        <h1>早上好，{{ appStore.storeName }}</h1>
        <p>门店运行平稳，四个智能体在线协同。下方为今日经营概览。</p>
      </div>
      <div class="chips">
        <div class="chip"><span class="k">营业状态</span><span class="v" style="color: var(--ok)">营业中</span></div>
        <div class="chip"><span class="k">在线智能体</span><span class="v tnum">4<small>/ 4</small></span></div>
      </div>
    </div>

    <LoadingBlock v-if="pageLoading" />
    <div v-else class="grid-4">
      <div class="kpi" style="--ac: var(--brand)">
        <div class="kpi-top">
          <span class="kpi-label">今日营收</span>
          <span v-if="revenueTrend.pct > 0" class="trend" :class="revenueTrend.up ? 'up' : 'down'">{{ revenueTrend.up ? '↑' : '↓' }} {{ revenueTrend.pct }}%</span>
        </div>
        <div class="kpi-val tnum">{{ formatMoney(todayRevenue) }}</div>
        <div class="kpi-sub">较昨日 <b>{{ revenueTrend.up ? '+' : '-' }}{{ formatMoney(Math.abs(todayRevenue - yesterdayRevenue)) }}</b></div>
      </div>
      <div class="kpi" style="--ac: var(--c-order)">
        <div class="kpi-top">
          <span class="kpi-label">今日订单</span>
          <span v-if="orderTrend.pct > 0" class="trend" :class="orderTrend.up ? 'up' : 'down'">{{ orderTrend.up ? '↑' : '↓' }} {{ orderTrend.pct }}%</span>
        </div>
        <div class="kpi-val tnum">{{ todayOrderCount }}</div>
        <div class="kpi-sub">客单价 <b>¥{{ avgOrderValue }}</b></div>
      </div>
      <div class="kpi" style="--ac: var(--c-stock)">
        <div class="kpi-top"><span class="kpi-label">库存预警</span><span class="tag bad" v-if="lowStock.length">需处理</span></div>
        <div class="kpi-val tnum">{{ lowStock.length }}<small> 项</small></div>
        <div class="kpi-sub">已生成 <b>采购建议</b></div>
      </div>
      <div class="kpi" style="--ac: var(--c-svc)">
        <div class="kpi-top"><span class="kpi-label">待处理工单</span><span class="tag warn" v-if="pendingTicketCount > 0">待人工</span></div>
        <div class="kpi-val tnum">{{ pendingTicketCount }}<small> 单</small></div>
        <div class="kpi-sub">自动解决率 <b>{{ autoSolveRate }}%</b></div>
      </div>
    </div>

    <div class="sec-label"><h2>常用操作</h2><div class="ln"></div></div>
    <div class="qa-grid">
      <button v-for="qa in quickActions" :key="qa.label" class="qa" @click="router.push(qa.path)">
        <span class="qi" :style="{ background: qa.tint, color: qa.color }">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round"><path :d="qa.icon" /></svg>
        </span>
        <span class="qt"><b>{{ qa.label }}</b><span>{{ qa.sub }}</span></span>
      </button>
    </div>

    <!-- 智能体协同状态 -->
    <div v-if="!pageLoading && agentStatus" class="sec-label" style="margin-top: 24px">
      <h2>智能体协同状态</h2><div class="ln"></div><span class="hint">点击进入各自工作台</span>
    </div>
    <div v-if="!pageLoading && agentStatus" class="grid-4">
      <div class="agent-tile" style="--ac: var(--c-order); --tint: var(--t-order)" @click="router.push('/agents/order')">
        <div class="at-head"><span class="at-ico"><svg viewBox="0 0 24 24" fill="none" stroke-linecap="round" stroke-linejoin="round"><path d="M21 11.5a8.4 8.4 0 0 1-8.5 8.5 8.5 8.5 0 0 1-3.8-.9L3 21l1.9-5.7a8.5 8.5 0 1 1 16.1-3.8z" /></svg></span><span class="at-name">点餐推荐</span><span class="at-live"><span class="pulse"></span>运行中</span></div>
        <div class="at-act">结合实时库存推荐菜品，自动规避缺货项</div>
        <div class="at-foot"><span class="m">采纳 <b>{{ agentStatus.order.task_count }}</b></span><span class="at-go">进入 ›</span></div>
      </div>
      <div class="agent-tile" style="--ac: var(--c-stock); --tint: var(--t-stock)" @click="router.push('/agents/stock')">
        <div class="at-head"><span class="at-ico"><svg viewBox="0 0 24 24" fill="none" stroke-linecap="round" stroke-linejoin="round"><path d="M21 8 12 3 3 8v8l9 5 9-5z" /><path d="M3 8l9 5 9-5" /><path d="M12 13v8" /></svg></span><span class="at-name">库存预测</span><span class="at-live"><span class="pulse"></span>运行中</span></div>
        <div class="at-act">{{ lowStock.length }} 项食材低于安全库存，已生成采购单</div>
        <div class="at-foot"><span class="m">预警 <b>{{ agentStatus.stock.task_count }}</b></span><span class="at-go">进入 ›</span></div>
      </div>
      <div class="agent-tile" style="--ac: var(--c-svc); --tint: var(--t-svc)" @click="router.push('/agents/service')">
        <div class="at-head"><span class="at-ico"><svg viewBox="0 0 24 24" fill="none" stroke-linecap="round" stroke-linejoin="round"><path d="M4 13v-1a8 8 0 0 1 16 0v1" /><rect x="2.5" y="13" width="4.5" height="6" rx="1.5" /><rect x="17" y="13" width="4.5" height="6" rx="1.5" /></svg></span><span class="at-name">客服处理</span><span class="at-live"><span class="pulse"></span>运行中</span></div>
        <div class="at-act">自动应答 {{ pendingTicketCount > 0 ? agentStatus.service.task_count + pendingTicketCount : 87 }} 条，{{ pendingTicketCount }} 条待人工</div>
        <div class="at-foot"><span class="m">解决 <b>{{ autoSolveRate }}%</b></span><span class="at-go">进入 ›</span></div>
      </div>
      <div class="agent-tile" style="--ac: var(--c-ana); --tint: var(--t-ana)" @click="router.push('/agents/analytics')">
        <div class="at-head"><span class="at-ico"><svg viewBox="0 0 24 24" fill="none" stroke-linecap="round" stroke-linejoin="round"><path d="M3 21h18M6 21V9M11 21V4M16 21v-8" /></svg></span><span class="at-name">经营分析</span><span class="at-live"><span class="pulse"></span>运行中</span></div>
        <div class="at-act">已生成今日经营摘要与优化建议</div>
        <div class="at-foot"><span class="m">营收 <b>{{ formatMoney(todayRevenue) }}</b></span><span class="at-go">进入 ›</span></div>
      </div>
    </div>

    <!-- 营收趋势 + 智能体动态 -->
    <div v-if="!pageLoading" class="row-2" style="margin-top: 18px">
      <div class="card">
        <div class="card-h"><h3>近 7 日营收趋势</h3><span class="sub">元</span></div>
        <div class="card-b">
          <div class="vbars">
            <div v-for="b in weekBars" :key="b.label" class="vbar" :class="{ peak: b.label === '今日' || b.label === weekBars[weekBars.length - 1]?.label }">
              <span class="fill" :style="{ height: Math.max(6, (b.amount / maxBar) * 120) + 'px' }"></span>
              <span class="x">{{ b.label }}</span>
            </div>
          </div>
        </div>
      </div>
      <div v-if="agentLogs.length" class="card">
        <div class="card-h"><h3>智能体动态</h3><span class="sub">实时</span></div>
        <div class="card-b" style="padding-top: 6px; padding-bottom: 8px">
          <div class="feed">
            <div v-for="(log, i) in agentLogs" :key="i" class="fi">
              <span class="fdot" :style="`--cl: ${log.color}`"></span>
              <div class="ftx">
                <div class="a" :style="`color: ${log.color}`">{{ log.agent }}</div>
                <div class="b">{{ log.text }}</div>
              </div>
              <div class="ftime">{{ log.time }}</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
