<script setup>
import { ref, watch } from 'vue'
import showdown from 'showdown'
import { useI18n } from 'vue-i18n'
const { t, locale } = useI18n()

const mdConverter = new showdown.Converter()

const { $backend } = useNuxtApp()
const metadata = ref(null)
const pagetitle = ref("")
const pagetitle_nl = ref("")
const pagetitle_fr = ref("")
const pagecontent_nl = ref("")
const pagecontent_fr = ref("")

async function getContent() {
  try {
    const reply = await $backend('filestore', 'anon_get_file', {
      group: 'pages',
      name: 'commissions.md'
    })
    metadata.value = useMarkdown(reply.data).metadata
    pagetitle_nl.value = metadata.value["title_nl"]
    pagetitle_fr.value = metadata.value["title_fr"]
    pagecontent_nl.value = mdConverter.makeHtml(metadata.value["content_nl"])
    pagecontent_fr.value = mdConverter.makeHtml(metadata.value["content_fr"])
  }
  catch (error) {
    console.log('failed')
  }
}

onMounted(() => {
  getContent()
})

</script>

<template>
  <v-container>
    <!-- <h1>{{ pagetitle }}</h1> -->
    <v-container class="mt-1 elevation-2">
        <v-tabs v-model="tab" light slider-color="deep-purple">
          <v-tab class="mx-2"> NL </v-tab>
          <v-tab class="mx-2"> FR </v-tab>
        </v-tabs>
        <v-window v-model="tab">
          <v-window-item>
            <h1>{{ pagetitle_nl }}</h1>
            <div class="mt-2 markdowncontent" v-html="content_nl" />
          </v-window-item>
          <v-window-item>
            <h1>{{ pagetitle_fr }}</h1>
            <div class="mt-2 markdowncontent" v-html="content_fr" />
          </v-window-item>
        </v-window>
      </v-container>
  </v-container>
</template>

<style scoped>
.v-card-title {
  white-space: normal;
}
</style>