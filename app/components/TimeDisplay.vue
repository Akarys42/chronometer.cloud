<template>
  <div
      class="font-mono text-6xl md:text-9xl flex grow items-end justify-self-center justify-center gap-1 transition-colors duration-300"
      :class="{
      'text-red-600': isOvertime,
      'animate-blink': paused
    }"
  >
    <span>{{ sign }}{{ hours }}:{{ minutes }}:{{ seconds }}</span>
    <span class="text-3xl md:text-6xl opacity-70">.{{ fractional }}</span>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  time: number  // In seconds, can be negative
  paused?: boolean
}>()

const isOvertime = computed(() => props.time < 0)

const absTime = computed(() => Math.abs(props.time))

const hours = computed(() =>
    Math.floor(absTime.value / 3600).toString().padStart(2, '0')
)

const minutes = computed(() =>
    Math.floor((absTime.value % 3600) / 60).toString().padStart(2, '0')
)

const seconds = computed(() =>
    Math.floor(absTime.value % 60).toString().padStart(2, '0')
)

const fractional = computed(() =>
    Math.floor((absTime.value % 1) * 10).toString()
)

const sign = computed(() => (props.time < 0 ? '-' : ''))
</script>

<style scoped>
@keyframes blink {
  0%, 49% { opacity: 1; }
  50%, 100% { opacity: 0.8; }
}

.animate-blink {
  animation: blink 2s step-start infinite;
}
</style>
