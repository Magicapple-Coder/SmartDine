<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { toast } from '../utils/toast'
import { adjustPoints, createMember, listMembers, updateMember } from '../api/member'
import { formatDateTime, formatMoney } from '../utils'
import { usePending } from '../utils/pending'
import LoadingBlock from '../components/LoadingBlock.vue'

const { isPending, run } = usePending()

const members = ref([])
const activeLevel = ref('全部')
const keyword = ref('')
const pageLoading = ref(true)
const pointsDialog = ref(false)
const pointsForm = reactive({ member_id: null, delta: 0, reason: '' })
const memberDialog = ref(false)
const editingMember = ref(null)
const memberForm = reactive({ name: '', phone: '', preferences: '' })

const levelTag = { 黑卡: { bg: '#211E1B', color: '#fff' }, 金卡: { cls: 'stock' }, 银卡: { cls: 'ana' }, 普通: { cls: 'mut' } }
const levels = ['全部', '黑卡', '金卡', '银卡', '普通']

const filtered = computed(() =>
  members.value.filter(
    (m) => (activeLevel.value === '全部' || m.level === activeLevel.value) && (m.name || m.phone).includes(keyword.value),
  ),
)

const totalCount = computed(() => members.value.length)
const totalBalance = computed(() => members.value.reduce((sum, m) => sum + Number(m.balance || 0), 0))

async function load() {
  pageLoading.value = true
  try {
    members.value = await listMembers()
  } finally {
    pageLoading.value = false
  }
}

function openPointsDialog(member) {
  Object.assign(pointsForm, { member_id: member.member_id, delta: 0, reason: '' })
  pointsDialog.value = true
}

async function submitPoints() {
  await run('submit-points', async () => {
    await adjustPoints(pointsForm.member_id, { delta: pointsForm.delta, reason: pointsForm.reason })
    toast.success('积分已更新')
    pointsDialog.value = false
    load()
  })
}

function openCreateMember() {
  editingMember.value = null
  Object.assign(memberForm, { name: '', phone: '', preferences: '' })
  memberDialog.value = true
}

function openEditMember(m) {
  editingMember.value = m
  Object.assign(memberForm, { name: m.name || '', phone: m.phone, preferences: m.preferences || '' })
  memberDialog.value = true
}

async function submitMember() {
  if (!memberForm.phone) {
    toast.error('请输入手机号')
    return
  }
  await run('submit-member', async () => {
    if (editingMember.value) {
      await updateMember(editingMember.value.member_id, { name: memberForm.name, preferences: memberForm.preferences })
      toast.success('会员信息已更新')
    } else {
      await createMember({ name: memberForm.name, phone: memberForm.phone, preferences: memberForm.preferences })
      toast.success('已添加会员')
    }
    memberDialog.value = false
    editingMember.value = null
    load()
  })
}

onMounted(load)
</script>

<template>
  <div>
    <div class="v-intro">
      <div>
        <h1>会员管理</h1>
        <p>管理顾客档案、等级与积分，沉淀复购与会员价值数据。</p>
      </div>
      <div class="chips">
        <div class="chip"><span class="k">会员总数</span><span class="v tnum">{{ totalCount }}</span></div>
        <div class="chip"><span class="k">在储余额</span><span class="v tnum">{{ formatMoney(totalBalance) }}</span></div>
      </div>
      <button class="btn primary" @click="openCreateMember()">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-linecap="round"><path d="M12 5v14M5 12h14" /></svg>
        添加会员
      </button>
    </div>

    <div class="toolbar">
      <div class="seg">
        <button v-for="l in levels" :key="l" :class="{ on: activeLevel === l }" @click="activeLevel = l">{{ l }}</button>
      </div>
      <div class="tb-grow"></div>
      <div class="search-box">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-linecap="round"><circle cx="11" cy="11" r="7" /><path d="m21 21-4.3-4.3" /></svg>
        <input v-model="keyword" placeholder="搜索姓名 / 手机号" />
      </div>
    </div>

    <table class="dtable">
      <thead><tr><th>会员</th><th class="c">等级</th><th class="r">积分</th><th class="r">储值余额</th><th class="r">到店次数</th><th class="r">累计消费</th><th class="r">最近到店</th><th class="r">操作</th></tr></thead>
      <tbody>
        <tr v-if="pageLoading"><td colspan="8"><LoadingBlock /></td></tr>
        <template v-else>
          <tr v-for="m in filtered" :key="m.member_id">
            <td>
              <div class="rowflex">
                <span class="ava-c" style="background: var(--brand)">{{ (m.name || m.phone)[0] }}</span>
                <div><div class="cellnm">{{ m.name || m.phone }}</div><div class="sub-c">{{ m.phone }}</div></div>
              </div>
            </td>
            <td class="c">
              <span v-if="m.level === '黑卡'" class="tag" style="background: #211e1b; color: #fff">黑卡</span>
              <span v-else class="tag" :class="levelTag[m.level]?.cls || 'mut'">{{ m.level }}</span>
            </td>
            <td class="r tnum">{{ m.points }}</td>
            <td class="r tnum">{{ formatMoney(m.balance) }}</td>
            <td class="r tnum">{{ m.visits }}</td>
            <td class="r tnum">{{ formatMoney(m.total_spend) }}</td>
            <td class="r sub-c">{{ m.last_visit ? formatDateTime(m.last_visit) : '—' }}</td>
            <td class="r">
                <div class="act-btns">
                  <button class="ibtn" @click="openEditMember(m)">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M12 20h9" /><path d="M16.5 3.5a2.1 2.1 0 0 1 3 3L7 19l-4 1 1-4z" /></svg>
                  </button>
                  <button class="btn sm" @click="openPointsDialog(m)">积分调整</button>
                </div>
              </td>
          </tr>
        </template>
      </tbody>
    </table>

    <div v-if="pointsDialog" class="overlay" @click.self="pointsDialog = false">
      <div class="modal">
        <div class="modal-h"><b>积分调整</b><button class="x" @click="pointsDialog = false"><svg viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path d="M18 6 6 18M6 6l12 12" /></svg></button></div>
        <div class="modal-b">
          <div class="field"><label>变动值<span class="opt">正数增加，负数兑换扣减</span></label><input v-model.number="pointsForm.delta" type="number" /></div>
          <div class="field"><label>备注<span class="opt">选填</span></label><input v-model="pointsForm.reason" type="text" /></div>
        </div>
        <div class="modal-f">
          <button class="btn" @click="pointsDialog = false">取消</button>
          <button class="btn primary" :disabled="isPending('submit-points')" @click="submitPoints">
            <span v-if="isPending('submit-points')" class="spin"></span>保存
          </button>
        </div>
      </div>
    </div>

    <div v-if="memberDialog" class="overlay" @click.self="memberDialog = false">
      <div class="modal">
        <div class="modal-h"><b>{{ editingMember ? '编辑会员' : '添加会员' }}</b><button class="x" @click="memberDialog = false"><svg viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path d="M18 6 6 18M6 6l12 12" /></svg></button></div>
        <div class="modal-b">
          <div class="field"><label>手机号<span v-if="editingMember" class="opt">不可修改</span></label><input v-model="memberForm.phone" type="text" :disabled="!!editingMember" /></div>
          <div class="field"><label>姓名<span class="opt">选填</span></label><input v-model="memberForm.name" type="text" /></div>
          <div class="field"><label>偏好/忌口<span class="opt">选填，逗号分隔</span></label><input v-model="memberForm.preferences" type="text" placeholder="如：不吃辣，偏好清淡" /></div>
        </div>
        <div class="modal-f">
          <button class="btn" @click="memberDialog = false">取消</button>
          <button class="btn primary" :disabled="isPending('submit-member')" @click="submitMember">
            <span v-if="isPending('submit-member')" class="spin"></span>保存
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
