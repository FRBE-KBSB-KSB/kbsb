<template>
  <v-container>
    <h1>{{ page.title }}</h1>
    <nuxt-content :document="page" />
  </v-container>
</template>

<script>
export default {

  layout: 'default',

  data () {
    return {
      page__nl: {},
      page__fr: {},
      page__de: {},
      page__en: {},
      tab: 0
    }
  },

  async fetch () {
    this.page__nl = await this.$content('pages', 'youth', 'international-youth_nl').fetch()
    this.page__fr = await this.$content('pages', 'youth', 'international-youth_fr').fetch()
    this.page__de = await this.$content('pages', 'youth', 'international-youth_de').fetch()
    this.page__de = await this.$content('pages', 'youth', 'international-youth_en').fetch()
  },

  head: {
    title: 'Internationale jeugdcompetities | Compétitions internationales de la jeunesse',
    link: [
      {
        rel: 'stylesheet',
        href:
          'https://fonts.googleapis.com/css?family=Roboto:100,300,400,500,700,900'
      },
      {
        rel: 'stylesheet',
        href: 'https://fonts.googleapis.com/css?family=Material+Icons'
      },
      {
        rel: 'stylesheet',
        href:
          'https://cdn.jsdelivr.net/npm/@mdi/font@latest/css/materialdesignicons.min.css'
      },
      { rel: 'favicon', href: 'favicon.ico' }
    ],
    meta: [
      { charset: 'utf-8' },
      { name: 'viewport', content: 'width=device-width, initial-scale=1' },
      { hid: 'home', name: 'description', content: 'Meta description' }
    ],
    script: [
      {
        src: 'https://apis.google.com/js/platform.js',
        async: true,
        defer: true
      }
    ]
  },
  computed: {
    page () { return this['page__' + this.$i18n.locale] }
  }
}
</script>
