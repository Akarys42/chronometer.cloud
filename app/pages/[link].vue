<template>
  <div v-if="permissions !== 'loading'" class="flex flex-col">
    <div class="flex flex-col items-center gap-2 m-5">
      <div class="w-full flex flex-col items-center relative">
        <h1 class="text-4xl mb-2 md:mb-5 md:text-5xl font-bold leading-none tracking-tight text-gray-900 dark:text-white text-center grow">{{ page.name }}</h1>
        <UButton v-if="permissions === 'edit'" class="absolute right-0 top-0 invisible md:visible" icon="i-lucide-settings" size="xl" variant="outline" color="neutral" @click="open_settings"/>
        <UButton v-if="permissions === 'edit'" class="mt-3 w-fit visible md:invisible md:absolute" icon="i-lucide-settings" variant="outline" color="neutral" @click="open_settings">{{ $t("page.button_settings") }}</UButton>
        <UTooltip :text="connection_status === 'disconnected' ? $t('page.status.reconnecting') : $t('page.status.disconnected')" :delay-duration="0" class="absolute left-0 bottom-0 md:top-0">
          <UIcon v-if="connection_status === 'disconnected' || connection_status === 'lost'" name="i-lucide-wifi-off" class="size-8 animate-pulsate" :class="connection_status === 'disconnected' ? 'text-warning' : 'text-error'" />
        </UTooltip>
      </div>
      <p v-if="page.timers.length === 0" class="mt-3 text-xl font-bold leading-none tracking-tight text-gray-800 dark:text-gray-300">{{ $t("page.no_chronometer") }}</p>
    </div>
    <div v-for="(timer, timer_number) in page.timers">
      <Timer :timer="timer" :permissions="permissions" :link="route.params.link as string" :timer_number="timer_number" :real_time_delta="real_time_delta" />
    </div>
    <USeparator v-if="permissions === 'edit'" class="m-2" />

    <div v-if="permissions === 'edit'" class="flex flex-col items-center justify-center gap-2 m-5">
      <h1 class="mb-4 text-2xl md:text-3xl font-bold leading-none tracking-tight text-gray-900 dark:text-white">{{ $t("page.new_chronometer.title") }}</h1>
      <DurationInput v-model="new_timer_duration"/>
      <UButton loading-auto class="m-2" size="xl" icon="i-lucide-alarm-clock-plus" :disabled="new_timer_duration === 0" @click="create_timer">{{ $t("page.new_chronometer.button_add") }}</UButton>
    </div>
    <USeparator v-if="permissions === 'edit'" class="m-2" />

    <div v-if="permissions === 'edit'" class="flex flex-col grow items-center justify-center gap-2 m-5">
      <h1 class="mb-4 text-2xl md:text-3xl font-bold leading-none tracking-tight text-gray-900 dark:text-white">{{ $t("page.links.title") }}</h1>
      <LinkElement :text="$t('page.links.private')" :fragment="route.params.link as string"/>
      <LinkElement :text="$t('page.links.public')" :fragment="page.public_link"/>
    </div>
  </div>

  <div v-else class="h-full">
    <div v-if="is_not_found" class="h-full flex flex-col items-center justify-center px-6 text-center space-y-10">
      <p>
        <span class="text-2xl">{{ $t("page.not_found.title") }}</span>
      </p>

      <ULink to="/">
        <UButton
            icon="i-lucide-arrow-left"
            size="xl"
            color="primary"
            variant="solid"
            loading-auto
        >
          {{ $t("page.not_found.button_back") }}
        </UButton>
      </ULink>
    </div>
    <div v-else>
      <USkeleton class="m-5 w-max-full h-20"/>
      <USkeleton class="m-5 w-max-full h-60"/>
      <USkeleton class="m-5 w-max-full h-60"/>
    </div>
  </div>

  <USlideover v-model:open="are_settings_open" :title="$t('page.settings.title')">
    <template #body>
      <div class="space-y-4">
        <UFormField :label="$t('page.settings.name')" size="xl" required>
          <UInput v-model="new_page_name" :placeholder="$t('page.settings.name_placeholder')" icon="i-lucide-text-cursor-input" />
        </UFormField>

        <UFormField :label="$t('page.settings.color')" size="xl" required>
          <TailwindColorPicker v-model:model-value="new_page_color" />
        </UFormField>

        <UButton loading-auto icon="i-lucide-save" size="xl" @click="save_settings" :disabled="new_page_name.length === 0">
          {{ $t('page.settings.button_save') }}
        </UButton>
      </div>
    </template>
  </USlideover>

  <UDrawer v-model:open="show_debug">
    <template #content>
      <div class="space-y-2 m-2 mb-10">
        <div>Real time delta: {{ real_time_delta }}ms</div>
        <div>RTT: {{ average_rtt }}ms</div>
        <div>Permissions: {{ permissions }}</div>
        <div>Connection status: {{ connection_status }}</div>
        <div>Locale: {{ i18n.locale.value }}</div>
        <div>New timer duration: {{ new_timer_duration }}s</div>
        <div>Remote version: {{ remote_version }}</div>
        <div>Local version: {{ local_version }}</div>
      </div>
    </template>
  </UDrawer>
</template>

<script setup lang="ts">
import {DurationInput, TailwindColorPicker} from "#components";
import LinkElement from "~/components/LinkElement.vue";
import {check_status} from "~/utils";
import {ChronoSocket} from "~/socket";
import {TimeSync} from "~/time_sync";

const backendUrl = useRuntimeConfig().public.backendUrl;
const websocketBackendUrl = useRuntimeConfig().public.websocketBackendUrl;
const toast = useToast();
const route = useRoute();
const appConfig = useAppConfig();
const i18n = useI18n();
const open_debug_panel = useState<undefined | (() => void)>('open-debug-panel', undefined)

const new_timer_duration = ref(300);
const are_settings_open = ref(false);
const new_page_name = ref("");
const new_page_color = ref<string | null>(null);
const connection_status = ref<"connected" | "disconnected" | "lost">("disconnected");
const is_not_found = ref(false);
const real_time_delta = ref(0);

const average_rtt = ref(0);
const show_debug = ref(false);
const remote_version = useState("unknown");
const local_version = useRuntimeConfig().public.gitSha;

let websocket: ChronoSocket | null;
let disconnect_toast_id: string | number | null;
let lost_toast_id: string | number | null;
let refresh_real_time_delta_interval_id: number | null;

watch(new_page_color, (newColor) => {
  if (newColor) {
    appConfig.ui.colors.primary = newColor;
  }
});

watch(are_settings_open, () => {
  new_page_name.value = page.value.name;
  new_page_color.value = page.value.color;
  appConfig.ui.colors.primary = page.value.color;
});

const permissions = useState<"loading" | "public" | "edit">("permissions", () => "loading");
const page = useState<{ timers: any[], public_link: string, name: string, color: string }>("page", () => {
  return {
    timers: [],
    public_link: "loading",
    name: "Loading...",
    color: "indigo"
  }
});

function open_settings() {
  are_settings_open.value = true;
}

async function create_timer() {
  if (new_timer_duration.value <= 0) {
    toast.add({
      title: $t("page.toast.invalid_duration.title"),
      description: $t("page.toast.invalid_duration.description"),
      color: "error",
      icon: "i-lucide-alert-triangle",
    });
    return;
  }

  await check_status(
      fetch(backendUrl + "/page/" + route.params.link + "/timers", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "User-Locale": i18n.locale.value,
        },
        body: JSON.stringify({duration: new_timer_duration.value})
      }),
      $t("page.toast.create.error")
  ).then(async r => {
    toast.add({
      title: $t("page.toast.create.success.title"),
      description: $t("page.toast.create.success.description"),
      color: "success",
      icon: "i-lucide-check-circle",
    });
  });
}

async function save_settings() {
  await check_status(
      fetch(backendUrl + "/page/" + route.params.link + "/settings", {
        method: "PUT",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          name: new_page_name.value,
          color: new_page_color.value
        })
      }),
      $t("page.toast.save.error")
  ).then(async r => {
    toast.add({
      title: $t("page.toast.save.success.title"),
      description: $t("page.toast.save.success.description"),
      color: "success",
      icon: "i-lucide-check-circle",
    });

    are_settings_open.value = false;
  });
}

function connect_websocket() {
  websocket = new ChronoSocket(
      websocketBackendUrl + "/subscribe/" + route.params.link,
      {
        onConnected(socket: ChronoSocket) {
          if (disconnect_toast_id) {
            toast.remove(disconnect_toast_id)
            disconnect_toast_id = null;
          }
          if (lost_toast_id) {
            toast.remove(lost_toast_id);
            lost_toast_id = null;
          }

          connection_status.value = "connected";

          if (!socket.isFirstConnection) {
            toast.add({
              title: $t("page.toast.connect.title"),
              description: $t("page.toast.connect.description"),
              color: "success",
              icon: "i-lucide-wifi",
            });
          }
        },
        onMessage(event: MessageEvent) {
          page.value = JSON.parse(event.data);
        },
        onDisconnected(socket: ChronoSocket) {
          if (connection_status.value !== "disconnected") {
            disconnect_toast_id = toast.add({
              title: $t("page.toast.disconnect.title"),
              description: $t("page.toast.disconnect.description"),
              color: "warning",
              icon: "i-lucide-wifi-off",
              duration: -1
            }).id;
          }
          if (lost_toast_id) {
            toast.remove(lost_toast_id);
            lost_toast_id = null;
          }

          connection_status.value = "disconnected";
        },
        onLost(socket: ChronoSocket) {
          if (disconnect_toast_id) {
            toast.remove(disconnect_toast_id)
            disconnect_toast_id = null;
          }

          connection_status.value = "lost";

          lost_toast_id = toast.add({
            title: $t("page.toast.lost.title"),
            description: $t("page.toast.lost.description"),
            color: "error",
            icon: "i-lucide-alert-triangle",
            duration: -1,
            actions: [{
              icon: 'i-lucide-refresh-cw',
              label: $t('page.toast.lost.action_reconnect'),
              color: 'neutral',
              variant: 'outline',
              onClick: (e) => {
                e?.stopPropagation()
                socket.connect()
              }
            }]
          }).id;
        }
      }
  );
  websocket.connect();
}

window.addEventListener("visibilitychange", () => {
  if (document.visibilityState === "visible" && connection_status.value === "lost" && websocket) {
    websocket.connect()
  }
});

async function refresh_offset() {
  const sync = new TimeSync(websocketBackendUrl + "/time");
  real_time_delta.value = await sync.synchronize();
  average_rtt.value = sync.getAverageRTT();
}

onMounted(async () => {
  open_debug_panel.value = () => {
    show_debug.value = true;
  }

  await check_status(fetch(backendUrl + "/page/" + route.params.link, {method: "GET"}), $t("page.toast.not_found.description"), true).then(async r => {
    if (r.status === 404) {
      is_not_found.value = true;
    } else {
      const data = await r.json();
      permissions.value = data.permissions;
      page.value = data.page;
      new_page_name.value = data.page.name;
      new_page_color.value = data.page.color;
    }
  });

  if (!is_not_found.value) {
    connect_websocket();
  }

  await refresh_offset();
  refresh_real_time_delta_interval_id = window.setInterval(() => {
    refresh_offset();
  }, 60000); // Refresh every 60 seconds

  await fetch(backendUrl + "/version")
      .then(r => r.json())
      .then(r => {
        if (r.version) {
          remote_version.value = r.version;
        }
      })
})

onBeforeUnmount(() => {
  open_debug_panel.value = undefined;

  if (websocket) {
    websocket.close();
  }

  if (refresh_real_time_delta_interval_id) {
    clearInterval(refresh_real_time_delta_interval_id);
  }
});

defineShortcuts({
  "d-e": () => {
    show_debug.value = !show_debug.value;
  }
})

useHead({
  title: "Chronometers.cloud | Your Cloud-Synchronized Chronometers",
});
useSeoMeta({
  title: "Chronometers.cloud | Your Cloud-Synchronized Chronometers",
  description: "Create and share synchronized chronometers for your events. Perfect for in-person or remote coordination.",
  ogTitle: "Chronometers.cloud | Your Cloud-Synchronized Chronometers",
  ogDescription: "Create and share synchronized chronometers for your events. Perfect for in-person or remote coordination.",
});
</script>
<style scoped>
@keyframes pulsate {
  0%, 100% {
    transform: scale(1);
    opacity: 0.8;
  }
  50% {
    transform: scale(1.2);
    opacity: 1;
  }
}

.animate-pulsate {
  animation: pulsate 2s infinite;
}
</style>
