<template>
  <div class="grid grid-cols-6 gap-2 p-4">
    <div
        v-for="[color, bg] in colors"
        :key="color"
        class="rounded ring-offset-2 transition-all aspect-square w-8"
        :class="[
          bg,
          isSelected(color) ? 'ring-2' : 'ring-0'
        ]"
    >
      <UButton
          square
          variant="ghost"
          class="w-full h-full bg-opacity-0"
          @click="$emit('update:modelValue', color)"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
const props = defineProps<{
  modelValue: string | null
}>()

const colors = [
  ["red", "bg-red-500"],
  ["rose", "bg-rose-500"],
  ["pink", "bg-pink-500"],
  ["fuchsia", "bg-fuchsia-500"],
  ["purple", "bg-purple-500"],
  ["indigo", "bg-indigo-500"],
  ["blue", "bg-blue-500"],
  ["cyan", "bg-cyan-500"],
  ["teal", "bg-teal-500"],
  ["emerald", "bg-emerald-500"],
  ["green", "bg-green-500"],
  ["lime", "bg-lime-500"],
  ["yellow", "bg-yellow-500"],
  ["amber", "bg-amber-500"],
  ["orange", "bg-orange-500"],
];

const isSelected = (color: string | undefined) => props.modelValue === color
</script>
