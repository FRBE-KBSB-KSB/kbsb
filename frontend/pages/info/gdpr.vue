<script setup>
import showdown from 'showdown'
import { ref } from 'vue'
import { VContainer, VTabs, VTab,VWindow, VWindowItem} from 'vuetify/lib/components/index.mjs';

const { locale } = useI18n()
const ttitle = `title_${locale.value}`
const { data }  = await useAsyncData('gdpr', () => queryContent('/pages/gdpr').findOne())
const tab = ref(null)
const mdConverter = new showdown.Converter()
function md(s) { return  mdConverter.makeHtml(s)}
</script>

<template>
  <v-container>
    <ContentRenderer :value="data">
      <h1 v-html="data[ttitle] ? data[ttitle] : data.title" />
      <v-container class="mt-1 elevation-2">
        <v-tabs v-model="tab" light slider-color="deep-purple">
          <v-tab class="mx-2"> NL </v-tab>
          <v-tab class="mx-2"> FR </v-tab>
        </v-tabs>
        <v-window v-model="tab">
          <v-window-item>
            <div class="mt-2 markdowncontent" v-html="md(data.content_nl)" />
          </v-window-item>
          <v-window-item>
            <div class="mt-2 markdowncontent" v-html="md(data.content_fr)" />
          </v-window-item>
        </v-window>
      </v-container>
    </ContentRenderer>
  </v-container>
</template>

