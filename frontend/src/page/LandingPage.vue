<template>
 <div>
  <v-parallax  v-if="$vuetify.breakpoint.mdAndUp"
                src="@/assets/img/landing_big.jpg" height="400" />
  <v-parallax v-if="$vuetify.breakpoint.sm"
              src="@/assets/img/landing_medium.jpg" height="300" />
  <v-parallax v-if="$vuetify.breakpoint.xs"
              src="@/assets/img/landing_small.jpg" height="200" />   
  <v-container class="mt-1">
    <v-row>
      <v-col cols=12 sm=8>
        <h1 v-html="title" />
        <div v-html="intro" class="mt-1"/>
        <hr/>
        <div v-html="body" class="mt-1" />
      </v-col>
      <v-col cols=12 sm=4>
        <v-card>
          <v-card-title class="green darken-1 white--text pa-3">
            <h4><i18n-text 
              nl="Tools"
              fr="Outils"
              de="Wekzeuge"
              en="Tools"
            /></h4>
          </v-card-title>
          <v-card-text>
            <div class="pa-2">
              <a class="green--text" :href="phpbaseurl + 'sites/manager/GestionFICHES/FRBE_Fiche.php'">
                Elo
              </a> 
            </div>
            <div class="pa-2">
              <a  class="green--text" :href="phpbaseurl + 'sites/manager/GestionCOMMON/GestionLogin.php'">
                Player - Club -  Interclub manager
              </a> 
            </div>            
            <div class="pa-2">
              <a  class="green--text" :href="phpbaseurl + 'sites/manager/GestionSWAR/SwarResults.php'">
                <i18n-text 
                  nl="Resulaten SWAR"  
                  fr="Résultats SWAR" 
                  de="Ergebnisse SWAR"
                  en="Results SWAR"
                />
              </a> 
            </div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
    <v-row class="mt-2">
      <v-col cols=12 sm=6 md=4 v-for="art in articles3" :key="art.id">
        <v-card>
          <v-card-title class="green lighten-1 black--text pa-3">
            {{ art.page_i18n_fields[locale].title }}
          </v-card-title>
          <v-card-text class="mt-2">
            {{ art.page_i18n_fields[locale].intro }}
          </v-card-text>
          <v-card-actions>
            <v-spacer />
            <v-btn>
              <i18n-text 
                nl="lees meer"  
                fr="en savoir plus"
                de="weiter lesen"
                en="read more"
              />
            </v-btn>
          </v-card-actions>            
        </v-card>
      </v-col>
    </v-row>
  </v-container>
  <v-parallax  v-if="$vuetify.breakpoint.mdAndUp"
    src="@/assets/img/chesscrowd_big.jpg" height="400" />
  <v-parallax  v-if="$vuetify.breakpoint.sm"
    src="@/assets/img/chesscrowd_medium.jpg" height="300" />
  <v-parallax v-if="$vuetify.breakpoint.xs"
    src="@/assets/img/chesscrowd_small.jpg" height="200" />
  <v-container>
    <h4>The other articles</h4>
  </v-container>  
 </div>
</template>

<script>
import {mapState} from "vuex"
import marked from 'marked'
import I18nText from "@/components/I18nText"

export default {

  name: 'LandingPage',

  data () {return {
    articles3: [],
    articlesRest: [],
    page: {},
    phpbaseurl: "https://www.frbe-kbsb.be/",
  }},

  components: {
    I18nText, 
  },

  computed: {
    body () { 
      return marked(this.page.body || '' )
    },
    intro () { 
      return marked(this.page.intro || '' )
    },
    title () { 
      return this.page.title || '' 
    },
    ...mapState(['api', 'locale', 'slug']),

  },

  methods: {
    
    getActiveArticles () {
      let self=this;
      this.api.get_activearticles().then(
        function(data){
          self.readArticles(data.obj.articles);
        },
        function(data){
          console.error('could not fetch articles', data)
        }
      );
    },

    getContent () {
      let self=this;
      this.api.get_localized_page({
        slug: this.slug,
        locale: this.locale,
      }).then(
        function(data){
          self.page =  data.obj.page;
        },
        function(data){
          console.error('could not fetch localized page', data)
        }
      );
    },

    readArticles(art) {
      let self=this;
      this.articles3 = [];
      this.articleRest = [];
      art.forEach(function (a, index) {
        if (index < 3) {
          self.articles3.push(a);
        }
        else {
          self.articlesRest.push(a);
        }
      })
       
    },

  },

  mounted () {
    this.getContent();
    this.getActiveArticles();
  },

  watch: {
    locale: function (nv, ov) {
      console.log('watch locale', nv, ov)
      this.$router.push('/page/' + this.slug + '/' + nv)
    },
    slug: function (nv, ov) {
      console.log('watch slug', nv, ov)
      this.$router.push('/page/' + nv + '/' + this.locale)
    },
  }

}
</script>


<style scoped>

.markedcontent table {
  border-collapse: collapse;
  min-width: 30em;
}

.markedcontent table {
  border: 1px solid black;
}

.markedcontent td {
  border: 1px solid black;
  padding: 6px;
}

.markedcontent  th {
  border: 1px solid black;
  padding: 6px;
}

a {
  text-decoration: none;
}

a:hover {
  font-weight: bold;
}

</style>
