<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { toast } from '../utils/toast'
import { createSchedule, createStaff, deleteStaff, listSchedules, listStaff, updateStaff } from '../api/staff'
import { usePending } from '../utils/pending'
import LoadingBlock from '../components/LoadingBlock.vue'

const { isPending, run } = usePending()

const staffList = ref([])
const schedules = ref([])
const pageLoading = ref(true)
const staffDialog = ref(false)
const scheduleDialog = ref(false)
const editingStaff = ref(null)
const staffForm = reactive({ name: '', role: '服务员', account: '', password: '' })
const scheduleForm = reactive({ staff_id: null, date: '', shift: '早' })

const avaColors = ['#E0613A', '#3B86D9', '#DD9020', '#1FA37A', '#7C6FE0', '#9C978C']
const shiftCls = { 早: 'am', 晚: 'pm', 全天: 'full', 休: 'off' }

const weekDates = computed(() => {
  const now = new Date()
  const monday = new Date(now)
  monday.setDate(now.getDate() - ((now.getDay() + 6) % 7))
  return [...Array(7)].map((_, i) => {
    const d = new Date(monday)
    d.setDate(monday.getDate() + i)
    return d
  })
})
const weekLabels = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']

function isoDate(d) {
  return d.toISOString().slice(0, 10)
}

function shiftFor(staffId, date) {
  const found = schedules.value.find((s) => s.staff_id === staffId && s.date === isoDate(date))
  return found ? found.shift : '休'
}

async function load() {
  pageLoading.value = true
  try {
    staffList.value = await listStaff()
    schedules.value = await listSchedules()
  } finally {
    pageLoading.value = false
  }
}

function openEditStaff(staff) {
  editingStaff.value = staff
  Object.assign(staffForm, { name: staff.name, role: staff.role, account: staff.account, password: '' })
  staffDialog.value = true
}

function openCreateStaff() {
  editingStaff.value = null
  Object.assign(staffForm, { name: '', role: '服务员', account: '', password: '' })
  staffDialog.value = true
}

async function submitStaff() {
  if (!staffForm.name || !staffForm.account) {
    toast.error('请填写姓名和账号')
    return
  }
  if (!editingStaff.value && !staffForm.password) {
    toast.error('新增员工请设置密码')
    return
  }
  await run('submit-staff', async () => {
    if (editingStaff.value) {
      const payload = { name: staffForm.name, role: staffForm.role, account: staffForm.account }
      if (staffForm.password) payload.password = staffForm.password
      await updateStaff(editingStaff.value.staff_id, payload)
      toast.success('员工信息已更新')
    } else {
      await createStaff(staffForm)
      toast.success('已新增员工')
    }
    staffDialog.value = false
    editingStaff.value = null
    load()
  })
}

function openScheduleDialog(staff, date) {
  const currentShift = date ? shiftFor(staff.staff_id, date) : '早'
  Object.assign(scheduleForm, { staff_id: staff.staff_id, date: date ? isoDate(date) : '', shift: currentShift })
  scheduleDialog.value = true
}

async function submitSchedule() {
  if (!scheduleForm.date) {
    toast.error('请选择日期')
    return
  }
  await run('submit-schedule', async () => {
    await createSchedule(scheduleForm)
    toast.success('已排班')
    scheduleDialog.value = false
    load()
  })
}

async function removeStaff(staff) {
  if (!confirm(`确定删除员工「${staff.name}」吗？其排班记录将一并删除。`)) return
  await run(`delete-staff-${staff.staff_id}`, async () => {
    await deleteStaff(staff.staff_id)
    toast.success('已删除员工')
    load()
  })
}

onMounted(load)
</script>

<template>
  <div>
    <div class="v-intro">
      <div>
        <h1>员工管理</h1>
        <p>管理员工账号与角色，安排本周班次与工时统计。</p>
      </div>
      <button class="btn primary" @click="openCreateStaff()">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-linecap="round"><path d="M12 5v14M5 12h14" /></svg>
        添加员工
      </button>
    </div>

    <table class="dtable">
      <thead><tr><th>员工</th><th>角色</th><th class="c">状态</th><th class="r">本周工时</th><th class="r">操作</th></tr></thead>
      <tbody>
        <tr v-if="pageLoading"><td colspan="5"><LoadingBlock /></td></tr>
        <template v-else>
          <tr v-for="(s, i) in staffList" :key="s.staff_id">
            <td><div class="rowflex"><span class="ava-c" :style="{ background: avaColors[i % avaColors.length] }">{{ s.name[0] }}</span><div class="cellnm">{{ s.name }}</div></div></td>
            <td>{{ s.role }}</td>
            <td class="c">
                <span v-if="s.is_on_shift" class="tag ok">在班</span>
                <span v-else-if="s.status === 1" class="tag warn">休息</span>
                <span v-else class="tag mut">离职</span>
              </td>
            <td class="r tnum">{{ s.weekly_hours }} h</td>
            <td class="r">
              <div class="act-btns">
                <button class="btn sm" @click="openScheduleDialog(s)">排班</button>
                <button class="ibtn" @click="openEditStaff(s)">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M12 20h9" /><path d="M16.5 3.5a2.1 2.1 0 0 1 3 3L7 19l-4 1 1-4z" /></svg>
                </button>
                <button
                  class="btn sm"
                  style="color: var(--bad); border-color: var(--bad)"
                  :disabled="isPending(`delete-staff-${s.staff_id}`)"
                  @click="removeStaff(s)"
                >
                  <span v-if="isPending(`delete-staff-${s.staff_id}`)" class="spin"></span>删除
                </button>
              </div>
            </td>
          </tr>
        </template>
      </tbody>
    </table>

    <div class="sec-label"><h2>本周排班</h2><div class="ln"></div><span class="hint">早 09–15 · 晚 15–21</span></div>
    <table class="sched">
      <thead>
        <tr><th>员工</th><th v-for="(l, i) in weekLabels" :key="l">{{ l }}<br /><span class="sub-c">{{ weekDates[i].getMonth() + 1 }}/{{ weekDates[i].getDate() }}</span></th></tr>
      </thead>
      <tbody>
        <tr v-if="pageLoading"><td colspan="8"><LoadingBlock /></td></tr>
        <template v-else>
          <tr v-for="s in staffList" :key="s.staff_id">
            <td>{{ s.name }}</td>
            <td v-for="d in weekDates" :key="d.getTime()">
              <button class="shift" :class="shiftCls[shiftFor(s.staff_id, d)]" @click="openScheduleDialog(s, d)">{{ shiftFor(s.staff_id, d) }}</button>
            </td>
          </tr>
        </template>
      </tbody>
    </table>

    <div v-if="staffDialog" class="overlay" @click.self="staffDialog = false">
      <div class="modal">
        <div class="modal-h"><b>{{ editingStaff ? '编辑员工' : '添加员工' }}</b><button class="x" @click="staffDialog = false"><svg viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path d="M18 6 6 18M6 6l12 12" /></svg></button></div>
        <div class="modal-b">
          <div class="field"><label>姓名</label><input v-model="staffForm.name" type="text" /></div>
          <div class="field">
            <label>角色</label>
            <select v-model="staffForm.role">
              <option value="店长">店长</option>
              <option value="收银">收银</option>
              <option value="后厨">后厨</option>
              <option value="服务员">服务员</option>
              <option value="奴隶">奴隶</option>
            </select>
          </div>
          <div class="frow2">
            <div class="field"><label>账号</label><input v-model="staffForm.account" type="text" /></div>
            <div class="field"><label>密码<span class="opt" v-if="editingStaff">选填，留空不修改</span></label><input v-model="staffForm.password" type="password" :placeholder="editingStaff ? '留空则不修改密码' : ''" /></div>
          </div>
        </div>
        <div class="modal-f">
          <button class="btn" @click="staffDialog = false">取消</button>
          <button class="btn primary" :disabled="isPending('submit-staff')" @click="submitStaff">
            <span v-if="isPending('submit-staff')" class="spin"></span>保存
          </button>
        </div>
      </div>
    </div>

    <div v-if="scheduleDialog" class="overlay" @click.self="scheduleDialog = false">
      <div class="modal">
        <div class="modal-h"><b>排班</b><button class="x" @click="scheduleDialog = false"><svg viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path d="M18 6 6 18M6 6l12 12" /></svg></button></div>
        <div class="modal-b">
          <div class="field"><label>日期</label><input v-model="scheduleForm.date" type="date" /></div>
          <div class="field">
            <label>班次</label>
            <select v-model="scheduleForm.shift">
              <option value="早">早（6h）</option>
              <option value="晚">晚（6h）</option>
              <option value="全天">全天（12h）</option>
              <option value="休">休</option>
            </select>
          </div>
        </div>
        <div class="modal-f">
          <button class="btn" @click="scheduleDialog = false">取消</button>
          <button class="btn primary" :disabled="isPending('submit-schedule')" @click="submitSchedule">
            <span v-if="isPending('submit-schedule')" class="spin"></span>保存
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
