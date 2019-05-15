<template>
  <v-app>
    <sidebar />
    <topbar />
    <v-content>
      <v-container grid-list-md>
        <h1>{{article.maintitle }}</h1>
          <v-tabs light slider-color="pink" v-model="langix">
            <v-tab class="mx-2"  v-for="l in languages" :key="l">
              <span>{{l}}</span>
            </v-tab>
          </v-tabs>
          <v-tabs-items v-model="langix">
            <v-tab-item  v-for="l in languages" :key="l"> 
              <div class="pa-2 mt-2" v-html="body[l]" /> 
            </v-tab-item>
          </v-tabs-items>
      </v-container>
    </v-content>
    <ad-carousel class="mt-4 mb-3"/>
    <kbsb-footer />
  </v-app>
</template>

<script>

import api from '../util/api'
import marked from 'marked'

import { loadLanguageAsync } from '../util/lang'

import Sidebar from '../components/Sidebar'
import Topbar from '../components/Topbar'
import KbsbFooter from '../components/KbsbFooter'
import AdCarousel from '../components/AdCarousel'

export default {

  name: "ViewArticle",

  data () {return {
    article: {},
    body: {},
    languages: ['nl', 'fr', 'de', 'en'],
    langix: 0,
  }},

  components: {
    'sidebar': Sidebar,
    'topbar': Topbar,
    'kbsb-footer': KbsbFooter,
    'ad-carousel': AdCarousel,
  },

  created () {
    loadLanguageAsync(window.config.lang);
  },

  methods: {

    getArticle() {
      var intro, content, title, ruler, locales;
      api('getArticle', {id: window.config.id}).then(
        function(data) {
          this.article = data.article;
          this.languages.forEach(function(l){
            locales = data.article[l];
            title = locales.title ?  "## " + locales.title  + "\n\n": "";
            ruler = locales.intro && locales.content ? "\n\n---\n<br>\n\n": "";
            intro = locales.intro ?  locales.intro + "\n\n": "";
            content = locales.content ? locales.content : "";
            this.body[l] = marked(title +  intro + ruler + content);  
          }.bind(this));
        }.bind(this));
    },


  },

  mounted () {
    this.langix = this.languages.indexOf(window.config.lang)
    console.log('getting article with id', window.config.id)
    this.getArticle();
  },

}
</script>

<style scoped>

</style>