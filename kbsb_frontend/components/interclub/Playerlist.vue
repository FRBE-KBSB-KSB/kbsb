<template>
  <v-container>
    <p>TO DO</p>
  </v-container>
</template>
<script>

export default {

  name: 'Playerlist',

  data() {
    return {
      club: {},
    }
  },


  computed: {
    logintoken() { return this.$store.state.oldlogin.value },
  },

  methods: {

    emitInterface() {
      this.$emit("interface", "getAnonPlayerlist", this.getAnonPlayerlist);
    },

    async getAnonPlayerlist(activeclub) {
      this.club = activeclub;
    }
  },

  mounted() {
    this.emitInterface();
  },

}
</script>