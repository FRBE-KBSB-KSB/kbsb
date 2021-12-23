<template>
  <v-container>
    <h1>{{ page.title }}</h1>
    <v-container class="mt-1 markedcontent elevation-2">
      <v-tabs v-model="tab" light slider-color="deep-purple">
        <v-tab class="mx-2">
          NL
        </v-tab>
        <v-tab class="mx-2">
          FR
        </v-tab>
      </v-tabs>
      <v-tabs-items v-model="tab">
        <v-tab-item>
          <nuxt-content :document="pagenl" class="mt-3" />
        </v-tab-item>
        <v-tab-item>
          <nuxt-content :document="pagefr" class="mt-3" />
        </v-tab-item>
      </v-tabs-items>
    </v-container>
  </v-container>
</template>

<script>
export default {

  layout: 'default',

  async asyncData ({ $content, app }) {
    const page = await $content('pages', 'admin', `statutes_${app.i18n.locale}`).fetch()
    const pagenl = await $content('pages', 'admin', 'statutes_nl').fetch()
    const pagefr = await $content('pages', 'admin', 'statutes_fr').fetch()
    return {
      page, pagefr, pagenl
    }
  },

  data () {
    return {
      tab: 0
    }
  },

  head: {
    title: 'Statuten - Statutes',
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
  }
}
</script>
