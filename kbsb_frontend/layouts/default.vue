<template>
<v-app>

  <v-navigation-drawer
    v-cloak
    v-model="drawer"
    app
    class="green darken-1"
    clipped
    height="100%"
  >

    <TheTopbar />
    
  </v-navigation-drawer>
    
  <TheTopbar :drawer="drawer" @updateDrawer="updateDrawer"/>
    
  <v-main>
    <nuxt />
    <TheCarousel />
  </v-main>

  <TheFooter />

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
import TheTopbar from '../components/TheTopbar.vue';
export default {
    data() {
        return {
            drawer: null,
            snackbar: false,
            snacktext: ""
        };
    },
    methods: {
        updateDrawer(value) {
            this.drawer = value;
        }
    },
    components: { TheTopbar }
}
</script>
