<script setup>
import { onMounted } from 'vue'
import { VContainer } from 'vuetify/components'
import { usePersonStore } from "@/store/person";
import { storeToRefs } from "pinia";

const localePath = useLocalePath()

const config = useRuntimeConfig()
const personstore = usePersonStore()
const { person } = storeToRefs(personstore)

let checkinlaunched = false
let checkinsuccess = false

definePageMeta({  
  layout: "mgmt",
})

useHead({
  title: 'Management Overview',
  // we need google script to load because we might redirect internally
  // to index in case we fail the authentication
  script: [
    { src: 'https://accounts.google.com/gsi/client', async: true, defer: true }
  ]
})


function checkAuth () {
  if (person.value.credentials.length === 0) {
    navigateTo('/mgmt')
  }
  if (!person.value.email.endsWith('@frbe-kbsb-ksb.be')) {
    navigateTo('/mgmt')
  }
}

async function checkin () {
  checkinlaunched = true
  const data = {
    user: person.value.user,
    email: person.value.email,
    branch: config.public.repo_branch,
  }
  let reply = await fetch(config.oublic.statamic_url + '/python/checkin', {
    method: 'POST',
    body: JSON.stringify(data),
    headers: {
      'Content-Type': 'application/json'
    }
  })
  checkinlaunched = false
  checkinsuccess = true
}

async function checkout () {
  checkoutlaunched = true
  const data = {
    user: person.value.user,
    email: person.value.email,
    branch: config.public.repo_branch,
  }
  const reply = await fetch(config.public.statamic_url + '/python/checkout', {
    method: 'POST',
    body: JSON.stringify(data),
    headers: {
      'Content-Type': 'application/json'
    }
  })
  checkoutlaunched = false
  checkoutsuccess = true
}

function openCollections () {
  const stUrl = config.public.statamic_url
  window.open(`${stUrl}/cp/collections`, '_statamic')
}

onMounted(()=> {
  checkAuth()
})
</script>


<template>
  <v-container class="markdowncontent">
    <h1>Overview</h1>
    <p>
      Documentation about the management of the website can be found at 
      <a href="https://sites.google.com/frbe-kbsb-ksb.be/internal/home">Internal site</a>
    </p>
    <ul>
      <li>Managing of the <NuxtLink :to="localePath('/mgmt/content')">Content</NuxtLink> (news articles and pages)</li>
      <li>Admin part of <NuxtLink :to="localePath('/mgmt/clubs')">Clubs Manager</NuxtLink></li>
      <li>Admin part of <NuxtLink :to="localePath('/mgmt/interclubs')">Interclubs Manager</NuxtLink></li>
      <li>Managing of <NuxtLink :to="localePath('/mgmt/filelist')">Files</NuxtLink> (reports and other assets)</li>
    </ul>
  </v-container>
</template>

