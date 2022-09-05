<template>
  <v-container>
    <p v-if="!club.idclub">Please select a club to edit the player list</p>
    <div v-if="club.idclub">
      <div v-if="teams.length">
        <v-stepper v-model="step" vertical @change="changeStep">

          <v-stepper-step :complete="step > 1" step="1" color="deep-purple">
            Intro
          </v-stepper-step>
          <v-stepper-content step="1">
            <MgmtinterclubPlayerlistintro />
          </v-stepper-content>

          <v-stepper-step :complete="step > 2" step="2" color="deep-purple">
            Define players
          </v-stepper-step>
          <v-stepper-content step="2">
            <MgmtinterclubPlayerlistplayers :club="club" :activenotloaded="activenotloaded" />
          </v-stepper-content>

          <v-stepper-step :complete="step > 3" step="3" color="deep-purple">
            Define players
          </v-stepper-step>
          <v-stepper-content step="2">
            <MgmtinterclubPlayerlisttransfer :club="club" />
          </v-stepper-content>

          <v-stepper-step :complete="step > 4" step="4" color="deep-purple">
            Define order
          </v-stepper-step>
          <v-stepper-content step="3">
            <MgmtinterclubPlayerlistorder />
          </v-stepper-content>

          <v-stepper-step :complete="step > 5" step="5" color="deep-purple">
            Define teams
          </v-stepper-step>
          <v-stepper-content step="4">
            <MgmtinterclubPlayerlistteams />
          </v-stepper-content>

          <v-stepper-step :complete="step > 6" step="6" color="deep-purple">
            Confirm
          </v-stepper-step>
          <v-stepper-content step="5">
            <MgmtinterclubPlayerlistconfirm />
          </v-stepper-content>

        </v-stepper>

      </div>
      <div v-if="!teams.length">
        <p>
          This club is not enrolled in the interclubs.
          As such, for this interclub season, it can transfer it members to other clubs
        </p>
        <MgmtinterclubPlayerlisttransfer :club="club" />
        <MgmtinterclubPlayerlistconfirm />

      </div>
    </div>
  </v-container>
</template>
<script>
import Vue from 'vue'
import club from '../../api/club';
import TheCarouselVue from '../TheCarousel.vue';

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
    step() {
      return this.$store.state.mgmtplayerlist.step
    },
    teams() {
      return this.$store.state.mgmtplayerlist.teams
    },

  },

  methods: {

    emitInterface() {
      this.$emit("interface", "playerlist_init", this.playerlist_init);
    },

    playerlist_init() {
      this.get_activemembers();
      this.get_interclubclub();
    },

    async get_activemembers() {
      console.log('get_activemembers called', this.club.idclub)
      try {
        const reply = await this.$api.old.get_clubmembers({
          idclub: this.club.idclub,
        })
        this.activenotloaded = false;
        this.$store.commit('mgmtplayerlist/updateActivemembers', reply.data.activemembers)
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
      console.log('get_interclubclub called', this.club.idclub)
      try {
        const reply = await this.$api.interclub.get_interclubclub({
          idclub: this.club.idclub,
        })
        this.$store.commit('mgmtplayerlist/updatePlayers', reply.data.players)
        this.$store.commit('mgmtplayerlist/updateTeams', reply.data.teams)
        this.$store.commit('mgmtplayerlist/updateTransferout', reply.data.transferout)
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
    this.emitInterface();
    this.$nextTick(() => {
      this.playerlist_init()
    })
  },

}
</script>