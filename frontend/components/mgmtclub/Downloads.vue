<template>
  <v-container>
    <h3>CSV Downloads</h3>
    <!-- <v-btn @click="downloadEnrollments">Download enrollments</v-btn>
    <v-btn @click="downloadVenues">Download venues</v-btn> -->
  </v-container>
</template>
<script>

function atou(b64) {
  return decodeURIComponent(escape(atob(b64)));
}

function utoa(data) {
  return btoa(unescape(encodeURIComponent(data)));
}

export default {

  name: 'Sownloads',


  computed: {
    logintoken() { return this.$store.state.newlogin.value },
  },

  methods: {

    async downloadEnrollments() {
      try {
        const reply = await this.$api.interclub.mgmt_csv_interclubenrollment({
          token: this.logintoken
        })
        console.log('reply', reply)
        const link = document.createElement('a')
        link.download = 'enrollments.csv'
        link.href = 'data:text/csv;base64,' + btoa(reply.data)
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)
        this.$root.$emit('snackbar', {
          text: 'Downloading CSV enrollments successful',
          color: 'black'
        })
      } catch (error) {
        const reply = error.response
        console.error('Downloading enrollment', reply.data.detail)
        this.$root.$emit('snackbar', { text: 'Downloading CSV enrollments failed' })
      }
    },

    async downloadVenues() {
      try {
        console.log('downloading venues')
        const reply = await this.$api.interclub.mgmt_csv_interclubvenues({
          token: this.logintoken
        })
        console.log('reply', reply)
        const link = document.createElement('a')
        link.download = 'venues.csv'
        link.href = 'data:text/csv;base64,' + utoa(reply.data)
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)
        this.$root.$emit('snackbar', {
          text: 'Downloading CSV venues successful',
          color: 'black'
        })
      } catch (error) {
        const reply = error.response
        console.error('Downloading venues', reply.data.detail)
        this.$root.$emit('snackbar', { text: 'Downloading CSV venues failed' })
      }
    },

  },


}
</script>