<template>
  <UContextMenu
      :items="permissions === 'edit' ? context_menu_items : []"
      class="mb-8"
  >
    <UCollapsible default-open :unmount-on-hide="false" class="flex flex-col gap-2">
      <UButton
          :label="timer.name"
          size="xl"
          color="neutral"
          variant="outline"
          trailing-icon="i-lucide-chevron-down"
          :ui="{
          trailingIcon: 'group-data-[state=open]:rotate-180 transition-transform duration-200'
        }"
          block
      />

      <template #content>
        <div class="flex mb-4">
          <div v-if="permissions === 'edit'" class="flex flex-col">
            <UButton loading-auto v-if="!timer.is_paused" icon="i-lucide-circle-pause" size="xl" variant="ghost" color="neutral" @click="pause_timer">Pause</UButton>
            <UButton loading-auto v-if="timer.is_paused" icon="i-lucide-circle-play" size="xl" variant="ghost" color="neutral" @click="start_timer">Start</UButton>
            <UButton loading-auto v-if="timer.is_paused" icon="i-lucide-timer-reset" size="xl" variant="ghost" color="neutral" @click="reset_timer">Reset</UButton>
          </div>

          <TimeDisplay :time="remainingTime" :paused="timer.is_paused" />

          <div v-if="permissions === 'edit'" class="flex flex-col">
            <UButton size="xl" variant="ghost" color="neutral" @click="async () => add_time(30)">+ 30''</UButton>
            <UButton size="xl" variant="ghost" color="neutral" @click="async () => add_time(60)">+ 1'</UButton>
            <UButton size="xl" variant="ghost" color="neutral" @click="async () => add_time(300)">+ 5'</UButton>
          </div>
        </div>

        <UProgress v-model="progress" :max="1" :color="progress === 1 ? 'error' : 'primary'" size="lg"/>
      </template>
    </UCollapsible>
  </UContextMenu>

  <USlideover v-model:open="is_renaming" title="Renaming Timer">
    <template #body>
      <div class="space-y-4">
        <UFormField label="New name" size="xl" required>
          <UInput v-model="new_name" placeholder="Enter the name of the timer" icon="i-lucide-text-cursor-input" />
        </UFormField>

        <UButton loading-auto icon="i-lucide-save" size="xl" :disabled="new_name.length === 0" @click="rename_timer">Rename</UButton>
      </div>
    </template>
  </USlideover>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, computed } from 'vue'
import type { ContextMenuItem } from '@nuxt/ui'

type TimerType = {
  unpaused_time: null | number,
  remaining_duration: number,
  is_paused: boolean,
  name: string,
  full_duration: number,
}

const context_menu_items = ref<ContextMenuItem[]>([
  {
    label: 'Rename',
    icon: 'i-lucide-edit',
    onSelect() {
      is_renaming.value = true;
    },
  },
  {
    label: "Start / Pause",
    icon: 'i-lucide-circle-play',
    onSelect() {
      if (props.timer.is_paused) {
        start_timer();
      } else {
        pause_timer();
      }
    }
  },
  {
    label: 'Reset',
    icon: 'i-lucide-timer-reset',
    onSelect() {
      reset_timer();
    }
  },
  {
    label: 'Delete',
    icon: 'i-lucide-trash-2',
    color: 'error',
    async onSelect() {
      await perform_action("", "Something went wrong while trying to delete the timer.", "DELETE");
    }
  }
])

const props = defineProps<{
  timer: TimerType,
  permissions: "public" | "edit",
  link: string,
  timer_number: number
}>();
const toast = useToast();
const backendUrl = useRuntimeConfig().public.backendUrl;
const is_renaming = ref(false);
const new_name = ref(props.timer.name);

async function perform_action(action: string, error: string, method: "POST" | "DELETE" = "POST") {
  await fetch(`${backendUrl}/timer/${props.link}/${props.timer_number}/${action}`, {
    method,
  }).then(async (response) => {
    if (!response.ok) {
      toast.add({
        title: "Uh oh!",
        description: error,
        color: "error",
        icon: "i-lucide-alert-triangle",
      })
    }
  });
}

async function start_timer() {
  await perform_action("start","Something went wrong while trying to start the timer.")
}

async function pause_timer() {
  await perform_action("pause","Something went wrong while trying to pause the timer.")
}

async function reset_timer() {
  await perform_action("reset","Something went wrong while trying to reset the timer.")
}

async function add_time(seconds: number) {
  await perform_action("add_time/" + seconds, "Something went wrong while trying to add time to the timer.")
}

async function rename_timer() {
  await perform_action("rename?name=" + encodeURIComponent(new_name.value), "Something went wrong while trying to rename the timer.");
  is_renaming.value = false;
}

const remainingTime = ref(props.timer.remaining_duration)
let interval: ReturnType<typeof setInterval>

const updateRemainingTime = () => {
  const { is_paused, unpaused_time, remaining_duration } = props.timer

  if (is_paused || !unpaused_time) {
    remainingTime.value = remaining_duration
  } else {
    const elapsed = Date.now() / 1000 - unpaused_time
    remainingTime.value = remaining_duration - elapsed
  }
}

onMounted(() => {
  updateRemainingTime()
  interval = setInterval(updateRemainingTime, 100)
})

onUnmounted(() => {
  clearInterval(interval)
})

const progress = computed(() => {
  const full = props.timer.full_duration
  return Math.min(full > 0 ? ((full - remainingTime.value) / full) : 0, 1)
})
</script>
