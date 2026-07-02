<script setup>
import { onMounted, reactive } from 'vue'
import { platformDashboard } from '../../api/platform'

const data = reactive({
  total_merchants: 0,
  active_merchants: 0,
  pending_merchants: 0,
  disabled_merchants: 0,
})

onMounted(async () => {
  try {
    const res = await platformDashboard()
    Object.assign(data, res)
  } catch (e) {
    console.error('加载平台仪表盘失败', e)
  }
})
</script>

<template>
  <div>
    <div class="v-intro">
      <div>
        <h1>平台运营总览</h1>
        <p>多商户平台数据概览，实时掌握各商户入驻与运营状态。</p>
      </div>
    </div>

    <div class="grid-4">
      <div class="kpi" style="--ac: var(--brand)">
        <div class="kpi-top"><span class="kpi-label">商户总数</span></div>
        <div class="kpi-val tnum">{{ data.total_merchants }}<small> 家</small></div>
      </div>
      <div class="kpi" style="--ac: var(--ok)">
        <div class="kpi-top"><span class="kpi-label">已开通</span><span class="tag ok">运营中</span></div>
        <div class="kpi-val tnum">{{ data.active_merchants }}<small> 家</small></div>
      </div>
      <div class="kpi" style="--ac: var(--warn)">
        <div class="kpi-top"><span class="kpi-label">待审核</span><span class="tag warn" v-if="data.pending_merchants > 0">需处理</span></div>
        <div class="kpi-val tnum">{{ data.pending_merchants }}<small> 家</small></div>
      </div>
      <div class="kpi" style="--ac: var(--ink-3)">
        <div class="kpi-top"><span class="kpi-label">已停用</span></div>
        <div class="kpi-val tnum">{{ data.disabled_merchants }}<small> 家</small></div>
      </div>
    </div>

    <div class="sec-label"><h2>快捷操作</h2><div class="ln"></div></div>
    <div style="display: flex; gap: 10px">
      <router-link to="/platform/merchants" class="btn primary">管理商户</router-link>
    </div>
  </div>
</template>
