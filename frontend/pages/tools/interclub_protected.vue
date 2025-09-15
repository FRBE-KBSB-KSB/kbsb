b
<script setup>
import { ref, onMounted } from "vue"
import { useI18n } from "vue-i18n"
import { useRouter } from "vue-router"
import { useIdtokenStore } from "@/store/idtoken"
import { useIdnumberStore } from "@/store/idnumber"
import showdown from "showdown"

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
const idnstore = useIdnumberStore()

// help dialog
const mdConverter = new showdown.Converter()
const helptitle = ref("")
const helpdialog = ref(false)
const helpcontent = ref("")

// locale
const { locale, t } = useI18n()

// API backend
const { $backend } = useNuxtApp()
const idstore = useIdtokenStore()
const { token: idtoken } = storeToRefs(idstore)

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
let registration_phase = false

// methods alphabetically

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
      refregistration.value.setup(icclub.value, icdata.value)
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
  if (!idtoken.value) {
    logindialog.value = true
  }
}

function displaySnackbar(text, color) {
  errortext.value = text
  snackbar.value = true
}

async function dologin() {
  console.log("doing a login")
  changeDialogCounter(1)
  let reply
  try {
    reply = await $backend("member", "login", {
      idnumber: login.value.idnumber,
      password: login.value.password,
    })
    console.log("did a login", reply.data)
  } catch (error) {
    console.error("failed login", error)
    displaySnackbar(t(error.message))
    return
  } finally {
    changeDialogCounter(-1)
  }
  idstore.updateToken(reply.data)
  idnstore.updateIdnumber(login.value.idnumber)
  logindialog.value = false
  changedTab()
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
}

async function getClubDetails() {
  let reply
  icclub.value = { idclub: idclub.value }
  changeDialogCounter(1)
  try {
    reply = await $backend("interclub", "clb_getICclub", {
      idclub: idclub.value,
      token: idtoken.value,
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

// async function getHelpContent() {
//   try {
//     const reply = await $backend("filestore", "anon_get_file", {
//       group: "data",
//       name: `help-login.md`,
//     })
//     metadata.value = useMarkdown(reply.data).metadata
//     helptitle.value = metadata.value["title_" + locale.value]
//     helpcontent.value = mdConverter.makeHtml(metadata.value["content_" + locale.value])
//   } catch (error) {
//     console.log("failed")
//   }
// }

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
  ic_rounds.value = Object.keys(icdata.value.rounds).map((x) => {
    return { value: x, title: `R${x}: ${icdata.value.rounds[x]}` }
  })
  registration_phase =
    icdata.value.registration_data.end >= new Date().toISOString().slice(0, 10)
  changedTab()
}

async function selectClub() {
  console.log("selected", idclub.value)
  await getClubDetails()
}

// startup

onMounted(async () => {
  console.log("mounted")
  let l = route.query.locale
  locale.value = l ? l : "nl"
  checkAuth()
  await processICdata()
  getClubs()
  changedTab()
  // await getHelpContent()
})

definePageMeta({
  layout: "nomenu",
})
</script>

<template>
  <VContainer>
    <h1>Interclubs Manager 2025-26</h1>
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
          <VBtn
            icon="mdi-help"
            color="green"
            class="float-right"
            @click="helpdialog = true"
          />
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
    <VDialog v-model="helpdialog" width="20em">
      <VCard>
        <VCardTitle v-html="helptitle" />
        <VDivider />
        <VCardText class="pa-3 ma-1 markdowncontent" v-html="helpcontent" />
      </VCard>
    </VDialog>
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
        <v-tab value="playerlist">{{ t("Player list") }}</v-tab>
        <!-- <v-tab value="results">{{ t("Results") }}</v-tab>
        <v-tab value="planning">{{ t("Planning") }}</v-tab> -->
        <!-- <v-tab value="registration">{{ t("icn.enr") }}</v-tab> -->
        <v-tab value="venues">{{ t("icn.ven_1") }}</v-tab>
      </v-tabs>
      <v-window v-model="tab" @update:modelValue="changedTab" :touch="false">
        <v-window-item :eager="true" value="playerlist">
          <Playerlist ref="refplayerlist" />
        </v-window-item>
        <!-- <v-window-item :eager="true" value="results">
          <Results
            ref="refresults"
            @snackbar="displaySnackbar"
            @changeDialogCounter="changeDialogCounter"
          />
        </v-window-item>
        <v-window-item :eager="true" value="planning">
          <Planning
            ref="refplanning"
            @snackbar="displaySnackbar"
            @changeDialogCounter="changeDialogCounter"
          />
        </v-window-item> -->
        <!-- <v-window-item :eager="true" value="registration">
          <Registration
            ref="refregistration"
            @snackbar="displaySnackbar"
            @changeDialogCounter="changeDialogCounter"
          />
        </v-window-item> -->
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
