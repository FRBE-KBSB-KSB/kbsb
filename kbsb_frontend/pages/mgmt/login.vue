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
            <v-col cols="12">
              <g-signin-button
                :params="googleSignInParams"
                @success="onSignInSuccess"
                @error="onSignInError"
              />
            </v-col>
            <v-divider />
            <v-col cols="12">
              <v-text-field
                v-model="login.username"
                xs="12"
                lg="4"
                label="Username"
              />
              <v-text-field
                v-model="login.password"
                xs="12"
                lg="6"
                label="Password"
                type="password"
              />
            </v-col>
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
import GSignInButton from 'vue-google-signin-button'
Vue.use(GSignInButton)

export default {
  layout: 'mgmt',

  data () {
    return {
      login: {},
      googleSignInParams: {
        client_id: process.env.google_client_id
      }
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

    onSignInSuccess (googleUser) {
      const idToken = googleUser.getAuthResponse().id_token
      this.$api.root.login({
        logintype: 'google',
        token: idToken
      }).then(
        (resp) => {
          this.$store.commit('token/update', resp.data)
          this.$router.push('/mgmt/pagelist')
        },
        (error) => {
          const resp = error.response
          console.log('failed login', resp.data.detail)
        }
      )
    },

    onSignInError (error) {
      console.log('Google login failed', error)
    },

    dologin () {
      this.$api.root.login({
        logintype: 'email',
        username: this.login.username,
        password: this.login.password
      }).then(
        (data) => {
          this.$store.commit('token/update', data.obj)
          this.$router.push('/mgmt/pagelist')
        },
        (data) => {
          console.log('failed login', data)
        }
      )
    }
  }
}
</script>

<style>
.g-signin-button {
   height: 46px;
   width: 191px;
   background-image: url('/img/btn_google_signin_light_normal_web.png');
}

.g-signin-button:hover {
   background-image: url('/img/btn_google_signin_light_focus_web.png');
}

</style>
