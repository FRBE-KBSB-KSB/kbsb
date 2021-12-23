<template>
  <v-app>
    <v-app-bar v-cloak dark app class="deep-purple darken-2">
      <v-app-bar-nav-icon @click.stop="drawer = !drawer" />
      <v-toolbar-items>
        <v-btn text large href="/">
          Management
        </v-btn>
      </v-toolbar-items>
      <v-spacer />
      <v-toolbar-title>Admin Interface</v-toolbar-title>
    </v-app-bar>
    <v-navigation-drawer
      v-cloak
      v-model="drawer"
      app
      class="deep-purple darken-2"
    >
      <v-list dark>
        <v-list-item>
          <v-list-item-title class="title">
            Menu
          </v-list-item-title>
        </v-list-item>
      </v-list>
      </v-toolbar>
      <v-list dark dense class="deep-purple">
        <v-list-item to="/mgmt/pagelist">
          <v-list-item-icon>
            <v-icon>mdi-file</v-icon>
          </v-list-item-icon>
          <v-list-item-content>Pages</v-list-item-content>
        </v-list-item>
        <v-list-item to="/mgmt/filelist">
          <v-list-item-icon>
            <v-icon>mdi-file-document</v-icon>
          </v-list-item-icon>
          <v-list-item-content>Files</v-list-item-content>
        </v-list-item>
      </v-list>
    </v-navigation-drawer>

    <v-main>
      <nuxt />
    </v-main>

    <v-snackbar v-model="snackbar" bottom>
      {{ snacktext }}
      <template #action="{ attrs }">
        <v-btn text v-bind="attrs" @click="snackbar = false">
          <v-icon>mdi-close</v-icon>
        </v-btn>
      </template>
    </v-snackbar>
    </v-navigation-drawer>
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

  mounted () {
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
    updateDrawer (value) {
      this.drawer = value
    }
  }

}
</script>
