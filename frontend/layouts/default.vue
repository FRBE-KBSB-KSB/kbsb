<template>
  <v-app>
    <v-navigation-drawer
      v-cloak
      v-model="drawer"
      app
      class="green darken-1"
    >
      <TheSidebar />
    </v-navigation-drawer>

    <TheTopbar landing="landing" :drawer="drawer" @updateDrawer="updateDrawer" />

    <v-main>
      <nuxt />
      <TheCarousel />
      <TheFooter />
    </v-main>

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
  data () {
    return {
      drawer: false,
      snackbar: false,
      snacktext: ''
    }
  },
  methods: {
    updateDrawer (value) {
      this.drawer = value
    }
  }
}
</script>
