<template>
  <v-container>
    <h1>Vademecum</h1>
    <p>
      Nederlandstalige versie dd 29-11-2021: <a href="/docs/vademecum_nl.pdf">vademecum_nl.pdf</a>
    </p>
    <p>La version en français est actuellement indisponible.  Nos excuses.</p>
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

  head: {
    title: 'Vademecum',
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
    ]
  }

}
</script>
