<template>
  <div>

    <div class="btn-language green darken-1">
      <v-btn text dark class="hover-darker btn-language" @click="setLocale('nl')">
        NL
      </v-btn>
      <v-btn text dark class="hover-darker btn-language" @click="setLocale('fr')">
        FR
      </v-btn>
      <v-btn text dark class="hover-darker btn-language" @click="setLocale('de')">
        DE
      </v-btn>
      <v-btn text dark class="hover-darker btn-language" @click="setLocale('en')">
        EN
      </v-btn>
    </div>

    <v-list dark dense class="green darken-1">
      <v-list-item to="/">
        <v-list-item-content>{{ $t('Home') }}</v-list-item-content>
      </v-list-item>

      <v-list-group no-action>
        <template #activator>
          <v-list-item-content>{{ $t('Administration') }}</v-list-item-content>
        </template>
        <v-list-item to="/admin/board">
          <v-list-item-content>{{ $t('Board') }}</v-list-item-content>
        </v-list-item>
        <v-list-item to="/admin/statutes">
          <v-list-item-content>{{ $t('Statutes') }}</v-list-item-content>
        </v-list-item>
        <v-list-item to="/admin/tournamentrules">
          <v-list-item-content>{{ $t('Tournament rules') }}</v-list-item-content>
        </v-list-item>
        <v-list-item to="/admin/internalrules">
          <v-list-item-content>{{ $t('Internal rules') }}</v-list-item-content>
        </v-list-item>
        <v-list-item to="/admin/reports">
          <v-list-item-content>{{ $t('Reports') }}</v-list-item-content>
        </v-list-item>
        <v-list-item to="/admin/vademecum">
          <v-list-item-content>Vademecum</v-list-item-content>
        </v-list-item>
        <v-list-item to="/admin/regional">
          <v-list-item-content>{{ $t('Regional') }} </v-list-item-content>
        </v-list-item>
        <v-list-item to="/admin/commissions">
          <v-list-item-content>{{ $t('Committees') }} </v-list-item-content>
        </v-list-item>

      </v-list-group>

      <v-list-group no-action>
        <template #activator>
          <v-list-item-content>{{ $t('Competitions') }}</v-list-item-content>
        </template>
        <v-list-item to="/competition/interclubs-2019-20">
          <v-list-item-content>
            Interclubs 2019-20
          </v-list-item-content>
        </v-list-item>
        <v-list-item to="/competition/interclubs-2021-22">
          <v-list-item-content>
            Interclubs 2021-22
          </v-list-item-content>
        </v-list-item>
        <v-list-item to="/competition/championships-adult">
          <v-list-item-content>{{ $t('BC Adults') }} </v-list-item-content>
        </v-list-item>
        <v-list-item to="/competition/championships-blitz">
          <v-list-item-content>{{ $t('BC Blitz') }}</v-list-item-content>
        </v-list-item>
        <v-list-item to="/competition/championships-rapid">
          <v-list-item-content>{{ $t('BC Rapid') }} </v-list-item-content>
        </v-list-item>
        <v-list-item to="/competition/international-adult">
          <v-list-item-content>{{ $t('International competitions') }}</v-list-item-content>
        </v-list-item>
      </v-list-group>

      <v-list-group no-action>
        <template #activator>
          <v-list-item-content>{{ $t('Youth') }}</v-list-item-content>
        </template>
        <v-list-item to="/youth/championships-youth">
          <v-list-item-content>{{ $t('BC Youth') }}</v-list-item-content>
        </v-list-item>
        <v-list-item to="/youth/international-youth">
          <v-list-item-content>{{ $t('International') }}</v-list-item-content>
        </v-list-item>
        <v-list-item to="/youth/school-chess">
          <v-list-item-content>{{ $t('BC School chess') }}</v-list-item-content>
        </v-list-item>
        <v-list-item to="/youth/g-licence">
          <v-list-item-content>{{ $t('G License') }} </v-list-item-content>
        </v-list-item>
      </v-list-group>

      <v-list-group no-action>
        <template #activator>
          <v-list-item-content>{{ $t('Useful information') }}</v-list-item-content>
        </template>
        <v-list-item to="/info/calendar">
          <v-list-item-content>{{ $t('Calendar') }}</v-list-item-content>
        </v-list-item>
        <v-list-item to="/info/email-addresses">
          <v-list-item-content>{{ $t('Email addresses') }}</v-list-item-content>
        </v-list-item>
        <v-list-item to="/info/elo-processing">
          <v-list-item-content>{{ $t('ELO processing') }}</v-list-item-content>
        </v-list-item>
        <v-list-item to="/info/gdpr">
          <v-list-item-content>{{ $t('GDPR') }}</v-list-item-content>
        </v-list-item>
      </v-list-group>

      <v-list-group no-action>
        <template #activator>
          <v-list-item-content>{{ $t('Tools') }}</v-list-item-content>
        </template>
        <v-list-item :to="gotorating">
          <v-list-item-content>
            {{ $t('ELO tournaments') }}
          </v-list-item-content>
        </v-list-item>
        <v-list-item to="/tools/club">
          <v-list-item-content>
            Club Manager
          </v-list-item-content>
        </v-list-item>
        <v-list-item :href="phpbaseurl + 'sites/manager/GestionCOMMON/GestionLogin.php'">
          <v-list-item-content>
            Player Manager
          </v-list-item-content>
        </v-list-item>
        <v-list-item to="/tools/interclub">
          <v-list-item-content>
            Interclub Manager
          </v-list-item-content>
        </v-list-item>
        <v-list-item :href="phpbaseurl + 'sites/manager/GestionFICHES/FRBE_Fiche.php'">
          <v-list-item-content>
            ELO
          </v-list-item-content>
        </v-list-item>
        <v-list-item :href="phpbaseurl + 'sites/manager/GestionSWAR/SwarResults.php'">
          <v-list-item-content>{{ $t('Results SWAR') }}</v-list-item-content>
        </v-list-item>
        <v-list-item :href="phpbaseurl + 'sites/manager/CalcNorm/norm.php'">
          <v-list-item-content>
            Calc Norm
          </v-list-item-content>
        </v-list-item>
      </v-list-group>

      <v-list-item to="/info/partners">
        <v-list-item-content>Partners</v-list-item-content>
      </v-list-item>
    </v-list>

  </div>
</template>

<script>
import { phpbaseurl } from '@/util/cms'

export default {

  name: 'TheSidebar',

  data() {
    return {
      fixtoolbar: false,
      authenticated: false,
      phpbaseurl
    }
  },

  computed: {
    gotorating() {
      return this.$i18n.locale === 'nl' ? '/tools/ratingnl' : '/tools/ratingfr'
    }
  },

  methods: {
    setLocale(l) {
      this.$i18n.setLocale(l)
    },
  }

}

</script>

<style scoped>
.v-application .primary--text {
  color: white !important;
}

.v-list-item__content {
  color: white !important;
}

.fixtoolbar {
  top: 50px;
}

.btn-language {
  min-width: 0 !important;
}
</style>
