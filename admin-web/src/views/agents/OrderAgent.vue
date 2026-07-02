<script setup>
// 点餐推荐智能体 —— 纯前端演示页
// Dify 点餐推荐智能体（chatOrder）尚未接入，当前展示静态样例数据
import { onMounted, ref } from 'vue'
import { getOrderRecommendations } from '../../api/agent'
import LoadingBlock from '../../components/LoadingBlock.vue'

const loading = ref(true)
const data = ref(null)
const nlqInput = ref('')
const nlqAnswer = ref('')

const quickQuestions = [
  '今天什么菜最受欢迎？',
  '推荐几道适合多人聚餐的菜',
  '有哪些低脂健康的菜品？',
]

function askNlq(q) {
  const question = q || nlqInput.value.trim()
  if (!question) return
  nlqAnswer.value = question
  nlqInput.value = ''
}

onMounted(async () => {
  try {
    data.value = await getOrderRecommendations()
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <div>
    <div class="v-intro">
      <div>
        <h1>🤖 点餐推荐智能体</h1>
        <p>结合顾客偏好、实时库存与菜品销量，为新订单智能推荐搭配菜品，自动规避缺货项。</p>
      </div>
    </div>

    <!-- NLQ 自然语言查询 -->
    <div class="nlq">
      <div class="nlq-h">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-linecap="round"><circle cx="11" cy="11" r="7" /><path d="m21 21-4.3-4.3" /></svg>
        快速提问
      </div>
      <div class="nlq-bar">
        <div class="box">
          <input v-model="nlqInput" placeholder="例如：推荐适合今晚聚餐的菜品组合…" @keyup.enter="askNlq()" />
        </div>
        <button class="btn primary" @click="askNlq()">分析</button>
      </div>
      <div v-if="nlqAnswer" class="nlq-ans">
        <div class="ic"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round"><path d="M21 11.5a8.4 8.4 0 0 1-8.5 8.5 8.5 8.5 0 0 1-3.8-.9L3 21l1.9-5.7a8.5 8.5 0 1 1 16.1-3.8z" /></svg></div>
        <div class="tx">
          基于今日库存与顾客偏好分析，为您推荐以下结果：
          <br /><br />
          <b>🔥 主推组合：</b>招牌牛肉面 + 老坛酸梅汤（客单价 ¥36，点选率最高）
          <br />
          <b>📊 数据洞察：</b>当前库存中 <span class="hl">椒麻鸡</span> 备货充足且毛利较高，建议优先推荐。另有 <span class="hl">3 项</span>食材库存紧张，已自动在推荐列表中去重。
        </div>
      </div>
    </div>

    <LoadingBlock v-if="loading" />
    <template v-else>
      <!-- 统计摘要 -->
      <div class="insight" style="margin-bottom: 20px; margin-top: 0">
        <h3>
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="18" height="18" rx="2" /><path d="M8 13v4M12 10v7M16 7v10" /></svg>
          本周推荐效果
        </h3>
        <div style="display: flex; gap: 28px; flex-wrap: wrap">
          <div><div style="font-size: 11px; color: var(--ink-3)">总展示次数</div><div style="font-size: 22px; font-weight: 700" class="tnum">312</div></div>
          <div><div style="font-size: 11px; color: var(--ink-3)">采纳次数</div><div style="font-size: 22px; font-weight: 700" class="tnum">54</div></div>
          <div><div style="font-size: 11px; color: var(--ink-3)">采纳率</div><div style="font-size: 22px; font-weight: 700; color: var(--c-order)">17.3%</div></div>
        </div>
      </div>

      <!-- 推荐菜品 + 饼图 -->
      <div class="row-2">
        <div class="card">
          <div class="card-h"><h3>智能推荐菜品</h3><span class="sub">实时生成</span></div>
          <div class="card-b" style="padding-top: 8px; padding-bottom: 8px">
            <div v-for="r in data.recommendations" :key="r.id" class="rec">
              <div class="info">
                <b>{{ r.name }}</b>
                <div class="why">{{ r.reason }}</div>
              </div>
              <span class="pr tnum">¥{{ r.price }}</span>
              <button class="add" title="加入订单">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-linecap="round"><path d="M12 5v14M5 12h14" /></svg>
              </button>
            </div>
          </div>
        </div>
        <div class="card">
          <div class="card-h"><h3>推荐类型分布</h3><span class="sub">近 7 日</span></div>
          <div class="card-b">
            <div class="donut-wrap">
              <div class="donut">
                <svg width="130" height="130" viewBox="0 0 130 130">
                  <circle cx="65" cy="65" r="52" fill="none" stroke="var(--surface-2)" stroke-width="20" />
                  <circle cx="65" cy="65" r="52" fill="none" stroke="var(--brand)" stroke-width="20" stroke-dasharray="120 326" stroke-linecap="round" transform="rotate(-90 65 65)" />
                  <circle cx="65" cy="65" r="52" fill="none" stroke="var(--c-stock)" stroke-width="20" stroke-dasharray="90 326" stroke-linecap="round" transform="rotate(30 65 65)" />
                  <circle cx="65" cy="65" r="52" fill="none" stroke="var(--c-order)" stroke-width="20" stroke-dasharray="60 326" stroke-linecap="round" transform="rotate(160 65 65)" />
                  <circle cx="65" cy="65" r="52" fill="none" stroke="var(--c-svc)" stroke-width="20" stroke-dasharray="56 326" stroke-linecap="round" transform="rotate(210 65 65)" />
                </svg>
                <div class="ctr"><b>T1</b><span>偏好</span></div>
              </div>
              <div class="lgd">
                <div class="li"><span class="sw" style="background: var(--brand)"></span><span class="nm">偏好匹配</span><span class="pc">37%</span></div>
                <div class="li"><span class="sw" style="background: var(--c-stock)"></span><span class="nm">搭配推荐</span><span class="pc">28%</span></div>
                <div class="li"><span class="sw" style="background: var(--c-order)"></span><span class="nm">热销菜品</span><span class="pc">18%</span></div>
                <div class="li"><span class="sw" style="background: var(--c-svc)"></span><span class="nm">健康推荐</span><span class="pc">17%</span></div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>
