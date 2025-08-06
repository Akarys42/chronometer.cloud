<template>
  <div>
    <h1>Index page</h1>
    <UButton icon="i-lucide-circle-plus" size="xl" color="primary" variant="solid" loading-auto @click="create_page">Create page</UButton>
  </div>
</template>
<script setup lang="ts">
const backendUrl = useRuntimeConfig().public.backendUrl;
const toast = useToast()

async function create_page() {
  await fetch(backendUrl + "/page/new", { method: "POST" }).then(async r => {
    if (!r.ok) {
      toast.add({
        title: "Uh oh!",
        description: "Something went wrong while trying to create a page.",
        color: "error",
        icon: "i-lucide-alert-triangle",
      })
      return
    }

    toast.add({
      title: "Success!",
      description: "Page created successfully.",
      color: "success",
      icon: "i-lucide-check-circle",
    });
    const data = await r.json();
    await navigateTo("/" + data.edit_link)
  });
}
</script>
