<template>
  <UApp>
    <div class="flex flex-col min-h-screen">
      <header class="border-b border-gray-200 dark:border-gray-800 bg-black/15">
        <UContainer class="flex items-center justify-center md:justify-start py-4">
          <NuxtLink to="/">
            <Logo class="h-15" />
          </NuxtLink>
        </UContainer>
      </header>

      <div class="flex grow">
        <UContainer class="py-8">
          <NuxtPage />
        </UContainer>
      </div>

      <footer class="border-t border-gray-200 dark:border-gray-800 bg-black/20">
        <UContainer class="flex items-center justify-center gap-4 py-6 text-sm text-gray-500 dark:text-gray-400">
          <p>Made with &lt;3 by Ambre Bertucci</p>
        </UContainer>
    </footer>
    </div>
  </UApp>
</template>

<script setup lang="ts">
import { Logo } from '#components';
</script>
