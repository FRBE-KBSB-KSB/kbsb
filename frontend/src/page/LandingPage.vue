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
        <h1>{{ title }}</h1>
        <div class="mt-1" v-html="intro" />
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
              </a>
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
            <div class="pa-2">
              <a  class="green--text" @click="ratingtrn">
                {{ $t('ELO tournaments') }}
              </a> 
            </div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
    <v-row class="mt-2">
      <v-col cols=12 sm=6 md=4 v-for="a in articles3" :key="a.id">
        <v-card>
          <v-card-title class="green lighten-1 black--text pa-3 hyphen">
            {{ a.title[locale].value }}
          </v-card-title>
          <v-card-text class="mt-2" v-html="marked(a.intro[locale].value)">
          </v-card-text>
          <v-card-actions>
            <v-spacer />
            <v-btn @click="gotoArticle(a)">{{ $t('read more') }}</v-btn>
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
      <v-col cols=12 sm=6 md=4 v-for="a in articlesRest" :key="a.id">
        <v-card >
          <v-card-title class="green lighten-1 black--text pa-3 hyphen">
            {{ a.title[locale].value }}
          </v-card-title>
          <v-card-text class="mt-2" v-html="marked(a.intro[locale].value)">
          </v-card-text>
          <v-card-actions>
            <v-spacer />
            <v-btn @click="gotoArticle(a)">{{ $t('read more') }}</v-btn>
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
import { notitle, nointro, phpbaseurl, goto } from "@/util/cms"


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
      this.api.getActiveArticles().then(
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
      goto('page', art.slug, this.locale)
    },

    marked(s) { 
      return marked(s ? s : '')
    }, 

    readArticles(articles) {
      let self=this;
      this.articles3 = [];
      this.articleRest = [];
      articles.forEach((a, index) =>  {
        console.log('art', a.title)
        if ( !a.title[self.locale] || !a.title[self.locale].value 
              || !a.title[self.locale].value.length ) {
          a.title[self.locale] = {value: notitle[self.locale]};
        }
        if ( !a.intro[self.locale] || !a.intro[self.locale].value || 
            !a.intro[self.locale].value.length) {
          a.intro[self.locale] = {value: nointro[self.locale]};
        }
        if (index < 3) {
          self.articles3.push(a);
        }
        else {
          self.articlesRest.push(a);
        }
      })
    },

    ratingtrn() {
      goto('rating', "", this.locale)      
    }

  },

  mounted () {
    console.log('LandingPage Mounted', this.slug, this.locale, this.$t('Tools'))
    this.getContent();
    this.getActiveArticles();
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
