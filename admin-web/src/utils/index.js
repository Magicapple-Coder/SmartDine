export function formatMoney(value) {
  const num = Number(value ?? 0)
  return `¥${num.toFixed(2)}`
}

export function formatDateTime(value) {
  if (!value) return '-'
  return new Date(value).toLocaleString('zh-CN', { hour12: false })
}
