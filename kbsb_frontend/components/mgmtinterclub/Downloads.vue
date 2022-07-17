<template>
  <v-container>
    <h3>CSV Downloads</h3>
    <v-btn>Download enrollments</v-btn>
    <v-btn>Download venues</v-btn>
  </v-container>
</template>
<script>

export default {

  name: 'Sownloads',


  computed: {
    logintoken() { return this.$store.state.oldlogin.value },
  },

  methods: {

    downloadVenues() {
      console.log('addEmpty Venue')
    },

    downloadEnrollments() {
      console.log('addEmpty Venue')
    },

  },


}
</script>