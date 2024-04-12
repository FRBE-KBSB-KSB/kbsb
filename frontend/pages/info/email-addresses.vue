<script setup>

import showdown from 'showdown'

const {data}  = await useAsyncData('emailaddresses', 
  () => queryContent('/pages/email-addresses').findOne())

const mdConverter = new showdown.Converter()
function md(s) { return  mdConverter.makeHtml(s)}

</script>

<template>
  <v-container>
    <ContentRenderer :value="data"  >
      <h1>{{ data.title }}</h1>
      <div v-html= "md(data.content_nl)" class="markdowncontent"/>
    </ContentRenderer>
  </v-container>
</template>


