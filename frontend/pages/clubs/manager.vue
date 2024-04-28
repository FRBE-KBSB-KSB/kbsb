<script setup>
import { ref, onMounted, nextTick } from 'vue'
import { useI18n } from 'vue-i18n'
import Details from '@/components/club/Details.vue'
import Board from '@/components/club/Board.vue'
import Access from '@/components/club/Access.vue'

import { EMPTY_CLUB } from '@/util/club'
import { useIdtokenStore } from '@/store/idtoken'
import { storeToRefs } from 'pinia'


const { locale, t } = useI18n()
const router = useRouter()
const { $backend } = useNuxtApp()
const idstore = useIdtokenStore()
const { token: idtoken } = storeToRefs(idstore)


const clubmembers = ref(null)
const clubmembers_id = ref(0)
const club = ref(EMPTY_CLUB)
const clubs = ref([])
const idclub = ref(null)
const waitingdialog = ref(false)
let dialogcounter = 0
const board = ref(null)
const detail = ref(null)
const access = ref(null)
const tab = ref(null)
const errortext = ref(null)
const snackbar = ref(null)

function checkAuth() {
  if (!idtoken.value) {
    gotoLogin()
  }
}

function changeDialogCounter(i) {
  dialogcounter += i
  waitingdialog.value = (dialogcounter > 0)
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
  club.value = EMPTY_CLUB
  if (idclub.value) {
    changeDialogCounter(1)
    try {
      reply = await $backend("club", "verify_club_access", {
        idclub: idclub.value,
        role: "ClubAdmin",
        token: idtoken.value,
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
        token: idtoken.value
      })
    } catch (error) {
      if (error.code == 401) gotoLogin()
      displaySnackbar(t(t(error.message)))
      return
    } finally {
      changeDialogCounter(-1)
    }
    club.value = reply.data
  }
  nextTick(() => {
    detail.value.readClubDetails()
    board.value.readClubDetails()
    access.value.readClubDetails()
  })
}

async function getClubMembers() {
  // get club members for member database currently on old site
  if (!idclub.value) return
  if (idclub.value == clubmembers_id.value) return  // it is already read in
  changeDialogCounter(1)
  let reply
  clubmembers.value = null
  try {
    reply = await $backend("member", "anon_getclubmembers", {
      idclub: idclub.value,
    })
  } catch (error) {
    if (error.code == 401) gotoLogin()
    displaySnackbar(t(error.message))
    return
  } finally {
    changeDialogCounter(-1)
  }
  clubmembers_id.value = idclub.value
  const members = reply.data
  members.forEach(p => {
    p.merged = `${p.idnumber}: ${p.first_name} ${p.last_name}`
  })
  clubmembers.value = members.sort((a, b) =>
    (a.last_name > b.last_name ? 1 : -1))
  nextTick(() => {
    board.value.readClubMembers()
    access.value.readClubMembers()
  })
}

async function gotoLogin() {
  await router.push('/tools/oldlogin?url=__clubs__manager')
}

function displaySnackbar(text, color) {
  errortext.value = text
  snackbar.value = true
}

async function selectClub() {
  await getClubDetails()
  await getClubMembers()
}

onMounted(() => {
  checkAuth()
  getClubs()
})
</script>

<template>
  <VContainer>
    <h1>Club Manager</h1>
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
        {{ $t('Select the club') }} ({{ $t('Start typing number or name') }})
        <VAutocomplete v-model="idclub" :items="clubs" item-title="merged" item-value="idclub"
          color="green" label="Club" clearable @update:model-value="selectClub">
        </VAutocomplete>
      </v-card-text>
    </v-card>
    <h3 class="mt-2">
      {{ $t('Selected club') }}: {{ club.idclub }} {{ club.name_short }}
    </h3>
    <div class="elevation-2">
      <v-tabs v-model="tab" color="green">
        <v-tab>{{ $t('Details') }}</v-tab>
        <v-tab>{{ $t('Board members') }}</v-tab>
        <v-tab>{{ $t('Access Rights') }}</v-tab>
      </v-tabs>
      <v-window v-model="tab">
        <v-window-item :eager="true">
          <Details :club="club" ref="detail" @snackbar="displaySnackbar"
            @updateClub="getClubDetails" />
        </v-window-item>
        <v-window-item :eager="true">
          <Board :club="club" :clubmembers="clubmembers" ref="board" @snackbar="displaySnackbar"
            @updateClub="getClubDetails" />
        </v-window-item>
        <v-window-item :eager="true">
          <Access :club="club" :clubmembers="clubmembers" ref="access" @snackbar="displaySnackbar"
            @updateClub="getClubDetails" />
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