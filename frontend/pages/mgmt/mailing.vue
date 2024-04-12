<script setup>
import { onMounted } from 'vue'
import { VContainer, VBtn } from 'vuetify/components'
import ProgressLoading from '@/components/ProgressLoading.vue'
import SnackbarMessage from '@/components/SnackbarMessage.vue'


// stores
import { useMgmtTokenStore } from "@/store/mgmttoken"
import { usePersonStore } from "@/store/person"
import { storeToRefs } from 'pinia'
const mgmtstore = useMgmtTokenStore()
const { token: mgmttoken } = storeToRefs(mgmtstore)
const personstore = usePersonStore();
const { person } = storeToRefs(personstore) 

// config
const runtimeConfig = useRuntimeConfig(); 

//  snackbar and loading widgets
const refsnackbar = ref(null)
let showSnackbar
const refloading = ref(null)
let showLoading

// communication
const { $backend } = useNuxtApp()

definePageMeta({  
  layout: "mgmt",
})

useHead({
  title: 'Management Mailings',
  // we need google script to load because we might redirect internally
  // to index in case we fail the authentication
  script: [
    { src: 'https://accounts.google.com/gsi/client', async: true, defer: true }
  ]
})

async function checkAuth() {
  let reply
  console.log('checking if auth is already set', mgmttoken.value)
  if (mgmttoken.value) return 
  if (person.value.credentials.length === 0) {
    navigateTo('/mgmt')
    return
  }
  if (!person.value.email.endsWith('@frbe-kbsb-ksb.be')) {
    navigateTo('/mgmt')
    return
  }
  showLoading(true)
  // now login using the Google auth token
  try {
    reply = await $backend("accounts", "login", {
      logintype: 'google',
      token: person.value.credentials,
      username: null,
      password: null,
    })
    mgmtstore.updateToken(reply.data)
  }
  catch (error) {
    console.error('error', error)
    navigateTo('/mgmt')
  }
  finally {
    showLoading(false)
  }
}

function download(){
  console.log('token', mgmttoken.value)
  const url = `${runtimeConfig.public.apiurl}api/v1/clubs/mgmt/mailinglist?token=${mgmttoken.value}`
  window.location.href = url
}

onMounted( () => {
  showSnackbar = refsnackbar.value.showSnackbar
  showLoading = refloading.value.showLoading  
  checkAuth()
})

</script>


<template>
  <v-container class="markdowncontent">
    <SnackbarMessage ref="refsnackbar" />
    <ProgressLoading ref="refloading"/>
    <h1>Mailing</h1>
    <p>
      Based on the data in Club Manager, you can download the following distribution lists
      <ul>
        <li>General mailing list</li>
        <li>Mailing for financial topics</li>
        <li>Mailing for administrative topics</li>
        <li>Mailing about interclubs</li>
      </ul> 
      All mailing list are downloadable in a single Excel file
      <p><VBtn @click="download" variant="flat" color="purple">Download Excel</VBtn></p>
    </p>
  </v-container>
</template>

