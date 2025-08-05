<script setup>
const config = useRuntimeConfig()
const posts = await $fetch(config.public.backendUrl)
</script>

<template>
  <div>
    <h1>See our awesome posts underneath!</h1>
    <ul>
      <li v-for="post in posts" :key="post.id">
        {{ post.content }}
      </li>
    </ul>
  </div>
</template>
