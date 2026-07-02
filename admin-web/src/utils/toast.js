import { reactive } from 'vue'

export const toastState = reactive({ items: [] })

let seq = 0

function push(message, type) {
  const id = ++seq
  toastState.items.push({ id, message, type })
  setTimeout(() => {
    const idx = toastState.items.findIndex((t) => t.id === id)
    if (idx !== -1) toastState.items.splice(idx, 1)
  }, 2600)
}

export const toast = {
  success(message) {
    push(message, 'ok')
  },
  error(message) {
    push(message, 'err')
  },
  info(message) {
    push(message, '')
  },
}
