<template>
  <v-container>
    <h1>Interclubs Manager</h1>
    <v-card>
      <v-card-title>
        Select the club
      </v-card-title>
      <v-card-text>
        <div>Start typing to filter (clubnumber or name)</div>
        <v-autocomplete
          v-model="idclub"
          :items="clubs"
          item-text="idclub"
          item-value="idclub"
          color="white"
          label="Club"
          filled
          dense
          @onchange="selectclub"
        >
          <template v-slot:item="data">
           {{ data.item.idclub}}: {{ data.item.name_short}} {{ data.item.name_long}}
          </template>
        </v-autocomplete>
      </v-card-text>
    </v-card>
    <h2 class="mt-2">Active club: {{ idclub }} </h2>
    <div class="elevation-2">

    <v-tabs v-model="tab">
      <v-tabs-slider color="green"></v-tabs-slider>
      <v-tab>Enrollment</v-tab>
      <v-tab>Venue</v-tab>
      <v-tab>Playerlist</v-tab>
      <v-tab>Planning</v-tab>
      <v-tab>Results</v-tab>
    </v-tabs>
    <v-tabs-items v-model="tab">
      <v-tab-item>
        <v-container>
          <h3>Enrollment</h3>
          <div v-if="!idclub">Please select a club to view the enrollment</div>

        </v-container>
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

  name: 'Clublist',

  layout: 'default',

  data () {
    return {
      activeclub: null,
      footerProps: {
        itemsPerPageOptions: [150, -1]
      },
      clubs: [],
      idclub: null,
      tab: null,
    }
  },

  computed: {
    oldlogin () { return this.$store.state.oldlogin.value },
  },

  mounted () {
    this.$store.commit('oldlogin/startup')
    if (!this.oldlogin.length) {
      this.gotoLogin()
    }
    this.getClubs()
  },

  methods: {

    async getClubs () {
      console.log('getClubs', this.oldlogin)
      try {
        const reply = await this.$api.club.get_c_clubs({
          token: this.oldlogin
        })
        console.log('reply', reply.data)
        this.clubs = reply.data.clubs
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
    }

  }

}
</script>

<style>
.lightgreyrow {
  color: #bbb;
}
</style>
