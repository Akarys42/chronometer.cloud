<template>
  <UApp>
    <NuxtLoadingIndicator />

    <UDashboardGroup class="!overflow-visible !relative">
      <UDashboardPanel>
        <div class="flex flex-col min-h-screen">
          <header class="border-b border-gray-200 dark:border-gray-800 bg-black/15">
            <UContainer class="relative flex items-center justify-between md:justify-start py-4">
              <NuxtLink to="/">
                <Logo class="h-15" />
              </NuxtLink>

              <UDashboardSidebarToggle icon="i-lucide-settings-2" class="md:hidden" variant="subtle" size="xl" />

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
      </UDashboardPanel>

      <UDashboardSidebar v-model:open="mobile_sidebar_open" class="md:!hidden" toggle-side="right">
        <template #header>
          <h2 class="text-xl font-medium">{{ $t("settings.title") }}</h2>
        </template>

        <div class="flex flex-col justify-between content-center flex-wrap h-full">
          <div class="w-fit flex flex-col gap-4 mt-4">
            <UDropdownMenu :items="langs">
              <UButton icon="i-lucide-globe" size="xl" variant="outline" color="neutral" @click="">
                {{ $t("settings.language") }}
              </UButton>
            </UDropdownMenu>

            <UButton :icon="isDark ? 'i-lucide-moon' : 'i-lucide-sun'" size="xl" variant="outline" color="neutral" @click="isDark = !isDark">
              {{ $t("settings.color") }}
            </UButton>
          </div>

          <p v-if="open_debug_panel !== undefined" class="underline text-muted text-center mb-5" @click="open_debug">
            {{ $t("settings.debug") }}
          </p>
        </div>
      </UDashboardSidebar>
    </UDashboardGroup>
  </UApp>
</template>

<script setup lang="ts">
import { Logo } from '#components';
import {addWindowEventListener} from "~/utils";

const colorMode = useColorMode()
const toast = useToast()
const { setLocale } = useI18n()

const mobile_sidebar_open = ref(false);
const open_debug_panel = useState<undefined | (() => void)>('open-debug-panel', undefined);

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
  },
  {
    label: 'Italiano',
    icon: 'i-circle-flags-it',
    onClick: () => {
      set_locale("it")
    }
  }
]

function open_debug() {
  if (open_debug_panel.value) {
    mobile_sidebar_open.value = false;
    open_debug_panel.value();
  }
}

addWindowEventListener("visibilitychange", () => {
  toast.clear()
})
</script>
