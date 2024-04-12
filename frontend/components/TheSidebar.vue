<script setup>
import { phpbaseurl } from '@/util/cms'
import { VBtn, VList, VListItem, VListGroup } from 'vuetify/components';

const { locale, setLocale } = useI18n()
const localePath = useLocalePath()

function gotorating() {
  return locale === 'nl' ? '/tools/ratingnl' : '/tools/ratingfr'
}

function gotoOldsite(url) {
  window.open(phpbaseurl + url, "oldsite")
}
</script>

<style scoped>
.btn-language {
  min-width: 0 !important;
}
</style>

<template>
  <div>

    <div>
      <v-btn variant="text" class="btn-language" @click="setLocale('nl')">NL</v-btn>
      <v-btn variant="text" class="btn-language" @click="setLocale('fr')">FR</v-btn>
      <v-btn variant="text" class="btn-language" @click="setLocale('de')">DE</v-btn>
      <v-btn variant="text" class="btn-language" @click="setLocale('en')">EN</v-btn>
    </div>

    <v-list nav>
      <v-list-item :to="localePath('/')" :title="$t('Home')" />

      <v-list-group>
        <template v-slot:activator="{ props }">
          <v-list-item v-bind="props" :title="$t('Administration')" />
        </template>
        <v-list-item :to="localePath('/admin/board')" :title="$t('Board')" />
        <v-list-item :to="localePath('/admin/goal')" :title="$t('Goal')" />
        <v-list-item :to="localePath('/admin/statutes')" :title="$t('Statutes')" />
        <v-list-item :to="localePath('/admin/tournamentrules')" :title="$t('Tournament rules')" />
        <v-list-item :to="localePath('/admin/internalrules')" :title="$t('Internal rules')" />
        <v-list-item :to="localePath('/admin/reports')" :title="$t('Reports')" />
        <v-list-item :to="localePath('/admin/vademecum')" title="Vademecum" />
        <v-list-item :to="localePath('/admin/regional')" :title="$t('Regional')" />
        <v-list-item :to="localePath('/admin/commissions')" :title="$t('Committees')" />
      </v-list-group>

      <v-list-group>
        <template v-slot:activator="{ props }">
          <v-list-item v-bind="props" :title="$t('Competitions')" />
        </template>
        <v-list-item :to="localePath('/interclubs/info')" title="Interclubs 2023-24" />
        <v-list-item :to="localePath('/interclubs/interclubs-2022-23')" title="Interclubs 2022-23" />
        <v-list-item :to="localePath('/competition/championships-adult')" :title="$t('BC Adults')" />
        <v-list-item :to="localePath('/competition/championships-blitz')" :title="$t('BC Blitz')" />
        <v-list-item :to="localePath('/competition/championships-rapid')" :title="$t('BC Rapid')" />
        <v-list-item :to="localePath('/competition/international-adult')"
          :title="$t('International competitions')" />
      </v-list-group>

      <v-list-group>
        <template v-slot:activator="{ props }">
          <v-list-item v-bind="props" :title="$t('Clubs')" />
        </template>
        <v-list-item :to="localePath('/clubs/info')" title="Club Info" />
        <v-list-item :to="localePath('/clubs/manager')" title="Club Manager" />
      </v-list-group>

      <v-list-group>
        <template v-slot:activator="{ props }">
          <v-list-item v-bind="props" :title="$t('Youth')" />
        </template>
        <v-list-item :to="localePath('/youth/championships-youth')" :title="$t('BC Youth')" />
        <v-list-item :to="localePath('/youth/international-youth')" :title="$t('International')" />
        <v-list-item :to="localePath('/youth/school-chess')" :title="$t('BC School chess')" />
        <v-list-item :to="localePath('/youth/license-g')" :title="$t('G License')" />
      </v-list-group>

      <v-list-group>
        <template v-slot:activator="{ props }">
          <v-list-item v-bind="props" :title="$t('Useful information')" />
        </template>
        <v-list-item :to="localePath('/info/calendar')" :title="$t('Calendar')" />
        <v-list-item :to="localePath('/info/email-addresses')" :title="$t('Email addresses')" />
        <v-list-item :to="localePath('/info/elo-processing')" :title="$t('ELO processing')" />
        <v-list-item :to="localePath('/info/gdpr')" :title="$t('GDPR')" />
        <v-list-item :to="localePath('/info/transgender')" :title="$t('Transgender')" />
      </v-list-group>

      <v-list-group>
        <template v-slot:activator="{ props }">
          <v-list-item v-bind="props" :title="$t('Tools')" />
        </template>
        <v-list-item :to="gotorating()" :title="$t('ELO tournaments')" />
        <v-list-item title="Player Manager"
          @click="gotoOldsite('sites/manager/GestionCOMMON/GestionLogin.php')" />
        <v-list-item :to="localePath('/clubs/manager')" title="Club Manager" />
        <v-list-item :to="localePath('/interclubs/manager')" title="Interclub Manager" />
        <v-list-item title="Elo" @click="gotoOldsite('sites/manager/GestionFICHES/FRBE_Fiche.php')" />
        <v-list-item :title="$t('Results SWAR')"
          @click="gotoOldsite('sites/manager/GestionSWAR/SwarResults.php')" />
        <v-list-item title="Calc Norm" @click="gotoOldsite('sites/manager/CalcNorm/norm.php')" />
      </v-list-group>

      <v-list-item :to="localePath('/info/partners')" title="Partners" />
    </v-list>

  </div>
</template>


