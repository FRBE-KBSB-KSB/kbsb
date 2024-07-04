<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import Enrollment  from '@/components/mgmtinterclubs/Enrollment'
import Downloads  from '@/components/mgmtinterclubs/Downloads'
import { parse } from 'yaml'
import { useMgmtTokenStore } from "@/store/mgmttoken"
// import { useMgmtInterclubStore } from "@/store/mgmtinterclub"
import { usePersonStore } from "@/store/person"
import { storeToRefs } from 'pinia'

// communication
const router = useRouter()
const waitingdialog = ref(false)
let dialogcounter = 0
const errortext = ref(null)
const snackbar = ref(null)


// API backend
const { $backend } = useNuxtApp()
const mgmttokenstore = useMgmtTokenStore()
const { token: mgmttoken } = storeToRefs(mgmttokenstore)
const personstore = usePersonStore();
const { person } = storeToRefs(personstore)
// const mgmtinterclubstore = useMgmtInterclubStore()
// const { club } = storeToRefs(mgmtinterclubstore)


// data model
const tab = ref(null)
const refenrollment = ref(null)
// const refplanning = ref(null)
// const refplayerlist = ref(null)
// const refresults = ref(null)
// const refvenues = ref(null)
const refdownloads = ref(null)
const icdata = ref({})
const clubs = ref([])
const icclub = ref({})          // the icclub data
const idclub = ref(null)
const ic_rounds = ref([])
const round = ref("1")

// layout + header
definePageMeta({
  layout: 'mgmt'
})
useHead({
  script: [
    { src: 'https://accounts.google.com/gsi/client', defer: true }
  ],
  title: 'Management Interclubs',
})

// methods alphabetically

function changeDialogCounter(i) {
  dialogcounter += i
  waitingdialog.value = (dialogcounter > 0)
}


function changeTab() {
  console.log('changeTab', tab.value)
  switch (tab.value) {
    case 'enrollment':
      refenrollment.value.setup(icclub.value, icdata.value)
      break
    case 'downloads':
      refdownloads.value.setup(icclub.value)
      break
  }
}

async function checkAuth() {
  console.log('checking if auth is already set', mgmttoken.value)
  if (mgmttoken.value) return
  if (person.value.credentials.length === 0) {
    gotoLogin()
    return
  }
  if (!person.value.email.endsWith('@frbe-kbsb-ksb.be')) {
    gotoLogin()
    return
  }
  let reply
  changeDialogCounter(1)
  // now login using the Google auth token
  try {
    reply = await $backend("accounts", "login", {
      logintype: 'google',
      token: person.value.credentials,
      username: null,
      password: null,
    })
    mgmttokenstore.updateToken(reply.data)    
  }
  catch (error) {
    console.log('failed login to backend', error)
    gotoLogin()
  }
  finally {
    changeDialogCounter(-1)
  }
}

function displaySnackbar(text, color) {
  errortext.value = text
  snackbar.value = true
}

async function getClubs() {
  let reply
  changeDialogCounter(1)
  try {
    reply = await $backend("club", "anon_get_clubs", {})
  } catch (error) {
    if (error.code == 401) gotoLogin()
    displaySnackbar(error.message)
    return
  }
  finally {
    changeDialogCounter(-1)
  }
  clubs.value = reply.data
  clubs.value.forEach(p => {
    p.merged = `${p.idclub}: ${p.name_short} ${p.name_long}`
  })
}

async function getClubDetails() {
  let reply
  icclub.value = {}
  if (idclub.value) {
    changeDialogCounter(1)
    try {
      reply = await $backend("interclub", "mgmt_getICclub", {
        idclub: idclub.value,
        token: idtoken.value
      })
    } catch (error) {
      if (error.code == 401) gotoLogin()
      displaySnackbar(error.message)
      return
    } finally {
      changeDialogCounter(-1)
    }
    icclub.value = reply.data
    changeTab()
  }
  else {
    changeTab()
  }
}


async function gotoLogin() {
  await router.push('/mgmt')
}

async function parseYaml(group, name) {
  try {
    const yamlcontent = await readBucket(group, name)
    if (!yamlcontent) {
      return null
    }
    return parse(yamlcontent)
  }
  catch (error) {
    console.error('cannot parse yaml', yamlcontent)
  }
}

async function processICdata() {
  icdata.value = await parseYaml("data", "ic2425.yml")
  ic_rounds.value = Object.keys(icdata.value.rounds).map((x) => {
    return { value: x, title: `R${x}: ${icdata.value.rounds[x]}` }
  })
}

async function readBucket(group, name) {
  try {
    const reply = await $backend('filestore', 'anon_get_file', {
      group,
      name,
    })
    return reply.data
  }
  catch (error) {
    console.error('failed to fetch file from bucket')
    return null
  }
}


function selectClub() {
  console.log('selected', idclub.value)
  getClubDetails()
}

// startup

onMounted(async () => {
  checkAuth()
  await processICdata()
  getClubs()
  tab.value = "enrollment"
  changeTab()
})



</script>

<template>
  <VContainer>
    <h1>Interclubs Manager 2024-25</h1>
    <v-dialog width="10em" v-model="waitingdialog">
      <v-card>
        <v-card-title>Loading...</v-card-title>
        <v-card-text>
          <v-progress-circular indeterminate color="deep-purple" />
        </v-card-text>
      </v-card>
    </v-dialog>
    <VCard>
      <VCardText>
        <v-row>
          <v-col cols="12" sm="6">
            <VAutocomplete v-model="idclub" :items="clubs" item-title="merged" item-value="idclub"
              color="deep-purple" label="Club" clearable @update:model-value="selectClub">
            </VAutocomplete>
          </v-col>
          <v-col cols="12" sm="6">
            <VSelect v-model="round" :items="ic_rounds" label="Round"
              @update:model-value="changeTab">
            </VSelect>
          </v-col>
        </v-row>
      </VCardText>
    </VCard>
    <h3 class="mt-2">
      Selected club: {{ icclub.idclub }} {{ icclub.name }}
    </h3>
    <div class="elevation-2">
      <VTabs v-model="tab" color="purple" @update:modelValue="changeTab">
        <VTab value="enrollment">Registration</VTab>
        <!-- <VTab value="results">Results</VTab>
        <VTab value="venues">Venues</VTab>
        <VTab value="playerlist">Player lists</VTab>
        <VTab value="teamforfeit">Team Forfeiting</VTab> -->
        <VTab value="downloads">Downloads</VTab>
      </VTabs>
      <VWindow v-model="tab" @update:modelValue="changeTab">
        <VWindowItem value="enrollment" :eager="true">
          <Enrollment ref="refenrollment" />
        </VWindowItem>
        <!-- <VWindowItem value="results" :eager="true">
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
        </VWindowItem> -->
        <VWindowItem value="downloads" :eager="true">
          <Downloads ref="refdownloads" />
        </VWindowItem>
      </VWindow>
    </div>
    <VSnackbar v-model="snackbar" timeout="6000">
      {{ errortext }}
      <template v-slot:actions>
        <v-btn color="deep-purple-lighten-2" variant="text" @click="snackbar = false" icon="mdi-close" />
      </template>
    </VSnackbar>    
  </VContainer>
</template>