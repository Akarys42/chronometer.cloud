<template>
  <span>
    {{ text }}
    <ULink active :to="fragment">/{{ fragment }}</ULink>
    <CopyButton :text="full_link"/>
    <ShareButton :link="full_link"/>
    <QRButton :link="full_link"/>
  </span>
</template>
<script setup lang="ts">
import { CopyButton, ShareButton, QRButton } from "#components";

const props = defineProps<{
  text: string,
  fragment: string,
}>();
const request_url = useRequestURL();

const full_link = computed(() => {
  const url = new URL(request_url);
  return url.origin + '/' + props.fragment;
});
</script>
