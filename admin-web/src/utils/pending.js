import { reactive } from 'vue'

export function usePending() {
  const keys = reactive(new Set())

  function isPending(key) {
    return keys.has(key)
  }

  async function run(key, fn) {
    keys.add(key)
    try {
      return await fn()
    } finally {
      keys.delete(key)
    }
  }

  return { isPending, run }
}
