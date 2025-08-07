<template>
  <div v-if="permissions !== 'loading'" class="flex flex-col">
    <div class="flex flex-col items-center gap-2 m-5">
      <div class="w-full flex flex-col items-center md:relative">
        <h1 class="text-2xl md:text-3xl font-bold leading-none tracking-tight text-gray-900 dark:text-white text-center grow">{{ page.name }}</h1>
        <UButton v-if="permissions === 'edit'" class="absolute right-0 top-0 invisible md:visible" icon="i-lucide-settings" size="xl" variant="outline" color="neutral" @click="open_settings"/>
        <UButton v-if="permissions === 'edit'" class="mt-3 w-fit visible md:invisible" icon="i-lucide-settings" variant="outline" color="neutral" @click="open_settings">Settings</UButton>
        <UTooltip :text="connection_status === 'disconnected' ? 'You are currently disconnected from the server. We\'re trying to reconnect you...' : 'You are currently disconnected from the server. Refresh the page to try again.'" :delay-duration="0" class="absolute left-0 top-0">
          <UIcon v-if="connection_status === 'disconnected' || connection_status === 'lost'" name="i-lucide-wifi-off" class="size-8 animate-pulsate" :class="connection_status === 'disconnected' ? 'text-warning' : 'text-error'" />
        </UTooltip>
      </div>
      <p v-if="page.timers.length === 0" class="mt-3 text-xl font-bold leading-none tracking-tight text-gray-800 dark:text-gray-300">No chronometer currently created.</p>
    </div>
    <div v-for="(timer, timer_number) in page.timers">
      <Timer :timer="timer" :permissions="permissions" :link="route.params.link as string" :timer_number="timer_number" />
    </div>
    <USeparator v-if="permissions === 'edit'" class="m-2" />

    <div v-if="permissions === 'edit'" class="flex flex-col items-center justify-center gap-2 m-5">
      <h1 class="mb-4 text-2xl md:text-3xl font-bold leading-none tracking-tight text-gray-900 dark:text-white">Create a new chronometer</h1>
      <DurationInput v-model="new_timer_duration"/>
      <UButton loading-auto class="m-2" size="xl" icon="i-lucide-alarm-clock-plus" :disabled="new_timer_duration === 0" @click="create_timer">Add</UButton>
    </div>
    <USeparator v-if="permissions === 'edit'" class="m-2" />

    <div v-if="permissions === 'edit'" class="flex flex-col grow items-center justify-center gap-2 m-5">
      <h1 class="mb-4 text-2xl md:text-3xl font-bold leading-none tracking-tight text-gray-900 dark:text-white">Links</h1>
      <LinkElement text="Private editing link:" :fragment="route.params.link as string"/>
      <LinkElement text="Public viewing link:" :fragment="page.public_link"/>
    </div>
  </div>

  <div v-else class="h-full">
    <div v-if="is_not_found" class="h-full flex flex-col items-center justify-center px-6 text-center space-y-10">
      <p>
        <span class="text-2xl">This chronometer page doesn't exist</span>
      </p>

      <ULink to="/">
        <UButton
            icon="i-lucide-arrow-left"
            size="xl"
            color="primary"
            variant="solid"
            loading-auto
        >
          Go Back
        </UButton>
      </ULink>
    </div>
    <div v-else>
      <USkeleton class="m-5 w-max-full h-20" />
      <USkeleton class="m-5 w-max-full h-60" />
      <USkeleton class="m-5 w-max-full h-60" />
    </div>
  </div>

  <USlideover v-model:open="are_settings_open" title="Page settings">
    <template #body>
      <div class="space-y-4">
        <UFormField label="Page name" size="xl" required>
          <UInput v-model="new_page_name" placeholder="Enter the name of the page" icon="i-lucide-text-cursor-input" />
        </UFormField>

        <UFormField label="Page color" size="xl" required>
          <TailwindColorPicker v-model:model-value="new_page_color" />
        </UFormField>

        <UButton loading-auto icon="i-lucide-save" size="xl" @click="save_settings" :disabled="new_page_name.length === 0">Save</UButton>
      </div>
    </template>
  </USlideover>
</template>

<script setup lang="ts">
import { DurationInput, TailwindColorPicker } from "#components";
import LinkElement from "~/components/LinkElement.vue";
import { check_status } from "~/utils";

const backendUrl = useRuntimeConfig().public.backendUrl;
const websocketBackendUrl = useRuntimeConfig().public.websocketBackendUrl;
const toast = useToast();
const route = useRoute();
const appConfig = useAppConfig();
const new_timer_duration = ref(300);
const are_settings_open = ref(false);
const new_page_name = ref("");
const new_page_color = ref<string | null>(null);
const websocket = ref<WebSocket | null>(null);
const connection_status = ref<"connected" | "disconnected" | "lost">("disconnected");
const is_not_found = ref(false);
let retries = 10;

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
    timers : [],
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
      title: "Invalid duration",
      description: "Please enter a valid duration greater than 0 seconds.",
      color: "error",
      icon: "i-lucide-alert-triangle",
    });
    return;
  }

  await check_status(
      fetch(backendUrl + "/page/" + route.params.link + "/timers", {
          method: "POST",
          headers: {
            "Content-Type": "application/json"
          },
          body: JSON.stringify({ duration: new_timer_duration.value })
      }),
      "Something went wrong while trying to create the chronometer."
  ).then(async r => {
    toast.add({
      title: "Success!",
      description: "Chronometer created successfully.",
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
          "Something went wrong while saving the page settings."
  ).then(async r => {
    toast.add({
      title: "Success!",
      description: "Page settings saved successfully.",
      color: "success",
      icon: "i-lucide-check-circle",
    });

    are_settings_open.value = false;
  });
}

function connect_websocket() {
  websocket.value = new WebSocket(websocketBackendUrl + "/subscribe/" + route.params.link);

  websocket.value.onopen = () => {
    retries = 10;
    connection_status.value = "connected";
    toast.add({
      title: "Connected",
      description: "Successfully connected to the server. Chronometers will update in real-time.",
      color: "success",
      icon: "i-lucide-wifi",
    });
  };

  websocket.value.onclose = (e) => {
    if (e.code === 1000) {
      // Normal closure
      return;
    }

    toast.add({
      title: "Disconnected",
      description: "The connection to the server has been lost. Attempting to reconnect...",
      color: "warning",
      icon: "i-lucide-wifi-off",
    });
    if (retries-- <= 0) {
      connection_status.value = "lost";
      toast.add({
        title: "Reconnection failed",
        description: "Unable to reconnect to the server after multiple attempts. Please refresh the page to try again.",
        color: "error",
        icon: "i-lucide-alert-triangle",
        duration: -1
      });
      return;
    } else {
      connection_status.value = "disconnected";
      setTimeout(() => {
        connect_websocket();
      }, 1.1 ** (10 - retries) * 1000); // Exponential backoff
    }
  };
  websocket.value.onmessage = async (event) => {
    page.value = JSON.parse(event.data);
  };
}

onMounted(async () => {
  await check_status(fetch(backendUrl + "/page/" + route.params.link, {method: "GET"}), "Something went wrong while looking up the page.", true).then(async r => {
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
})

onBeforeUnmount(() => {
  if (websocket.value) {
    websocket.value.close(1000);
  }
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
