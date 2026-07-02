<script setup>
import { toastState } from '../utils/toast'
</script>

<template>
  <div class="toast-stack">
    <div v-for="t in toastState.items" :key="t.id" class="toast" :class="t.type">{{ t.message }}</div>
  </div>
</template>
