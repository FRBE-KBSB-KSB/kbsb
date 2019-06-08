<template>
    <v-navigation-drawer v-cloak dark temporary fixed v-model="drawer"
                         class="navmax green darken-1" :class="{fixtoolbar: fixtoolbar}">
      <v-toolbar flat class="green">
        <v-list>
          <v-list-tile>
            <v-list-tile-title class="title">
              Menu
            </v-list-tile-title>
          </v-list-tile>
        </v-list>
      </v-toolbar>
      <v-divider></v-divider>
      <div class="btn-language green darken-1">
        <v-btn flat class="hover-darker btn-language" :href="url_i18nn('nl')">NL</v-btn>
        <v-btn flat class="hover-darker btn-language" :href="url_i18nn('fr')">FR</v-btn>
        <v-btn flat class="hover-darker btn-language" :href="url_i18nn('de')">DE</v-btn>
        <v-btn flat class="hover-darker btn-language" :href="url_i18nn('en')">EN</v-btn>
      </div>
      <v-list dark dense class="green darken-1">
        <cms-menu-items></cms-menu-items>
        <v-list-group>
          <v-list-tile slot="activator">
            <v-list-tile-content>{{$t('Tools')}}</v-list-tile-content>
          </v-list-tile>
          <v-list-tile :href="phpbaseurl + 'sites/manager/GestionCOMMON/GestionLogin.php'">
            <v-list-tile-action></v-list-tile-action>
            <v-list-tile-content>
              <v-list-tile-title>Player - Club Manager</v-list-tile-title>
            </v-list-tile-content>
          </v-list-tile>
          <v-list-tile :href="phpbaseurl + 'sites/manager/GestionCOMMON/GestionLogin.php'">
            <v-list-tile-action></v-list-tile-action>
            <v-list-tile-content>
              <v-list-tile-title>Interclub Manager</v-list-tile-title>
            </v-list-tile-content>
          </v-list-tile>
          <v-list-tile :href="phpbaseurl + 'sites/manager/GestionFICHES/FRBE_Fiche.php'">
            <v-list-tile-action></v-list-tile-action>
            <v-list-tile-content>
              <v-list-tile-title>ELO</v-list-tile-title>
            </v-list-tile-content>
          </v-list-tile>
          <v-list-tile :href="phpbaseurl + 'sites/manager/GestionSWAR/SwarResults.php'">
            <v-list-tile-action></v-list-tile-action>
            <v-list-tile-content>
              <v-list-tile-title>{{ $t('Results SWAR')}}</v-list-tile-title>
            </v-list-tile-content>
          </v-list-tile>
          <v-list-tile :href="phpbaseurl + 'sites/manager/CalcNorm/norm.php'">
            <v-list-tile-action></v-list-tile-action>
            <v-list-tile-content>
              <v-list-tile-title>Calc Norm</v-list-tile-title>
            </v-list-tile-content>
          </v-list-tile>
        </v-list-group>

      </v-list>
      <v-divider></v-divider>
      <v-list dark dense class="green darken-1" v-if="authenticated">
        <v-list-group>
          <v-list-tile slot="activator">
            <v-list-tile-content>Management</v-list-tile-content>
          </v-list-tile>
          <v-list-tile href="/mgmt/members">
            <v-list-tile-action></v-list-tile-action>
            <v-list-tile-content>
              <v-list-tile-title>Members</v-list-tile-title>
            </v-list-tile-content>
          </v-list-tile>
          <v-list-tile href="/mgmt/articles">
            <v-list-tile-action></v-list-tile-action>
            <v-list-tile-content>
              <v-list-tile-title>Articles</v-list-tile-title>
            </v-list-tile-content>
          </v-list-tile>
        </v-list-group>
      </v-list>
    </v-navigation-drawer>
</template>

<script>


export default {

  name: "Sidebar",

  computed: {
    drawer: {
      get () {
        return this.$store.state.drawer
      },
      set (value) {
        this.$store.commit('updateDrawer', value)
      }
    },
  },

  data () {return {
    fixtoolbar: false,
    authenticated: false,
    sections: {
      participants: window.config.participants_enabled,
      subscription: window.config.subscriptions_enabled,
      tournament: window.config.tournament_enabled,
    },
    phpbaseurl: window.config.phpbaseurl,
  }},

  mounted() {
    if (window.CMS) {
      this.fixtoolbar = true;
    }
  },

  methods: {
    url_i18nn (lang) {
      return window.config.url_i18n[lang];
    }
  }


}

</script>

<style scoped>
.fixtoolbar {
  top: 50px;
}
.btn-language {
  min-width: 0;
}
</style>