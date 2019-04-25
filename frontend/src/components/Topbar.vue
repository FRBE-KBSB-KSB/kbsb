<template>
<v-toolbar v-cloak fixed dark app
           class="green darken-2" :class="{fixtoolbar: fixtoolbar, landing: landing}">
  <v-toolbar-side-icon @click.stop="openDrawer"></v-toolbar-side-icon>
  <v-toolbar-items>
    <v-btn flat large href="/">{{ $t('RBCF')}}</v-btn>
  </v-toolbar-items>
  <v-spacer></v-spacer>
  <v-toolbar-items class="hidden-sm-and-down">
    <v-btn flat large href="/interclub">{{ $t('Interclub')}}
    </v-btn>
    <v-btn flat large href="/info/lodging-and-meals">ELO
    </v-btn>
  </v-toolbar-items>
</v-toolbar>
</template>

<script>
export default {

  name: "Topbar",

  data () {return {
    fixtoolbar: false,
    landing: window.config.landing,
  }},

  mounted() {
    if (window.CMS) {
      this.fixtoolbar = true;
    }
  },

  methods:   {
    openDrawer () {
      this.$store.commit('updateDrawer', true)
    },
    url_i18nn (lang) {
      return window.config.url_i18n[lang];
    }
  },
}
</script>

<style scoped>
.fixtoolbar {
  top: 50px;
}

.landing.green.darken-2 {
  background-color: rgba(77, 94, 101, 0.4) !important;
  /*background-color: green;*/
}
</style>