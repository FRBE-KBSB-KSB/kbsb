<script setup>
import { useI18n } from 'vue-i18n'
const { t, locale } = useI18n()

function setLocale(l) {
  console.log('setting locale', l)
  locale.value = l
}

</script>

<template>
  <div>
    <v-toolbar dark text class="bg-green">
      <v-list>
        <v-list-item title="Menu" />
      </v-list>
    </v-toolbar>
    <div class="bg-green-darken-1">
      <v-btn variant="text" class="btn-language hover-darker" @click="setLocale('nl')">NL</v-btn>
      <v-btn variant="text" class="btn-language hover-darker" @click="setLocale('fr')">FR</v-btn>
      <v-btn variant="text" class="btn-language hover-darker" @click="setLocale('de')">DE</v-btn>
      <v-btn variant="text" class="btn-language hover-darker" @click="setLocale('en')">EN</v-btn>
    </div>
    <v-list nav class="bg-green-darken-1">
      <v-list-item to="/" :title="t('Home')" />
    </v-list>

  </div>
</template>

<style scoped>
.btn-language.v-btn {
  min-width: 0;
  color: white;
}

.v-list-group--active.primary--text {
  color: white !important;
}

.menucell {
  width: 60px;
}

.left72 {
  padding-left: 72px;
}
</style>
