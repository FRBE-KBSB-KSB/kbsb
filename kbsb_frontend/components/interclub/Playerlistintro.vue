<template>
  <div>
    <h3>Intro Player List</h3>
    <div>The player list of a club is established in 4 steps</div>
    <ul>
      <li>Define who are the players on the list</li>
      <li>Define the incoming and outgoing transfers</li>
      <li>Define the order of the players in the list. This is done by adapting the rating of
        the players</li>
      <li>Define the titulars per team</li>
    </ul>
    <div class="mt-2">
      <v-btn color="deep-purple" class="white--text" @click="next">
        {{ $t('Continue') }}
      </v-btn>
    </div>
  </div>
</template>

<script>

export default {

  computed: {
    step() {
      return this.$store.state.mgmtplayerlist.step
    }
  },

  methods: {
    next() {
      this.$store.commit('mgmtplayerlist/updateStep', this.step + 1)
    }
  }
}
</script>

<style scoped>
</style>
