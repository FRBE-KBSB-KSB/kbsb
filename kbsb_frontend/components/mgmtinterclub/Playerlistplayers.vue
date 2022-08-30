<template>
  <div>
    <h3>Players in player list</h3>
    <div>TODO</div>
    <div class="mt-2">
      <v-btn color="deep-purple" class="white--text" @click="next">
        Continue
      </v-btn>
      <v-btn @click="prev">
        Back
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
    },
    prev() {
      this.$store.commit('mgmtplayerlist/updateStep', this.step - 1)
    }
  }
}
</script>

