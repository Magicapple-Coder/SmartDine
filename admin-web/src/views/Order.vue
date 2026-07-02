<script setup>
import { computed, onMounted, ref } from 'vue'
import { toast } from '../utils/toast'
import { deleteOrder, listOrders, updateOrderStatus } from '../api/order'
import { formatDateTime, formatMoney } from '../utils'
import { usePending } from '../utils/pending'
import LoadingBlock from '../components/LoadingBlock.vue'

const { isPending, run } = usePending()

const orders = ref([])
const activeFilter = ref('全部')
const keyword = ref('')
const pageLoading = ref(true)

const payStatusText = ['待付', '已付', '已退款']
const cookStatusText = ['待出餐', '出餐中', '已完成']
const payTagType = ['warn', 'ok', 'bad']

const filters = ['全部', '待付', '已付', '出餐中', '已完成']

const filtered = computed(() => {
  return orders.value.filter((o) => {
    if (keyword.value && !String(o.order_id).includes(keyword.value)) return false
    if (activeFilter.value === '全部') return true
    if (activeFilter.value === '待付') return o.pay_status === 0
    if (activeFilter.value === '已付') return o.pay_status === 1
    if (activeFilter.value === '出餐中') return o.cook_status === 1
    if (activeFilter.value === '已完成') return o.cook_status === 2
    return true
  })
})

const todayCount = computed(() => orders.value.length)
const todayRevenue = computed(() => orders.value.reduce((sum, o) => sum + Number(o.amount || 0), 0))

async function load() {
  pageLoading.value = true
  try {
    orders.value = await listOrders()
  } finally {
    pageLoading.value = false
  }
}

async function markPaid(order) {
  await run(`pay-${order.order_id}`, async () => {
    await updateOrderStatus(order.order_id, { pay_status: 1 })
    toast.success('已标记为已付')
    load()
  })
}

async function advanceCookStatus(order) {
  await run(`cook-${order.order_id}`, async () => {
    const next = Math.min(order.cook_status + 1, 2)
    await updateOrderStatus(order.order_id, { cook_status: next })
    toast.success('出餐状态已更新')
    load()
  })
}

async function removeOrder(order) {
  if (!confirm(`确定删除订单 #${order.order_id} 吗？该订单的明细与评价也将一并清除。`)) return
  await run(`delete-${order.order_id}`, async () => {
    await deleteOrder(order.order_id)
    toast.success('订单已删除')
    load()
  })
}

onMounted(load)
</script>

<template>
  <div>
    <div class="v-intro">
      <div>
        <h1>订单管理</h1>
        <p>查看堂食、外卖全部订单，跟踪每笔订单的支付与出餐状态。</p>
      </div>
      <div class="chips">
        <div class="chip"><span class="k">订单数</span><span class="v tnum">{{ todayCount }}</span></div>
        <div class="chip"><span class="k">营业额</span><span class="v tnum">{{ formatMoney(todayRevenue) }}</span></div>
      </div>
    </div>

    <div class="toolbar">
      <div class="seg">
        <button v-for="f in filters" :key="f" :class="{ on: activeFilter === f }" @click="activeFilter = f">{{ f }}</button>
      </div>
      <div class="tb-grow"></div>
      <div class="search-box">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-linecap="round"><circle cx="11" cy="11" r="7" /><path d="m21 21-4.3-4.3" /></svg>
        <input v-model="keyword" placeholder="搜索订单号" />
      </div>
    </div>

    <table class="dtable">
      <thead>
        <tr><th>订单号</th><th>桌台</th><th>菜品</th><th class="r">金额</th><th class="c">支付</th><th class="c">状态</th><th class="r">时间</th><th class="r">操作</th></tr>
      </thead>
      <tbody>
        <tr v-if="pageLoading"><td colspan="8"><LoadingBlock /></td></tr>
        <template v-else>
          <tr v-for="o in filtered" :key="o.order_id">
            <td class="cellnm tnum">#{{ o.order_id }}</td>
            <td>{{ o.table_id ? o.table_id + ' 号桌' : '外卖' }}</td>
            <td class="sub-c">共 {{ o.items.length }} 项</td>
            <td class="r tnum">{{ formatMoney(o.amount) }}</td>
            <td class="c"><span class="tag" :class="payTagType[o.pay_status]">{{ payStatusText[o.pay_status] }}</span></td>
            <td class="c">{{ cookStatusText[o.cook_status] }}</td>
            <td class="r sub-c tnum">{{ formatDateTime(o.created_at) }}</td>
            <td class="r">
              <div class="act-btns">
                <button class="btn sm" :disabled="o.pay_status === 1 || isPending(`pay-${o.order_id}`)" @click="markPaid(o)">
                  <span v-if="isPending(`pay-${o.order_id}`)" class="spin"></span>收款
                </button>
                <button class="btn sm" :disabled="o.cook_status === 2 || isPending(`cook-${o.order_id}`)" @click="advanceCookStatus(o)">
                  <span v-if="isPending(`cook-${o.order_id}`)" class="spin"></span>推进出餐
                </button>
                <button class="ibtn danger" :disabled="isPending(`delete-${o.order_id}`)" @click="removeOrder(o)">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M3 6h18M8 6V4h8v2M6 6l1 14h10l1-14" /></svg>
                </button>
              </div>
            </td>
          </tr>
        </template>
      </tbody>
    </table>
  </div>
</template>
