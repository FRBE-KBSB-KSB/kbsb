import vuetify, { transformAssetUrls } from 'vite-plugin-vuetify'

export default defineNuxtConfig({
  app: {
    head: {
      link: [
        {
          rel: 'stylesheet',
          href: '/css/kbsb.css',
        },
      ],
    },
  },

  build: {
    transpile: ['vuetify'],
  },

  css: [
    'vuetify/lib/styles/main.sass',
    '@mdi/font/css/materialdesignicons.min.css',
  ],

  devtools: {
    timeline: {
      enabled: true
    }
  },

  experimental: {
    payloadExtraction: false,
  },

  googleSignIn: {
    clientId: '658290412135-ti3t11ovj5q2g10t4mla66r4m8orc2ev.apps.googleusercontent.com',
  },

  modules: [
    '@pinia/nuxt',
    'nuxt-vue3-google-signin',
    async (options, nuxt) => {
      nuxt.hooks.hook('vite:extendConfig',
        config => config.plugins.push(vuetify())
      )
    },
  ],

  nitro: {
    prerender: {
      crawlLinks: true,
      failOnError: false,
    }
  },

  runtimeConfig: {
    public: {
      apiUrl: process.env.API_URL || 'http://localhost:8000/',
      statamicurl: process.env.STATAMIC_URL || 'http://localhost:8000/',
      repo_branch: 'master',
    },
  },

  vite: {
    vue: {
      template: {
        transformAssetUrls
      }
    }
  },

  compatibilityDate: '2024-09-02',
})