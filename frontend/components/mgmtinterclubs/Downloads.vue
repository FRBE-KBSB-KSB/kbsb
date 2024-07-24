<script setup>
import { ref, computed } from 'vue'
import { useMgmtTokenStore } from "@/store/mgmttoken"
import { storeToRefs } from 'pinia'

// communication
defineExpose({ setup })
const mgmttokenstore = useMgmtTokenStore()
const { token: idtoken } = storeToRefs(mgmttokenstore)
const { $backend } = useNuxtApp()

//  snackbar and loading widgets
import ProgressLoading from '@/components/ProgressLoading.vue'
import SnackbarMessage from '@/components/SnackbarMessage.vue'
const refsnackbar = ref(null)
let showSnackbar
const refloading = ref(null)
let showLoading


async function download_registrations() {
  let reply, xls
  showLoading(true)
  try {
    reply = await $backend("interclub", "mgmt_xls_icregistrations", {
      token: idtoken.value
    })
    xls = reply.data.xls64
  }
  catch (error) {
    console.log('download error', error)
    showSnackbar('Download error: ' + error.detail)
  }
  finally {
    showLoading(false)
  }
  const link = document.createElement('a')
  link.download = 'reservations_2425.xlsx'
  link.href = 'data:application/excel;base64,' + xls
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  showSnackbar('Downloading reservations successful')
}

async function download_venues() {
  let reply, xls
  showLoading(true)
  try {
    reply = await $backend("interclub", "mgmt_xls_icvenues", {
      token: idtoken.value
    })
    xls = reply.data.xls64
  }
  catch (error) {
    console.log('download error', error)
    showSnackbar('Download error: ' + error.detail)
  }
  finally {
    showLoading(false)
  }
  const link = document.createElement('a')
  link.download = 'venues_2425.xlsx'
  link.href = 'data:application/excel;base64,' + xls
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  showSnackbar('Downloading reservations successful')
}

// async function generateBelELO() {
//   showLoading(true)
//   try {
//     const reply = await $backend("interclub", "mgmt_generate_bel_elo", {
//       round: round.value,
//       token: mgmttoken.value,
//     })
//     showSnackbar("BEL elo rapport created")
//   }
//   catch (error) {
//     showSnackbar(error.message)
//   }
//   finally {
//     showLoading(false)
//   }
// }

// async function generateFideELO() {
//   showLoading(true)
//   try {
//     const reply = await $backend("interclub", "mgmt_generate_fide_elo", {
//       round: round.value,
//       token: mgmttoken.value,
//     })
//     showSnackbar("FIDE elo rapport created")
//   }
//   catch (error) {
//     console.error(error)
//     showSnackbar(error.message)
//   }
//   finally {
//     showLoading(false)
//   }
// }

async function setup(icclub_, icdata_) {
  console.log('setup Downloads', icclub_, icdata_)
}

// trigger
onMounted(() => {
  showSnackbar = refsnackbar.value.showSnackbar
  showLoading = refloading.value.showLoading
})

</script>

<template>
  <VContainer>
    <SnackbarMessage ref="refsnackbar" />
    <ProgressLoading ref="refloading" />
    <h3>Registrations</h3>
    <v-btn @click="download_registrations">Download registrations</v-btn>
    <h3>Venues</h3>
    <v-btn @click="download_venues">Download venues</v-btn>
  </VContainer>
</template>
