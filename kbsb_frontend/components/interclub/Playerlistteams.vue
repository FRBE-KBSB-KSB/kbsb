<template>
  <div>
    <h3>{{ $t('Titulars for the teams') }}</h3>
    <div v-for="(t,ix) in tt" :key="ix" class="my-3">
      <v-card v-if="t.nteams > 0" color="#f4f4f4">
        <v-card-title>
          {{ $t('Teams in division') }} {{ ix + 1 }}
        </v-card-title>
        <v-divider />
        <v-card-text>
          <div v-if="t.nteams == 1">
            {{ $t('Titulars for') }} {{ t.names[0]}}
            <ol>
              <li v-for="(pix, jx) in t.range" :key="jx">
                {{ first_name(pix) }} {{ last_name(pix) }}
              </li>
            </ol>
          </div>
          <div v-if="t.nteams > 1">
            <v-row v-for="(pix, jx) in t.range" :key="jx">
              <v-col cols="3">
                {{ first_name(pix)}} {{ last_name(pix)}}
              </v-col>
              <v-col cols="3">
                <v-select dense v-model="selmodel[pix]" label="Team" :items="t.names"
                  :hide-details="true" />
              </v-col>
            </v-row>
          </div>
        </v-card-text>
      </v-card>
    </div>
    <div class="mt-2">
      <v-btn color="green" class="white--text" @click="next">
        {{ $t('Continue') }}
      </v-btn>
      <v-btn @click="prev">
        {{ $t('Back') }}
      </v-btn>
    </div>
  </div>
</template>

<script>

function range(size, startAt = 0) {
  return [...Array(size || 0).keys()].map(i => i + startAt);
}


export default {

  data() {
    return {
      selmodel: []
    }
  },

  props: {
    club: Object,
  },

  computed: {
    step() {
      return this.$store.state.playerlist.step
    },
    players() {
      return this.$store.state.playerlist.players
    },
    teams() {
      return this.$store.state.playerlist.teams
    },
    tt() {
      const tt = [
        { nteams: this.teams.filter(x => x.division == 1).length, nplayers: 8 },
        { nteams: this.teams.filter(x => x.division == 2).length, nplayers: 8 },
        { nteams: this.teams.filter(x => x.division == 3).length, nplayers: 6 },
        { nteams: this.teams.filter(x => x.division == 4).length, nplayers: 4 },
        { nteams: this.teams.filter(x => x.division == 5).length, nplayers: 4 },
      ]
      let s = 0
      tt.forEach((x) => {
        x.start = s
        s += x.nteams * x.nplayers
      })
      let nt = 1
      tt.forEach((x) => {
        x.range = range(x.nteams * x.nplayers, x.start)
        x.names = range(x.nteams, nt).map(y => `${this.club.name_short} ${y}`)
        nt += x.nteams
      })
      return tt
    },

  },

  methods: {

    first_name(pix) {
      return pix < this.players.length ? this.players[pix].first_name : ""
    },

    fillTitular() {
      console.log('fill titular')
      const teams = JSON.parse(JSON.stringify(this.teams))
      let error = false
      teams.forEach((tm) => {
        let t = this.tt[tm.division - 1]
        let teamnr = tm.name.split(" ").pop()
        console.log(tm.name, t)
        if (t.nteams == 1) {
          tm.titular = t.range.map(x => this.players[x].idnumber)
        }
        if (t.nteams > 1) {
          tm.titular = []
          t.range.forEach(x => {
            if (this.selmodel[x].split(" ").pop() == teamnr) {
              tm.titular.push(this.players[x].idnumber)
            }
          })
        }
        if (tm.titular.length != t.nplayers) {
          this.$root.$emit('snackbar', { text: this.$t('Invalid number of players in team') })
          console.log('invalid tm', tm, t, this.selmodel)
          error = true
          return
        }
      })
      if (error) return false
      this.$store.commit('playerlist/updateTeams', teams)
      return true
    },

    last_name(pix) {
      return pix < this.players.length ? this.players[pix].last_name : ""
    },

    next() {
      if (this.fillTitular()) {
        this.$store.commit('playerlist/updateStep', this.step + 1)
      }
    },

    prev() {
      this.$store.commit('playerlist/updateStep', this.step - 1)
    },




  }
}
</script>

