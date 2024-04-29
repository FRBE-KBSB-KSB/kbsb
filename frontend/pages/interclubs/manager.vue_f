<script setup>
import { ref, onMounted, } from 'vue'
import { useI18n } from 'vue-i18n'
import Results from '@/components/interclubs/Results.vue'
import Planning from '@/components/interclubs/Planning.vue'
import Playerlist from '@/components/interclubs/Playerlist.vue'
import Venue from '@/components/interclubs/Venue.vue'

import { useIdtokenStore } from '@/store/idtoken'
import { storeToRefs } from 'pinia'
import { INTERCLUBS_ROUNDS } from '@/util/interclubs'


// i18n
const { locale, t: $t } = useI18n()
const router = useRouter()

// idtoken
const idstore = useIdtokenStore()
const { token: idtoken } = storeToRefs(idstore)


function checkAuth() {
  if (!idtoken.value) {
    gotoLogin()
  }
}

async function gotoLogin() {
  await router.push('/tools/oldlogin?url=__interclubs__manager')
}

// communication with tabbed children
const tab = ref(null)
const refplanning = ref(null)
const refplayerlist = ref(null)
const refresults = ref(null)
const refvenues = ref(null)
function changeTab() {
  console.log('changeTab', tab.value)
  switch (tab.value) {
    case 'planning':
      refplanning.value.setup(icclub.value, round.value)
      break
    case 'playerlist':
      refplayerlist.value.setup(icclub.value)
      break
    case 'results':
      refresults.value.setup(icclub.value, round.value)
      break
    case 'venues':
      refvenues.value.setup(icclub.value)
      break
  }
}

// datamodel
const clubs = ref([])
const icclub = ref({})          // the icclub data
const idclub = ref(null)
const ic_rounds = Object.keys(INTERCLUBS_ROUNDS).map((x) => {
  return { value: x, title: `R${x}: ${INTERCLUBS_ROUNDS[x]}` }
})
const round = ref("1")

// waiting dialog
const waitingdialog = ref(false)
let dialogcounter = 0

function changeDialogCounter(i) {
  dialogcounter += i
  waitingdialog.value = (dialogcounter > 0)
}

// snackbar
const errortext = ref(null)
const snackbar = ref(null)
function displaySnackbar(text, color) {
  errortext.value = text
  snackbar.value = true
}

// API backend
const { $backend } = useNuxtApp()

// methods alphabetically


async function getClubs() {
  let reply
  changeDialogCounter(1)
  try {
    reply = await $backend("club", "anon_get_clubs", {})
  } catch (error) {
    if (error.code == 401) gotoLogin()
    displaySnackbar($t(error.message))
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
      reply = await $backend("interclub", "clb_getICclub", {
        idclub: idclub.value,
        token: idtoken.value
      })
    } catch (error) {
      if (error.code == 401) gotoLogin()
      displaySnackbar($t(error.message))
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


function selectClub() {
  console.log('selected', idclub.value)
  getClubDetails()
}

onMounted(() => {
  checkAuth()
  getClubs()
  tab.value = "results"
  changeTab()
})

</script>

<template>
  <VContainer>
    <h1>Interclubs Manager</h1>
    <v-dialog width="10em" v-model="waitingdialog">
      <v-card>
        <v-card-title>{{ $t('Loading...') }}</v-card-title>
        <v-card-text>
          <v-progress-circular indeterminate color="green" />
        </v-card-text>
      </v-card>
    </v-dialog>
    <v-card>
      <v-card-text>
        <v-row>
          <v-col cols="12" sm="6">
            <VAutocomplete v-model="idclub" :items="clubs" item-title="merged" item-value="idclub"
              color="green" label="Club" clearable @update:model-value="selectClub">
            </VAutocomplete>
          </v-col>
          <v-col cols="12" sm="6">
            <VSelect v-model="round" :items="ic_rounds" :label="$t('Round')"
              @update:model-value="changeTab">
            </VSelect>
          </v-col>
        </v-row>
      </v-card-text>
    </v-card>
    <h3 class="my-2">
      {{ $t('Selected club') }}: {{ icclub.idclub }} {{ icclub.name }}
    </h3>
    <div class="elevation-2">
      <v-tabs v-model="tab" color="green" @update:modelValue="changeTab">
        <v-tab value="results">{{ $t('Results') }}</v-tab>
        <v-tab value="planning">{{ $t('Planning') }}</v-tab>
        <v-tab value="venues">{{ $t('Venue') }}</v-tab>
        <v-tab value="playerlist">{{ $t('Player list') }}</v-tab>
      </v-tabs>
      <v-window v-model="tab" @update:modelValue="changeTab">
        <v-window-item :eager="true" value="results">
          <Results ref="refresults" @snackbar="displaySnackbar"
            @changeDialogCounter="changeDialogCounter" />
        </v-window-item>
        <v-window-item :eager="true" value="planning">
          <Planning ref="refplanning" @snackbar="displaySnackbar"
            @changeDialogCounter="changeDialogCounter" />
        </v-window-item>
        <v-window-item :eager="true" value="venues">
          <Venue ref="refvenues" @snackbar="displaySnackbar"
            @changeDialogCounter="changeDialogCounter" />
        </v-window-item>
        <v-window-item :eager="true" value="playerlist">
          <Playerlist ref="refplayerlist" />
        </v-window-item>
      </v-window>
    </div>
    <VSnackbar v-model="snackbar" timeout="6000">
      {{ errortext }}
      <template v-slot:actions>
        <v-btn color="green-lighten-2" variant="text" @click="snackbar = false" icon="mdi-close" />
      </template>
    </VSnackbar>
  </VContainer>

</template>