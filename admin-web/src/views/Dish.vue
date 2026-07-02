<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { toast } from '../utils/toast'
import { createDish, deleteDish, listAllDishes, setDishStatus, updateDish } from '../api/dish'
import { formatMoney } from '../utils'
import { usePending } from '../utils/pending'
import LoadingBlock from '../components/LoadingBlock.vue'

const { isPending, run } = usePending()

const dishes = ref([])
const activeCategory = ref('全部')
const keyword = ref('')
const dialogVisible = ref(false)
const editing = ref(null)
const form = reactive({ name: '', category: '', price: 0, tags: '', allergens: '' })
const pageLoading = ref(true)

// 分类 → emoji 映射（匹配原型）
const CATEGORY_EMOJI = {
  '面食': '🍜', '面': '🍜', '粉': '🍜',
  '炒菜': '🥘', '热菜': '🥘', '烧菜': '🍲', '煲': '🍲',
  '凉菜': '🍗', '冷菜': '🍗',
  '饮品': '🥤', '饮料': '🥤', '酒水': '🍺',
  '小吃': '🍢', '汤': '🥣', '甜品': '🍰',
}

function catEmoji(cat) {
  if (!cat) return '🍽'
  for (const [key, emoji] of Object.entries(CATEGORY_EMOJI)) {
    if (cat.includes(key)) return emoji
  }
  return '🍽'
}

function tagClass(tag) {
  if (!tag) return ''
  if (tag.includes('招牌')) return 'order'
  if (tag.includes('热销') || tag.includes('爆款')) return 'bad'
  if (tag.includes('新品')) return 'ana'
  if (tag.includes('辣')) return 'stock'
  return 'order'
}

const categories = computed(() => {
  const cats = [...new Set(dishes.value.map((d) => d.category))]
  return ['全部', ...cats]
})
const filtered = computed(() =>
  dishes.value.filter(
    (d) => (activeCategory.value === '全部' || d.category === activeCategory.value) && d.name.includes(keyword.value),
  ),
)

async function load() {
  pageLoading.value = true
  try {
    dishes.value = await listAllDishes()
  } finally {
    pageLoading.value = false
  }
}

function openCreate() {
  editing.value = null
  Object.assign(form, { name: '', category: '', price: 0, tags: '', allergens: '' })
  dialogVisible.value = true
}

function openEdit(dish) {
  editing.value = dish
  Object.assign(form, { name: dish.name, category: dish.category, price: dish.price, tags: dish.tags, allergens: dish.allergens })
  dialogVisible.value = true
}

async function submit() {
  if (!form.name || !form.category) {
    toast.error('请填写菜名和分类')
    return
  }
  await run('submit', async () => {
    if (editing.value) {
      await updateDish(editing.value.dish_id, form)
    } else {
      await createDish(form)
    }
    toast.success('已保存')
    dialogVisible.value = false
    load()
  })
}

async function toggleStatus(dish) {
  await run(`status-${dish.dish_id}`, async () => {
    await setDishStatus(dish.dish_id, dish.status === 1 ? 0 : 1)
    toast.success(dish.status === 1 ? '已下架' : '已上架')
    load()
  })
}

async function removeDish(dish) {
  if (!confirm(`确定删除菜品「${dish.name}」吗？`)) return
  await run(`delete-${dish.dish_id}`, async () => {
    await deleteDish(dish.dish_id)
    toast.success('已删除菜品')
    load()
  })
}

onMounted(load)
</script>

<template>
  <div>
    <div class="v-intro">
      <div>
        <h1>菜品管理</h1>
        <p>维护菜单在售菜品信息，支持新增、编辑、上下架与分类标签管理。</p>
      </div>
      <button class="btn primary" @click="openCreate">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-linecap="round"><path d="M12 5v14M5 12h14" /></svg>
        新增菜品
      </button>
    </div>

    <div class="toolbar">
      <div class="seg">
        <button v-for="c in categories" :key="c" :class="{ on: activeCategory === c }" @click="activeCategory = c">{{ c }}</button>
      </div>
      <div class="tb-grow"></div>
      <div class="search-box">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-linecap="round"><circle cx="11" cy="11" r="7" /><path d="m21 21-4.3-4.3" /></svg>
        <input v-model="keyword" placeholder="搜索菜品名称" />
      </div>
    </div>

    <table class="dtable">
      <thead>
        <tr><th>菜品</th><th>分类</th><th class="r">售价</th><th class="c">标签</th><th class="r">周销量</th><th class="c">状态</th><th class="r">操作</th></tr>
      </thead>
      <tbody>
        <tr v-if="pageLoading"><td colspan="7"><LoadingBlock /></td></tr>
        <template v-else>
          <tr v-for="d in filtered" :key="d.dish_id">
            <td>
              <div class="rowflex">
                <span class="thumb">{{ catEmoji(d.category) }}</span>
                <div>
                  <div class="cellnm">{{ d.name }}</div>
                  <div class="sub-c" v-if="d.allergens">过敏原：{{ d.allergens }}</div>
                </div>
              </div>
            </td>
            <td>{{ d.category }}</td>
            <td class="r tnum">{{ formatMoney(d.price) }}</td>
            <td class="c"><span v-if="d.tags" class="tag" :class="tagClass(d.tags)">{{ d.tags }}</span><span v-else class="sub-c">—</span></td>
            <td class="r tnum">{{ d.weekly_sales }}</td>
            <td class="c"><span class="tag" :class="d.status === 1 ? 'ok' : 'mut'">{{ d.status === 1 ? '在售' : '停售' }}</span></td>
            <td class="r">
              <div class="act-btns">
                <button class="ibtn" @click="openEdit(d)">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M12 20h9" /><path d="M16.5 3.5a2.1 2.1 0 0 1 3 3L7 19l-4 1 1-4z" /></svg>
                </button>
                <button class="ibtn" :disabled="isPending(`status-${d.dish_id}`)" @click="toggleStatus(d)" :title="d.status === 1 ? '下架' : '上架'">
                  <svg v-if="d.status === 1" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z" /><circle cx="12" cy="12" r="3" /></svg>
                  <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24" /><line x1="1" y1="1" x2="23" y2="23" /></svg>
                </button>
                <button class="ibtn danger" :disabled="isPending(`delete-${d.dish_id}`)" @click="removeDish(d)">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M3 6h18M8 6V4h8v2M6 6l1 14h10l1-14" /></svg>
                </button>
              </div>
            </td>
          </tr>
        </template>
      </tbody>
    </table>

    <div v-if="dialogVisible" class="overlay" @click.self="dialogVisible = false">
      <div class="modal">
        <div class="modal-h"><b>{{ editing ? '编辑菜品' : '新增菜品' }}</b><button class="x" @click="dialogVisible = false"><svg viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path d="M18 6 6 18M6 6l12 12" /></svg></button></div>
        <div class="modal-b">
          <div class="field"><label>菜品名称</label><input v-model="form.name" type="text" placeholder="例：麻婆豆腐" /></div>
          <div class="frow2">
            <div class="field"><label>分类</label><input v-model="form.category" type="text" placeholder="如：热菜" /></div>
            <div class="field"><label>售价</label><div class="in-prefix"><span>¥</span><input v-model.number="form.price" type="number" placeholder="0.00" /></div></div>
          </div>
          <div class="field"><label>标签<span class="opt">选填，逗号分隔</span></label><input v-model="form.tags" type="text" placeholder="畅销，辣，新品" /></div>
          <div class="field"><label>过敏原标注<span class="opt">选填，逗号分隔</span></label><input v-model="form.allergens" type="text" placeholder="花生，麸质，乳制品" /></div>
        </div>
        <div class="modal-f">
          <button class="btn" @click="dialogVisible = false">取消</button>
          <button class="btn primary" :disabled="isPending('submit')" @click="submit">
            <span v-if="isPending('submit')" class="spin"></span>保存菜品
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
