// https://nuxt.com/docs/api/configuration/nuxt-config
import tailwindcss from "@tailwindcss/vite";


export default defineNuxtConfig({
    ssr: false,
    modules: ['@nuxt/ui'],
    css: ['~/assets/css/main.css'],
    runtimeConfig: {
        public: {
            backendUrl: process.env.NODE_ENV === 'production' ? 'https://api.chronometer.cloud' : 'http://localhost:8000',
            websocketBackendUrl: process.env.NODE_ENV === 'production' ? 'wss://api.chronometer.cloud' : 'ws://localhost:8000',
        }
    },
    app: {
        head: {
            title: 'Chronometers.cloud | Cloud-synchronized chronometers',
            htmlAttrs: {
                lang: 'en',
            },
            link: [
                { rel: 'icon', type: 'image/x-icon', href: '/favicon.ico' },
            ]
        }
    },
    nitro: {
        preset: "cloudflare_module",
        cloudflare: {
            deployConfig: true,
            nodeCompat: true
        },
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
