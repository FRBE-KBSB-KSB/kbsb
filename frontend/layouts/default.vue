<template>
  <v-app>

    <v-navigation-drawer v-cloak v-model="drawer" app class="green darken-1" clipped height="100%">

      <TheSidebar />

    </v-navigation-drawer>

    <TheTopbar :drawer="drawer" @updateDrawer="updateDrawer" />

    <v-main>
      <nuxt />
      <TheCarousel />
      <hr />
      <TheFooter />
    </v-main>

    <TheCredentials />

    <v-snackbar v-model="snackbar" top>
      {{ snacktext }}
      <template #action="{ attrs }">
        <v-btn text v-bind="attrs" @click="snackbar = false">
          <v-icon>mdi-close</v-icon>
        </v-btn>
      </template>
    </v-snackbar>

  </v-app>
</template>

<script>
export default {
  data() {
    return {
      drawer: null,
      snackbar: false,
      snacktext: ""
    };
  },

  mounted() {
    this.$root.$on('snackbar', (ev) => {
      console.log('received snackbar event', ev.text)
      if (ev.text) {
        this.snacktext = ev.text
        this.reason = ev.reason
        this.snackbar = true
      }
    })
  },

  methods: {
    updateDrawer(value) {
      this.drawer = value;
    }
  },

}
</script>
