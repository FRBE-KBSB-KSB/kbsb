<script setup>
import { ref, onMounted } from 'vue'
import { Downloads, Playerlist, Results, Venue, Teamforfeit } from '@/components/mgmtinterclubs'
import ProgressLoading from '@/components/ProgressLoading.vue'
import SnackbarMessage from '@/components/SnackbarMessage.vue'
import { INTERCLUBS_ROUNDS } from '@/util/interclubs'

//  snackbar and loading widgets
const refsnackbar = ref(null)
let showSnackbar
const refloading = ref(null)
let showLoading

// stores
import { useMgmtTokenStore } from "@/store/mgmttoken";
import { useMgmtInterclubStore } from "@/store/mgmtinterclub"
import { usePersonStore } from "@/store/person"
import { storeToRefs } from 'pinia'
const mgmttokenstore = useMgmtTokenStore()
const { token: mgmttoken } = storeToRefs(mgmttokenstore)
const personstore = usePersonStore();
const { person } = storeToRefs(personstore)
const mgmtinterclubstore = useMgmtInterclubStore()
const { club, round } = storeToRefs(mgmtinterclubstore)


// datamodel
const clubs = ref([])
const roundchoices = Object.keys(INTERCLUBS_ROUNDS).map((x) => {
  return { value: x, title: `R${x}: ${INTERCLUBS_ROUNDS[x]}` }
})
const myround = ref(null)
const myidclub = ref(null)

// communication
const { $backend } = useNuxtApp()
const tab = ref(null)
const refdownloads = ref(null)
const refplayerlist = ref(null)
const refresults = ref(null)
const refvenues = ref(null)
const refteamforfeit = ref(null)



// layout + header
definePageMeta({
  layout: 'mgmt'
})
useHead({
  script: [
    { src: 'https://accounts.google.com/gsi/client', defer: true }
  ],
  title: 'Management Clubs',
})

// methods alphabetically

async function checkAuth() {
  console.log('checking if auth is already set', mgmttoken.value)
  if (mgmttoken.value) return
  if (person.value.credentials.length === 0) {
    await navigateTo('/mgmt')
    return
  }
  if (!person.value.email.endsWith('@frbe-kbsb-ksb.be')) {
    await navigateTo('/mgmt')
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
    await navigateTo('/mgmt')
  }
  finally {
    showLoading(false)
  }
  mgmttokenstore.updateToken(reply.data)
}

async function getClubs() {
  let reply
  showLoading(true)
  try {
    reply = await $backend("club", "anon_get_clubs", {})
  } catch (error) {
    console.log('getClubs error')
    showSnackbar(error.message)
    return
  }
  finally {
    showLoading(false)
  }
  clubs.value = reply.data
  clubs.value.forEach(p => {
    p.merged = `${p.idclub}: ${p.name_short} ${p.name_long}`
  })
}

async function getClubDetails() {
  if (myidclub.value) {
    showLoading(true)
    try {
      const reply = await $backend("interclub", "mgmt_getICclub", {
        idclub: myidclub.value,
        token: mgmttoken.value
      })
      mgmtinterclubstore.updateClub(reply.data)
    } catch (error) {
      showSnackbar(error.message)
      mgmtinterclubstore.updateClub({})
    } finally {
      showLoading(false)
      updatedStore()
    }
  }
}

function updateRound() {
  mgmtinterclubstore.updateRound(myround.value)
  updatedStore()
}

async function updatedStore() {
  console.log('updatedStore', tab.value)
  switch (tab.value) {
    case 'downloads':
      await refdownloads.value.checkStore()
      break
    case 'playerlist':
      await refplayerlist.value.checkStore()
      break
    case 'results':
      await refresults.value.checkStore()
      break
    case 'teamforfeit':
      await refteamforfeit.value.checkStore()
      break
    case 'venues':
      await refvenues.value.checkStore()
      break
  }
}


// triggers

onMounted(() => {
  showSnackbar = refsnackbar.value.showSnackbar
  showLoading = refloading.value.showLoading
  checkAuth()
  getClubs()
})


</script>

<template>
  <VContainer>
    <SnackbarMessage ref="refsnackbar" />
    <ProgressLoading ref="refloading" />
    <h1>Interclubs Manager</h1>
    <VCard>
      <VCardText>
        <VRow>
          <VCol cols="12" sm="6">
            <VAutocomplete v-model="myidclub" :items="clubs" item-title="merged" item-value="idclub"
              color="purple" label="Club" clearable @update:model-value="getClubDetails">
            </VAutocomplete>
          </VCol>
          <VCol cols="12" sm="6">
            <VSelect v-model="myround" :items="roundchoices" label="Round"
              @update:model-value="updateRound">
            </VSelect>
          </VCol>
        </VRow>
      </VCardText>
    </VCard>
    <h3 class="mt-2">
      Selected club: {{ club.idclub }} {{ club.name }}
    </h3>
    <div class="elevation-2">
      <VTabs v-model="tab" color="purple" @update:modelValue="updatedStore">
        <VTab value="results">Results</VTab>
        <VTab value="venues">Venues</VTab>
        <VTab value="playerlist">Player lists</VTab>
        <VTab value="teamforfeit">Team Forfeiting</VTab>
        <VTab value="downloads">Downloads</VTab>
      </VTabs>
      <VWindow v-model="tab" @update:modelValue="updatedStore">
        <VWindowItem value="results" :eager="true">
          <Results ref="refresults" />
        </VWindowItem>
        <VWindowItem value="venues" :eager="true">
          <Venue ref="refvenues" />
        </VWindowItem>
        <VWindowItem value="playerlist" :eager="true">
          <Playerlist ref="refplayerlist" />
        </VWindowItem>
        <VWindowItem value="teamforfeit" :eager="true">
          <Teamforfeit ref="refteamforfeit" />
        </VWindowItem>
        <VWindowItem value="downloads" :eager="true">
          <Downloads ref="refdownloads" />
        </VWindowItem>
      </VWindow>
    </div>
  </VContainer>
</template>