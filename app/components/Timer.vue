<template>
  <component
    :is="permissions === 'edit' ? UContextMenu : 'div'"
    v-bind="permissions === 'edit' ? { items: context_menu_items, class: 'mb-8' } : {}"
  >
    <UCollapsible default-open :unmount-on-hide="false" class="flex flex-col gap-2" ref="component">
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
          @dblclick="() => {
            if (permissions === 'edit') {
              is_renaming = true;
            }
          }"
      />

      <template #content>
        <div class="flex mb-4 flex-col md:flex-row relative">
          <div v-if="permissions === 'edit'" class="flex flex-row justify-center md:justify-start md:flex-col">
            <UButton loading-auto v-if="!timer.is_paused" icon="i-lucide-circle-pause" size="xl" variant="ghost" color="neutral" @click="pause_timer">{{ $t("timer.action.pause") }}</UButton>
            <UButton loading-auto v-if="timer.is_paused" icon="i-lucide-circle-play" size="xl" variant="ghost" color="neutral" @click="start_timer">{{ $t("timer.action.start") }}</UButton>
            <UButton loading-auto v-if="timer.is_paused" icon="i-lucide-timer-reset" size="xl" variant="ghost" color="neutral" @click="reset_timer">{{ $t("timer.action.reset") }}</UButton>
            <UButton loading-auto icon="i-lucide-menu" size="xl" variant="ghost" color="neutral" @click="() => { are_extra_actions_opened = true }">{{ $t("timer.more") }}</UButton>
          </div>

          <TimeDisplay :time="remainingTime" :paused="timer.is_paused && progress > 0" />

          <UButton
              v-if="permissions === 'public'"
              icon="i-lucide-maximize-2"
              size="md"
              color="neutral"
              variant="ghost"
              class="invisible md:visible absolute top-2 right-2 z-10 transition-opacity"
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
  </component>

  <USlideover v-model:open="is_renaming" :title="$t('timer.rename.title')">
    <template #body>
      <div class="space-y-4">
        <UFormField label="New name" size="xl" required>
          <UInput v-model="new_name" :placeholder="$t('timer.rename.placeholder')" icon="i-lucide-text-cursor-input" @keydown.enter="rename_timer" />
        </UFormField>

        <UButton loading-auto icon="i-lucide-save" size="xl" :disabled="new_name.length === 0" @click="rename_timer">{{ $t("timer.rename.button_rename") }}</UButton>
      </div>
    </template>
  </USlideover>

  <USlideover v-model:open="are_extra_actions_opened" :title="$t('timer.other_actions')">
    <template #body>
      <div class="flex flex-col">
        <UButton loading-auto icon="i-lucide-edit" size="xl" variant="ghost" color="neutral" @click="() => {
          is_renaming = true;
          are_extra_actions_opened = false;
        }">{{ $t("timer.action.rename") }}</UButton>

        <UButton loading-auto icon="i-lucide-trash-2" size="xl" variant="ghost" color="error" @click="async () => {
          await delete_timer();
          are_extra_actions_opened = false;
        }">{{ $t("timer.action.delete") }}</UButton>

        <UButton class="md:hidden" icon="i-lucide-square-mouse-pointer" size="xl" variant="ghost" @click="() => {
          is_remote_mode = true
          are_extra_actions_opened = false
        }">{{ $t("timer.remote_mode.enter") }}</UButton>
      </div>
    </template>
  </USlideover>

  <UModal fullscreen v-model:open="isFullscreen">
    <template #content>
      <div class="w-full h-full flex items-center justify-center flex-col">
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

  <UModal fullscreen v-model:open="is_remote_mode">
    <template #content>
      <div class="flex flex-col w-full h-full">
        <div class="flex items-center justify-center flex-col mt-5">
          <div class="flex flex-col gap-2">
            <h1 class="text-2xl font-bold leading-none tracking-tight text-gray-900 dark:text-white text-center grow">{{ timer.name }}</h1>
            <TimeDisplay class="max-h-fit" :time="remainingTime" :paused="timer.is_paused && progress > 0" />
            <UProgress v-model="progress" class="w-inherit" :max="1" :color="progress === 1 ? 'error' : 'primary'"/>
          </div>
        </div>

        <div class="flex flex-col grow items-center justify-evenly">
          <UButton class="w-fit rounded-full border-8" variant="subtle" color="neutral" size="xl" @click="async () => {
            if (timer.is_paused) {
              await start_timer();
            } else {
              await pause_timer();
            }
          }">
            <UIcon :name="timer.is_paused ? 'i-lucide-play' : 'i-lucide-pause'" class="size-50 m-8" />
          </UButton>
          <UButton class="w-fit rounded-full border-8" variant="subtle" color="neutral" size="xl" @click="reset_timer">
            <UIcon name="i-lucide-rotate-ccw" class="size-50 m-8" />
          </UButton>
        </div>

        <div class="flex items-center justify-center mb-5">
          <UButton icon="i-lucide-x" size="xl" variant="subtle" color="neutral" @click="is_remote_mode = false">
            {{ $t("timer.remote_mode.exit") }}
          </UButton>
        </div>
      </div>
    </template>
  </UModal>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, computed, useTemplateRef } from 'vue'
import type { ContextMenuItem } from '@nuxt/ui'
import {check_status} from "~/utils";
import {UContextMenu} from "#components";

type TimerType = {
  unpaused_time: null | number,
  remaining_duration: number,
  is_paused: boolean,
  name: string,
  full_duration: number,
  real_time_delta: number,
}

const props = defineProps<{
  timer: TimerType,
  permissions: "public" | "edit",
  link: string,
  timer_number: number,
  real_time_delta: number,
}>();

const backendUrl = useRuntimeConfig().public.backendUrl;
const toast = useToast();
const component = useTemplateRef("component");

const is_renaming = ref(false);
const are_extra_actions_opened = ref(false);
const new_name = ref(props.timer.name);

const isFullscreen = ref(false);
const showFullscreenButton = ref(true);
let hideTimer: ReturnType<typeof setTimeout> | null = null;

const is_remote_mode = ref(false);

const context_menu_items: ContextMenuItem[] = [
  {
    label: $t('timer.action.start_pause'),
    icon: 'i-lucide-circle-play',
    kbds: ['s'],
    async onSelect() {
      if (props.timer.is_paused) {
        await start_timer();
      } else {
        await pause_timer();
      }
    }
  },
  {
    label: $t('timer.action.reset'),
    icon: 'i-lucide-timer-reset',
    kbds: ['r'],
    async onSelect() {
      await reset_timer();
    }
  },
  {
    label: $t('timer.action.rename'),
    icon: 'i-lucide-edit',
    kbds: ['e'],
    onSelect() {
      is_renaming.value = true;
    },
  },
  {
    label: $t('timer.action.delete'),
    icon: 'i-lucide-trash-2',
    color: 'error',
    async onSelect() {
      await delete_timer()
    }
  }
]

async function perform_action(action: string, error: string, method: "POST" | "DELETE" = "POST") {
  const end = action.length > 0 ? `/${action}` : "";

  await check_status(fetch(`${backendUrl}/timer/${props.link}/${props.timer_number}${end}`, {
    method,
  }), error);
}

async function start_timer() {
  await perform_action("start",$t("timer.error.start"));
}

async function pause_timer() {
  await perform_action("pause",$t("timer.error.pause"));
}

async function reset_timer() {
  await perform_action("reset", $t("timer.error.reset"));
}

async function add_time(seconds: number) {
  await perform_action("add_time/" + seconds, $t("timer.error.add_time"));
}

async function rename_timer() {
  await perform_action("rename?name=" + encodeURIComponent(new_name.value), $t("timer.error.rename"));
  is_renaming.value = false;
}

async function delete_timer() {
  await perform_action("", $t("timer.error.delete"), "DELETE");
  toast.add({
    title: $t("timer.toast.delete.title"),
    description: $t("timer.toast.delete.description"),
    color: "success",
    icon: "i-lucide-check-circle",
  })
}

const remainingTime = ref(props.timer.remaining_duration)
let interval: ReturnType<typeof setInterval>

const updateRemainingTime = () => {
  const { is_paused, unpaused_time, remaining_duration } = props.timer

  if (is_paused || !unpaused_time) {
    remainingTime.value = remaining_duration
  } else {
    const elapsed = Date.now() / 1000 - unpaused_time
    remainingTime.value = remaining_duration - elapsed - (props.real_time_delta / 1000)
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
  return Math.max(0, Math.min(full > 0 ? ((full - remainingTime.value) / full) : 0, 1))
})

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

function is_hovering() {
  if (!component.value) return false;
  return component.value.$el.matches(":hover");
}

defineShortcuts({
  s: async () => {
    if (props.permissions !== "edit") return;
    if (!is_hovering()) return;
    if (props.timer.is_paused) {
      await start_timer();
    } else {
      await pause_timer();
    }
  },
  r: async () => {
    if (props.permissions !== "edit") return;
    if (!is_hovering()) return;
    await reset_timer();
  },
  e: () => {
    if (props.permissions !== "edit") return;
    if (!is_hovering()) return;
    is_renaming.value = true;
  },
})

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
