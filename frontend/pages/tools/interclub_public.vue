<script setup>
import { ref, onMounted } from "vue"
import { useI18n } from "vue-i18n"
import { useRoute } from "vue-router"
import ResultsPublic from "@/components/interclubs/ResultsPublic.vue"
import Standings from "@/components/interclubs/Standings.vue"
import VenuePublic from "@/components/interclubs/VenuePublic.vue"
import PlayerlistPublic from "@/components/interclubs/PlayerlistPublic.vue"

// locale
const { locale, t } = useI18n()

// communication
const route = useRoute()
const waitingdialog = ref(false)
let dialogcounter = 0
const errortext = ref(null)
const snackbar = ref(null)

// API backend
const { $backend } = useNuxtApp()

// datamodel
const tab = ref(null)
const refresults = ref(null)
const refstandings = ref(null)
const refplayerlist = ref(null)
const refvenues = ref(null)
const clubs = ref([])
const icclub = ref({}) // the icclub data
const idclub = ref(null)
const icdata = ref({})
const ic_rounds = ref([])

// methods alphabetically

function changeDialogCounter(i) {
  dialogcounter += i
  waitingdialog.value = dialogcounter > 0
}

function changedTab() {
  console.log("changeTab", tab.value)
  switch (tab.value) {
    case "results":
      refresults.value.setup(icdata.value)
      break
    case "standings":
      refstandings.value.setup(icdata.value)
      break
    case "playerlist":
      refplayerlist.value.setup()
      break
    case "venues":
      refvenues.value.setup(idclub.value, icdata.value)
      break
  }
}

function displaySnackbar(text, color) {
  errortext.value = text
  snackbar.value = true
}

async function getICClubs() {
  let reply
  changeDialogCounter(1)
  try {
    reply = await $backend("interclub", "anon_getICclubs", {})
    console.log("reply", reply)
  } catch (error) {
    if (error.code == 401) gotoLogin()
    displaySnackbar(error.message)
    return
  } finally {
    changeDialogCounter(-1)
  }
  clubs.value = reply.data
  clubs.value.forEach((p) => {
    console.log("p", p)
    p.merged = `${p.idclub}: ${p.name}`
  })
}

async function processICdata() {
  let reply
  changeDialogCounter(1)
  try {
    reply = await $backend("interclub", "icdata", {})
  } catch (error) {
    displaySnackbar(t(error.message))
    return
  } finally {
    changeDialogCounter(-1)
  }
  icdata.value = reply.data
  ic_rounds.value = Object.keys(icdata.value.rounds11).map((x) => {
    return { value: x, title: `R${x}: ${icdata.value.rounds11[x]}` }
  })
  changedTab()
}

function selectClub() {
  console.log("selected", idclub.value)
  changedTab()
}

onMounted(async () => {
  let l = route.query.locale
  locale.value = l ? l : "nl"
  await processICdata()
  await getICClubs()

  changedTab()
})

definePageMeta({
  layout: "nomenu",
})
</script>

<template>
  <v-container>
    <h1>Interclubs 2026-27</h1>
    <VCard>
      <VCardText>
        <v-row>
          <v-col cols="12" sm="6">
            <VAutocomplete
              v-model="idclub"
              :items="clubs"
              item-title="merged"
              item-value="idclub"
              color="green"
              label="Club"
              clearable
              @update:model-value="selectClub"
            >
            </VAutocomplete>
          </v-col>
          <v-col cols="12" sm="6">
            <VSelect
              v-model="round"
              :items="ic_rounds"
              label="Round"
              @update:model-value="changedTab"
            >
            </VSelect>
          </v-col>
        </v-row>
      </VCardText>
    </VCard>
    <v-tabs v-model="tab" color="green" @update:modelValue="changedTab">
      <!-- <v-tab value="results">{{ t("Results") }}</v-tab>
      <v-tab value="standings">{{ t("Standings") }}</v-tab>
      <v-tab value="playerlist">{{ t("Player list") }}</v-tab> -->
      <v-tab value="venues">{{ t("icn.ven_2") }}</v-tab>
    </v-tabs>
    <v-window v-model="tab" @update:modelValue="changedTab" :touch="false">
      <v-window-item :eager="true" value="venues">
        <VenuePublic ref="refvenues" />
      </v-window-item>
      <v-window-item :eager="true" value="results">
        <ResultsPublic ref="refresults" />
      </v-window-item>
      <v-window-item :eager="true" value="standings">
        <Standings ref="refstandings" />
      </v-window-item>
      <v-window-item :eager="true" value="playerlist">
        <PlayerlistPublic ref="refplayerlist" />
      </v-window-item>
    </v-window>
  </v-container>
</template>
