<template>
  <UApp>
    <div class="flex flex-col min-h-screen">
      <header class="border-b border-gray-200 dark:border-gray-800 bg-black/15">
        <UContainer class="relative flex items-center justify-center md:justify-start py-4">
          <NuxtLink to="/">
            <Logo class="h-15" />
          </NuxtLink>
          <UButton class="absolute right-5 top-5 invisible md:visible" :icon="isDark ? 'i-lucide-moon' : 'i-lucide-sun'" size="xl" variant="outline" color="neutral" @click="isDark = !isDark"/>
        </UContainer>
      </header>

      <div class="flex grow">
        <UContainer class="py-8">
          <NuxtPage />
        </UContainer>
      </div>

      <footer class="border-t border-gray-200 dark:border-gray-800 bg-black/20">
        <UContainer class="flex flex-col items-center justify-center gap-4 py-6 text-sm text-gray-500 dark:text-gray-400">
          <p>Made with &lt;3 by Ambre Bertucci</p>
          <p>Enjoying the tool? <a target="_blank" class="underline" href="https://paypal.me/ambrebertucci">Buy me a coffee</a></p>
        </UContainer>
    </footer>
    </div>
  </UApp>
</template>

<script setup lang="ts">
import { Logo } from '#components';

const colorMode = useColorMode()

const isDark = computed({
  get() {
    return colorMode.value === 'dark'
  },
  set(_isDark) {
    colorMode.preference = _isDark ? 'dark' : 'light'
  }
})
</script>
