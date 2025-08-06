<template>
    <div v-if="permissions !== 'loading'" class="flex flex-col">
      <div class="flex flex-col items-center gap-2 m-5">
        <div class="w-full relative">
          <h1 class="text-3xl font-bold leading-none tracking-tight text-gray-900 dark:text-white text-center grow">{{ page.name }}</h1>
          <UButton v-if="permissions === 'edit'" class="absolute right-0 top-0" icon="i-lucide-settings" size="xl" variant="outline" color="neutral" @click="open_settings"/>
        </div>
        <p v-if="page.timers.length === 0" class="text-xl font-bold leading-none tracking-tight text-gray-800 dark:text-gray-300">No timers currently created.</p>
      </div>
      <div v-for="(timer, timer_number) in page.timers">
        <Timer :timer="timer" :permissions="permissions" :link="route.params.link as string" :timer_number="timer_number" />
      </div>
      <USeparator class="m-2" />

      <div v-if="permissions === 'edit'" class="flex flex-col items-center justify-center gap-2 m-5">
        <h1 class="mb-4 text-3xl font-bold leading-none tracking-tight text-gray-900 dark:text-white">Create a new timer</h1>
        <DurationInput v-model="new_timer_duration"/>
        <UButton loading-auto class="m-2" size="xl" icon="i-lucide-alarm-clock-plus" :disabled="new_timer_duration === 0" @click="create_timer">Add</UButton>
      </div>
      <USeparator v-if="permissions === 'edit'" class="m-2" />

      <div class="flex flex-col grow items-center justify-center gap-2 m-5">
        <h1 class="mb-4 text-3xl font-bold leading-none tracking-tight text-gray-900 dark:text-white">Links</h1>
        <span>Public link: <ULink :to="'/' + page.public_link">/{{ page.public_link }}</ULink></span>
        <span v-if="permissions === 'edit'">Private editing link: <ULink :to="'/' + route.params.link">/{{ route.params.link }}</ULink></span>
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
import DurationInput from "~/components/DurationInput.vue";
import TailwindColorPicker from "~/components/TailwindColorPicker.vue";

const backendUrl = useRuntimeConfig().public.backendUrl;
const websocketBackendUrl = useRuntimeConfig().public.websocketBackendUrl;
const toast = useToast();
const route = useRoute();
const appConfig = useAppConfig();
const new_timer_duration = ref(300);
const are_settings_open = ref(false);
const new_page_name = ref("");
const new_page_color = ref<string | null>(null);

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
let websocket: WebSocket;
let retries = 10;

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

  await fetch(backendUrl + "/page/" + route.params.link + "/timers", {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({ duration: new_timer_duration.value })
  }).then(async r => {
    if (!r.ok) {
      toast.add({
        title: "Uh oh!",
        description: "Something went wrong while trying to create the timer.",
        color: "error",
        icon: "i-lucide-alert-triangle",
      });
      return;
    }

    toast.add({
      title: "Success!",
      description: "Timer created successfully.",
      color: "success",
      icon: "i-lucide-check-circle",
    });
  });
}

async function save_settings() {
  await fetch(backendUrl + "/page/" + route.params.link + "/settings", {
    method: "PUT",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      name: new_page_name.value,
      color: new_page_color.value
    })
  }).then(async r => {
    if (!r.ok) {
      toast.add({
        title: "Uh oh!",
        description: "Something went wrong while saving the page settings.",
        color: "error",
        icon: "i-lucide-alert-triangle",
      });
      return;
    }

    toast.add({
      title: "Success!",
      description: "Page settings saved successfully.",
      color: "success",
      icon: "i-lucide-check-circle",
    });

    are_settings_open.value = false;
  });
}

await callOnce(async () => {
  await fetch(backendUrl + "/page/" + route.params.link, {method: "GET"}).then(async r => {
    if (!r.ok) {
      toast.add({
        title: "Uh oh!",
        description: "Something went wrong while looking up the page.",
        color: "error",
        icon: "i-lucide-alert-triangle",
      })
      return
    }

    const data = await r.json();
    permissions.value = data.permissions;
    page.value = data.page;
    new_page_name.value = data.page.name;
    new_page_color.value = data.page.color;
  });
});

function connect_websocket() {
  websocket = new WebSocket(websocketBackendUrl + "/subscribe/" + route.params.link);

  websocket.onopen = () => {
    retries = 10;
    console.log("WebSocket connection established");
    toast.add({
      title: "Connected",
      description: "Successfully connected to the server. Timers will update in real-time.",
      color: "success",
      icon: "i-lucide-wifi",
    });
  };

  websocket.onclose = (e) => {
    console.log("WebSocket connection closed", e);
    toast.add({
      title: "Disconnected",
      description: "The connection to the server has been lost. Attempting to reconnect...",
      color: "warning",
      icon: "i-lucide-wifi-off",
    });
    if (retries-- <= 0) {
      toast.add({
        title: "Reconnection failed",
        description: "Unable to reconnect to the server after multiple attempts. Please refresh the page to try again.",
        color: "error",
        icon: "i-lucide-alert-triangle",
        duration: -1
      });
      return;
    } else {
      setTimeout(() => {
        connect_websocket();
      }, 2 ** (10 - retries) * 500); // Exponential backoff
    }
  };
  websocket.onmessage = async (event) => {
    page.value = JSON.parse(event.data);
  };
}

onMounted(() => {
  connect_websocket();
})

onBeforeUnmount(() => {
  if (websocket) {
    websocket.close();
  }
});
</script>
