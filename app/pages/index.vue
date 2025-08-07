<template>
  <div class="h-full flex flex-col items-center justify-center px-6 text-center space-y-10">
    <div class="bg-gradient-to-r from-[var(--ui-color-primary-700)] to-[var(--ui-color-primary-300)] bg-clip-text text-transparent animate-gradient text-5xl font-bold">
      Cloud-Synchronized Chronometers
    </div>

    <div class="max-w-xl space-y-4 text-gray-700 dark:text-gray-300">
      <p>
        Create a <strong>shared chronometer page</strong> for your event. You'll get:
      </p>
      <ul class="list-disc list-inside text-left">
        <li><strong>Private link</strong> to control and manage all chronometers</li>
        <li><strong>Public link</strong> to display read-only chronometers on any screen</li>
        <li>Perfect for in-person events, or remote coordination</li>
        <li>Each page can contain one or multiple chronometers</li>
      </ul>
    </div>

    <UButton
        icon="i-lucide-circle-plus"
        size="xl"
        color="primary"
        variant="solid"
        loading-auto
        @click="create_page"
    >
      Create Your Chronometer Page
    </UButton>

    <div class="text-sm text-gray-400">
      No login, payment or ads. Now and forever.
    </div>
  </div>
</template>

<script setup lang="ts">
import {check_status} from "~/utils";

const backendUrl = useRuntimeConfig().public.backendUrl;
const toast = useToast();

async function create_page() {
  await check_status(fetch(backendUrl + "/page/new", { method: "POST" }), "Something went wrong while trying to create a page.").then(async r => {
    toast.add({
      title: "Success!",
      description: "Page created successfully.",
      color: "success",
      icon: "i-lucide-check-circle",
    });
    const data = await r.json();
    await navigateTo("/" + data.edit_link);
  });
}
</script>

<style scoped>
@keyframes gradient-x {
  0%, 100% {
    background-position: left center;
  }
  50% {
    background-position: right center;
  }
}
.animate-gradient {
  background-size: 200% 200%;
  animation: gradient-x 5s ease infinite;
}
</style>
