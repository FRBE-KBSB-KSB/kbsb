<script setup>
import showdown from 'showdown'
import { VContainer, VBtn, VCard, VCardTitle, VCardText, VDialog, 
  VProgressCircular, VSnackbar} from 'vuetify/lib/components/index.mjs';


const { locale, t } = useI18n()
const { $backend } = useNuxtApp()
const route = useRoute()
const slug = route.query.slug || ""
const ttitle = `title_${locale.value}`
const tintro = `intro_${locale.value}`
const ttext = `text_${locale.value}`
const article = ref({})

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

async function getArticle() {
  console.log('running getArticles')
  let reply
  changeDialogCounter(1)
  try {
    reply = await $backend("content","anon_get_article", {
      slug: slug
    })
  } catch (error) {
    displaySnackbar(t(error.message))
    return
  }
  finally {
    changeDialogCounter(-1)
  }
  article.value = reply.data
}

onMounted(()=>{
  getArticle()
})

</script>

<template>
  <v-container>
    <ContentRenderer v-if="slug" :value="article">
      <h1 v-html="article[ttitle] ? article[ttitle] : article.title" />
      <div v-html="article[tintro]" class="my-2"/>
      <hr />
      <div v-html="md(article[ttext])" class="my-1 markdowncontent" />
    </ContentRenderer>
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
  </v-container>
</template>

