<script setup>
// 客服处理智能体 —— 纯前端演示页
// Dify 客服处理智能体（chatService）尚未接入，当前展示静态工单样例
import { computed, onMounted, ref } from 'vue'
import { countPendingTickets, getTicketDetail, listServiceTickets } from '../../api/agent'

const tickets = ref([])
const pendingCount = ref(0)
const autoCount = ref(0)
const activeTicketId = ref(null)
const activeTicket = ref(null)
const loading = ref(false)
const replyDraft = ref('')
const chatInput = ref('')

const activeTicketMeta = computed(() => tickets.value.find((t) => t.id === activeTicketId.value))

async function loadTickets() {
  tickets.value = await listServiceTickets()
  const counts = await countPendingTickets()
  pendingCount.value = counts.pending
  autoCount.value = counts.auto
}

async function selectTicket(ticket) {
  loading.value = true
  activeTicketId.value = ticket.id
  try {
    activeTicket.value = await getTicketDetail(ticket.id)
    replyDraft.value = activeTicket.value.draft
    chatInput.value = ''
  } finally {
    loading.value = false
  }
}

function sendReply() {
  if (!chatInput.value.trim()) return
  activeTicket.value.messages.push({ from: 'bot', text: chatInput.value.trim(), time: new Date().toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' }) })
  chatInput.value = ''
}

onMounted(loadTickets)
</script>

<template>
  <div>
    <div class="v-intro">
      <div>
        <h1>💬 客服处理智能体</h1>
        <p>自动分类顾客咨询并生成智能回复草稿，强投诉与敏感事件自动分流至人工坐席。</p>
      </div>
      <div class="chips">
        <div class="chip"><span class="k">自动解决</span><span class="v tnum">{{ autoCount }}<small> 单</small></span></div>
        <div class="chip"><span class="k">待人工</span><span class="v tnum" style="color: var(--bad)">{{ pendingCount }}<small> 单</small></span></div>
      </div>
    </div>

    <!-- 工单信箱 -->
    <div class="inbox">
      <!-- 左侧工单列表 -->
      <div class="msg-list">
        <div class="msg-list-h">
          <b>工单信箱</b><span>共 {{ tickets.length }} 条</span>
        </div>
        <div v-for="t in tickets" :key="t.id" class="mi" :class="{ on: activeTicketId === t.id }" @click="selectTicket(t)">
          <div class="mc">
            <div class="top">
              <b>{{ t.member }}</b>
              <span class="tm">{{ t.time }}</span>
            </div>
            <div class="pv">{{ t.preview }}</div>
            <div class="meta">
              <span class="tag" :class="{ svc: t.category === '投诉', warn: t.category === '建议', mut: t.category === '咨询' || t.category === '预订' }">{{ t.category }}</span>
              <span class="st" :class="t.to_human ? 'wait' : 'auto'">
                <span class="d"></span>{{ t.to_human ? '待人工' : '自动处理' }}
              </span>
            </div>
          </div>
        </div>
      </div>

      <!-- 右侧对话面板 -->
      <div class="conv">
        <template v-if="activeTicket">
          <div class="conv-h">
            <div class="ava-c" style="background: var(--c-svc); width: 34px; height: 34px; font-size: 13px">{{ activeTicketMeta?.member?.[0] }}</div>
            <div class="ti">
              <b>{{ activeTicketMeta?.member }}</b>
              <div class="sub" style="font-size: 11px; color: var(--ink-3)">{{ activeTicketMeta?.channel }} · {{ activeTicketMeta?.time }}</div>
            </div>
          </div>
          <div class="conv-body">
            <div v-for="(msg, i) in activeTicket.messages" :key="i" style="margin-bottom: 12px">
              <template v-if="msg.from === 'customer'">
                <div class="cust-msg">
                  {{ msg.text }}
                  <div class="meta">{{ msg.name }} · {{ msg.time }}</div>
                </div>
              </template>
              <template v-else>
                <div class="bot-row">
                  <div class="b-from">
                    <div class="ic"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round"><path d="M21 11.5a8.4 8.4 0 0 1-8.5 8.5 8.5 8.5 0 0 1-3.8-.9L3 21l1.9-5.7a8.5 8.5 0 1 1 16.1-3.8z" /></svg></div>
                    <b>智能体</b><span>{{ msg.time }}</span>
                  </div>
                  <div class="bubble bot">{{ msg.text }}</div>
                </div>
              </template>
            </div>

            <!-- AI 分析 -->
            <div class="analysis">
              <div class="a"><span class="k">分类</span><span class="v" style="color: var(--c-order)">{{ activeTicket.analysis?.category }}</span></div>
              <div class="a"><span class="k">情绪</span><span class="v" :style="{ color: activeTicket.analysis?.sentiment === '强' ? 'var(--bad)' : 'var(--ok)' }">{{ activeTicket.analysis?.sentiment }}</span></div>
              <div class="a"><span class="k">意图</span><span class="v" style="color: var(--c-ana)">{{ activeTicket.analysis?.intent }}</span></div>
            </div>

            <!-- 草稿回复 -->
            <div class="draft">
              <div class="draft-h">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round"><path d="M16.5 3.5a2.1 2.1 0 0 1 3 3L7 19l-4 1 1-4z" /></svg>
                <b>智能回复草稿</b><span class="ed">可编辑</span>
              </div>
              <div class="draft-tx">{{ replyDraft }}</div>
              <div class="draft-act">
                <button class="btn sm primary" @click="sendReply">✅ 采纳并发送</button>
                <button class="btn sm">✏️ 重新生成</button>
              </div>
            </div>
          </div>
        </template>
        <div v-else style="flex: 1; display: flex; align-items: center; justify-content: center; color: var(--ink-3); font-size: 13px">
          ← 选择一条工单以查看详情
        </div>

        <!-- 输入区 -->
        <div v-if="activeTicket" class="chat-input">
          <div class="box"><input v-model="chatInput" placeholder="输入回复内容…" @keyup.enter="sendReply" /></div>
          <button class="send" @click="sendReply">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round"><path d="M22 2 11 13" /><path d="m22 2-7 20-4-9-9-4z" /></svg>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
