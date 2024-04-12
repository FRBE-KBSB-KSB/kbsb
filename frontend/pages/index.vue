<script setup>
import showdown from 'showdown'
import { VContainer, VBtn, VCard, VCardTitle, VCardText, VCardActions, VRow, VCol, 
  VDialog, VProgressCircular, VImg, VSnackbar, VSpacer} from 'vuetify/components';


const localePath = useLocalePath()

const { locale, t } = useI18n()
const { $backend } = useNuxtApp()
const ttitle = `title_${locale.value}`
const tcontent = `content_${locale.value}`
const { data } = await useAsyncData('home',
  () => queryContent('/pages/').findOne())
const calitems = ref([])  
const { data: caldata } = await useAsyncData('calendar',
  () => queryContent('/calendar').find())
const articles = ref([])
const articles3 = ref([])
const articlesRest = ref([])

// wating dialog
let dialogcounter = 0
const waitingdialog = ref(false)
function changeDialogCounter(i) {
    dialogcounter += i
    waitingdialog.value = (dialogcounter > 0)
}

// snackbar
const errortext = ref(null)
const snackbar = ref(null) 
function displaySnackbar(text, color) {
  errortext.value = text
  snackbar.value = true
}

const mdConverter = new showdown.Converter()
function md(s) { return mdConverter.makeHtml(s) }

function compareDates(a, b) {
  return a.date - b.date
}

const future_ci = computed(() => {
  const yesterday = new Date() - 86400000
  return calitems.value.filter(ci => ci.date > yesterday).slice(0, 4)
})

function calenderItem(c) {
  const output = []
  output.push(c.date.toLocaleDateString(locale, { dateStyle: 'medium' }) + ':')
  output.push(c.title)
  if (c.round) {
    output.push(t('Round'))
    output.push(c.round)
  }
  if (c.status === 'postponed') {
    output.push(t('postponed'))
  }
  return output.join(' ')
}

function calenderText(c) {
  return ''
}

function gotoArticle (a) {
  navigateTo(localePath('/article?slug=' + a.slug))
}

function parseCalendarItems(listci) {
  listci.forEach((ci) => {
    if (ci.multiple) {
      parseCalendarItems(ci.multiple)
      return
    }
    if (ci.date) {
      const item = { ...ci, date: new Date(ci.date) }
      calitems.value.push(item)
      return
    }
    if (ci.rounds) {
      Object.entries(ci.rounds).forEach(([rnr, date]) => {
        const { rounds, ...item } = { ...ci, date: new Date(date), round: rnr }
        calitems.value.push(item)
      })
    }
  })
}

async function getArticles(){
  let reply
  changeDialogCounter(1)
  try {
    reply = await $backend("content","anon_get_articles", {})
  } catch (error) {
    displaySnackbar(t(error.message))
    return
  }
  finally {
    changeDialogCounter(-1)
  }
  articles.value = reply.data
  readArticles()
}

function readArticles () {
  const now = new Date()
  const activearticles = []
  articles.value.forEach((a, index) => {
    const activedate = new Date(a.active_since)
    const expirydate = new Date(a.active_since)
    expirydate.setDate(expirydate.getDate() + Number(a.active_days))
    if (activedate < now && expirydate > now) {
      const titlei18n = a[`title_${locale.value}`]
      const introi18n = a[`intro_${locale.value}`]
      activearticles.push({
        activedate,
        expirydate,
        title: titlei18n && titlei18n.length ? titlei18n : a.title,
        intro: introi18n && introi18n.length ? introi18n : a.intro,
        slug: a.slug
      })
    }
  })
  activearticles.sort((a, b) => b.activedate - a.activedate)
  activearticles.forEach((a, ix) => {
    if (ix < 3) {
      articles3.value.push(a)
    } else {
      articlesRest.value.push(a)
    }
  })
}

onMounted(()=> {
  parseCalendarItems(caldata.value)
  calitems.value.sort(compareDates)
  getArticles()
})

</script>
<template>
  <main>
    <VContainer>
      <v-row>
        <v-col cols="12" sm="8">
          <div class="float-right " style="background-color: white;">
            <v-img src="/img/logo.svg" class="ma-2 hidden-xs-only " width="100px" height="150px"/>
            <v-img src="/img/logo.svg" class="ma-2 hidden-sm-and-up" width ="50px" height="75px"/>
          </div>
          <ContentRenderer :value="data">
            <h1 v-html="data[ttitle] ? data[ttitle] : data.title" />
            <div v-html="md(data[tcontent])" class="markdowncontent" />
          </ContentRenderer>
        </v-col>
        <v-col cols="12" sm="4">
          <v-card class="mt-2">
            <v-card-title class="bg-green-darken-1 text-white pa-3 ">
              {{ $t('Calendar') }}
            </v-card-title>
            <v-card-text class="mt-2 markdowncontent">
              <ul>
                <li v-for="c, ix in future_ci" :key="ix">
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
            <v-card-title class="bg-green-lighten-1 text-black pa-3 ">
              {{ a.title }}
            </v-card-title>
            <v-card-text class="mt-2"  >
              <i v-html="Intl.DateTimeFormat('nl').format(a.activedate)"></i>
              <div v-html="a.intro" />
            </v-card-text>
            <v-card-actions>
              <v-spacer />
              <v-btn @click="gotoArticle(a)">
                {{ $t('read more') }}
              </v-btn>
            </v-card-actions>
          </v-card>
        </v-col>
      </v-row>          

    </VContainer>
    <!-- <v-parallax v-if="$vuetify.breakpoint.mdAndUp" src="/img/chesscrowd_big.jpg" height="400" />
    <v-parallax v-if="$vuetify.breakpoint.sm" src="/img/chesscrowd_medium.jpg" height="300" />
    <v-parallax v-if="$vuetify.breakpoint.xs" src="/img/chesscrowd_small.jpg" height="200" />     -->
    <VContainer>
      <v-row class="mt-2">
        <v-col v-for="a in articlesRest" :key="a.id" cols="12" sm="6" md="4">
          <v-card>
            <v-card-title class="bg-green-lighten-1 text-black pa-3 ">
              {{ a.title }}
            </v-card-title>
            <v-card-text class="mt-2"  >
              <i v-html="Intl.DateTimeFormat('nl').format(a.activedate)"></i>
              <div v-html="a.intro" />
            </v-card-text>
            <v-card-actions>
              <v-spacer />
              <v-btn @click="gotoArticle(a)">
                {{ $t('read more') }}
              </v-btn>
            </v-card-actions>
          </v-card>
        </v-col>
      </v-row>     
    </VContainer>
    <hr />
    <v-dialog width="10em" v-model="waitingdialog">
      <v-card>
        <v-card-title>{{ $t('Loading...')}}</v-card-title>
        <v-card-text>
          <v-progress-circular indeterminate color="green" />
        </v-card-text>
      </v-card>
    </v-dialog>
    <VSnackbar v-model="snackbar" timeout="6000">
      {{ errortext }}
      <template v-slot:actions>
        <v-btn color="green-lighten-2" variant="text" @click="snackbar = false" icon="mdi-close" />
      </template>
    </VSnackbar>         
  </main>

</template>

<style>
h1:after {
  content: ' ';
  display: block;
  border: 1px solid #aaa;
  margin-bottom: 1em;
}

.v-card__text, .v-card__title {
  word-break: normal; /* maybe !important  */
}
.footer a {
  color: white;
}
</style>