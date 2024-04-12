<script setup>
import { VContainer  } from 'vuetify/components';
definePageMeta({
  layout: 'mgmt',
})
useHead({
  title: 'Management Overview',
  // we need google script to load because we might redirect internally
  // to index in case we fail the authentication
  script: [
    { src: 'https://accounts.google.com/gsi/client', async: true, defer: true }
  ]
})
</script>

<template>
  <v-container>
    <h1>Reports</h1>
    Porting to Vue3 not done yet
  </v-container>
</template>