<template>
  <v-container>
    <h1>Interclubs Manager</h1>
    <v-card>
      <v-card-title>
        Select the club
      </v-card-title>
      <v-card-text>
        <div>Start typing to filter (clubnumber or name)</div>
        <v-autocomplete v-model="idclub" :items="clubs" item-text="merged" item-value="idclub" color="green"
          label="Club" clearable @change="selectclub">
          <template v-slot:item="data">
            {{ data.item.merged }}
          </template>
        </v-autocomplete>
      </v-card-text>
    </v-card>
    <h2 class="mt-2">Active club: {{ activeclub.idclub }} {{ activeclub.name_short }}</h2>
    <div class="elevation-2">

      <v-tabs v-model="tab" color="green">
        <v-tabs-slider color="green"></v-tabs-slider>
        <v-tab>Enrollment</v-tab>
        <v-tab>Venue</v-tab>
        <v-tab>Playerlist</v-tab>
        <v-tab>Planning</v-tab>
        <v-tab>Results</v-tab>
      </v-tabs>
      <v-tabs-items v-model="tab">
        <v-tab-item>
          <InterclubEnrollment @interface="registerChildMethod" />
        </v-tab-item>
        <v-tab-item>
          <h3>Venue</h3>
          TODO
        </v-tab-item>
        <v-tab-item>
          <h3>Playerlist</h3>
          TODO
        </v-tab-item>
        <v-tab-item>
          <h3>Planning</h3>
          TODO
        </v-tab-item>
        <v-tab-item>
          <h3>Results</h3>
          TODO
        </v-tab-item>
      </v-tabs-items>
    </div>
  </v-container>
</template>

<script>

export default {

  name: 'Interclub',

  layout: 'default',

  data() {
    return {
      activeclub: {},
      childmethods: {},
      footerProps: {
        itemsPerPageOptions: [150, -1]
      },
      clubs: [],
      idclub: null,
      tab: null,
    }
  },

  computed: {
    logintoken() { return this.$store.state.oldlogin.value },
  },

  mounted() {
    this.$store.commit('oldlogin/startup')
    if (!this.logintoken.length) {
      this.gotoLogin()
    }
    this.getClubs()
  },

  methods: {

    registerChildMethod(child, method) {
      this.childmethods[child] = method
    },

    async getClubs() {
      try {
        const reply = await this.$api.club.get_c_clubs({
          token: this.logintoken
        })
        this.clubs = reply.data.clubs
        this.clubs.forEach(p => {
          p.merged = `${p.idclub}: ${p.name_short} ${p.name_long}`
        })
      } catch (error) {
        console.log('error', error)
        const reply = error.response
        console.error('getting get_c_clubs', reply)
        if (reply.status === 401) {
          this.gotoLogin()
        } else {
          this.$root.$emit('snackbar', { text: 'Getting clubs failed', reason: reply.data.detail })
        }
      }
    },

    gotoLogin() {
      this.$router.push('/tools/oldlogin?url=__tools__interclub')
    },

    selectclub() {
      console.log('selected ', this.idclub)
      if (!this.idclub) {
        this.activeclub = {}
      }
      else {
        this.clubs.forEach(c => {
          if (c.idclub == this.idclub) this.activeclub = c
        })
      }
      const getAnonEnrollment = this.childmethods.enrollment
      getAnonEnrollment(this.activeclub)
    }

  }

}
</script>

<style>
</style>
