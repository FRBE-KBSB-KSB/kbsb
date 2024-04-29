<script setup>
import { ref, onMounted, nextTick } from 'vue'
import ProgressLoading from '@/components/ProgressLoading.vue'
import SnackbarMessage from '@/components/SnackbarMessage.vue'

import { EMPTY_CLUB } from '@/util/club'
import { useMgmtTokenStore } from "@/store/mgmttoken";
import { usePersonStore } from "@/store/person"
import { storeToRefs } from 'pinia'

// stores
const mgmtstore = useMgmtTokenStore()
const { token: mgmttoken } = storeToRefs(mgmtstore)
const personstore = usePersonStore();
const { person } = storeToRefs(personstore)

//  snackbar and loading widgets
const refsnackbar = ref(null)
let showSnackbar
const refloading = ref(null)
let showLoading

// datamodel
const clubmembers = ref(null)
const clubmembers_id = ref(0)
const club = ref(EMPTY_CLUB)
const clubs = ref([])
const idclub = ref(null)


// communication
const { $backend } = useNuxtApp()
const tab = ref(null)
const refboard = ref(null)
const refdetails = ref(null)
const refaccess = ref(null)
function changeTab() {
  console.log('changeTab', tab.value)
  switch (tab.value) {
    case 'access':
      refaccess.value.setup(club.value)
      break
    case 'board':
      refboard.value.setup(club.value)
      break
    case 'details':
      console.log('refdetails', refdetails.value)
      refdetails.value.setup(club.value)
      break
  }
}


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

async function checkAuth() {
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
    navigateTo('/mgmt')
  }
  finally {
    showLoading(false)
  }
  mgmtstore.updateToken(reply.data)
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
  let reply
  club.value = EMPTY_CLUB
  if (idclub.value) {
    showLoading(true)
    try {
      reply = await $backend("club", "mgmt_get_club", {
        idclub: idclub.value,
        token: mgmttoken.value
      })
    } catch (error) {
      console.log('getClubDetails error', error)
      showSnackbar(error.message)
      return
    } finally {
      showLoading(false)
    }
    club.value = reply.data
    refdetails.value.setup(club.value)
    refaccess.value.setup(club.value)
  }
}

async function getClubMembers() {
  // get club members for member database currently on old site
  if (!idclub.value) return
  if (idclub.value == clubmembers_id.value) return  // it is already read in
  let reply
  clubmembers.value = null
  showLoading(true)
  try {
    reply = await $backend("member", "anon_getclubmembers", {
      idclub: idclub.value,
    })
  } catch (error) {
    console.log('getClubMembers error')
    showSnackbar(error.message)
    return
  } finally {
    showLoading(false)
  }
  clubmembers_id.value = idclub.value
  const members = reply.data
  members.forEach(p => {
    p.merged = `${p.idnumber}: ${p.first_name} ${p.last_name}`
  })
  clubmembers.value = members.sort((a, b) =>
    (a.last_name > b.last_name ? 1 : -1))
  refboard.value.copyClubMembers(clubmembers.value)
  refaccess.value.copyClubMembers(clubmembers.value)
}

async function selectClub() {
  await getClubDetails()
  await getClubMembers()
}

function updateClubDetails() {
  console.log('getting updated club details')
}

onMounted(() => {
  showSnackbar = refsnackbar.value.showSnackbar
  showLoading = refloading.value.showLoading
  changeTab('details')
  checkAuth()
  getClubs()
})

</script>

<template>
  <VContainer>
    <SnackbarMessage ref="refsnackbar" />
    <ProgressLoading ref="refloading" />
    <h1>Management Reports</h1>
    Still in progress
  </VContainer>
</template>