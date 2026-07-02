<script setup>
import { onMounted, reactive, ref } from 'vue'
import { toast } from '../utils/toast'
import { useAppStore } from '../store/app'

const appStore = useAppStore()
const loading = ref(false)
const form = reactive({
  storeName: '',
  address: '',
  hours: '',
  phone: '',
})

async function loadInfo() {
  await appStore.loadStoreInfo()
  form.storeName = appStore.storeName
  form.address = appStore.address
  form.hours = appStore.hours
  form.phone = appStore.phone
}

async function saveStoreInfo() {
  loading.value = true
  try {
    await appStore.saveStoreInfo(form)
    toast.success('门店信息已保存')
  } catch {
    toast.error('保存失败，请重试')
  } finally {
    loading.value = false
  }
}

onMounted(loadInfo)
</script>

<template>
  <div>
    <div class="v-intro">
      <div>
        <h1>系统设置</h1>
        <p>管理门店基本信息与平台参数配置。</p>
      </div>
    </div>

    <div class="card" style="max-width: 640px">
      <div class="card-h"><h3>门店信息</h3></div>
      <div class="card-b">
        <div class="field"><label>门店名称</label><input v-model="form.storeName" type="text" placeholder="例：城西旗舰店" /></div>
        <div class="field"><label>地址<span class="opt">选填</span></label><input v-model="form.address" type="text" placeholder="详细地址" /></div>
        <div class="frow2">
          <div class="field"><label>营业时间</label><input v-model="form.hours" type="text" placeholder="10:00 - 21:00" /></div>
          <div class="field"><label>联系电话<span class="opt">选填</span></label><input v-model="form.phone" type="text" placeholder="联系电话" /></div>
        </div>
        <button class="btn primary" :disabled="loading" @click="saveStoreInfo">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round"><path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z" /><polyline points="17 21 17 13 7 13 7 21" /><polyline points="7 3 7 8 15 8" /></svg>
          {{ loading ? '保存中...' : '保存修改' }}
        </button>
      </div>
    </div>
  </div>
</template>
