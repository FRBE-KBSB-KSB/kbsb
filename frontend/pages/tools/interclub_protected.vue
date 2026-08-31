b
<script setup>
import { ref, onMounted } from "vue"
import { useI18n } from "vue-i18n"
import { useRouter } from "vue-router"
import { useIdtokenStore } from "@/store/idtoken"
import { useIdbelStore } from "@/store/idbel"

import Registration from "~/components/interclubs/Registration.vue"
import Results from "@/components/interclubs/Results.vue"
import Planning from "@/components/interclubs/Planning.vue"
import Playerlist from "@/components/interclubs/Playerlist.vue"
import Venue from "@/components/interclubs/Venue.vue"
import { parse } from "yaml"
import { storeToRefs } from "pinia"

// communication
const router = useRouter()
const route = useRoute()
const waitingdialog = ref(false)
let dialogcounter = 0
const errortext = ref(null)
const snackbar = ref(null)

// login
const logindialog = ref(false)
const login = ref({})
const idbelstore = useIdbelStore()

// locale
const { locale, t } = useI18n()

// API backend
const { $backend } = useNuxtApp()
const idstore = useIdtokenStore()
const { token } = storeToRefs(idstore)

// data model
const tab = ref("registration")
const refregistration = ref(null)
const refplanning = ref(null)
const refplayerlist = ref(null)
const refresults = ref(null)
const refvenues = ref(null)
const icdata = ref({})
const clubs = ref([])
const icclub = ref({}) // the icclub data
const idclub = ref(null)
const ic_rounds = ref([])
const round = ref("1")
const phase = ref("unknown")

// methods alphabetically

function calcPhase() {
  if (route.query.phase) {
    phase.value = route.query.phase
    if (phase.value == "registration") {
      tab.value = "registration"
      changedTab()
    }
    return
  }
  let start_registration = new Date(icdata.value.registration_data.start)
  console.log("start_registration", start_registration)
  let end_registration = new Date(icdata.value.registration_data.end)
  console.log("end_registration", end_registration)
  let today = new Date()
  if (
    end_registration.valueOf() >= today.valueOf() &&
    start_registration.valueOf() <= today.valueOf()
  ) {
    phase.value = "registration"
    tab.value = "registration"
    changedTab()
    return
  }
  if (start_registration.valueOf() > today.valueOf()) {
    phase.value = "unknown"
    return
  }
  phase.value = "started"
}

function changeDialogCounter(i) {
  dialogcounter += i
  waitingdialog.value = dialogcounter > 0
}

function changedTab() {
  console.log("changedTab", tab.value)
  switch (tab.value) {
    case "planning":
      refplanning.value.setup(icclub.value, round.value, icdata.value)
      break
    case "playerlist":
      refplayerlist.value.setup(icclub.value, icdata.value)
      break
    case "registration":
      refregistration.value.setup(icclub.value, icdata.value, locale.value)
      break
    case "results":
      refresults.value.setup(icclub.value, round.value, icdata.value)
      break
    case "venues":
      refvenues.value.setup(icclub.value, icdata.value)
      break
  }
}

function checkAuth() {
  if (!token.value) {
    gotoLogin()
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
    displaySnackbar(t(error.message))
    return
  } finally {
    changeDialogCounter(-1)
  }
  clubs.value = reply.data
  clubs.value.forEach((p) => {
    p.merged = `${p.idclub}: ${p.name_short} ${p.name_long}`
  })
  console.log("got clubs", clubs.value)
}

async function getClubDetails() {
  let reply
  icclub.value = { idclub: idclub.value }
  changeDialogCounter(1)
  try {
    reply = await $backend("interclub", "clb_getICclub", {
      idclub: idclub.value,
      token: token.value,
    })
    icclub.value = { idclub: idclub.value, ...(reply.data || {}) }
  } catch (error) {
    console.log("did not find clubdetails", icclub.value)
    if (error.code == 401) gotoLogin()
    displaySnackbar(t(error.message))
    return
  } finally {
    changeDialogCounter(-1)
    changedTab()
  }
}

async function gotoLogin() {
  await router.push(
    "/tools/odoologin?url=__tools__interclub_protected?locale=" + locale.value
  )
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
}

async function selectClub() {
  console.log("selected", idclub.value)
  await getClubDetails()
}

// startup

onMounted(async () => {
  let l = route.query.locale
  locale.value = l ? l : "nl"
  checkAuth()
  await processICdata()
  calcPhase()
  getClubs()
  changedTab()
})

definePageMeta({
  layout: "nomenu",
})
</script>

<template>
  <VContainer>
    <h1>Interclubs Manager 2026-27</h1>
    <v-dialog width="10em" v-model="waitingdialog">
      <v-card>
        <v-card-title>{{ t("Loading...") }}</v-card-title>
        <v-card-text>
          <v-progress-circular indeterminate color="green" />
        </v-card-text>
      </v-card>
    </v-dialog>
    <v-dialog width="25em" v-model="logindialog">
      <VCard>
        <VCardTitle>
          <VIcon large> mdi-account </VIcon>
          <label class="headline ml-3">{{ $t("Sign in") }}</label>
        </VCardTitle>
        <VDivider />
        <VCardText>
          <VTextField v-model="login.idnumber" :label="$t('ID number')" />
          <VTextField
            v-model="login.password"
            xs="12"
            lg="6"
            :label="$t('Password')"
            type="password"
          />
        </VCardText>
        <VCardActions>
          <VSpacer />
          <VBtn @click="dologin()">
            {{ $t("Submit") }}
          </VBtn>
        </VCardActions>
      </VCard>
    </v-dialog>
    <v-card>
      <v-card-text>
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
              :label="t('Round')"
              @update:model-value="changedTab"
            >
            </VSelect>
          </v-col>
        </v-row>
      </v-card-text>
    </v-card>
    <h3 class="my-2">{{ t("Selected club") }}: {{ icclub.idclub }} {{ icclub.name }}</h3>
    <div class="elevation-2">
      <v-tabs v-model="tab" color="green" @update:modelValue="changedTab">
        <v-tab v-if="phase == 'started'" value="results">{{ t("Results") }}</v-tab>
        <v-tab v-if="phase == 'started'" value="planning">{{ t("Planning") }}</v-tab>
        <v-tab v-if="phase == 'started'" value="playerlist">{{ t("Player list") }}</v-tab>
        <v-tab v-if="phase == 'registration'" value="registration">{{
          t("icn.enr")
        }}</v-tab>
        <v-tab value="venues">{{ t("icn.ven_1") }}</v-tab>
      </v-tabs>
      <v-window v-model="tab" @update:modelValue="changedTab" :touch="false">
        <v-window-item :eager="true" value="results">
          <Results ref="refresults" />
        </v-window-item>
        <v-window-item :eager="true" value="planning">
          <Planning ref="refplanning" />
        </v-window-item>
        <v-window-item :eager="true" value="playerlist">
          <Playerlist ref="refplayerlist" />
        </v-window-item>
        <v-window-item :eager="true" value="registration">
          <Registration
            ref="refregistration"
            @snackbar="displaySnackbar"
            @changeDialogCounter="changeDialogCounter"
          />
        </v-window-item>
        <v-window-item :eager="true" value="venues">
          <Venue
            ref="refvenues"
            @snackbar="displaySnackbar"
            @changeDialogCounter="changeDialogCounter"
          />
        </v-window-item>
      </v-window>
    </div>
    <VSnackbar v-model="snackbar" timeout="6000">
      {{ errortext }}
      <template v-slot:actions>
        <v-btn
          color="green-lighten-2"
          variant="text"
          @click="snackbar = false"
          icon="mdi-close"
        />
      </template>
    </VSnackbar>
  </VContainer>
</template>
