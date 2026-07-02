<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { toast } from '../utils/toast'
import {
  checkoutTable,
  cleanTable,
  createReservation,
  createTable,
  deleteReservation,
  deleteTable,
  listReservations,
  listTables,
  openTable,
} from '../api/table'
import { formatDateTime } from '../utils'
import { usePending } from '../utils/pending'
import LoadingBlock from '../components/LoadingBlock.vue'

const { isPending, run } = usePending()

const tables = ref([])
const reservations = ref([])
const pageLoading = ref(true)
const createDialog = ref(false)
const reserveDialog = ref(false)
const form = reactive({ no: '', seats: 2 })
const reserveForm = reactive({ table_id: null, contact_name: '', contact_phone: '', reserve_time: '', guests: 1 })

const statusMeta = [
  { text: '空闲', cls: 'free', tag: 'ok' },
  { text: '就餐中', cls: 'busy', tag: 'warn' },
  { text: '已预订', cls: 'book', tag: 'ana' },
  { text: '待清理', cls: 'clean', tag: 'mut' },
]

const freeCount = computed(() => tables.value.filter((t) => t.status === 0).length)
const busyCount = computed(() => tables.value.filter((t) => t.status === 1).length)
const bookCount = computed(() => tables.value.filter((t) => t.status === 2).length)

async function load() {
  pageLoading.value = true
  try {
    tables.value = await listTables()
    reservations.value = await listReservations()
  } finally {
    pageLoading.value = false
  }
}

async function submitCreate() {
  if (!form.no) {
    toast.error('请填写桌号')
    return
  }
  await run('create-table', async () => {
    await createTable(form)
    toast.success('已新增桌台')
    createDialog.value = false
    load()
  })
}

async function handleOpen(table) {
  await run(`open-${table.table_id}`, async () => {
    await openTable(table.table_id)
    load()
  })
}

async function handleCheckout(table) {
  await run(`checkout-${table.table_id}`, async () => {
    await checkoutTable(table.table_id)
    load()
  })
}

async function handleClean(table) {
  await run(`clean-${table.table_id}`, async () => {
    await cleanTable(table.table_id)
    load()
  })
}

function openReserve(table) {
  Object.assign(reserveForm, { table_id: table.table_id, contact_name: '', contact_phone: '', reserve_time: '', guests: 1 })
  reserveDialog.value = true
}

async function submitReserve() {
  await run('submit-reserve', async () => {
    await createReservation(reserveForm)
    toast.success('已创建预订')
    reserveDialog.value = false
    load()
  })
}

async function removeTable(table) {
  if (!confirm(`确定删除桌台「T${table.no}」吗？`)) return
  await run(`delete-table-${table.table_id}`, async () => {
    await deleteTable(table.table_id)
    toast.success('已删除桌台')
    load()
  })
}

async function removeReservation(reservation) {
  if (!confirm('确定删除该预订记录吗？')) return
  await run(`delete-res-${reservation.reservation_id}`, async () => {
    await deleteReservation(reservation.reservation_id)
    toast.success('已删除预订')
    load()
  })
}

onMounted(load)
</script>

<template>
  <div>
    <div class="v-intro">
      <div>
        <h1>桌台管理</h1>
        <p>实时查看座位使用状态与预订情况。</p>
      </div>
      <div class="chips">
        <div class="chip"><span class="k">空闲</span><span class="v tnum" style="color: var(--ok)">{{ freeCount }}</span></div>
        <div class="chip"><span class="k">就餐中</span><span class="v tnum" style="color: var(--warn)">{{ busyCount }}</span></div>
        <div class="chip"><span class="k">已预订</span><span class="v tnum" style="color: var(--c-ana)">{{ bookCount }}</span></div>
      </div>
    </div>

    <div class="toolbar">
      <div class="tb-grow"></div>
      <button class="btn primary" @click="createDialog = true">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-linecap="round"><path d="M12 5v14M5 12h14" /></svg>
        新增桌台
      </button>
    </div>

    <LoadingBlock v-if="pageLoading" />
    <div v-else class="floor">
      <div v-for="t in tables" :key="t.table_id" class="tbl-card" :class="statusMeta[t.status].cls">
        <div class="no">T{{ t.no }}</div>
        <div class="seats">{{ t.seats }} 人桌</div>
        <span class="stt tag" :class="statusMeta[t.status].tag">{{ statusMeta[t.status].text }}</span>
        <div class="ops">
          <button v-if="[0, 2].includes(t.status)" class="btn sm" :disabled="isPending(`open-${t.table_id}`)" @click="handleOpen(t)">
            <span v-if="isPending(`open-${t.table_id}`)" class="spin"></span>开台
          </button>
          <button v-if="t.status === 1" class="btn sm" :disabled="isPending(`checkout-${t.table_id}`)" @click="handleCheckout(t)">
            <span v-if="isPending(`checkout-${t.table_id}`)" class="spin"></span>结账
          </button>
          <button v-if="t.status === 3" class="btn sm" :disabled="isPending(`clean-${t.table_id}`)" @click="handleClean(t)">
            <span v-if="isPending(`clean-${t.table_id}`)" class="spin"></span>清理完成
          </button>
          <button class="btn sm" @click="openReserve(t)">预订</button>
          <button
            v-if="t.status !== 1"
            class="btn sm"
            style="color: var(--bad); border-color: var(--bad)"
            :disabled="isPending(`delete-table-${t.table_id}`)"
            @click="removeTable(t)"
          >
            <span v-if="isPending(`delete-table-${t.table_id}`)" class="spin"></span>删除
          </button>
        </div>
      </div>
    </div>

    <div class="sec-label"><h2>预订记录</h2><div class="ln"></div></div>
    <table class="dtable">
      <thead><tr><th>预订号</th><th>桌台</th><th>联系人</th><th>电话</th><th>预订时间</th><th class="r">人数</th><th class="r">操作</th></tr></thead>
      <tbody>
        <tr v-if="pageLoading"><td colspan="7"><LoadingBlock /></td></tr>
        <template v-else>
          <tr v-for="r in reservations" :key="r.reservation_id">
            <td class="cellnm tnum">#{{ r.reservation_id }}</td>
            <td>T{{ r.table_id }}</td>
            <td>{{ r.contact_name || '—' }}</td>
            <td>{{ r.contact_phone || '—' }}</td>
            <td class="sub-c">{{ formatDateTime(r.reserve_time) }}</td>
            <td class="r tnum">{{ r.guests }}</td>
            <td class="r">
              <button
                class="btn sm"
                style="color: var(--bad); border-color: var(--bad)"
                :disabled="isPending(`delete-res-${r.reservation_id}`)"
                @click="removeReservation(r)"
              >
                <span v-if="isPending(`delete-res-${r.reservation_id}`)" class="spin"></span>删除
              </button>
            </td>
          </tr>
        </template>
      </tbody>
    </table>

    <div v-if="createDialog" class="overlay" @click.self="createDialog = false">
      <div class="modal">
        <div class="modal-h"><b>新增桌台</b><button class="x" @click="createDialog = false"><svg viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path d="M18 6 6 18M6 6l12 12" /></svg></button></div>
        <div class="modal-b">
          <div class="field"><label>桌号</label><input v-model="form.no" type="text" placeholder="如：8" /></div>
          <div class="field"><label>座位数</label><input v-model.number="form.seats" type="number" min="1" /></div>
        </div>
        <div class="modal-f">
          <button class="btn" @click="createDialog = false">取消</button>
          <button class="btn primary" :disabled="isPending('create-table')" @click="submitCreate">
            <span v-if="isPending('create-table')" class="spin"></span>保存
          </button>
        </div>
      </div>
    </div>

    <div v-if="reserveDialog" class="overlay" @click.self="reserveDialog = false">
      <div class="modal">
        <div class="modal-h"><b>新增预订</b><button class="x" @click="reserveDialog = false"><svg viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path d="M18 6 6 18M6 6l12 12" /></svg></button></div>
        <div class="modal-b">
          <div class="field"><label>联系人</label><input v-model="reserveForm.contact_name" type="text" /></div>
          <div class="field"><label>电话</label><input v-model="reserveForm.contact_phone" type="text" /></div>
          <div class="frow2">
            <div class="field"><label>预订时间</label><input v-model="reserveForm.reserve_time" type="datetime-local" /></div>
            <div class="field"><label>人数</label><input v-model.number="reserveForm.guests" type="number" min="1" /></div>
          </div>
        </div>
        <div class="modal-f">
          <button class="btn" @click="reserveDialog = false">取消</button>
          <button class="btn primary" :disabled="isPending('submit-reserve')" @click="submitReserve">
            <span v-if="isPending('submit-reserve')" class="spin"></span>保存
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
