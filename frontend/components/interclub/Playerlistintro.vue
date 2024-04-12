<template>
  <div>
    <h3>{{ $t('Intro Player List') }}</h3>
    <div>{{ $t('The player list of a club is established in 4 steps') }}</div>
    <ul>
      <li>{{ $t('Define who are the players on the list.') }}</li>
      <li>{{ $t('Define the incoming and outgoing transfers.') }}</li>
      <li>{{ $t('Define the order of the players in the list.') }} 
        {{ $t('This is done by adapting the rating of the players.') }}
      </li>
      <li>{{ $t('Define the titulars per team') }}</li>
    </ul>
    <div class="mt-2">
      <v-btn color="green" class="white--text" @click="next">
        {{ $t('Continue') }}
      </v-btn>
    </div>
  </div>
</template>

<script>

export default {

  computed: {
    step() {
      return this.$store.state.playerlist.step
    }
  },

  methods: {
    next() {
      this.$store.commit('playerlist/updateStep', this.step + 1)
    }
  }
}
</script>

<style scoped>
</style>
