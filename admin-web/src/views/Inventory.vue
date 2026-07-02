<script setup>
import { onMounted, reactive, ref } from 'vue'
import { toast } from '../utils/toast'
import {
  createIngredient,
  createSupplier,
  deleteIngredient,
  deleteSupplier,
  listIngredients,
  listStockLogs,
  listSuppliers,
  recordStockLog,
} from '../api/inventory'
import { formatDateTime } from '../utils'
import { usePending } from '../utils/pending'
import LoadingBlock from '../components/LoadingBlock.vue'

const { isPending, run } = usePending()

const activeTab = ref('stock')
const ingredients = ref([])
const stockLogs = ref([])
const suppliers = ref([])
const pageLoading = ref(true)

const ingredientDialog = ref(false)
const stockDialog = ref(false)
const supplierDialog = ref(false)
const ingredientForm = reactive({ name: '', unit: '', supplier_id: null, stock: 0, safe_threshold: 0 })
const stockForm = reactive({ ingredient_id: null, type: '入库', qty: 0, operator: '', remark: '' })
const supplierForm = reactive({ name: '', category: '', contact: '', phone: '', lead_time: 1 })

const typeTag = { 入库: 'ok', 出库: 'ana', 损耗: 'bad' }

async function load() {
  pageLoading.value = true
  try {
    ;[ingredients.value, stockLogs.value, suppliers.value] = await Promise.all([
      listIngredients(false),
      listStockLogs(),
      listSuppliers(),
    ])
  } finally {
    pageLoading.value = false
  }
}

function statusOf(ing) {
  const stock = Number(ing.stock)
  const threshold = Number(ing.safe_threshold)
  if (stock <= threshold) return { text: '紧张', tag: 'bad' }
  if (stock <= threshold * 1.5) return { text: '预警', tag: 'warn' }
  return { text: '充足', tag: 'ok' }
}

async function submitIngredient() {
  if (!ingredientForm.name || !ingredientForm.unit) {
    toast.error('请填写食材名称和单位')
    return
  }
  await run('submit-ingredient', async () => {
    await createIngredient(ingredientForm)
    toast.success('已新增食材')
    ingredientDialog.value = false
    load()
  })
}

function openStockDialog(ingredient) {
  Object.assign(stockForm, { ingredient_id: ingredient.ingredient_id, type: '入库', qty: 0, operator: '', remark: '' })
  stockDialog.value = true
}

async function submitStock() {
  if (!stockForm.operator || !stockForm.qty) {
    toast.error('请填写数量和操作人')
    return
  }
  await run('submit-stock', async () => {
    await recordStockLog(stockForm)
    toast.success('已登记出入库')
    stockDialog.value = false
    load()
  })
}

async function submitSupplier() {
  if (!supplierForm.name) {
    toast.error('请填写供应商名称')
    return
  }
  await run('submit-supplier', async () => {
    await createSupplier(supplierForm)
    toast.success('已新增供应商')
    supplierDialog.value = false
    load()
  })
}

async function removeIngredient(ing) {
  if (!confirm(`确定删除食材「${ing.name}」吗？`)) return
  await run(`delete-ing-${ing.ingredient_id}`, async () => {
    await deleteIngredient(ing.ingredient_id)
    toast.success('已删除食材')
    load()
  })
}

async function removeSupplier(supplier) {
  if (!confirm(`确定删除供应商「${supplier.name}」吗？`)) return
  await run(`delete-sup-${supplier.supplier_id}`, async () => {
    await deleteSupplier(supplier.supplier_id)
    toast.success('已删除供应商')
    load()
  })
}

onMounted(load)
</script>

<template>
  <div>
    <div class="v-intro">
      <div>
        <h1>库存管理</h1>
        <p>维护食材基础库存，记录出入库流水与供应商信息。</p>
      </div>
      <div>
        <button class="btn" @click="supplierDialog = true">新增供应商</button>
        <button class="btn primary" style="margin-left: 8px" @click="ingredientDialog = true">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-linecap="round"><path d="M12 5v14M5 12h14" /></svg>
          新增食材
        </button>
      </div>
    </div>

    <div class="vtabs">
      <button class="vtab" :class="{ on: activeTab === 'stock' }" @click="activeTab = 'stock'">食材库存</button>
      <button class="vtab" :class="{ on: activeTab === 'log' }" @click="activeTab = 'log'">出入库记录</button>
      <button class="vtab" :class="{ on: activeTab === 'sup' }" @click="activeTab = 'sup'">供应商</button>
    </div>

    <div v-show="activeTab === 'stock'">
      <table class="dtable">
        <thead><tr><th>食材</th><th class="r">当前库存</th><th class="r">安全阈值</th><th class="c">状态</th><th class="r">操作</th></tr></thead>
        <tbody>
          <tr v-if="pageLoading"><td colspan="5"><LoadingBlock /></td></tr>
          <template v-else>
            <tr v-for="ing in ingredients" :key="ing.ingredient_id">
              <td><div class="rowflex"><span class="thumb">📦</span><span class="cellnm">{{ ing.name }}</span></div></td>
              <td class="r tnum">{{ ing.stock }} {{ ing.unit }}</td>
              <td class="r tnum">{{ ing.safe_threshold }} {{ ing.unit }}</td>
              <td class="c"><span class="tag" :class="statusOf(ing).tag">{{ statusOf(ing).text }}</span></td>
              <td class="r">
                <div class="act-btns">
                  <button class="btn sm" @click="openStockDialog(ing)">出入库</button>
                  <button
                    class="btn sm"
                    style="color: var(--bad); border-color: var(--bad)"
                    :disabled="isPending(`delete-ing-${ing.ingredient_id}`)"
                    @click="removeIngredient(ing)"
                  >
                    <span v-if="isPending(`delete-ing-${ing.ingredient_id}`)" class="spin"></span>删除
                  </button>
                </div>
              </td>
            </tr>
          </template>
        </tbody>
      </table>
      <p class="cap">
        基于库存消耗趋势，系统会自动预警低库存食材并及时生成采购建议。
      </p>
    </div>

    <div v-show="activeTab === 'log'">
      <table class="dtable">
        <thead><tr><th>时间</th><th class="c">类型</th><th>食材</th><th class="r">数量</th><th>操作人</th><th>备注</th></tr></thead>
        <tbody>
          <tr v-if="pageLoading"><td colspan="6"><LoadingBlock /></td></tr>
          <template v-else>
            <tr v-for="log in stockLogs" :key="log.log_id">
              <td class="sub-c tnum">{{ formatDateTime(log.time) }}</td>
              <td class="c"><span class="tag" :class="typeTag[log.type]">{{ log.type }}</span></td>
              <td class="cellnm">{{ ingredients.find((i) => i.ingredient_id === log.ingredient_id)?.name || '#' + log.ingredient_id }}</td>
              <td class="r tnum">{{ log.qty }}</td>
              <td>{{ log.operator }}</td>
              <td class="sub-c">{{ log.remark || '—' }}</td>
            </tr>
          </template>
        </tbody>
      </table>
    </div>

    <div v-show="activeTab === 'sup'">
      <table class="dtable">
        <thead><tr><th>供应商</th><th>主营分类</th><th>联系人</th><th>联系电话</th><th class="r">采购周期</th><th class="r">操作</th></tr></thead>
        <tbody>
          <tr v-if="pageLoading"><td colspan="6"><LoadingBlock /></td></tr>
          <template v-else>
            <tr v-for="s in suppliers" :key="s.supplier_id">
              <td class="cellnm">{{ s.name }}</td>
              <td>{{ s.category || '—' }}</td>
              <td>{{ s.contact || '—' }}</td>
              <td class="tnum">{{ s.phone || '—' }}</td>
              <td class="r tnum">{{ s.lead_time }} 天</td>
              <td class="r">
                <button
                  class="btn sm"
                  style="color: var(--bad); border-color: var(--bad)"
                  :disabled="isPending(`delete-sup-${s.supplier_id}`)"
                  @click="removeSupplier(s)"
                >
                  <span v-if="isPending(`delete-sup-${s.supplier_id}`)" class="spin"></span>删除
                </button>
              </td>
            </tr>
          </template>
        </tbody>
      </table>
    </div>

    <div v-if="ingredientDialog" class="overlay" @click.self="ingredientDialog = false">
      <div class="modal">
        <div class="modal-h"><b>新增食材</b><button class="x" @click="ingredientDialog = false"><svg viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path d="M18 6 6 18M6 6l12 12" /></svg></button></div>
        <div class="modal-b">
          <div class="frow2">
            <div class="field"><label>名称</label><input v-model="ingredientForm.name" type="text" /></div>
            <div class="field"><label>单位</label><input v-model="ingredientForm.unit" type="text" placeholder="如：kg" /></div>
          </div>
          <div class="field">
            <label>供应商<span class="opt">选填</span></label>
            <select v-model="ingredientForm.supplier_id">
              <option :value="null">不指定</option>
              <option v-for="s in suppliers" :key="s.supplier_id" :value="s.supplier_id">{{ s.name }}</option>
            </select>
          </div>
          <div class="frow2">
            <div class="field"><label>初始库存</label><input v-model.number="ingredientForm.stock" type="number" /></div>
            <div class="field"><label>安全阈值</label><input v-model.number="ingredientForm.safe_threshold" type="number" /></div>
          </div>
        </div>
        <div class="modal-f">
          <button class="btn" @click="ingredientDialog = false">取消</button>
          <button class="btn primary" :disabled="isPending('submit-ingredient')" @click="submitIngredient">
            <span v-if="isPending('submit-ingredient')" class="spin"></span>保存
          </button>
        </div>
      </div>
    </div>

    <div v-if="stockDialog" class="overlay" @click.self="stockDialog = false">
      <div class="modal">
        <div class="modal-h"><b>出入库登记</b><button class="x" @click="stockDialog = false"><svg viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path d="M18 6 6 18M6 6l12 12" /></svg></button></div>
        <div class="modal-b">
          <div class="field">
            <label>类型</label>
            <select v-model="stockForm.type">
              <option value="入库">入库</option>
              <option value="出库">出库</option>
              <option value="损耗">损耗</option>
            </select>
          </div>
          <div class="field"><label>数量</label><input v-model.number="stockForm.qty" type="number" min="0" /></div>
          <div class="field"><label>操作人</label><input v-model="stockForm.operator" type="text" /></div>
          <div class="field"><label>备注<span class="opt">选填</span></label><input v-model="stockForm.remark" type="text" /></div>
        </div>
        <div class="modal-f">
          <button class="btn" @click="stockDialog = false">取消</button>
          <button class="btn primary" :disabled="isPending('submit-stock')" @click="submitStock">
            <span v-if="isPending('submit-stock')" class="spin"></span>保存
          </button>
        </div>
      </div>
    </div>

    <div v-if="supplierDialog" class="overlay" @click.self="supplierDialog = false">
      <div class="modal">
        <div class="modal-h"><b>新增供应商</b><button class="x" @click="supplierDialog = false"><svg viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path d="M18 6 6 18M6 6l12 12" /></svg></button></div>
        <div class="modal-b">
          <div class="field"><label>名称</label><input v-model="supplierForm.name" type="text" /></div>
          <div class="frow2">
            <div class="field"><label>主营分类</label><input v-model="supplierForm.category" type="text" /></div>
            <div class="field"><label>采购周期（天）</label><input v-model.number="supplierForm.lead_time" type="number" min="1" /></div>
          </div>
          <div class="frow2">
            <div class="field"><label>联系人</label><input v-model="supplierForm.contact" type="text" /></div>
            <div class="field"><label>联系电话</label><input v-model="supplierForm.phone" type="text" /></div>
          </div>
        </div>
        <div class="modal-f">
          <button class="btn" @click="supplierDialog = false">取消</button>
          <button class="btn primary" :disabled="isPending('submit-supplier')" @click="submitSupplier">
            <span v-if="isPending('submit-supplier')" class="spin"></span>保存
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
