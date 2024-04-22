<script setup>
import showdown from 'showdown'
import { computed, ref } from 'vue'

const props = defineProps({
  file: String
})
const { locale } = useI18n()
const ttitle = `title_${locale.value}`
const tcontent = `content_${locale.value}`
const helptopic = `help-${props.file}`
console.log('helptopic', helptopic)
const { data }  = await useAsyncData(helptopic, () => queryContent(`/pages/${help-topic.value}`).findOne())
const dialog = ref(false)
const mdConverter = new showdown.Converter()

function md(s) { return  mdConverter.makeHtml(s)}

</script>

<template>
  <v-dialog v-model="dialog" width="20em">
    <template v-slot:activator="{ on, attrs }">
      <v-btn icon="mdi-help" color="green" size="x-small" v-bind="attrs" v-on="on">
      </v-btn>
    </template>

    <ContentRenderer :value="data">
      <v-card>
        <v-card-title v-html="data[ttitle] ? data[ttitle] : data.title" />
        <v-divider></v-divider>
        <v-card-text class="pt-3 markdowncontent" v-html="md(data[tcontent])"> 
        </v-card-text>
      </v-card>
    </ContentRenderer>

  </v-dialog>
</template>

