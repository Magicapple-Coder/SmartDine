<script setup>
import { onMounted, ref } from 'vue'
import { listMerchants, approveMerchant, rejectMerchant, disableMerchant, enableMerchant } from '../../api/platform'

const merchants = ref([])
const statusFilter = ref(null)

const statusMap = { 0: '待审核', 1: '已开通', 2: '已停用', 3: '已注销' }
function statusText(s) { return statusMap[s] || '未知' }
function statusClass(s) {
  return { 0: 'warn', 1: 'ok', 2: 'bad', 3: 'mut' }[s] || ''
}
function formatDate(d) {
  if (!d) return '-'
  return new Date(d).toLocaleDateString('zh-CN')
}

async function loadMerchants() {
  try {
    merchants.value = await listMerchants(statusFilter.value)
  } catch (e) {
    console.error('加载商户列表失败', e)
  }
}

async function approve(id) {
  await approveMerchant(id)
  loadMerchants()
}
async function rejectMerchantFn(id) {
  const reason = prompt('驳回理由（可选）：')
  await rejectMerchant(id, reason || '')
  loadMerchants()
}
async function disableMerchantFn(id) {
  if (confirm('确定停用该商户吗？')) {
    await disableMerchant(id)
    loadMerchants()
  }
}
async function enableMerchantFn(id) {
  await enableMerchant(id)
  loadMerchants()
}

onMounted(loadMerchants)
</script>

<template>
  <div>
    <div class="v-intro">
      <div>
        <h1>商户管理</h1>
        <p>管理平台全部入驻商户，支持审核、启用、停用等操作。</p>
      </div>
    </div>

    <div class="toolbar">
      <select v-model="statusFilter" @change="loadMerchants" style="padding: 8px 13px; border: 1px solid var(--line-2); border-radius: var(--r-s); font-size: 13px; font-family: inherit; color: var(--ink); background: var(--surface); outline: none;">
        <option :value="null">全部状态</option>
        <option :value="0">待审核</option>
        <option :value="1">已开通</option>
        <option :value="2">已停用</option>
        <option :value="3">已注销</option>
      </select>
    </div>

    <table class="dtable" v-if="merchants.length">
      <thead>
        <tr>
          <th>ID</th>
          <th>商户名称</th>
          <th>品类</th>
          <th>联系人</th>
          <th>联系电话</th>
          <th class="c">状态</th>
          <th>入驻时间</th>
          <th class="r">操作</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="m in merchants" :key="m.merchant_id">
          <td>#{{ m.merchant_id }}</td>
          <td><span class="cellnm">{{ m.name }}</span></td>
          <td>{{ m.category || '-' }}</td>
          <td>{{ m.contact_name || '-' }}</td>
          <td>{{ m.contact_phone || '-' }}</td>
          <td class="c"><span class="tag" :class="statusClass(m.status)">{{ statusText(m.status) }}</span></td>
          <td>{{ formatDate(m.created_at) }}</td>
          <td class="r">
            <div class="act-btns">
              <button v-if="m.status === 0" class="btn sm primary" @click="approve(m.merchant_id)">通过</button>
              <button v-if="m.status === 0" class="btn sm" style="color: var(--bad); border-color: var(--bad)" @click="rejectMerchantFn(m.merchant_id)">驳回</button>
              <button v-if="m.status === 1" class="btn sm" style="color: var(--warn); border-color: var(--warn)" @click="disableMerchantFn(m.merchant_id)">停用</button>
              <button v-if="m.status === 2" class="btn sm primary" @click="enableMerchantFn(m.merchant_id)">启用</button>
            </div>
          </td>
        </tr>
      </tbody>
    </table>
    <div v-else class="empty-hint">暂无商户数据</div>
  </div>
</template>
