<script setup>
import { ref, watch } from 'vue'
import showdown from 'showdown'
import { useI18n } from 'vue-i18n'


const { locale, t } = useI18n()
const { $backend } = useNuxtApp()
const route = useRoute()
const slug = route.query.slug || ""

const metadata = ref(null)
const art_title = ref("")
const art_intro = ref("")
const art_text = ref("")

const mdConverter = new showdown.Converter()

async function getArticle() {
  try {
    const reply = await $backend('filestore', 'anon_get_file', {
      group: 'articles',
      name: slug
    })
    metadata.value = useMarkdown(reply.data).metadata
    updateLocale(locale.value)
  }
  catch (error) {
    console.log('failed')
  }
}

function updateLocale(l) {
  console.log("Updating locale", l)
  locale.value = l
  if (process.client) {
    localStorage.setItem("locale", l)
  }
  art_title.value = metadata.value["title_" + l]
  art_intro.value = metadata.value["intro_" + l]
  art_text.value = mdConverter.makeHtml(metadata.value["text_" + l])
}


watch(locale, (nl, ol) => updateLocale(nl))

onMounted(() => {
  getArticle()
})

</script>

<template>
  <v-container>
    <div v-if="slug">
      <h1 v-html="art_title" />
      <div v-html="art_intro" class="my-2" />
      <hr />
      <div v-html="art_text" class="my-1 markdowncontent" />
    </div>
  </v-container>
</template>
