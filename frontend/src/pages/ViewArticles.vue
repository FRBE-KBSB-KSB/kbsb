<template>
  <v-app>
    <sidebar />
    <topbar />
    <v-content>
      <v-container grid-list-md>
        <h1>Articles</h1>
        <v-layout row wrap >
            <v-flex xs12 sm6 md4 xl3 v-for="art in articles" :key="art.id">
              <v-card class="my-2">
                <v-card-title class="green lighten-2">
                  <h4>{{ art.title || art.maintitle }}</h4>
                </v-card-title>
                <v-card-text v-html="intro(art)">
                  
                </v-card-text>
                <v-card-actions>
                  <v-btn @click="openArticle(art)">Read more</v-btn>
                </v-card-actions>
              </v-card>            
            </v-flex>
        </v-layout>  
      </v-container>
    </v-content>
    <ad-carousel class="mt-4 mb-3"/>
    <kbsb-footer />
  </v-app>
</template>

<script>

import api from '../util/api'
import marked from 'marked'

import Sidebar from '../components/Sidebar'
import Topbar from '../components/Topbar'
import KbsbFooter from '../components/KbsbFooter'
import AdCarousel from '../components/AdCarousel'

export default {

  name: "ViewArticles",

  data () {return {
    articles: [],
  }},

  components: {
    'sidebar': Sidebar,
    'topbar': Topbar,
    'kbsb-footer': KbsbFooter,
    'ad-carousel': AdCarousel,
  },

  methods: {

    getArticles() {
      api('getArticles', {}).then(
        function(data) {
          this.articles = data.articles;
        }.bind(this));
    },

    intro (art){
      var html = marked(art.title || "")
      console.log('html', html)
      return html
    },

    openArticle(art) {
      window.location.href = '/articles/view/'+ art.slug;
    },

  },

  mounted () {
    this.getArticles();
  },

}
</script>

<style scoped>

</style>