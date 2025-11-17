<template>
  <UButton square icon="i-lucide-copy" variant="ghost" class="ml-1" size="xs" color="neutral" @click="do_copy" />
</template>
<script setup>
const props = defineProps({
  text: {
    type: String,
    required: true,
  },
})
const toast = useToast();

function do_copy() {
  navigator.clipboard.writeText(props.text).then(() => {
    toast.add({
      title: $t("copy.toast.success.title"),
      description: $t("copy.toast.success.description"),
      color: "success",
      icon: "i-lucide-copy-check",
    });
  }).catch(() => {
    toast.add({
      title: $t("copy.toast.error.title"),
      description: $t("copy.toast.error.description"),
      color: "error",
      icon: "i-lucide-alert-triangle",
    });
  });
}
</script>
