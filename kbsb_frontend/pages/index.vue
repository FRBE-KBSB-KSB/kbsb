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
                <a class="green--text"
                  :href="phpbaseurl + 'sites/manager/GestionFICHES/FRBE_Fiche.php'">
                  Elo
                </a>
              </div>
              <div class="pa-2">
                <b>NEW</b> <a class="green--text" href="/tools/club">
                  Club manager
                </a>
              </div>
              <div class="pa-2">
                <a class="green--text" href="/tools/interclub">
                  Interclub manager
                </a>
              </div>
              <div class="pa-2">
                <a class="green--text"
                  :href="phpbaseurl + 'sites/manager/GestionCOMMON/GestionLogin.php'">
                  Player manager
                </a>
              </div>
              <div class="pa-2">
                <a class="green--text"
                  :href="phpbaseurl + 'sites/manager/GestionSWAR/SwarResults.php'">
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
          <v-card class="mt-2">
            <v-card-title class="green darken-1 white--text pa-3 hyphen">
              {{ $t('Calendar') }}
            </v-card-title>
            <v-card-text class="mt-2">
              <ul>
                <li v-for="c, ix in future_4ci" :key="ix">
                  {{ calenderItem(c) }}
                </li>
              </ul>
            </v-card-text>
            <v-card-actions>
              <v-spacer />
              <v-btn to="/info/calendar">
                {{ $t('More') }} ...
              </v-btn>
            </v-card-actions>
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
    <v-parallax v-if="$vuetify.breakpoint.mdAndUp" src="/img/chesscrowd_big.jpg" height="400" />
    <v-parallax v-if="$vuetify.breakpoint.sm" src="/img/chesscrowd_medium.jpg" height="300" />
    <v-parallax v-if="$vuetify.breakpoint.xs" src="/img/chesscrowd_small.jpg" height="200" />
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
import { phpbaseurl, notitle, nointro } from '@/util/cms'

function compareDates(a, b) {
  return a.date - b.date
}

export default {
  layout: 'landing',

  data() {
    return {
      articles3: [],
      articlesRest: [],
      calitems: [],
      page__nl: {},
      page__fr: {},
      page__de: {},
      page__en: {},
      phpbaseurl
    }
  },

  async fetch() {
    this.page__nl = await this.$content('pages', 'index_nl').fetch()
    this.page__fr = await this.$content('pages', 'index_fr').fetch()
    this.page__de = await this.$content('pages', 'index_de').fetch()
    this.page__en = await this.$content('pages', 'index_en').fetch()
    this.parseCalendarItems(await this.$content('calendar').fetch())
    this.calitems.sort(compareDates)
  },

  computed: {
    page() { return this['page__' + this.$i18n.locale] },
    future_4ci() {
      const yesterday = new Date() - 86400000
      return this.calitems.filter(ci => ci.date > yesterday).slice(0, 4)
    }
  },

  mounted() {
    this.getActiveArticles()
  },

  methods: {

    calenderItem(c) {
      const output = []
      output.push(c.date.toLocaleDateString(this.$i18n.locale, { dateStyle: 'medium' }) + ':')
      output.push(c.title)
      if (c.round) {
        output.push(this.$t('Round'))
        output.push(c.round)
      }
      return output.join(' ')
    },

    getActiveArticles() {
      console.log('fetching articles', this.$api)
      this.$api.page.get_anon_articles().then(
        (resp) => {
          console.log('got articles', resp.data.pages)
          this.readArticles(resp.data.pages)
        },
        resp => (console.error('could not fetch articles', resp))
      )
    },

    gotoArticle(a) {
      window.location.href = '/article?slug=' + a.slug
    },

    parseCalendarItems(listci) {
      listci.forEach((ci) => {
        if (ci.multiple) {
          this.parseCalendarItems(ci.multiple)
        }
        if (ci.date) {
          const item = { ...ci, date: new Date(ci.date) }
          this.calitems.push(item)
          return
        }
        if (ci.rounds) {
          Object.entries(ci.rounds).forEach(([rnr, date]) => {
            const { rounds, ...item } = { ...ci, date: new Date(date), round: rnr }
            this.calitems.push(item)
          })
        }
      })
    },

    ratingtrn() {
      if (this.$i18n.locale === 'nl') {
        window.location.href = '/tools/ratingnl'
      } else {
        window.location.href = '/tools/ratingfr'
      }
    },

    readArticles(articles) {
      const locale = this.$i18n.locale
      this.articles3 = []
      this.articleRest = []
      articles.forEach((a, index) => {
        const b = { slug: a.slug }
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
h1:after {
  content: ' ';
  display: block;
  border: 1px solid #aaa;
  margin-bottom: 1em;
}

.nuxt-content td,
.nuxt-content th {
  padding: 8px;
  border: 1px solid #ddd;
}

.nuxt-content table {
  border-collapse: collapse;
}

.nuxt-content ul,
.nuxt-content ol,
.nuxt-content h2,
.nuxt-content h3 {
  margin-bottom: 0.5em;
}
</style>
