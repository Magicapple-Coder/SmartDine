<script setup>
import { onMounted, reactive, ref } from 'vue'
import { toast } from '../utils/toast'
import { createCampaign, createCoupon, deleteCampaign, deleteCoupon, listCampaigns, listCoupons } from '../api/marketing'
import { usePending } from '../utils/pending'
import LoadingBlock from '../components/LoadingBlock.vue'

const { isPending, run } = usePending()

const campaigns = ref([])
const coupons = ref([])
const pageLoading = ref(true)
const campaignDialog = ref(false)
const couponDialog = ref(false)
const campaignForm = reactive({ name: '', type: '优惠券', rule: '', period: '' })
const couponForm = reactive({ campaign_id: null, amount: 0, threshold: 0 })

async function load() {
  pageLoading.value = true
  try {
    campaigns.value = await listCampaigns()
    coupons.value = await listCoupons()
  } finally {
    pageLoading.value = false
  }
}

function couponsOf(campaignId) {
  return coupons.value.filter((c) => c.campaign_id === campaignId)
}

async function submitCampaign() {
  if (!campaignForm.name) {
    toast.error('请填写活动名称')
    return
  }
  await run('submit-campaign', async () => {
    await createCampaign(campaignForm)
    toast.success('已创建活动')
    campaignDialog.value = false
    load()
  })
}

function openCouponDialog(campaign) {
  Object.assign(couponForm, { campaign_id: campaign.campaign_id, amount: 0, threshold: 0 })
  couponDialog.value = true
}

async function submitCoupon() {
  await run('submit-coupon', async () => {
    await createCoupon(couponForm)
    toast.success('已创建优惠券')
    couponDialog.value = false
    load()
  })
}

async function removeCampaign(campaign) {
  if (!confirm(`确定删除活动「${campaign.name}」吗？其名下优惠券将一并删除。`)) return
  await run(`delete-campaign-${campaign.campaign_id}`, async () => {
    await deleteCampaign(campaign.campaign_id)
    toast.success('已删除活动')
    load()
  })
}

async function removeCoupon(coupon) {
  if (!confirm('确定删除该优惠券吗？')) return
  await run(`delete-coupon-${coupon.coupon_id}`, async () => {
    await deleteCoupon(coupon.coupon_id)
    toast.success('已删除优惠券')
    load()
  })
}

onMounted(load)
</script>

<template>
  <div>
    <div class="v-intro">
      <div>
        <h1>营销活动</h1>
        <p>管理优惠券、套餐与限时促销，跟踪领取与核销效果。</p>
      </div>
      <button class="btn primary" @click="campaignDialog = true">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-linecap="round"><path d="M12 5v14M5 12h14" /></svg>
        创建活动
      </button>
    </div>

    <div class="sec-label"><h2>优惠券</h2><div class="ln"></div></div>
    <LoadingBlock v-if="pageLoading" />
    <template v-else>
      <div v-if="coupons.length === 0" class="empty-hint">暂无优惠券，先创建一个活动后在下方添加优惠券</div>
      <div class="grid-2">
        <div v-for="c in coupons" :key="c.coupon_id" class="coupon">
          <div class="amt"><b>¥{{ c.amount }}</b><span>满 {{ c.threshold }} 可用</span></div>
          <div class="info">
            <div class="nm">{{ campaigns.find((x) => x.campaign_id === c.campaign_id)?.name || '活动 #' + c.campaign_id }}</div>
            <div class="cond">优惠券 #{{ c.coupon_id }}</div>
            <div class="stats">
              <div>已领取<b>{{ c.claimed }}</b></div>
              <div>已核销<b>{{ c.redeemed }}</b></div>
              <div>核销率<b>{{ c.claimed ? Math.round((c.redeemed / c.claimed) * 100) : 0 }}%</b></div>
            </div>
            <button
              class="btn sm"
              style="margin-top: 10px; color: var(--bad); border-color: var(--bad)"
              :disabled="isPending(`delete-coupon-${c.coupon_id}`)"
              @click="removeCoupon(c)"
            >
              <span v-if="isPending(`delete-coupon-${c.coupon_id}`)" class="spin"></span>删除
            </button>
          </div>
        </div>
      </div>
    </template>

    <div class="sec-label"><h2>活动 / 套餐</h2><div class="ln"></div></div>
    <table class="dtable">
      <thead><tr><th>活动名称</th><th>类型</th><th>规则</th><th>周期</th><th class="r">已售/核销</th><th class="r">操作</th></tr></thead>
      <tbody>
        <tr v-if="pageLoading"><td colspan="6"><LoadingBlock /></td></tr>
        <template v-else>
          <tr v-for="c in campaigns" :key="c.campaign_id">
            <td class="cellnm">{{ c.name }}</td>
            <td><span class="tag order">{{ c.type }}</span></td>
            <td class="sub-c">{{ c.rule || '—' }}</td>
            <td class="sub-c">{{ c.period || '—' }}</td>
            <td class="r tnum">{{ c.sold }}</td>
            <td class="r">
              <div class="act-btns">
                <button class="btn sm" @click="openCouponDialog(c)">新建优惠券</button>
                <button
                  class="btn sm"
                  style="color: var(--bad); border-color: var(--bad)"
                  :disabled="isPending(`delete-campaign-${c.campaign_id}`)"
                  @click="removeCampaign(c)"
                >
                  <span v-if="isPending(`delete-campaign-${c.campaign_id}`)" class="spin"></span>删除
                </button>
              </div>
            </td>
          </tr>
        </template>
      </tbody>
    </table>

    <div v-if="campaignDialog" class="overlay" @click.self="campaignDialog = false">
      <div class="modal">
        <div class="modal-h"><b>创建活动</b><button class="x" @click="campaignDialog = false"><svg viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path d="M18 6 6 18M6 6l12 12" /></svg></button></div>
        <div class="modal-b">
          <div class="field"><label>活动名称</label><input v-model="campaignForm.name" type="text" placeholder="如：周末满50减10" /></div>
          <div class="field">
            <label>类型</label>
            <select v-model="campaignForm.type">
              <option value="优惠券">优惠券</option>
              <option value="套餐">套餐</option>
              <option value="限时促销">限时促销</option>
            </select>
          </div>
          <div class="field"><label>规则<span class="opt">选填</span></label><input v-model="campaignForm.rule" type="text" placeholder="如：满50减10" /></div>
          <div class="field"><label>活动周期<span class="opt">选填</span></label><input v-model="campaignForm.period" type="text" placeholder="如：2026-07-01~2026-07-31" /></div>
        </div>
        <div class="modal-f">
          <button class="btn" @click="campaignDialog = false">取消</button>
          <button class="btn primary" :disabled="isPending('submit-campaign')" @click="submitCampaign">
            <span v-if="isPending('submit-campaign')" class="spin"></span>保存
          </button>
        </div>
      </div>
    </div>

    <div v-if="couponDialog" class="overlay" @click.self="couponDialog = false">
      <div class="modal">
        <div class="modal-h"><b>新建优惠券</b><button class="x" @click="couponDialog = false"><svg viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path d="M18 6 6 18M6 6l12 12" /></svg></button></div>
        <div class="modal-b">
          <div class="frow2">
            <div class="field"><label>面额</label><div class="in-prefix"><span>¥</span><input v-model.number="couponForm.amount" type="number" /></div></div>
            <div class="field"><label>满减门槛</label><div class="in-prefix"><span>¥</span><input v-model.number="couponForm.threshold" type="number" /></div></div>
          </div>
        </div>
        <div class="modal-f">
          <button class="btn" @click="couponDialog = false">取消</button>
          <button class="btn primary" :disabled="isPending('submit-coupon')" @click="submitCoupon">
            <span v-if="isPending('submit-coupon')" class="spin"></span>保存
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
