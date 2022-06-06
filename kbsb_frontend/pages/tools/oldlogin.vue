<template>
  <v-container>
    <v-row align="start">
      <v-col cols="12" md="6" offset-md="3" lg="6" offset-lg="3">
        <v-card>
          <v-card-title>
            <v-icon large>
              mdi-account
            </v-icon>
            <label class="headline ml-3">Login</label>
            <v-spacer />
          </v-card-title>
          <v-divider />
          <v-card-text>
              <v-text-field
                v-model="login.idnumber"
                label="Idnumber"
              />
              <v-text-field
                v-model="login.password"
                xs="12"
                lg="6"
                label="Password"
                type="password"
              />
          </v-card-text>
          <v-card-actions>
            <v-spacer />
            <v-btn @click="dologin()">
              Submit
            </v-btn>
          </v-card-actions>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import Vue from 'vue'

export default {
  layout: 'default',

  data () {
    return {
      login: {},
      url: this.$route.query.url
    }
  },

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
      { rel: 'favicon', href: 'favicon.ico' }
    ],
    meta: [
      { charset: 'utf-8' },
      { name: 'viewport', content: 'width=device-width, initial-scale=1' },
      { hid: 'home', name: 'description', content: 'Meta description' }
    ]
  },

  methods: {


    dologin () {
      const returnUrl = this.url ? this.url.replaceAll("__","/") : '/'
      this.$api.old.login({
        idnumber: this.login.idnumber,
        password: this.login.password
      }).then(
        (reply) => {
          this.$store.commit('oldlogin/update', reply.data)
          this.$router.push(returnUrl)
        },
        (reply) => {
          console.log('failed login', reply)
        }
      )
    }
  }
}
</script>

<style>


</style>
