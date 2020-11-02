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
            <h4>{{ $t('Tools') }}</h4>
          </v-card-title>
          <v-card-text>
            <div class="pa-2">
              <a class="green--text" :href="phpbaseurl + 'sites/manager/GestionFICHES/FRBE_Fiche.php'">
                Elo
              </a> Naamloze
            </div>
            <div class="pa-2">
              <a  class="green--text" :href="phpbaseurl + 'sites/manager/GestionCOMMON/GestionLogin.php'">
                Player - Club -  Interclub manager
              </a> 
            </div>            
            <div class="pa-2">
              <a  class="green--text" :href="phpbaseurl + 'sites/manager/GestionSWAR/SwarResults.php'">
                {{ $t('Results SWAR') }}
              </a> 
            </div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
    <v-row class="mt-2">
      <v-col cols=12 sm=6 md=4 v-for="art in articles3" :key="art.id">
        <v-card>
          <v-card-title class="green lighten-1 black--text pa-3 hyphen">
            {{ art.page_i18n_fields[locale].title }}
          </v-card-title>
          <v-card-text class="mt-2">
            {{ art.page_i18n_fields[locale].intro }}
          </v-card-text>
          <v-card-actions>
            <v-spacer />
            <v-btn @click="gotoArticle(art)">{{ $t('read more') }}</v-btn>
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
    <v-row class="mt-2">
      <v-col cols=12 sm=6 md=4 v-for="art in articlesRest" :key="art.id">
        <v-card >
          <v-card-title class="green lighten-1 black--text pa-3 hyphen">
            {{ art.page_i18n_fields[locale].title }}
          </v-card-title>
          <v-card-text class="mt-2">
            {{ art.page_i18n_fields[locale].intro }}
          </v-card-text>
          <v-card-actions>
            <v-spacer />
            <v-btn @click="gotoArticle(art)">{{ $t('read more') }}</v-btn>
          </v-card-actions>            
        </v-card>
        <v-card v-if="locale in art.page_i18n_fields == false">
          <v-card-title class="green lighten-1 black--text pa-3">
            <i18n-text 
              nl="Geen titel beschikbaar"
            />
          </v-card-title>
          <v-card-text class="mt-2">

          </v-card-text>
          <v-card-actions>
            <v-spacer />
            <v-btn @click="gotoArticle(art)">{{ $t('read more') }}</v-btn>
          </v-card-actions>            
        </v-card>
      </v-col>
    </v-row>
  </v-container>  
 </div>
</template>

<script>
import { mapState } from "vuex"
import marked from 'marked'
import { notitle, nointro, phpbaseurl  } from "@/util/cms"


export default {

  name: 'LandingPage',

  data () {return {
    articles3: [],
    articlesRest: [],
    page: {},
    phpbaseurl: phpbaseurl,
  }},

  computed: {
    body () { 
      let pt = '';
      if (this.page.body) {
        pt = this.page.body.default.value;
        if (this.page.body[this.locale]) 
          pt = this.page.body[this.locale].value;
      }
      return marked(pt);
    },
    intro () { 
      let pt = '';
      if (this.page.intro) {
        pt = this.page.intro.default.value;
        if (this.page.intro[this.locale]) 
          pt = this.page.intro[this.locale].value;
      }
      return marked(pt);
    },
    title () {
      let pt = '';
      if (this.page.title) {
        pt = this.page.title.default.value;
        if (this.page.title[this.locale]) 
          pt = this.page.title[this.locale].value;
      }
      return pt;
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
      console.log('trying to get pages')
      this.api.anon_slug_page({
        slug: this.slug,
      }).then(
        function(data){
          self.page =  data.obj;
        },
        function(data){
          console.error('could not fetch localized page', data)
        }
      );
    },

    gotoArticle(art) {
      this.$router.push('/page/' +  art.slug + '/' + this.locale)
    },

    readArticles(art) {
      let self=this;
      this.articles3 = [];
      this.articleRest = [];
      art.forEach(function (a, index) {
        if (self.locale in a.page_i18n_fields === false) {
          a.page_i18n_fields[self.locale] = {
            title: '',
            intro: '',
            body: ''
          }
        }
        if (!a.page_i18n_fields[self.locale].title)
          a.page_i18n_fields[self.locale].title = notitle[self.locale];
        if (!a.page_i18n_fields[self.locale].intro)
          a.page_i18n_fields[self.locale].intro = nointro[self.locale];
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
    console.log('LandingPage Mounted', this.slug)
    this.getContent();
    // this.getActiveArticles();
  },

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

.hyphen {
  word-break: normal;
}
</style>
