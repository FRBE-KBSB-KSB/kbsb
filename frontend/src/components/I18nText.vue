<template>
  <span>
    <span v-show="locale == 'nl'">{{ nl }}</span>
    <span v-show="locale == 'fr'">{{ fr }}</span>
    <span v-show="locale == 'de'">{{ de }}</span>
    <span v-show="locale == 'en'">{{ en }}</span>
  </span>
</template>

<script>

import {mapState} from "vuex"

export default {
  
  name: "I18nText",
  
  props: ["nl", "fr", "en", "de"],
  
  computed: {
    ...mapState(['locale', ]),  
  }
}
</script>

<style scoped>

</style>