<script setup>
import { ref, watch } from 'vue'
import showdown from 'showdown'
import { useI18n } from 'vue-i18n'

const { t, locale } = useI18n()

const mdConverter = new showdown.Converter()

const { $backend } = useNuxtApp()
const metadata = ref(null)
const pagetitle = ref("")
const pagecontent = ref("")
const articles = ref([])
const router = useRouter()

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

function gotoArticle(a) {
  router.push('/article?slug=' + a.name)
}

async function getArticlesList() {
  try {
    const reply = await $backend('filestore', 'anon_get_filelist', {
      group: 'articles',
    })
    await processArticles(reply.data)
  }
  catch (error) {
    console.log('failed')
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

function updateLocale(l) {
  locale.value = l
  pagetitle.value = metadata.value["title_" + l]
  pagecontent.value = mdConverter.makeHtml(metadata.value["content_" + l])
  articles.value.forEach(art => processArticle(art))
}

watch(locale, (nl, ol) => updateLocale(nl))

onMounted(() => {
  getContent()
  getArticlesList()
})

</script>

<template>
  <v-container>
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