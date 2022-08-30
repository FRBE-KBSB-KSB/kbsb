<template>
  <v-container>
    Management FRBE KBSB KSB
    <ul>
      <li><a href='/mgmt/pagelist'>News articles</a></li>
      <li><a href='/mgmt/interclub'>Interclub Manager</a></li>
      <li><a href='/mgmt/club'>Club Manager</a></li>
    </ul>
    <div class="mt-2">
      <v-btn @click="logout">Logout</v-btn>
    </div>
  </v-container>
</template>

<script>
export default {
  layout: 'mgmt',

  computed: {
    logintoken() { return this.$store.state.newlogin.value },
  },

  head: {
    title: 'Management',
  },

  methods: {

    gotoLogin() {
      this.$router.push('/mgmt/login?url=__mgmt')
    },

    logout() {
      this.$store.commit('newlogin/update', null)
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
