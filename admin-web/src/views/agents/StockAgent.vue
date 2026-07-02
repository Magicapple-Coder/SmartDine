<script setup>
// 库存预测智能体 —— 纯前端演示页
// Dify 库存预测智能体（runStockForecast）尚未接入，当前展示静态样例数据
import { onMounted, ref } from 'vue'
import { getStockForecast } from '../../api/agent'
import LoadingBlock from '../../components/LoadingBlock.vue'

const loading = ref(true)
const data = ref(null)
const nlqInput = ref('')
const nlqAnswer = ref('')

function askNlq() {
  const q = nlqInput.value.trim()
  if (!q) return
  nlqAnswer.value = q
  nlqInput.value = ''
}

onMounted(async () => {
  try {
    data.value = await getStockForecast()
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <div>
    <div class="v-intro">
      <div>
        <h1>📦 库存预测智能体</h1>
        <p>基于历史消耗趋势与营业计划，预测未来 7 日食材需求，自动生成采购建议与预警清单。</p>
      </div>
    </div>

    <!-- NLQ -->
    <div class="nlq">
      <div class="nlq-h">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-linecap="round"><circle cx="11" cy="11" r="7" /><path d="m21 21-4.3-4.3" /></svg>
        库存分析提问
      </div>
      <div class="nlq-bar">
        <div class="box"><input v-model="nlqInput" placeholder="例如：预测下周牛肉用量，或分析库存周转…" @keyup.enter="askNlq()" /></div>
        <button class="btn primary" @click="askNlq()">分析</button>
      </div>
      <div v-if="nlqAnswer" class="nlq-ans">
        <div class="ic"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round"><path d="M21 8 12 3 3 8v8l9 5 9-5z" /></svg></div>
        <div class="tx">
          基于近 30 日消耗数据与周末客流模型，<b>牛肉</b> 预计 2 日内低于安全库存（需采购 30kg）；
          <br /><b>酸梅汤料</b> 受高温天气影响消耗加速，建议本周末前补货 20 包。
          <br /><br /><span class="hl">采购优先级：牛肉 > 酸梅汤料 > 面粉</span>
        </div>
      </div>
    </div>

    <LoadingBlock v-if="loading" />
    <template v-else>
      <!-- 预警清单 -->
      <div class="sec-label"><h2>库存预警</h2><div class="ln"></div><span class="hint">当前 {{ data.alerts.length }} 项</span></div>
      <table class="dtable">
        <thead><tr><th>食材</th><th class="r">当前库存</th><th class="r">安全阈值</th><th class="r">预计可用</th><th>供应商</th><th class="c">优先级</th></tr></thead>
        <tbody>
          <tr v-for="a in data.alerts" :key="a.name">
            <td class="cellnm">{{ a.name }}</td>
            <td class="r tnum">{{ a.stock }} {{ a.unit }}</td>
            <td class="r tnum">{{ a.safe }} {{ a.unit }}</td>
            <td class="r"><span class="tag" :class="a.days_left <= 2 ? 'bad' : 'warn'">{{ a.days_left }} 天</span></td>
            <td class="sub-c">{{ a.supplier }}</td>
            <td class="c"><span class="tag" :class="a.priority === 'high' ? 'bad' : 'warn'">{{ a.priority === 'high' ? '紧急' : '注意' }}</span></td>
          </tr>
        </tbody>
      </table>

      <!-- 需求预测 + 采购建议 -->
      <div class="grid-2" style="margin-top: 18px">
        <div class="card">
          <div class="card-h"><h3>未来 7 日需求预测</h3><span class="sub">牛肉（kg）</span></div>
          <div class="card-b">
            <div class="fc-bars">
              <div v-for="f in data.forecast" :key="f.day" class="b">
                <span class="f" :style="{ height: (f.demand / 28) * 60 + 'px' }"></span>
                <span class="vv">{{ f.demand }}</span>
                <span class="x">{{ f.day }}</span>
              </div>
            </div>
            <p style="font-size: 11px; color: var(--ink-3); margin-top: 12px">
              周六峰值 28kg · 日均 22kg · 当前库存 12kg · <b style="color: var(--bad)">缺口 30kg</b>
            </p>
          </div>
        </div>
        <div class="card">
          <div class="card-h"><h3>采购建议</h3><span class="sub">智能生成</span></div>
          <div class="card-b" style="padding-bottom: 4px">
            <div v-for="(s, i) in data.suggestions" :key="i" class="buy">
              <span class="pri" :class="s.priority === 'high' ? 'hi' : 'mid'">{{ s.priority === 'high' ? '紧急' : '注意' }}</span>
              <div class="bd">
                <b>{{ s.text }}</b>
                <div class="rs">基于 ARIMA 模型预测 · 置信度 {{ s.priority === 'high' ? '92' : '85' }}%</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>
