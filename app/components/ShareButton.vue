<template>
  <UButton square icon="i-lucide-share-2" variant="ghost" class="ml-1" size="xs" color="neutral" @click="do_share" />
</template>
<script setup>
const props = defineProps({
  link: {
    type: String,
    required: true,
  },
})
const toast = useToast();

function do_share() {
  if (navigator.share) {
    navigator.share({
      url: props.link,
    }).catch(() => {
      toast.add({
        title: "Error",
        description: "Failed to share the page.",
        color: "error",
        icon: "i-lucide-alert-triangle",
      });
    });
  } else {
    toast.add({
      title: "Share not supported",
      description: "Your browser does not support the Web Share API.",
      color: "warning",
      icon: "i-lucide-info",
    });
  }
}
</script>
