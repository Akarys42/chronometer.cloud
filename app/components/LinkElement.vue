<template>
  <span>
    {{ text }}
    <ULink active :to="fragment">/{{ fragment }}</ULink>
    <CopyButton :text="full_link"/>
  </span>
</template>
<script setup lang="ts">
import { CopyButton } from "#components";

const props = defineProps<{
  text: string,
  fragment: string,
}>();

const full_link = computed(() => {
  const url = new URL(window.location.href);
  return url.origin + '/' + props.fragment;
});
</script>
