<template>
  <div>
    <v-container>
      <v-row>
        <v-col cols="4" md="2">
          <v-img contain src="/img/logo.svg" />
        </v-col>
        <v-col cols="8" sm="7">
          <h1>{{ page.title }}</h1>
          <nuxt-content :document="page" />
        </v-col>
        <v-col cols="12" sm="3">
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
                <a class="green--text" :href="phpbaseurl + 'sites/manager/GestionCOMMON/GestionLogin.php'">
                  Player - Club -  Interclub manager
                </a>
              </div>
              <div class="pa-2">
                <a class="green--text" :href="phpbaseurl + 'sites/manager/GestionSWAR/SwarResults.php'">
                  {{ $t('Results SWAR') }}
                </a>
              </div>
              <div class="pa-2">
                <a class="green--text" @click="ratingtrn">
                  {{ $t('ELO tournaments') }}
                </a>
              </div>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>
      <v-row class="mt-2">
        <v-col v-for="a in articles3" :key="a.id" cols="12" sm="6" md="4">
          <v-card>
            <v-card-title class="green lighten-1 black--text pa-3 hyphen">
              {{ a.title }}
            </v-card-title>
            <v-card-text class="mt-2" v-html="a.intro" />
            <v-card-actions>
              <v-spacer />
              <v-btn @click="gotoArticle(a)">
                {{ $t('read more') }}
              </v-btn>
            </v-card-actions>
          </v-card>
        </v-col>
      </v-row>
    </v-container>
    <v-parallax
      v-if="$vuetify.breakpoint.mdAndUp"
      src="/img/chesscrowd_big.jpg"
      height="400"
    />
    <v-parallax
      v-if="$vuetify.breakpoint.sm"
      src="/img/chesscrowd_medium.jpg"
      height="300"
    />
    <v-parallax
      v-if="$vuetify.breakpoint.xs"
      src="/img/chesscrowd_small.jpg"
      height="200"
    />
    <v-container>
      <v-row class="mt-2">
        <v-col v-for="a in articlesRest" :key="a.id" cols="12" sm="6" md="4">
          <v-card>
            <v-card-title class="green lighten-1 black--text pa-3 hyphen">
              {{ a.title }}
            </v-card-title>
            <v-card-text class="mt-2" v-html="a.intro" />
            <v-card-actions>
              <v-spacer />
              <v-btn @click="gotoArticle(a)">
                {{ $t('read more') }}
              </v-btn>
            </v-card-actions>
          </v-card>
        </v-col>
      </v-row>
    </v-container>
  </div>
</template>

<script>

import { marked } from 'marked'
import { phpbaseurl, goto, notitle, nointro } from '@/util/cms'

export default {
  layout: 'landing',

  async asyncData ({ $content, app }) {
    const page = await $content('pages', `index_${app.i18n.locale}`).fetch()
    return {
      page
    }
  },

  data () {
    return {
      articles3: [],
      articlesRest: [],
      page: {},
      phpbaseurl
    }
  },

  mounted () {
    console.log('LandingPage Mounted')
    this.getActiveArticles()
  },

  methods: {

    getActiveArticles () {
      this.$api.content.getActiveArticles().then(
        (resp) => {
          console.log('get articles', resp.data.articles)
          this.readArticles(resp.data.articles)
        },
        resp => (console.error('could not fetch articles', resp))
      )
    },

    ratingtrn () {
      if (this.$i18n.locale == 'nl') { window.location.href = '/ratingnl' } else { window.location.href = '/ratingfr' }
    },

    readArticles (articles) {
      const locale = this.$i18n.locale
      this.articles3 = []
      this.articleRest = []
      articles.forEach((a, index) => {
        const b = { slug: a.slug }
        console.log('art', a.intro.nl.value)
        if (!a.title[locale] || !a.title[locale].value || !a.title[locale].value.length) {
          b.title = notitle[locale]
        } else {
          b.title = a.title[locale].value
        }
        if (!a.intro[locale] || !a.intro[locale].value || !a.intro[locale].value.length) {
          b.intro = marked.parse(nointro[this.$i18n.locale])
        } else {
          b.intro = marked.parse(a.intro[locale].value)
        }
        console.log('b', b)
        if (index < 3) {
          this.articles3.push(b)
        } else {
          this.articlesRest.push(b)
        }
      })
    }
  }

}
</script>

<style>
h1:after
{
    content:' ';
    display: block;
    border:1px solid #aaa;
    margin-bottom: 1em;
}
.nuxt-content td, .nuxt-content th {
  padding: 8px;
  border: 1px solid #ddd;
}
.nuxt-content table {
  border-collapse: collapse;
}
.nuxt-content ul , .nuxt-content ol, .nuxt-content h2, .nuxt-content h3 {
    margin-bottom: 0.5em;
}
</style>
