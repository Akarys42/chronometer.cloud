<template>
  <div class="h-full flex flex-col items-center justify-center px-6 text-center space-y-10">
    <div class="bg-gradient-to-r from-[var(--ui-color-primary-700)] to-[var(--ui-color-primary-300)] bg-clip-text text-transparent animate-gradient text-5xl font-bold">
      {{ $t("general.title") }}
    </div>

    <div class="max-w-xl space-y-4 text-gray-700 dark:text-gray-300">
      <i18n-t keypath="index.features.intro.text" tag="p">
        <strong>{{ $t("index.features.intro.strong") }}</strong>
      </i18n-t>
      <ul class="list-disc list-inside text-left">
        <li><strong>{{ $t("index.features.private_link.name") }}</strong>{{ $t("index.features.private_link.text") }}</li>
        <li><strong>{{ $t("index.features.public_link.name") }}</strong>{{ $t("index.features.public_link.text") }}</li>
        <li>{{ $t("index.features.usage") }}</li>
        <li>{{ $t("index.features.flexibility") }}</li>
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
      {{ $t("index.button_create") }}
    </UButton>

    <div class="text-sm text-gray-400">
      {{ $t("index.disclaimer") }}
    </div>
  </div>
</template>

<script setup lang="ts">
import {check_status} from "~/utils";

const backendUrl = useRuntimeConfig().public.backendUrl;
const toast = useToast();
const i18n = useI18n();

async function create_page() {
  await check_status(fetch(backendUrl + "/page/new", { method: "POST", headers: {"User-Locale": i18n.locale.value} }), $t("index.toast.create.error")).then(async r => {
    toast.add({
      title: $t("index.toast.create.success.title"),
      description: $t("index.toast.create.success.description"),
      color: "success",
      icon: "i-lucide-check-circle",
    });
    const data = await r.json();
    await navigateTo("/" + data.edit_link);
  });
}

useSeoMeta({
  title: "Cloud-Synchronized Chronometers",
  description: "Create and share synchronized chronometers for your events. Perfect for in-person or remote coordination.",
  ogTitle: "Cloud-Synchronized Chronometers",
  ogDescription: "Create and share synchronized chronometers for your events. Perfect for in-person or remote coordination.",
})
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
