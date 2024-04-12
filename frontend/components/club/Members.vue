<template>
  <v-container>
    <p>TO DO</p>
  </v-container>
</template>
<script>

export default {

  name: 'Detail',

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
      this.$emit("interface", "getClub", this.getClub);
    },

    async getClub(activeclub) {
      this.club = activeclub;
    }
  },

  mounted() {
    this.emitInterface();
  },

}
</script>