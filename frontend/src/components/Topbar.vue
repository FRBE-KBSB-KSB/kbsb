<template>
<v-app-bar v-cloak fixed dark app class="green darken-2">
  <v-app-bar-nav-icon @click.stop="toggleDrawer" />
  <v-toolbar-items>
    <v-btn text large href="/">
      <i18n-text nl="KBSB" fr="FRBE" de="KSB" en="RBCF"/>
    </v-btn>
  </v-toolbar-items>
  <v-spacer></v-spacer>
  <v-toolbar-items class="hidden-sm-and-down">
    <v-btn text large href="/competitions/interclub-2019-20/">Interclub
    </v-btn>
    <v-btn text large :href="phpbaseurl + 'sites/manager/GestionFICHES/FRBE_Fiche.php'">
      ELO
    </v-btn>
  </v-toolbar-items>
</v-app-bar>
</template>

<script>

import I18nText from "@/components/I18nText"

export default {

  name: "Topbar",

  data () {return {
    phpbaseurl: "https://www.frbe-kbsb.be/",
  }},

  components: {
    I18nText,
  },

  mounted() {
  },

  methods:   {
    toggleDrawer () {
      this.$store.commit('updateDrawer', !this.drawer)
    },
  },
}
</script>

<style scoped>
.landing.green.darken-2 {
  background-color: rgba(77, 94, 101, 0.4) !important;
}
</style>