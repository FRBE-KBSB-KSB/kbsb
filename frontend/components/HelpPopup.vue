<script setup>
import { ref } from 'vue'
import showdown from 'showdown'
import { useI18n } from 'vue-i18n';

const mdConverter = new showdown.Converter()
const props = defineProps({
  file: String
})
const { locale } = useI18n()
const ttitle = `title_${locale.value}`
const metadata = ref({})
const pagecontent = ref("")

async function getContent() {
  try {
    const reply = await $backend('filestore', 'anon_get_file', {
      group: 'pages',
      name: `help-${props.file}.md`
    })
    metadata.value = useMarkdown(reply.data).metadata
    pagecontent.value = mdConverter.makeHtml(metadata.value["content_" + l])
  }
  catch (error) {
    console.log('failed')
  }
}


</script>

<template>
  <v-dialog v-model="dialog" width="20em">
    <template v-slot:activator="{ on, attrs }">
      <v-btn icon="mdi-help" color="green" size="x-small" v-bind="attrs" v-on="on">
      </v-btn>
    </template>


    <v-card>
      <v-card-title v-html="metadata[ttitle] ? metadata[ttitle] : metadata.title" />
      <v-divider></v-divider>
      <v-card-text v-html="pagecontent" class="markdowncontent" />
    </v-card>

  </v-dialog>
</template>
