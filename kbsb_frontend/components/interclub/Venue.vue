<template>
  <v-container>
    <p>TO DO</p>
  </v-container>
</template>
<script>

export default {

  name: 'Venue',

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
      this.$emit("interface", "getAnonVenues", this.getAnonVenues);
    },

    async getAnonVenues(activeclub) {
      this.club = activeclub;
    }
  },

  mounted() {
    this.emitInterface();
  },

}
</script>