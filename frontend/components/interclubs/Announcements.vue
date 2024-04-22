<script setup>
import showdown from 'showdown'
import { VContainer } from 'vuetify/lib/components/index.mjs';

const { locale } = useI18n()
const ttitle = `title_${locale.value}`
const tcontent = `content_${locale.value}`
const { data }  = await useAsyncData('interclubs-announcements', () => queryContent('/pages/interclubs-announcements').findOne())

const mdConverter = new showdown.Converter()

function md(s) { return  mdConverter.makeHtml(s)}
</script>

<template>
  <v-container>
    <ContentRenderer :value="data"  >
      <h2 v-html= "data[ttitle] ? data[ttitle] : data.title" />
      <div v-html= "md(data[tcontent])" class="markdowncontent" />
    </ContentRenderer>
  </v-container>
</template>
