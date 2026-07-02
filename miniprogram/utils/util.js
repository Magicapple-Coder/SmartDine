export function formatMoney(value) {
  return `¥${Number(value || 0).toFixed(2)}`
}

export function formatDateTime(value) {
  if (!value) return ''
  const d = new Date(value.replace(/-/g, '/'))
  const pad = (n) => String(n).padStart(2, '0')
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}`
}
