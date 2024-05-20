<script setup>
import { ref, watch } from 'vue'
import showdown from 'showdown'
import { useI18n } from 'vue-i18n'
import { parse } from 'yaml'

const { t, locale } = useI18n()
const mdConverter = new showdown.Converter()


//  snackbar and loading widgets
const refsnackbar = ref(null)
let showSnackbar
const refloading = ref(null)
let showLoading

const { $backend } = useNuxtApp()
const metadata = ref(null)
const pagetitle = ref("")
const pagecontent = ref("")
const articles = ref([])
const router = useRouter()
const calitems = ref([])
const caldata = ref([])
const yesterday = new Date() - 86400000


function addCalendarItem(ci) {
  console.log('add item', ci.date, yesterday)
  if (ci.date > yesterday) {
    calitems.value.push(ci)
  }
}

function calenderItem(c) {
  const output = []
  output.push(c.date.toLocaleDateString(locale.value, { dateStyle: 'medium' }) + ':')
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

async function getArticle(art) {
  try {
    const reply = await $backend('filestore', 'anon_get_file', {
      group: 'articles',
      name: art.name,
    })
    art.metadata = useMarkdown(reply.data).metadata
    processArticle(art)
  }
  catch (error) {
    console.log('failed')
  }
}

async function getArticlesList() {
  showLoading(true)
  try {
    const reply = await $backend('filestore', 'anon_get_filelist', {
      group: 'articles',
    })
    await processArticles(reply.data)
  }
  catch (error) {
    console.log('failed')
  }
  finally {
    showLoading(false)
  }
}

async function getCalendar(cal) {
  console.log('calling get calendar', cal.name, cal.data)
  try {
    const reply = await $backend('filestore', 'anon_get_file', {
      group: 'calendar',
      name: cal.name,
    })
    cal.data = await parseYaml(reply.data)
    console.log("yaml processed", cal.name, cal.data)
  }
  catch (error) {
    console.error(' get calendar failed', error)
  }
}

async function getCalendarList() {
  showLoading(true)
  console.log('calling calender list')
  try {
    const reply = await $backend('filestore', 'anon_get_filelist', {
      group: 'calendar',
    })
    await readCalenders(reply.data)
  }
  catch (error) {
    console.error('get calendarlist failed', error)
  }
  finally {
    showLoading(false)
  }
}

async function getContent() {
  try {
    const reply = await $backend('filestore', 'anon_get_file', {
      group: 'pages',
      name: 'index.md'
    })
    metadata.value = useMarkdown(reply.data).metadata
    updateLocale(locale.value)
  }
  catch (error) {
    console.log('failed')
  }
}

function gotoArticle(a) {
  router.push('/article?slug=' + a.name)
}

async function parseYaml(yamlcontent) {
  try {
    return parse(yamlcontent)
  }
  catch (error) {
    console.error('cannot parse yaml', yamlcontent)
  }
}

function processArticle(art) {
  art.title = art.metadata["title_" + locale.value] || art.metadata.title
  art.intro = art.metadata["intro_" + locale.value]
  art.activedate = new Date(art.metadata.active_since)
}

async function processArticles(la) {
  articles.value = []
  let allpromises = []
  la.forEach(e => {
    let name = e.split('/')[1]
    articles.value.push({ name })
  });
  articles.value.forEach(async art => {
    allpromises.push(getArticle(art))
  })
  await Promise.all(allpromises)
  articles.value.sort((a, b) => b.activedate - a.activedate)
}

function processCalendar(ci) {
  console.log('process calendar', ci)
  if (ci.multiple) {
    ci.multiple.forEach((c) => processCalendar(c))
  }
  if (ci.date) {
    const item = { ...ci, date: new Date(ci.date) }
    addCalendarItem(item)
    return
  }
  if (ci.rounds) {
    Object.entries(ci.rounds).forEach(([rnr, date]) => {
      const { rounds, ...item } = { ...ci, date: new Date(date), round: rnr }
      addCalendarItem(item)
    })
  }
}

function processCalendars() {
  console.log('process calendars', caldata.value.length)
  calitems.value = []
  caldata.value.forEach((cal) => {
    console.log('trying to process', cal.name, cal.data)
    processCalendar(cal.data)
  })
  calitems.value.sort((a, b) => a.date > b.date)
  calitems.value = calitems.value.slice(0, 5)
}

async function readCalenders(lc) {
  caldata.value = []
  let allpromises = []
  lc.forEach(e => {
    let name = e.split('/')[1]
    if (name) {
      console.log('adding calendar', name)
      caldata.value.push({ name })
    }
  });
  caldata.value.forEach(async cal => {
    allpromises.push(getCalendar(cal))
  })
  await Promise.all(allpromises)
  processCalendars()
}

function updateLocale(l) {
  if (process.client) {
    localStorage.setItem("locale", l)
  }
  locale.value = l
  pagetitle.value = metadata.value["title_" + l]
  pagecontent.value = mdConverter.makeHtml(metadata.value["content_" + l])
  articles.value.forEach(art => processArticle(art))
  processCalendars()
}

watch(locale, (nl, ol) => updateLocale(nl))

onMounted(() => {
  showSnackbar = refsnackbar.value.showSnackbar
  showLoading = refloading.value.showLoading
  getContent()
  getArticlesList()
  getCalendarList()
})

</script>

<template>
  <v-container>
    <SnackbarMessage ref="refsnackbar" />
    <ProgressLoading ref="refloading" />
    <v-row>
      <v-col cols="12" sm="8">
        <div class="float-right " style="background-color: white;">
          <v-img src="/img/logo.svg" class="ma-2 hidden-xs-only " width="100px" height="150px" />
          <v-img src="/img/logo.svg" class="ma-2 hidden-sm-and-up" width="50px" height="75px" />
        </div>
        <h1>{{ pagetitle }}</h1>
        <div v-html="pagecontent" class="markdowncontent"></div>
      </v-col>
      <v-col cols="12" sm="4">
        <v-card class="mt-2">
          <v-card-title class="bg-green-darken-1 text-white pa-3 ">
            {{ $t('Calendar') }}
          </v-card-title>
          <v-card-text class="mt-2 markdowncontent">
            <ul>
              <li v-for="c, ix in calitems" :key="ix">
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
    <v-row>
      <v-col v-for="a in articles.slice(0, 3)" :key="a.id" cols="12" sm="6" md="4">
        <v-card>
          <v-card-title class="bg-green-lighten-1 text-black pa-3 ">
            {{ a.title }}
          </v-card-title>
          <v-card-text class="mt-2">
            <i v-html="Intl.DateTimeFormat('nl').format(a.activedate)"></i>
            <div v-html="a.intro" class="mt-2" />
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
  </v-container>
  <!-- <v-parallax v-if="$vuetify.breakpoint.mdAndUp" src="/img/chesscrowd_big.jpg" height="400" />
  <v-parallax v-if="$vuetify.breakpoint.sm" src="/img/chesscrowd_medium.jpg" height="300" />
  <v-parallax v-if="$vuetify.breakpoint.xs" src="/img/chesscrowd_small.jpg" height="200" /> -->
  <v-container>
    <v-row class="mt-2">
      <v-col v-for="a in articles.slice(3)" :key="a.id" cols="12" sm="6" md="4">
        <v-card>
          <v-card-title class="bg-green-lighten-1 text-black pa-3 ">
            {{ a.title }}
          </v-card-title>
          <v-card-text class="mt-2">
            <i v-html="Intl.DateTimeFormat('nl').format(a.activedate)"></i>
            <div v-html="a.intro" class="mt-2" />
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
  </v-container>
</template>

<style scoped>
.v-card-title {
  white-space: normal;
}
</style>