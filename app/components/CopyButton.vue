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

function do_copy() {
  navigator.clipboard.writeText(props.text).then(() => {
    const toast = useToast();
    toast.add({
      title: "Copied!",
      description: "The text has been copied to your clipboard.",
      color: "success",
      icon: "i-lucide-copy-check",
    });
  }).catch(() => {
    const toast = useToast();
    toast.add({
      title: "Error",
      description: "Failed to copy the text.",
      color: "error",
      icon: "i-lucide-alert-triangle",
    });
  });
}
</script>
