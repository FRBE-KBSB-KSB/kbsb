<template>
  <div>
    <v-toolbar text class="green" dark>
      <v-list>
        <v-list-item>
          <v-list-item-title class="title">
            Menu
          </v-list-item-title>
        </v-list-item>
      </v-list>
    </v-toolbar>

    <v-divider />

    <div class="btn-language green darken-1">
      <v-btn text dark class="hover-darker btn-language" @click="$i18n.setLocale('nl')">
        NL
      </v-btn>
      <v-btn text dark class="hover-darker btn-language" @click="$i18n.setLocale('fr')">
        FR
      </v-btn>
      <v-btn text dark class="hover-darker btn-language" @click="$i18n.setLocale('de')">
        DE
      </v-btn>
      <v-btn text dark class="hover-darker btn-language" @click="$i18n.setLocale('en')">
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
        <v-list-item to="/board">
          <v-list-item-content>{{ $t('Board') }}</v-list-item-content>
        </v-list-item>
        <v-list-item to="/statutes">
          <v-list-item-content>{{ $t('Statutes') }}</v-list-item-content>
        </v-list-item>
        <v-list-item to="/tournament-rules">
          <v-list-item-content>{{ $t('Tournament rules') }}</v-list-item-content>
        </v-list-item>
        <v-list-item to="/internal-rules">
          <v-list-item-content>{{ $t('Internal rules') }}</v-list-item-content>
        </v-list-item>
        <v-list-item to="/reports">
          <v-list-item-content>{{ $t('Reports') }}</v-list-item-content>
        </v-list-item>
        <v-list-item to="/vademecum">
          <v-list-item-content>Vademecum</v-list-item-content>
        </v-list-item>
        <v-list-item to="/regional">
          <v-list-item-content>{{ $t('Regional') }} </v-list-item-content>
        </v-list-item>
        <v-list-item to="/commissions">
          <v-list-item-content>{{ $t('Committees') }} </v-list-item-content>
        </v-list-item>
        <v-list-item to="/book100">
          <v-list-item-content>{{ $t('Book 100 years') }} </v-list-item-content>
        </v-list-item>
      </v-list-group>

      <v-list-group no-action>
        <template #activator>
          <v-list-item-content>{{ $t('Competitions') }}</v-list-item-content>
        </template>
        <v-list-item to="/interclub-2019-20">
          <v-list-item-content>
            Interclub 2019-20
          </v-list-item-content>
        </v-list-item>
        <v-list-item to="/interclub-2021-22">
          <v-list-item-content>
            Interclub 2021-22
          </v-list-item-content>
        </v-list-item>
        <v-list-item to="/championships-adult">
          <v-list-item-content>{{ $t('BC Adults') }} </v-list-item-content>
        </v-list-item>
        <v-list-item to="/championships-blitz">
          <v-list-item-content>{{ $t('BC Blitz') }}</v-list-item-content>
        </v-list-item>
        <v-list-item to="/championships-rapid">
          <v-list-item-content>{{ $t('BC Rapid') }} </v-list-item-content>
        </v-list-item>
        <v-list-item to="/international-adults">
          <v-list-item-content>{{ $t('International competitions') }}</v-list-item-content>
        </v-list-item>
      </v-list-group>

      <v-list-group no-action>
        <template #activator>
          <v-list-item-content>{{ $t('Youth') }}</v-list-item-content>
        </template>
        <v-list-item to="/championships-youth">
          <v-list-item-content>{{ $t('BC Youth') }}</v-list-item-content>
        </v-list-item>
        <v-list-item to="/international-youth">
          <v-list-item-content>{{ $t('International') }}}</v-list-item-content>
        </v-list-item>
        <v-list-item to="/school-chess">
          <v-list-item-content>{{ $t('BC School chess') }}</v-list-item-content>
        </v-list-item>
      </v-list-group>

      <v-list-group no-action>
        <template #activator>
          <v-list-item-content>{{ $t('Useful information') }}</v-list-item-content>
        </template>
        <v-list-item to="/email-addresses">
          <v-list-item-content>{{ $t('Email addresses') }}</v-list-item-content>
        </v-list-item>
        <v-list-item to="/elo-processing">
          <v-list-item-content>{{ $t('ELO processing') }}</v-list-item-content>
        </v-list-item>
        <v-list-item to="/gdpr')">
          <v-list-item-content>{{ $t('GDPR') }}</v-list-item-content>
        </v-list-item>
        <v-list-item to="/g-licence">
          <v-list-item-content>{{ $t('G License') }} </v-list-item-content>
        </v-list-item>
      </v-list-group>

      <v-list-group no-action>
        <template #activator>
          <v-list-item-content>{{ $t('Tools') }}</v-list-item-content>
        </template>
        <v-list-item to="/ratedtournaments">
          <v-list-item-content>
            {{ $t('ELO tournaments') }}
          </v-list-item-content>
        </v-list-item>
        <v-list-item :href="phpbaseurl + 'sites/manager/GestionCOMMON/GestionLogin.php'">
          <v-list-item-content>
            Player - Club Manager
          </v-list-item-content>
        </v-list-item>
        <v-list-item :href="phpbaseurl + 'sites/manager/GestionCOMMON/GestionLogin.php'">
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

      <v-list-item to="/partners">
        <v-list-item-content>Partners</v-list-item-content>
      </v-list-item>
    </v-list>
  </div>
</template>

<script>
import { phpbaseurl } from '@/util/cms'

export default {

  name: 'TheSidebar',

  data () {
    return {
      fixtoolbar: false,
      authenticated: false,
      phpbaseurl
    }
  },

  methods: {

    ratedtournaments () {
      // goto('rating', "", this.locale)
    },

    updateLocale (l) {
      // goto(window.base.section, this.slug || "", l)
      // this.$router.push('/page/'+ this.slug + '/' + l)
    },

    updateSlug (s) {
      // goto('page', s, this.locale)
      // this.$router.push('/page/'+ s + '/' + this.locale)
    }

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
