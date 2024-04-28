<script setup>
import { ref, onMounted } from 'vue'
import ProgressLoading from '@/components/ProgressLoading.vue'
import SnackbarMessage from '@/components/SnackbarMessage.vue'

import { useMgmtTokenStore } from "@/store/mgmttoken"
import { usePersonStore } from "@/store/person";
import { storeToRefs } from "pinia";

// communication
const { $backend } = useNuxtApp()
const router = useRouter()

//  snackbar and loading widgets
const refsnackbar = ref(null)
let showSnackbar
const refloading = ref(null)
let showLoading


// stores
const mgmtstore = useMgmtTokenStore()
const { token } = storeToRefs(mgmtstore)
const personstore = usePersonStore()
const { person } = storeToRefs(personstore)

definePageMeta({
  layout: "mgmt",
})

useHead({
  title: 'Management Articles',
})

async function archivearticles() {
  let reply
  showLoading(true)
  try {
    reply = await $backend("page", "archivearticles", {
      token: token.value,
    })
  }
  catch (error) {
    console.error('failed', error)
    showSnackbar("Error while archiving")
    return
  }
  finally {
    showLoading(false)
  }
  showSnackbar("Articles archived")
  mgmtstore.updateToken(reply.data)
}

async function checkAuth() {
  console.log('checking if auth is already set', token.value)
  if (token.value) return
  if (person.value.credentials.length === 0) {
    router.push('/mgmt')
    return
  }
  if (!person.value.email.endsWith('@frbe-kbsb-ksb.be')) {
    router.push('/mgmt')
    return
  }
  let reply
  showLoading(true)
  // now login using the Google auth token
  try {
    reply = await $backend("accounts", "login", {
      logintype: 'google',
      token: person.value.credentials,
      username: null,
      password: null,
    })
  }
  catch (error) {
    console.log('failed login redirecting to /mgmt')
    mgmtstore.updateToken(null)
    router.push('/mgmt')
  }
  finally {
    showLoading(false)
  }
  mgmtstore.updateToken(reply.data)
}

async function copyarticles() {
  let reply
  showLoading(true)
  try {
    reply = await $backend("page", "copyarticles", {
      token: token.value,
    })
  }
  catch (error) {
    console.error('failed', error)
    showSnackbar("Error while copying content to operational site")
    return
  }
  finally {
    showLoading(false)
  }
  showSnackbar("Content copied to operational site")
  mgmtstore.updateToken(reply.data)
}

function openPageCollection() {
  window.open(`https://st.frbe-kbsb-ksb.be/cp/collections/pages`, '_statamic')
}


onMounted(() => {
  showSnackbar = refsnackbar.value.showSnackbar
  showLoading = refloading.value.showLoading
  checkAuth()
})
</script>


<template>
  <v-container>
    <SnackbarMessage ref="refsnackbar" />
    <ProgressLoading ref="refloading" />

    <h1>Management Articles</h1>
    <p>Here you can modify the articles of the FRBE-KBSB-KSB website</p>
    <p>We use a tool called Statamic</p>
    <p>In order to make changes to a page, you have the following steps</p>
    <ul>
      <li>Open the Statamic tool (it opens in a separate browser tab/window)</li>
      <v-btn variant="tonal" @click="openPageCollection">open Statamic</v-btn><br><br>
      <li>Modify the pages in the statamic tool</li><br>
      <li>Copy the modified content in Statamic to the operational site</li>
      <v-btn variant="tonal" @click="copyarticles">copy</v-btn><br><br>
      <li>Archive articles</li>
      <v-btn variant="tonal" :disabled="true" @click="archivearticles">archive</v-btn><br><br>
    </ul>
    <br>
    <p>
      When opening the Statamic tool for the first time, you will need to provide a
      username + password.
    </p>
    <ul>
      <li><b>username:</b> board@frbe-kbsb-ksb.be</li>
      <li><b>password:</b> frbekbsb2024</li>

    </ul>
  </v-container>
</template>
