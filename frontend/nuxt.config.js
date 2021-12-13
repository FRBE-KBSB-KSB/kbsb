export default {

  axios: {
    proxy: true
  },

  build: {
    extend (config, { loaders }) {
      config.module.rules.push({
        test: /\.ya?ml$/,
        type: 'json', // Required by Webpack v4
        use: 'yaml-loader'
      })
    }
  },

  buildModules: ['@nuxtjs/vuetify'],

  components: true,

  css: [],

  head: {
    link: [{ rel: 'icon', type: 'image/x-icon', href: '/favicon.ico' }],
    meta: [
      { charset: 'utf-8' },
      { name: 'viewport', content: 'width=device-width, initial-scale=1' },
      { hid: 'description', name: 'description', content: '' }
    ],
    titleTemplate: '%s - KBSB - FRBE - KSB',
    title: 'KBSB'
  },

  i18n: {
    baseUrl: process.env.I18N_URL || '',
    lazy: true,
    locales: [
      { code: 'nl', file: 'nl.js' },
      { code: 'fr', file: 'fr.js' },
      { code: 'de', file: 'de.js' },
      { code: 'en', file: 'en.js' }
    ],
    langDir: 'lang/',
    strategy: 'prefix',
    defaultLocale: 'nl',
    vueI18n: {
      silentTranslationWarn: false,
      silentFallbackWarn: true
    }
  },

  markdownit: {
    html: true
  },

  modules: [
    '@nuxtjs/axios',
    '@nuxtjs/i18n',
    '@nuxtjs/markdownit',
    '@nuxt/content',
    ['nuxt-vuex-localstorage', { localStorage: ['token'] }]
  ],

  plugins: [{ src: '~plugins/api', ssr: false }],

  proxy: {
    '/api/': 'http://localhost:8000'
  },

  publicRuntimeConfig: {
    axios: {
      browserBaseURL: process.env.BROWSER_BASE_URL
    },
    VALIDATIION_FORM: process.env.VALIDATIION_FORM || true
  },

  target: 'static',

  vuetify: {
    customVariables: ['~/assets/variables.scss'],
    theme: {
      light: true
    }
  }

}
