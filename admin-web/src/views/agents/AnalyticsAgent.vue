<script setup>
// 经营分析智能体 —— 纯前端演示页
// Dify 经营分析智能体（chatAnalytics / runAnalyticsSummary）尚未接入，当前展示静态样例数据
import { onMounted, ref } from 'vue'
import { getAnalyticsSummary } from '../../api/agent'
import LoadingBlock from '../../components/LoadingBlock.vue'

const loading = ref(true)
const data = ref(null)
const nlqInput = ref('')
const nlqAnswer = ref('')

const maxCause = ref(32)

function askNlq() {
  const q = nlqInput.value.trim()
  if (!q) return
  nlqAnswer.value = q
  nlqInput.value = ''
}

onMounted(async () => {
  try {
    data.value = await getAnalyticsSummary()
    maxCause.value = Math.max(...data.value.causes.map((c) => c.pct))
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <div>
    <div class="v-intro">
      <div>
        <h1>📊 经营分析智能体</h1>
        <p>自动归集门店经营数据，生成营收趋势、菜品排行与优化建议。每日 09:00 自动推送摘要。</p>
      </div>
    </div>

    <!-- NLQ -->
    <div class="nlq">
      <div class="nlq-h">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-linecap="round"><circle cx="11" cy="11" r="7" /><path d="m21 21-4.3-4.3" /></svg>
        经营数据提问
      </div>
      <div class="nlq-bar">
        <div class="box"><input v-model="nlqInput" placeholder="例如：分析上周营收下降原因，或对比工作日与周末客流量…" @keyup.enter="askNlq()" /></div>
        <button class="btn primary" @click="askNlq()">分析</button>
      </div>
      <div v-if="nlqAnswer" class="nlq-ans">
        <div class="ic"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round"><path d="M3 21h18M6 21V9M11 21V4M16 21v-8" /></svg></div>
        <div class="tx">
          根据最近 30 天数据分析：<br />
          <b>营收：</b>本周总营收 <span class="hl">¥58,240</span>，环比增长 12.5%。<br />
          <b>峰值：</b>周六为客流最高峰，日均收入是工作日的 <b>1.4x</b>。<br />
          <b>问题：</b>周四营收相较周三下滑 8%，可能与周边竞品活动相关。
        </div>
      </div>
    </div>

    <LoadingBlock v-if="loading" />
    <template v-else>
      <!-- KPI 卡片 -->
      <div class="grid-4">
        <div v-for="k in data.kpis" :key="k.label" class="kpi" :style="`--ac: ${k.trend_up ? 'var(--ok)' : 'var(--warn)'}`">
          <div class="kpi-top">
            <span class="kpi-label">{{ k.label }}</span>
            <span class="trend" :class="k.trend_up ? 'up' : 'down'">{{ k.trend_up ? '↑' : '↓' }} {{ k.pct }}</span>
          </div>
          <div class="kpi-val tnum">{{ k.value }}</div>
          <div class="kpi-sub">环比 <b>{{ k.trend_up ? '增长' : '变化' }} {{ k.pct }}</b></div>
        </div>
      </div>

      <!-- 菜品排行 + 客诉因子 -->
      <div class="row-2" style="margin-top: 18px">
        <div class="card">
          <div class="card-h"><h3>本周菜品销量排行</h3><span class="sub">份</span></div>
          <div class="card-b">
            <div v-for="(d, i) in data.top_dishes" :key="d.name" class="hbar">
              <span class="l"><span class="rank-no">{{ i + 1 }}</span>{{ d.name }}</span>
              <span class="t"><span class="f" :style="{ width: (d.sales / data.top_dishes[0].sales * 100) + '%' }"></span></span>
              <span class="v tnum">{{ d.sales }}</span>
            </div>
            <div style="margin-top: 10px; font-size: 11.5px; color: var(--ink-3)">
              💰 营收最高：<b style="color: var(--ink)">麻辣香锅 ¥11,256</b>（单品贡献 19.3%）
            </div>
          </div>
        </div>
        <div class="card">
          <div class="card-h"><h3>差评客诉因子</h3><span class="sub">占比</span></div>
          <div class="card-b">
            <div v-for="c in data.causes" :key="c.label" class="cause" style="margin-top: 0; padding-top: 0; border-top: none">
              <div class="ci">
                <span class="l">{{ c.label }}</span>
                <span class="t"><span class="f" :style="{ width: (c.pct / maxCause * 100) + '%' }"></span></span>
                <span class="v">{{ c.pct }}%</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 深度洞察 -->
      <div class="insight">
        <h3>
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10" /><path d="M12 16v-4M12 8h.01" /></svg>
          智能洞察与优化建议
        </h3>
        <ul>
          <li v-for="(tip, i) in data.insights" :key="i">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12" /></svg>
            {{ tip }}
          </li>
        </ul>
      </div>
    </template>
  </div>
</template>
