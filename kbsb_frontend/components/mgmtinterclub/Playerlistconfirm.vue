<template>
  <div>
    <h2>Order for player list</h2>
    <div>TODO</div>
    <div class="mt-2">
      <v-btn color="deep-purple" class="white--text" @click="save">
        Save
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
    save() {
    },
    prev() {
      this.$store.commit('mgmtplayerlist/updateStep', this.step - 1)
    }
  }
}
</script>

