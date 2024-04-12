<template>
  <v-app>

    <v-navigation-drawer v-cloak v-model="drawer" class="green darken-1" app height="100%">
      <TheSidebar />
    </v-navigation-drawer>

    <TheTopbar landing="landing" :drawer="drawer" @updateDrawer="updateDrawer" />

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
import TheCredentials from "../components/TheCredentials.vue";
import TheFooter from "../components/TheFooter.vue";
export default {
  data() {
    return {
      drawer: false,
      snackbar: false,
      snacktext: ""
    };
  },
  methods: {
    updateDrawer(value) {
      this.drawer = value;
    }
  },
  components: { TheCredentials, TheFooter }
}
</script>
<style scoped>
.footer a {
  color: white;
}
</style>