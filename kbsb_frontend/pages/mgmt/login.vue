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
          <v-card-text>
            <v-col cols="12">
              <div>Login with your @frbe-kbsb-ksb.be account</div>
              <g-signin-button :params="googleSignInParams" @success="onSignInSuccess"
                @error="onSignInError" />
            </v-col>
          </v-card-text>
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

  data() {
    return {
      login: {},
      googleSignInParams: {
        client_id: process.env.google_client_id
      },
      url: this.$route.query.url
    }
  },

  head: {
    title: 'Login',
  },

  methods: {

    onSignInSuccess(googleUser) {
      const idToken = googleUser.getAuthResponse().id_token
      this.$api.root.login({
        logintype: 'google',
        token: idToken
      }).then(
        (resp) => {
          this.$store.commit('newlogin/update', resp.data)
          const returnUrl = this.url ? this.url.replaceAll("__", "/") : '/mgmt'
          this.$router.push(returnUrl)
        },
        (error) => {
          const resp = error.response
          console.log('failed login', resp.data.detail)
        }
      )
    },

    onSignInError(error) {
      console.log('Google login failed', error)
    },

    dologin() {
      this.$api.root.login({
        logintype: 'email',
        username: this.login.username,
        password: this.login.password
      }).then(
        (data) => {
          this.$store.commit('newlogin/update', data.obj)
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
