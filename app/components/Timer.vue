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
          class="text-2xl"
          :ui="{
            label: 'justify-self-center grow',
          trailingIcon: 'group-data-[state=open]:rotate-180 transition-transform duration-200'
        }"

      />

      <template #content>
        <div class="flex mb-4 flex-col md:flex-row relative">
          <div v-if="permissions === 'edit'" class="flex flex-row justify-center md:justify-start md:flex-col">
            <UButton loading-auto v-if="!timer.is_paused" icon="i-lucide-circle-pause" size="xl" variant="ghost" color="neutral" @click="pause_timer">Pause</UButton>
            <UButton loading-auto v-if="timer.is_paused" icon="i-lucide-circle-play" size="xl" variant="ghost" color="neutral" @click="start_timer">Start</UButton>
            <UButton loading-auto v-if="timer.is_paused" icon="i-lucide-timer-reset" size="xl" variant="ghost" color="neutral" @click="reset_timer">Reset</UButton>
            <UButton loading-auto icon="i-lucide-menu" size="xl" variant="ghost" color="neutral" @click="() => { are_extra_actions_opened = true }">More</UButton>
          </div>

          <TimeDisplay :time="remainingTime" :paused="timer.is_paused && progress > 0" />

          <UButton
              v-if="permissions === 'public'"
              icon="i-lucide-maximize-2"
              size="md"
              color="neutral"
              variant="ghost"
              class="absolute top-2 right-2 z-10 transition-opacity"
              :class="{
                'opacity-100 duration-300': showFullscreenButton,
                'opacity-0 duration-1000': !showFullscreenButton
              }"
              @click="toggleFullscreen"
          />

          <div v-if="permissions === 'edit'" class="flex flex-row justify-center md:justify-start md:flex-col">
            <UButton size="xl" variant="ghost" color="neutral" @click="async () => add_time(30)">+ 30''</UButton>
            <UButton size="xl" variant="ghost" color="neutral" @click="async () => add_time(60)">+ 1'</UButton>
            <UButton size="xl" variant="ghost" color="neutral" @click="async () => add_time(300)">+ 5'</UButton>
          </div>
        </div>

        <UProgress v-model="progress" :max="1" :color="progress === 1 ? 'error' : 'primary'" size="lg"/>
      </template>
    </UCollapsible>
  </UContextMenu>

  <USlideover v-model:open="is_renaming" title="Renaming Chronometer">
    <template #body>
      <div class="space-y-4">
        <UFormField label="New name" size="xl" required>
          <UInput v-model="new_name" placeholder="Enter the name of the chronometer" icon="i-lucide-text-cursor-input" />
        </UFormField>

        <UButton loading-auto icon="i-lucide-save" size="xl" :disabled="new_name.length === 0" @click="rename_timer">Rename</UButton>
      </div>
    </template>
  </USlideover>

  <USlideover v-model:open="are_extra_actions_opened" title="Other Actions">
    <template #body>
      <div class="flex flex-col">
        <UButton loading-auto icon="i-lucide-edit" size="xl" variant="ghost" color="neutral" @click="() => {
          is_renaming = true;
          are_extra_actions_opened = false;
        }">Rename</UButton>
        <UButton loading-auto icon="i-lucide-trash-2" size="xl" variant="ghost" color="error" @click="async () => {
          await delete_timer();
          are_extra_actions_opened = false;
        }">Delete</UButton>
      </div>
    </template>
  </USlideover>

  <UModal fullscreen v-model:open="isFullscreen">
    <template #content>
      <div ref="fullscreen_content" class="w-full h-full flex items-center justify-center flex-col">
        <UButton
            v-if="permissions === 'public'"
            icon="i-lucide-maximize-2"
            size="md"
            color="neutral"
            variant="ghost"
            class="absolute top-2 right-2 z-10 transition-opacity"
            :class="{
                'opacity-100 duration-300': showFullscreenButton,
                'opacity-0 duration-1000': !showFullscreenButton
              }"
            @click="toggleFullscreen"
        />

        <div>
          <h1 class="text-7xl font-bold leading-none tracking-tight text-gray-900 dark:text-white text-center grow">{{ timer.name }}</h1>
          <TimeDisplay :is_big="true" class="max-h-fit" :time="remainingTime" :paused="timer.is_paused && progress > 0" />
          <UProgress v-model="progress" class="w-inherit" :max="1" :color="progress === 1 ? 'error' : 'primary'" size="lg"/>
        </div>
      </div>
    </template>
  </UModal>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, computed } from 'vue'
import type { ContextMenuItem } from '@nuxt/ui'
import {check_status} from "~/utils";

type TimerType = {
  unpaused_time: null | number,
  remaining_duration: number,
  is_paused: boolean,
  name: string,
  full_duration: number,
}

const context_menu_items = ref<ContextMenuItem[]>([
  {
    label: "Start / Pause",
    icon: 'i-lucide-circle-play',
    async onSelect() {
      if (props.timer.is_paused) {
        await start_timer();
      } else {
        await pause_timer();
      }
    }
  },
  {
    label: 'Reset',
    icon: 'i-lucide-timer-reset',
    async onSelect() {
      await reset_timer();
    }
  },
  {
    label: 'Rename',
    icon: 'i-lucide-edit',
    onSelect() {
      is_renaming.value = true;
    },
  },
  {
    label: 'Delete',
    icon: 'i-lucide-trash-2',
    color: 'error',
    async onSelect() {
      await delete_timer()
    }
  }
])

const props = defineProps<{
  timer: TimerType,
  permissions: "public" | "edit",
  link: string,
  timer_number: number
}>();
const backendUrl = useRuntimeConfig().public.backendUrl;
const is_renaming = ref(false);
const are_extra_actions_opened = ref(false);
const new_name = ref(props.timer.name);
const fullscreen_content = useTemplateRef<Element>("fullscreen_content");

async function perform_action(action: string, error: string, method: "POST" | "DELETE" = "POST") {
  const end = action.length > 0 ? `/${action}` : "";

  await check_status(fetch(`${backendUrl}/timer/${props.link}/${props.timer_number}${end}`, {
    method,
  }), error);
}

async function start_timer() {
  await perform_action("start","Something went wrong while trying to start the chronometer.")
}

async function pause_timer() {
  await perform_action("pause","Something went wrong while trying to pause the chronometer.")
}

async function reset_timer() {
  await perform_action("reset","Something went wrong while trying to reset the chronometer.")
}

async function add_time(seconds: number) {
  await perform_action("add_time/" + seconds, "Something went wrong while trying to add time to the chronometer.")
}

async function rename_timer() {
  await perform_action("rename?name=" + encodeURIComponent(new_name.value), "Something went wrong while trying to rename the chronometer.");
  is_renaming.value = false;
}

async function delete_timer() {
  await perform_action("", "Something went wrong while trying to delete the chronometer.", "DELETE");
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




const isFullscreen = ref(false);
const showFullscreenButton = ref(true);
let hideTimer: ReturnType<typeof setTimeout> | null = null;

function resetHideTimer() {
  showFullscreenButton.value = true;
  if (hideTimer) clearTimeout(hideTimer);
  hideTimer = setTimeout(() => {
    showFullscreenButton.value = false;
  }, 3000);
}

async function toggleFullscreen() {
  isFullscreen.value = !isFullscreen.value;

  requestAnimationFrame(async () => {
    if (isFullscreen.value) {
      await document.documentElement.requestFullscreen();
    } else {
      await document.exitFullscreen();
    }
  });

  resetHideTimer();
}

async function onFullscreenChange() {
  if (!document.fullscreenElement) {
    isFullscreen.value = false;
  }
}

onMounted(() => {
  window.addEventListener("mousemove", resetHideTimer);
  document.addEventListener("fullscreenchange", onFullscreenChange);
  resetHideTimer();
});
onUnmounted(() => {
  window.removeEventListener("mousemove", resetHideTimer);
  document.removeEventListener("fullscreenchange", onFullscreenChange);
  if (hideTimer) clearTimeout(hideTimer);
});
</script>
