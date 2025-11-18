<template>
  <UApp>
    <NuxtLoadingIndicator />
    <div class="flex flex-col min-h-screen">
      <header class="border-b border-gray-200 dark:border-gray-800 bg-black/15">
        <UContainer class="relative flex items-center justify-center md:justify-start py-4">
          <NuxtLink to="/">
            <Logo class="h-15" />
          </NuxtLink>
          <UButton class="absolute right-5 top-5 invisible md:visible" :icon="isDark ? 'i-lucide-moon' : 'i-lucide-sun'" size="xl" variant="outline" color="neutral" @click="isDark = !isDark"/>

          <UDropdownMenu class="absolute right-18 top-5 invisible md:visible" :items="langs">
            <UButton icon="i-lucide-globe" size="xl" variant="outline" color="neutral" @click=""/>
          </UDropdownMenu>
        </UContainer>
      </header>

      <div class="flex grow">
        <UContainer class="py-8">
          <NuxtPage />
        </UContainer>
      </div>

      <footer class="border-t border-gray-200 dark:border-gray-800 bg-black/20">
        <UContainer class="flex flex-col items-center justify-center gap-4 py-6 text-sm text-gray-500 dark:text-gray-400">
          <p>{{ $t("footer.author") }}</p>
          <p>{{ $t("footer.call_to_action.text") }}<a target="_blank" class="underline" href="https://paypal.me/ambrebertucci">{{ $t("footer.call_to_action.link") }}</a></p>
        </UContainer>
    </footer>
    </div>
  </UApp>
</template>

<script setup lang="ts">
import { Logo } from '#components';

const colorMode = useColorMode()
const toast = useToast()
const { setLocale } = useI18n()

const isDark = computed({
  get() {
    return colorMode.value === 'dark'
  },
  set(_isDark) {
    colorMode.preference = _isDark ? 'dark' : 'light'
  }
})

function set_locale(lang: string) {
  setLocale(lang as any)
  localStorage.setItem("locale", lang)
}

const langs = [
  {
    label: 'English',
    icon: 'i-circle-flags-us',
    onClick: () => {
      set_locale("en")
    }
  },
  {
    label: 'Français',
    icon: 'i-circle-flags-fr',
    onClick: () => {
      set_locale("fr")
    }
  },
  {
    label: 'Español',
    icon: 'i-circle-flags-es',
    onClick: () => {
      set_locale("es")
    }
  }
]

window.addEventListener("visibilitychange", () => {
  toast.clear()
})
</script>
