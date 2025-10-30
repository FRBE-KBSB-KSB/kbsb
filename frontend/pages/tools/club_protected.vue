<script setup>
import { ref, onMounted } from "vue"
import { useI18n } from "vue-i18n"
import { useRouter } from "vue-router"
import { useIdtokenStore } from "@/store/idtoken"
import { useIdnumberStore } from "@/store/idnumber"

import Details from "@/components/club/Details.vue"
import Board from "@/components/club/Board.vue"
import Access from "@/components/club/Access.vue"

import { EMPTY_CLUB } from "@/util/club"
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

// locale
const { locale, t } = useI18n()

// API backend
const { $backend } = useNuxtApp()
const idstore = useIdtokenStore()
const { token } = storeToRefs(idstore)

// data model
const tab = ref("details")
const clubmembers = ref(null)
const clubmembers_id = ref(0)
const club = ref(EMPTY_CLUB)
const clubs = ref([])
const idclub = ref(null)
const refboard = ref(null)
const refdetails = ref(null)
const refaccess = ref(null)

function changeDialogCounter(i) {
  dialogcounter += i
  waitingdialog.value = dialogcounter > 0
}

function changeTab() {
  console.log("changeTab", tab.value)
  switch (tab.value) {
    case "details":
      refdetails.value.setup(club.value)
      break
    case "board":
      refboard.value.setup(club.value, clubmembers.value)
      break
    case "access":
      refaccess.value.setup(club.value, clubmembers.value)
  }
}

function checkAuth() {
  if (!token.value) {
    gotoLogin()
  }
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
  changeTab()
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
  club.value = EMPTY_CLUB
  if (idclub.value) {
    changeDialogCounter(1)
    try {
      reply = await $backend("club", "verify_club_access", {
        idclub: idclub.value,
        role: "ClubAdmin",
        token: token.value,
      })
    } catch (error) {
      if (error.code == 401) gotoLogin()
      displaySnackbar(t(error.message))
      return
    } finally {
      changeDialogCounter(-1)
    }
    changeDialogCounter(1)
    try {
      reply = await $backend("club", "clb_get_club", {
        idclub: idclub.value,
        token: token.value,
      })
      club.value = reply.data
    } catch (error) {
      if (error.code == 401) gotoLogin()
      displaySnackbar(t(t(error.message)))
      return
    } finally {
      changeDialogCounter(-1)
      changeTab()
    }
  }
}

async function getClubMembers() {
  // get club members for member database currently on old site
  if (!idclub.value) return
  if (idclub.value == clubmembers_id.value) return // it is already read in
  changeDialogCounter(1)
  let reply
  clubmembers.value = null
  try {
    reply = await $backend("member", "anon_getclubmembers", {
      idclub: idclub.value,
    })
    clubmembers_id.value = idclub.value
    const members = reply.data
    members.forEach((p) => {
      p.merged = `${p.idnumber}: ${p.first_name} ${p.last_name}`
    })
    clubmembers.value = members.sort((a, b) => (a.last_name > b.last_name ? 1 : -1))
  } catch (error) {
    if (error.code == 401) gotoLogin()
    displaySnackbar(t(error.message))
    return
  } finally {
    changeDialogCounter(-1)
    changeTab()
  }
}

function displaySnackbar(text, color) {
  errortext.value = text
  snackbar.value = true
}

async function gotoLogin() {
  await router.push("/tools/oldlogin?url=__tools__club_protected?locale=" + locale.value)
}

async function selectClub() {
  await getClubDetails()
  await getClubMembers()
}

// setup

onMounted(() => {
  let l = route.query.locale
  console.log("query locale", l)
  locale.value = l ? l : "nl"
  checkAuth()
  getClubs()
})

definePageMeta({
  layout: "nomenu",
})
</script>

<template>
  <VContainer>
    <h1>Club Manager</h1>
    <v-dialog width="10em" v-model="waitingdialog">
      <v-card>
        <v-card-title>{{ $t("Loading...") }}</v-card-title>
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
    <v-card>
      <v-card-text>
        {{ $t("Select the club") }} ({{ $t("Start typing number or name") }})
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
      </v-card-text>
    </v-card>
    <h3 class="mt-2">
      {{ $t("Selected club") }}: {{ club.idclub }} {{ club.name_short }}
    </h3>
    <div class="elevation-2">
      <v-tabs v-model="tab" color="green" @update:modelValue="changeTab">
        <v-tab value="details">{{ $t("Details") }}</v-tab>
        <v-tab value="board">{{ $t("Board members") }}</v-tab>
        <v-tab value="access">{{ $t("Access Rights") }}</v-tab>
      </v-tabs>
      <v-window v-model="tab" @update:modelValue="changeTab" :touch="false">
        <v-window-item :eager="true" value="details">
          <Details ref="refdetails" @updateClub="getClubDetails" />
        </v-window-item>
        <v-window-item :eager="true" value="board">
          <Board ref="refboard" @updateClub="getClubDetails" />
        </v-window-item>
        <v-window-item :eager="true" value="access">
          <Access ref="refaccess" @updateClub="getClubDetails" />
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
