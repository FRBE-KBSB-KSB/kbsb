<template>
  <v-container>
    <p v-if="!club.idclub">{{ $t('Please select a club to edit the player list') }}</p>
    <div v-if="club.idclub">
      <div v-if="teams.length">
        <v-stepper v-model="step" vertical>

          <v-stepper-step :complete="step > 1" step="1" color="green">
            {{ $t('Intro') }}
          </v-stepper-step>
          <v-stepper-content step="1">
            <InterclubPlayerlistintro />
          </v-stepper-content>

          <v-stepper-step :complete="step > 2" step="2" color="green">
            {{ $t('Define players') }}
          </v-stepper-step>
          <v-stepper-content step="2">
            <InterclubPlayerlistplayers :club="club" :activenotloaded="activenotloaded" />
          </v-stepper-content>

          <v-stepper-step :complete="step > 3" step="3" color="green">
            {{ $t('Define transfers') }}
          </v-stepper-step>
          <v-stepper-content step="3">
            <InterclubPlayerlisttransfer :club="club" :activenotloaded="activenotloaded" />
          </v-stepper-content>

          <v-stepper-step :complete="step > 4" step="4" color="green">
            {{ $t('Define order') }}
          </v-stepper-step>
          <v-stepper-content step="4">
            <InterclubPlayerlistorder />
          </v-stepper-content>

          <v-stepper-step :complete="step > 5" step="5" color="green">
            {{ $t('Define teams') }}
          </v-stepper-step>
          <v-stepper-content step="5">
            <InterclubPlayerlistteams :club="club" />
          </v-stepper-content>

          <v-stepper-step :complete="step > 6" step="6" color="green">
            {{ $t('Confirmation') }}
          </v-stepper-step>
          <v-stepper-content step="6">
            <InterclubPlayerlistconfirm :club="club" />
          </v-stepper-content>

        </v-stepper>

      </div>
      <div v-if="!teams.length">
        <p>
          {{ $t('This club is not enrolled in the interclubs.') }}
          {{ $t('As such, for this interclub season, it can transfer it members to other clubs.') }}
        </p>
        <InterclubPlayerlisttransfer :club="club" />
        <InterclubPlayerlistconfirm :club="club" />

      </div>
    </div>
  </v-container>
</template>
<script>
import Vue from 'vue'

function compareAssignedrating(a, b) {
  return b.assignedrating - a.assignedrating
}

export default {

  name: 'Playerlist',

  data() {
    return {
      activenotloaded: true,
    }
  },

  props: {
    club: Object
  },

  computed: {
    activemembers() {
      return this.$store.state.playerlist.activemembers
    },
    players() {
      return this.$store.state.playerlist.players
    },
    step() {
      return this.$store.state.playerlist.step
    },
    teams() {
      return this.$store.state.playerlist.teams
    },
  },

  methods: {

    addmember(x) {
      const players = [...this.players]
      players.push({
        fiderating: x.fiderating,
        first_name: x.first_name,
        idnumber: x.idnumber,
        idclub: x.idclub,
        last_name: x.last_name,
        natrating: x.natrating,
        transfer: false
      })
      this.$store.commit('playerlist/updatePlayers', players)
    },

    buildplayers() {
      console.log('building players')
      const players = [...this.players]
      players.forEach((x) => {
        let nr = x.natrating || 0
        let fr = x.fiderating || 0
        if (nr > 0 && fr > 0) {
          if (x.assignedrating == null) x.assignedrating = nr
          x.maxrating = Math.max(nr, fr) + 100
          x.minrating = Math.min(nr, fr) - 100
        }
        if (nr > 0 && fr == 0) {
          if (x.assignedrating == null) x.assignedrating = nr
          x.maxrating = nr + 100
          x.minrating = nr - 100
        }
        if (nr == 0 && fr > 0) {
          if (x.assignedrating == null) x.assignedrating = fr
          x.maxrating = fr + 100
          x.minrating = fr - 100
        }
        if (nr == 0 && fr == 0) {
          if (x.assignedrating == null) x.assignedrating = 1150
          x.maxrating = 1600
          x.minrating = 1000
        }
      })
      players.sort(compareAssignedrating)
      this.$store.commit('playerlist/updatePlayers', players)
    },

    emitInterface() {
      this.$emit("interface", "playerlist_init", this.playerlist_init);
    },

    playerlist_init() {
      this.get_activemembers();
      this.get_interclubclub();
    },

    async get_activemembers() {
      try {
        const reply = await this.$api.old.get_clubmembers({
          idclub: this.club.idclub,
        })
        this.activenotloaded = false;
        this.$store.commit('playerlist/updateActivemembers', reply.data.activemembers)
      } catch (error) {
        switch (reply.status) {
          case 401:
            this.gotoLogin()
            break
          case 403:
            this.$root.$emit('snackbar', { text: this.$t('Permission denied') })
            break
          default:
            console.error('Getting active members', reply.data.detail)
            this.$root.$emit('snackbar', { text: this.$t('Getting active club members failed') })
        }
      }
    },

    async get_interclubclub() {
      try {
        const reply = await this.$api.interclub.get_interclubclub({
          idclub: this.club.idclub,
        })
        console.log('reply interclubclub', reply.data)
        this.$store.commit('playerlist/updatePlayers', reply.data.players)
        this.$store.commit('playerlist/updateTeams', reply.data.teams)
        this.$store.commit('playerlist/updateTransfersout', reply.data.transfersout)
        console.log('icc done', reply.data.players.length)
      } catch (error) {
        switch (reply.status) {
          case 401:
            this.gotoLogin()
            break
          case 403:
            this.$root.$emit('snackbar', { text: this.$t('Permission denied') })
            break
          default:
            console.error('Getting interclub clubdetails', reply.data.detail)
            this.$root.$emit('snackbar', { text: this.$t('Getting interclub club details failed') })
        }
      }
    },

  },

  mounted() {
    this.$root.$on('addmember', ((pl) => {
      this.addmember(pl)
    }))
    this.$root.$on('buildplayers', (() => {
      this.buildplayers()
    }))
    this.emitInterface()
    this.$nextTick(() => {
      this.playerlist_init()
    })
  },

  watch: {
    step: function (nv, ov) {
      console.log('step', nv)
      if (nv == 4) {
        this.buildplayers()
      }
      if (nv == 5) {
        this.$root.$emit('buildtitulars')
      }
    }
  },


}
</script>