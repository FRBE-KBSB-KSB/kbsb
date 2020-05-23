<template>
    <v-navigation-drawer v-cloak dark temporary fixed v-model="drawer"
                         class="green darken-1" >
      <v-toolbar text class="green">
        <v-list>
          <v-list-item>
            <v-list-item-title class="title">
              Menu
            </v-list-item-title>
          </v-list-item>
        </v-list>
      </v-toolbar>
      <v-divider></v-divider>
      <div class="btn-language green darken-1">
        <v-btn text class="hover-darker btn-language" @click="updateLocale('nl')">NL</v-btn>
        <v-btn text class="hover-darker btn-language" @click="updateLocale('fr')">FR</v-btn>
        <v-btn text class="hover-darker btn-language" @click="updateLocale('de')">DE</v-btn>
        <v-btn text class="hover-darker btn-language" @click="updateLocale('en')">EN</v-btn>
      </div>
      <v-list dark dense class="green darken-1">
        <v-list-item @click="updateSlug('home')" >
          <v-list-item-content>Home</v-list-item-content>
        </v-list-item>
        <v-list-group no-action>
          <template v-slot:activator>
            <v-list-item-content>
              <i18n-text nl="Beheer" fr="Adminstration" de="Administration" en="Adminstration" />
            </v-list-item-content>
          </template>
          <v-list-item @click="updateSlug('statutes')" >
            <v-list-item-content>Statutes</v-list-item-content>
          </v-list-item>
          <v-list-item @click="updateSlug('competition-rules')" >
            <v-list-item-content>Competition Rules</v-list-item-content>
          </v-list-item>
        </v-list-group>                
        <v-list-group no-action>
          <template v-slot:activator>
            <v-list-item-content>Tools</v-list-item-content>
          </template>
          <v-list-item :href="phpbaseurl + 'sites/manager/GestionCOMMON/GestionLogin.php'">
            <v-list-item-content>
              <v-list-item-title>Player - Club Manager</v-list-item-title>
            </v-list-item-content>
          </v-list-item>
          <v-list-item :href="phpbaseurl + 'sites/manager/GestionCOMMON/GestionLogin.php'">
            <v-list-item-content>
              <v-list-item-title>Interclub Manager</v-list-item-title>
            </v-list-item-content>
          </v-list-item>
          <v-list-item :href="phpbaseurl + 'sites/manager/GestionFICHES/FRBE_Fiche.php'">
            <v-list-item-content>
              <v-list-item-title>ELO</v-list-item-title>
            </v-list-item-content>
          </v-list-item>
          <v-list-item :href="phpbaseurl + 'sites/manager/GestionSWAR/SwarResults.php'">
            <v-list-item-content>
              <v-list-item-title>Results SWAR</v-list-item-title>
            </v-list-item-content>
          </v-list-item>
          <v-list-item :href="phpbaseurl + 'sites/manager/CalcNorm/norm.php'">
            <v-list-item-content>
              <v-list-item-title>Calc Norm</v-list-item-title>
            </v-list-item-content>
          </v-list-item>
        </v-list-group>

      </v-list>
    </v-navigation-drawer>
</template>

<script>

import I18nText from "@/components/I18nText"

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

  components: {
    I18nText,
  },

  data () {return {
    fixtoolbar: false,
    authenticated: false,
    phpbaseurl: "https://www.frbe-kbsb.be/",
  }},

  mounted() {

  },

  methods: {
    updateLocale: function(l){
      this.$store.commit('updateLocale', l)
    },
    updateSlug: function(s){
      console.log('updating slug', s)
      this.$store.commit('updateSlug', s)
    },
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