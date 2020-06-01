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
          <v-list-item-content>
              <i18n-text 
                nl="Home" 
                fr="Accueil" 
                de="Startseite" 
                en="Home" />
          </v-list-item-content>
        </v-list-item>
        <v-list-group no-action >
          <template v-slot:activator>
            <v-list-item-content  >
              <i18n-text 
                nl="Beheer" 
                fr="Adminstration" 
                de="Administration" 
                en="Adminstration" />
            </v-list-item-content>
          </template>
          <v-list-item @click="updateSlug('board')" >
            <v-list-item-content>
              <i18n-text 
                nl="Bestuur" 
                fr="Conseil d'Adminstration" 
                de="Verwaltungsraad" 
                en="Board" />              
            </v-list-item-content>
          </v-list-item>
          <v-list-item @click="updateSlug('statutes')" >
            <v-list-item-content>
              <i18n-text 
                nl="Statuten" 
                fr="Statuts" 
                de="Statuten" 
                en="Statutes" />              
            </v-list-item-content>
          </v-list-item>
          <v-list-item @click="updateSlug('tournament-rules')" >
            <v-list-item-content>
              <i18n-text 
                nl="Wedstrijdreglement" 
                fr="Règlement des tournois" 
                de="Turnierregeln" 
                en="Tournament rules" />              
            </v-list-item-content>
          </v-list-item>
          <v-list-item @click="updateSlug('internal-rules')" >
            <v-list-item-content>
              <i18n-text 
                nl="Intern Reglement" 
                fr="Règlement d'ordre intérieur" 
                de="Hausinterne Satzung" 
                en="Internal rules" />              
            </v-list-item-content>
          </v-list-item>
          <v-list-item @click="updateSlug('reports')" >
            <v-list-item-content>
              <i18n-text 
                nl="Verslagen" 
                fr="Procès verbaux" 
                de="Berichte" 
                en="Reports" />              
            </v-list-item-content>
          </v-list-item>
          <v-list-item @click="updateSlug('vademecum')" >
            <v-list-item-content>
              Vademecum
            </v-list-item-content>
          </v-list-item>
          <v-list-item @click="updateSlug('regional')" >
            <v-list-item-content>
              <i18n-text 
                nl="Regionaal" 
                fr="Régional" 
                de="Regional" 
                en="Regional" />              
            </v-list-item-content>
          </v-list-item>
          <v-list-item @click="updateSlug('commissions')" >
            <v-list-item-content>
              <i18n-text 
                nl="Commissies" 
                fr="Commissions" 
                de="Ausschüsse" 
                en="Committees" />              
            </v-list-item-content>
          </v-list-item>
        </v-list-group>   
        <v-list-group no-action>
          <template v-slot:activator>
            <v-list-item-content>
              <i18n-text 
                nl="Competities" 
                fr="Compétitions" 
                de="Wettbewerbe" 
                en="Competitions" />
            </v-list-item-content>
          </template>
          <v-list-item @click="updateSlug('interclub-2019-20')" >
            <v-list-item-content>
              Interclub 2019-20              
            </v-list-item-content>
          </v-list-item>
          <v-list-item @click="updateSlug('interclub-2020-21')" >
            <v-list-item-content>
              Interclub 2020-21              
            </v-list-item-content>
          </v-list-item>
          <v-list-item @click="updateSlug('championships-adult')" >
            <v-list-item-content>
              <i18n-text 
                nl="BK volwassenen" 
                fr="CB adultes" 
                de="BLM Erwachsene" 
                en="BC Adults" />              
            </v-list-item-content>
          </v-list-item>
          <v-list-item @click="updateSlug('championships-blitz')" >
            <v-list-item-content>
              <i18n-text 
                nl="BK Blitz" 
                fr="CB Blitz" 
                de="BLM Blitz" 
                en="BC Blitz" />              
            </v-list-item-content>
          </v-list-item>
          <v-list-item @click="updateSlug('championships-rapid')" >
            <v-list-item-content>
              <i18n-text 
                nl="BK Rapid" 
                fr="CB Rapid" 
                de="BLM Rapid" 
                en="BC Rapid" />              
            </v-list-item-content>
          </v-list-item>
          <v-list-item @click="updateSlug('international-adults')" >
            <v-list-item-content>
              <i18n-text 
                nl="Internationale competities" 
                fr="Compétitions internationales" 
                de="Internationale Wettbewerbe" 
                en="International competitions" />              
            </v-list-item-content>
          </v-list-item>
        </v-list-group>

        <v-list-group no-action>
          <template v-slot:activator>
            <v-list-item-content>
              <i18n-text 
                nl="Jeugd" 
                fr="Jeunesse" 
                de="Jugend" 
                en="Youth" />
            </v-list-item-content>
          </template>
          <v-list-item @click="updateSlug('championships-youth')" >
            <v-list-item-content>
              <i18n-text 
                nl="BK jeugd" 
                fr="CB jeunesse" 
                de="Administration" 
                en="Adminstration" />              
            </v-list-item-content>
          </v-list-item>
          <v-list-item @click="updateSlug('international-youth')" >
            <v-list-item-content>
              <i18n-text 
                nl="Internationaal" 
                fr="International" 
                de="International" 
                en="International" />              
            </v-list-item-content>
          </v-list-item>
          <v-list-item @click="updateSlug('top-talent')" >
            <v-list-item-content>
              Top Talent
            </v-list-item-content>
          </v-list-item>
          <v-list-item @click="updateSlug('school-chess')" >
            <v-list-item-content>
              <i18n-text 
                nl="BK Schoolschaak" 
                fr="CB inter-écoles " 
                de="BLM Schulschah" 
                en="BC School Chess" />              
            </v-list-item-content>
          </v-list-item>
        </v-list-group>
        <v-list-group no-action>
          <template v-slot:activator>
            <v-list-item-content>
              <i18n-text 
                nl="Nuttige informatie" 
                fr="Information utile" 
                de="Nützliche Informationen" 
                en="Useful information" />
            </v-list-item-content>
          </template>
          <v-list-item @click="updateSlug('email-addresses')" >
            <v-list-item-content>
              <i18n-text 
                nl="E-mailadressen" 
                fr="Adresses e-mail" 
                de="E-mailadressen" 
                en="Email addresses" />              
            </v-list-item-content>
          </v-list-item>
          <v-list-item @click="updateSlug('elo-processing')" >
            <v-list-item-content>
              <i18n-text 
                nl="ELO-verwerking" 
                fr="Traitement ELO" 
                de="ELO-Verarbeitung"
                en="ELO processing" />              
            </v-list-item-content>
          </v-list-item>
          <v-list-item @click="updateSlug('fide')" >
            <v-list-item-content>
              FIDE
            </v-list-item-content>
          </v-list-item>
          <v-list-item @click="updateSlug('g-licence')" >
            <v-list-item-content>
              <i18n-text 
                nl="G licentie" 
                fr="Licence G"
                de="G Lizenz" 
                en="G License" />              
            </v-list-item-content>
          </v-list-item>
          <v-list-item @click="updateSlug('equipment')" >
            <v-list-item-content>
              <i18n-text 
                nl="Schaakmateriaal" 
                fr="Equipement d'échecs" 
                de="Schachausrüstung" 
                en="Chess equiment" />              
            </v-list-item-content>
          </v-list-item>
        </v-list-group>
        <v-list-group no-action>
          <template v-slot:activator>
            <v-list-item-content>
              <i18n-text 
                nl="Tools" 
                fr="Outils" 
                de="Werkzeuge" 
                en="Tools" />              
            </v-list-item-content>
          </template>
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
            <v-list-item-content>
              <i18n-text 
                nl="SWAR-Resultaten" 
                fr="Résultats SWAR" 
                de="SWAR-Ergebnisse" 
                en="Results SWAR" />              
            </v-list-item-content>
          </v-list-item>
          <v-list-item :href="phpbaseurl + 'sites/manager/CalcNorm/norm.php'">
            <v-list-item-content>
              Calc Norm
            </v-list-item-content>
          </v-list-item>
        </v-list-group>
      </v-list>
    </v-navigation-drawer>
</template>

<script>

import I18nText from "@/components/I18nText"

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
  },

  components: {
    I18nText,
  },

  data () {return {
    fixtoolbar: false,
    authenticated: false,
    phpbaseurl: "https://www.frbe-kbsb.be/",
  }},

  mounted() {

  },

  methods: {
    updateLocale: function(l){
      this.$store.commit('updateLocale', l)
    },
    updateSlug: function(s){
      console.log('updating slug', s)
      this.$store.commit('updateSlug', s)
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