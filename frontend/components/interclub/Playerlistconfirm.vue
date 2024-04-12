<template>
  <div>
    <h4>{{ $t('Save changes') }}</h4>
    <div v-if="!confirmed" class="mt-2">
      <v-btn color="green" class="white--text" @click="save">
        {{ $t('Save') }}
      </v-btn>
      <v-btn @click="prev">
        {{ $t('Back') }}
      </v-btn>
    </div>
    <div v-if="confirmed" class="mt-2">
      <p>{{ $t('Playerlist saved') }}</p>
      <v-btn color="green" class="white--text" @click="reset">
        {{ $t('Modify playerlist again') }}
      </v-btn>
    </div>

  </div>
</template>

<script>

export default {


  data() {
    return {
      confirmed: false
    }
  },

  computed: {
    logintoken() { return this.$store.state.oldlogin.value },
    step() {
      return this.$store.state.playerlist.step
    },
    players() {
      return this.$store.state.playerlist.players
    },
    teams() {
      return this.$store.state.playerlist.teams
    },
    transfersout() {
      return this.$store.state.playerlist.transfersout
    },

  },

  props: {
    club: Object,
    activenotloaded: Boolean,
  },

  methods: {

    async save() {
      try {
        const reply = await this.$api.interclub.clb_set_interclubclub({
          token: this.logintoken,
          idclub: this.club.idclub,
          players: this.players,
          teams: this.teams,
          transfersout: this.transfersout
        })
        this.confirmed = true
        this.$root.$emit('snackbar', { text: this.$t('Playerlist saved') })
      } catch (error) {
        const reply = error.response
        switch (reply.status) {
          case 401:
            this.gotoLogin()
            break
          case 403:
            this.$root.$emit('snackbar', { text: this.$t('Permission denied') })
            break
          default:
            console.error('Saving playerlist failed', reply.data.detail)
            this.$root.$emit('snackbar', { text: this.$t('Saving playerlist failed') })
        }
      }
    },

    prev() {
      this.$store.commit('playerlist/updateStep', this.step - 1)
    },

    reset() {
      this.confirmed = false
      this.$store.commit('playerlist/updateStep', 2)
    }

  }
}
</script>

