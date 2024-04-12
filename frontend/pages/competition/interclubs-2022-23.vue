<template>
  <v-container>
    <h1>Interclubs 2022-23</h1>
    <v-tabs v-model="tab" color="green">
      <v-tabs-slider color="green"></v-tabs-slider>
      <v-tab>{{ $t('Announcements') }}</v-tab>
      <v-tab>{{ $t('Dates') }}</v-tab>
      <v-tab>{{ $t('Player list') }}</v-tab>
      <v-tab>{{ $t('Results') }}</v-tab>
      <v-tab>{{ $t('Standings') }}</v-tab>
    </v-tabs>
    <v-tabs-items v-model="tab">
      <v-tab-item>
        <InterclubAnnouncement />
      </v-tab-item>
      <v-tab-item>
        <InterclubDates />
      </v-tab-item>
      <v-tab-item>
        TO DO
      </v-tab-item>
      <v-tab-item>
        <InterclubResult />  
      </v-tab-item>
      <v-tab-item>
        TO DO
      </v-tab-item>
    </v-tabs-items>
  </v-container>
</template>

<script>

export default {

  layout: 'default',

  data() {
    return {
      tab: 0
    }
  },


  head: {
    title: 'Interclubs 2022-23',
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

}
</script>
