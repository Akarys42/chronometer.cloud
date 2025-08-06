// https://nuxt.com/docs/api/configuration/nuxt-config
import tailwindcss from "@tailwindcss/vite";


export default defineNuxtConfig({
    ssr: false,
    modules: ['@nuxt/ui'],
    css: ['~/assets/css/main.css'],
    runtimeConfig: {
        public: {
            backendUrl: process.env.NODE_ENV === 'production' ? 'TBD' : 'http://localhost:8000',
            websocketBackendUrl: process.env.NODE_ENV === 'production' ? 'TBD' : 'ws://localhost:8000',
        }
    },
    nitro: {
        prerender: {
            autoSubfolderIndex: false
        }
    },
    vite: {
        plugins: [
            tailwindcss(),
        ],
    },
})
