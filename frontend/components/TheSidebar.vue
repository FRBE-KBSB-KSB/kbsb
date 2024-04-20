<script setup>
import { useI18n } from 'vue-i18n'
import { phpbaseurl } from '@/util/cms'
const { t, locale } = useI18n()

function setLocale(l) {
  console.log('setting locale', l)
  locale.value = l
}

function gotorating() {
  return locale === 'nl' ? '/tools/ratingnl' : '/tools/ratingfr'
}

function gotoOldsite(url) {
  window.open(phpbaseurl + url, "oldsite")
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
      
      <v-list-group>
        <template v-slot:activator="{ props }">
          <v-list-item v-bind="props" :title="t('Administration')" />
        </template>
        <v-list-item to="/admin/board" :title="t('Board')" />
        <v-list-item to="/admin/goal" :title="t('Goal')" />
        <v-list-item to="/admin/statutes" :title="t('Statutes')" />
        <v-list-item to="/admin/tournamentrules" :title="t('Tournament rules')" />
        <v-list-item to="/admin/internalrules" :title="t('Internal rules')" />
        <!-- <v-list-item :to="localePath('/admin/reports')" :title="$t('Reports')" /> -->
        <v-list-item to="/admin/vademecum" title="Vademecum" />
        <v-list-item to="/admin/regional" :title="t('Regional')" />
        <v-list-item to="/admin/commissions" :title="t('Committees')" /> 
      </v-list-group>

      <v-list-group>
        <template v-slot:activator="{ props }">
          <v-list-item v-bind="props" :title="t('Competitions')" />
        </template>
        <v-list-item to="/interclubs/info" title="Interclubs 2023-24" />
        <v-list-item to="/interclubs/interclubs-2022-23" title="Interclubs 2022-23" />
        <v-list-item to="/competition/championships-adult" :title="t('BC Adults')" />
        <v-list-item to="/competition/championships-blitz" :title="t('BC Blitz')" />
        <v-list-item to="/competition/championships-rapid" :title="t('BC Rapid')" />
        <v-list-item to="/competition/international-adult" :title="t('International competitions')" />
      </v-list-group>

      <v-list-group>
        <template v-slot:activator="{ props }">
          <v-list-item v-bind="props" :title="t('Clubs')" />
        </template>
        <v-list-item to="/clubs/info" title="Club Info" />
        <v-list-item to="/clubs/manager" title="Club Manager" />
      </v-list-group>

      <v-list-group>
        <template v-slot:activator="{ props }">
          <v-list-item v-bind="props" :title="t('Youth')" />
        </template>
        <v-list-item to="/youth/championships-youth" :title="t('BC Youth')" />
        <v-list-item to="/youth/international-youth" :title="t('International')" />
        <v-list-item to="/youth/school-chess" :title="t('BC School chess')" />
        <v-list-item to="/youth/license-g" :title="t('G License')" />
      </v-list-group>

      <v-list-group>
        <template v-slot:activator="{ props }">
          <v-list-item v-bind="props" :title="$t('Useful information')" />
        </template>
        <!-- <v-list-item to="/info/calendar" :title="t('Calendar')" /> -->
        <v-list-item to="/info/email-addresses" :title="t('Email addresses')" />
        <v-list-item to="/info/elo-processing" :title="t('ELO processing')" />
        <v-list-item to="/info/gdpr" :title="t('GDPR')" />
        <v-list-item to="/info/transgender" :title="t('Transgender')" />
      </v-list-group>

      <v-list-group>
        <template v-slot:activator="{ props }">
          <v-list-item v-bind="props" :title="t('Tools')" />
        </template>
        <v-list-item :to="gotorating()" :title="t('ELO tournaments')" />
        <v-list-item title="Player Manager"
          @click="gotoOldsite('sites/manager/GestionCOMMON/GestionLogin.php')" />
        <v-list-item to="/clubs/manager" title="Club Manager" />
        <v-list-item to="/interclubs/manager" title="Interclub Manager" />
        <v-list-item title="Elo" @click="gotoOldsite('sites/manager/GestionFICHES/FRBE_Fiche.php')" />
        <v-list-item title="t('Results SWAR')"
          @click="gotoOldsite('sites/manager/GestionSWAR/SwarResults.php')" />
        <v-list-item title="Calc Norm" @click="gotoOldsite('sites/manager/CalcNorm/norm.php')" />
      </v-list-group>

      <v-list-item to="/info/partners" title="Partners" />

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
