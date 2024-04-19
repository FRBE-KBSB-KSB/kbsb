<script setup>
import { ref, watch } from 'vue'
import showdown from 'showdown'
import { useI18n } from 'vue-i18n'
const { t, locale } = useI18n()

const mdConverter = new showdown.Converter()

const { $backend } = useNuxtApp()
const tab = ref(0)
const pagetitle_nl = ref("")
const pagetitle_fr = ref("")
const pagecontent_nl = ref("")
const pagecontent_fr = ref("")

async function getContent() {
  try {
    const reply = await $backend('filestore', 'anon_get_file', {
      group: 'pages',
      name: 'tournament-rules.md'
    })
    let metadata = useMarkdown(reply.data).metadata
    console.log('metadata', metadata)
    pagetitle_nl.value = metadata.title_nl
    pagetitle_fr.value = metadata.title_fr
    pagecontent_nl.value = mdConverter.makeHtml(metadata.content_nl)
    pagecontent_fr.value = mdConverter.makeHtml(metadata.content_fr)
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
          <div class="mt-2 markdowncontent" v-html="pagecontent_nl" />
        </v-window-item>
        <v-window-item>
          <h1>{{ pagetitle_fr }}</h1>
          <div class="mt-2 markdowncontent" v-html="pagecontent_fr" />
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