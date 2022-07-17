<template>
  <v-container>
    Management FRBE KBSB KSB
  </v-container>
</template>

<script>
export default {
  layout: 'mgmt',

  computed: {
    logintoken() { return this.$store.state.oldlogin.value },
  },

  head: {
    title: 'Management KBSB - FREB- KSB',
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

  methods: {

    gotoLogin() {
      this.$router.push('/mgmt/login?url=__mgmt__interclub')
    },

  },

  mounted() {
    this.$store.commit('newlogin/startup')
    if (!this.logintoken.length) {
      this.gotoLogin()
    }
  },

}
</script>
