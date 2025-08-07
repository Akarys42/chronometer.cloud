<template>
  <UFormField
      :label="label"
      :error="overLimit ? 'Maximum allowed time is 23:59:59' : undefined"
  >
    <UInput
        ref="input"
        v-model="displayValue"
        inputmode="numeric"
        maxlength="8"
        @keydown.prevent="onKeyDown"
        @input.prevent="onInput"
        @focus="moveCursorToEnd"
        @click="moveCursorToEnd"
        @blur="onBlur"
        size="xl"
        :ui="{
          root: 'w-fit',
          base: 'w-[11ch] font-mono text-6xl text-center tracking-widest leading-none caret-transparent',
        }"
    />
  </UFormField>
</template>

<script setup lang="ts">
import { ref, computed, nextTick } from 'vue'

const emit = defineEmits<{
  (e: 'update:modelValue', value: number): void
}>()

const props = defineProps<{
  modelValue: number // in seconds
  label?: string
}>()

const input = ref<HTMLInputElement | null>(null)
const digits = ref(getDigitsFromSeconds(props.modelValue, false)) // raw buffer

const MAX_SECONDS = 23 * 3600 + 59 * 60 + 59 // 86399

const displayValue = computed(() => formatDigits(digits.value))

const overLimit = computed(() => {
  return getSecondsFromDigits(digits.value, false) > MAX_SECONDS
})

// Desktop: key-based input logic
function onKeyDown(e: KeyboardEvent) {
  if (/^[0-9]$/.test(e.key)) {
    digits.value = (digits.value + e.key).slice(-6)
  } else if (e.key === 'Backspace') {
    digits.value = digits.value.slice(0, -1).padStart(6, '0')
  }

  updateModel()
}

// Mobile: input event logic (detect add/remove)
function onInput(e: Event) {
  const el = e.target as HTMLInputElement
  const raw = el.value.replace(/\D/g, '') // remove colons

  if (raw.length < 8) {
    // Backspace detected
    digits.value = digits.value.slice(0, -1).padStart(6, '0');
  } else {
    // New digit input
    const newChar = raw.slice(-1)
    if (/^\d$/.test(newChar)) {
      digits.value = (digits.value + newChar).slice(-6);
    }
  }

  el.value = formatDigits(digits.value)

  updateModel()
  moveCursorToEnd()
}

function updateModel() {
  const seconds = getSecondsFromDigits(digits.value, false)
  emit('update:modelValue', Math.min(seconds, MAX_SECONDS + 3600))
}

function onBlur() {
  const clamped = getSecondsFromDigits(digits.value, true)
  digits.value = getDigitsFromSeconds(clamped, false)
  emit('update:modelValue', clamped)
}

function moveCursorToEnd() {
  nextTick(() => {
    const el = input.value?.el?.querySelector('input') as HTMLInputElement | null
    if (el) {
      const len = el.value.length
      el.setSelectionRange(len, len)
    }
  })
}

function getDigitsFromSeconds(seconds: number, clamp = true): string {
  let h = Math.floor(seconds / 3600)
  let m = Math.floor((seconds % 3600) / 60)
  let s = seconds % 60

  if (clamp) {
    h = Math.min(h, 23)
    m = Math.min(m, 59)
    s = Math.min(s, 59)
  }

  return (
      h.toString().padStart(2, '0') +
      m.toString().padStart(2, '0') +
      s.toString().padStart(2, '0')
  )
}

function getSecondsFromDigits(digits: string, clamp = true): number {
  const padded = digits.padStart(6, '0')
  let h = parseInt(padded.slice(0, 2), 10)
  let m = parseInt(padded.slice(2, 4), 10)
  let s = parseInt(padded.slice(4, 6), 10)

  if (clamp) {
    h = Math.min(h, 23)
    m = Math.min(m, 59)
    s = Math.min(s, 59)
  }

  return h * 3600 + m * 60 + s
}

function formatDigits(digits: string): string {
  const padded = digits.padStart(6, '0')
  return `${padded.slice(0, 2)}:${padded.slice(2, 4)}:${padded.slice(4, 6)}`
}
</script>
