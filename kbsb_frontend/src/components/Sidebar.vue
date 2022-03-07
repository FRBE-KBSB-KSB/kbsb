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
      
        <v-list-item @click="updateSlug('home')">
          <v-list-item-content>{{ $t('Home') }}</v-list-item-content>
        </v-list-item>

        <v-list-group no-action >
          <template v-slot:activator>
            <v-list-item-content>{{ $t('Administration')}}</v-list-item-content>
          </template>
          <v-list-item @click="updateSlug('board')" >
            <v-list-item-content>{{ $t('Board') }}</v-list-item-content>
          </v-list-item>
          <v-list-item @click="updateSlug('statutes')" >
            <v-list-item-content>{{ $t('Statutes') }}</v-list-item-content>
          </v-list-item>
          <v-list-item @click="updateSlug('tournament-rules')" >
            <v-list-item-content>{{ $t('Tournament rules') }}</v-list-item-content>
          </v-list-item>
          <v-list-item @click="updateSlug('internal-rules')" >
            <v-list-item-content>{{ $t('Internal rules') }}</v-list-item-content>
          </v-list-item>
          <v-list-item @click="updateSlug('reports')" >
            <v-list-item-content>{{ $t('Reports') }}</v-list-item-content>
          </v-list-item>
          <v-list-item @click="updateSlug('vademecum')" >
            <v-list-item-content>Vademecum</v-list-item-content>
          </v-list-item>
          <v-list-item @click="updateSlug('regional')" >
            <v-list-item-content>{{ $t('Regional') }} </v-list-item-content>
          </v-list-item>
          <v-list-item @click="updateSlug('commissions')" >
            <v-list-item-content>{{ $t('Committees') }} </v-list-item-content>
          </v-list-item>
          <v-list-item @click="updateSlug('book100')" >
            <v-list-item-content>{{ $t('Book 100 years') }} </v-list-item-content>
          </v-list-item>
        </v-list-group>

        <v-list-group no-action>
          <template v-slot:activator>
            <v-list-item-content>{{ $t('Competitions') }}</v-list-item-content>
          </template>
          <v-list-item @click="updateSlug('interclub-2019-20')" >
            <v-list-item-content>
              Interclub 2019-20              
            </v-list-item-content>
          </v-list-item>
          <v-list-item @click="updateSlug('interclub-2021-22')" >
            <v-list-item-content>
              Interclub 2021-22              
            </v-list-item-content>
          </v-list-item>
          <v-list-item @click="updateSlug('championships-adult')" >
            <v-list-item-content>{{ $t('BC Adults')}} </v-list-item-content>
          </v-list-item>
          <v-list-item @click="updateSlug('championships-blitz')" >
            <v-list-item-content>{{ $t('BC Blitz')}}</v-list-item-content>
          </v-list-item>
          <v-list-item @click="updateSlug('championships-rapid')" >
            <v-list-item-content>{{ $t('BC Rapid') }} </v-list-item-content>
          </v-list-item>
          <v-list-item @click="updateSlug('international-adults')" >
            <v-list-item-content>{{ $t('International competitions')}}</v-list-item-content>
          </v-list-item>
        </v-list-group>

        <v-list-group no-action>
          <template v-slot:activator>
            <v-list-item-content>{{ $t('Youth') }}</v-list-item-content>
          </template>
          <v-list-item @click="updateSlug('championships-youth')" >
            <v-list-item-content>{{ $t('BC Youth') }}</v-list-item-content>
          </v-list-item>
          <v-list-item @click="updateSlug('international-youth')" >
            <v-list-item-content>{{ $t('International') }}}</v-list-item-content>
          </v-list-item>
          <v-list-item @click="updateSlug('top-talent')" >
            <v-list-item-content>
              Top Talent
            </v-list-item-content>
          </v-list-item>
          <v-list-item @click="updateSlug('school-chess')" >
            <v-list-item-content>{{ $t('BC School chess') }}</v-list-item-content>
          </v-list-item>
        </v-list-group>

        <v-list-group no-action>
          <template v-slot:activator>
            <v-list-item-content>{{ $t('Useful information')}}</v-list-item-content>
          </template>
          <v-list-item @click="updateSlug('email-addresses')">
            <v-list-item-content>{{ $t('Email addresses') }}</v-list-item-content>
          </v-list-item>
          <v-list-item @click="updateSlug('elo-processing')" >
            <v-list-item-content>{{ $t('ELO processing')}}</v-list-item-content>
          </v-list-item>
          <v-list-item @click="updateSlug('fide')" >
            <v-list-item-content>
              FIDE
            </v-list-item-content>
          </v-list-item>
          <v-list-item @click="updateSlug('gdpr')" >
            <v-list-item-content>{{ $t('GDPR') }}</v-list-item-content>
          </v-list-item>
          <v-list-item @click="updateSlug('g-licence')" >
            <v-list-item-content>{{ $t('G License')}} </v-list-item-content>
          </v-list-item>
          <v-list-item @click="updateSlug('equipment')" >
            <v-list-item-content>{{ $t('Chess equiment')}}</v-list-item-content>
          </v-list-item>
        </v-list-group>

        <v-list-group  no-action> 
          <template v-slot:activator>
            <v-list-item-content>{{ $t('Tools') }}</v-list-item-content>
          </template>
          <v-list-item @click="ratedtournaments">
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

        <v-list-item @click="updateSlug('partners')">
          <v-list-item-content>Partner</v-list-item-content>
        </v-list-item>
      </v-list>
    </v-navigation-drawer>
</template>

<script>

import { mapState } from 'vuex'
import { goto } from '@/util/cms'


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
    ...mapState(['slug', 'locale']),    
  },


  data () {return {
    fixtoolbar: false,
    authenticated: false,
    phpbaseurl: "https://www.frbe-kbsb.be/",
  }},

  mounted() {

  },

  methods: {

    ratedtournaments (){
      goto('rating', "", this.locale)
    },
    
    updateLocale: function(l){
      goto(window.base.section, this.slug || "", l)
      // this.$router.push('/page/'+ this.slug + '/' + l)
    },
    
    updateSlug: function(s){
      goto('page', s, this.locale)
      // this.$router.push('/page/'+ s + '/' + this.locale)
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
  min-width: 0;
}
</style>