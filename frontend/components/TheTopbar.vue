<template>
  <v-app-bar v-cloak fixed dark app class="green darken-2">
    <v-app-bar-nav-icon @click.stop="toggleDrawer" />
    <v-toolbar-items>
      <v-btn text large href="/">
        {{ $t("RBCF") }}
      </v-btn>
    </v-toolbar-items>
    <v-spacer />
    <v-toolbar-items class="hidden-sm-and-down">
      <v-btn text large :href="'/page/interclub-2021-22/'+$i18n.locale">
        Interclub 21-22
      </v-btn>
      <v-btn text large :href="phpbaseurl + 'sites/manager/GestionFICHES/FRBE_Fiche.php'">
        ELO
      </v-btn>
    </v-toolbar-items>
  </v-app-bar>
</template>

<script>

import { phpbaseurl } from '@/util/cms'

export default {

  props: {
    landing: {
      type: String,
      default: null
    },
    drawer: {
      type: Boolean,
      default: null
    }
  },

  data () {
    return {
      phpbaseurl
    }
  },

  methods: {
    toggleDrawer () {
      this.$emit('updateDrawer', !this.drawer)
    }
  }
}
</script>
