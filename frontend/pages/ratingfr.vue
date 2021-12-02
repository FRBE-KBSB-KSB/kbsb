<template>
  <v-container>
    <app-root />
  </v-container>
</template>

<script>
export default {
  layout: 'default',

  head: {
    title: 'Partners',
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
      {
        rel: 'stylesheet',
        href: 'https://api.frbe-kbsb-ksb.be/static/fr-BE/styles.css'
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
      },
      {
        src: 'https://api.frbe-kbsb-ksb.be/static/fr-BE/runtime.js',
        defer: true
      },
      {
        src: 'https://api.frbe-kbsb-ksb.be/static/fr-BE/polyfills.js',
        defer: true
      },
      {
        src: 'https://api.frbe-kbsb-ksb.be/static/fr-BE/main.js',
        defer: true
      }
    ]
  }
}
</script>
