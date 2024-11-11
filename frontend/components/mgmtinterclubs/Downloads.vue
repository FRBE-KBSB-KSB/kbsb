<script setup>
import { ref, computed } from "vue"
import { useMgmtTokenStore } from "@/store/mgmttoken"
import { storeToRefs } from "pinia"

// communication
defineExpose({ setup })
const mgmttokenstore = useMgmtTokenStore()
const { token: idtoken } = storeToRefs(mgmttokenstore)
const { $backend } = useNuxtApp()

//  snackbar and loading widgets
import ProgressLoading from "@/components/ProgressLoading.vue"
import SnackbarMessage from "@/components/SnackbarMessage.vue"
const refsnackbar = ref(null)
let showSnackbar
const refloading = ref(null)
let showLoading

// data model
let icclub, round, icdata
const bel_reports = ref([])
const fide_reports = ref([])
const penalties_reports = ref([])

async function download_registrations() {
  let reply, xls
  showLoading(true)
  try {
    reply = await $backend("interclub", "mgmt_xls_icregistrations", {
      token: idtoken.value,
    })
    xls = reply.data.xls64
  } catch (error) {
    console.log("download error", error)
    showSnackbar("Download error: " + error.detail)
  } finally {
    showLoading(false)
  }
  const link = document.createElement("a")
  link.download = "reservations_2425.xlsx"
  link.href = "data:application/excel;base64," + xls
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  showSnackbar("Downloading registrations successful")
}

async function download_venues() {
  let reply, xls
  showLoading(true)
  try {
    reply = await $backend("interclub", "mgmt_xls_icvenues", {
      token: idtoken.value,
    })
    xls = reply.data.xls64
  } catch (error) {
    console.log("download error", error)
    showSnackbar("Download error: " + error.detail)
  } finally {
    showLoading(false)
  }
  const link = document.createElement("a")
  link.download = "venues_2425.xlsx"
  link.href = "data:application/excel;base64," + xls
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  showSnackbar("Downloading venues successful")
}

async function download_playerlists() {
  let reply, xls
  showLoading(true)
  try {
    reply = await $backend("interclub", "mgmt_xls_playerlists", {
      token: idtoken.value,
    })
    xls = reply.data.xls64
  } catch (error) {
    console.log("download error", error)
    showSnackbar("Download error: " + error.detail)
  } finally {
    showLoading(false)
  }
  const link = document.createElement("a")
  link.download = "playerlists_2425.xlsx"
  link.href = "data:application/excel;base64," + xls
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  showSnackbar("Downloading playerlists successful")
}

async function get_bel_report(bp) {
  let reply, report
  showLoading(true)
  try {
    reply = await $backend("interclub", "get_bel_report", {
      token: idtoken.value,
      path: bp,
    })
    report = reply.data.report
  } catch (error) {
    console.log("download error", error)
    showSnackbar("Download error: " + error.detail)
  } finally {
    showLoading(false)
  }
  const link = document.createElement("a")
  link.download = bp
  link.href = "data:text/plain;base64," + report
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  showSnackbar("Downloading bel report successful")
}

async function list_bel_reports() {
  let reply, report
  showLoading(true)
  try {
    reply = await $backend("interclub", "list_bel_reports", {
      token: idtoken.value,
    })
    bel_reports.value = reply.data
  } catch (error) {
    console.log("download error", error)
    showSnackbar("Download error: " + error.detail)
  } finally {
    showLoading(false)
  }
}

async function get_fide_report(bp) {
  let reply, report
  showLoading(true)
  try {
    reply = await $backend("interclub", "get_fide_report", {
      token: idtoken.value,
      path: bp,
    })
    report = reply.data.report
  } catch (error) {
    console.log("download error", error)
    showSnackbar("Download error: " + error.detail)
  } finally {
    showLoading(false)
  }
  const link = document.createElement("a")
  link.download = bp
  link.href = "data:text/plain;base64," + report
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  showSnackbar("Downloading fide report successful")
}

async function list_fide_reports() {
  let reply, report
  showLoading(true)
  try {
    reply = await $backend("interclub", "list_fide_reports", {
      token: idtoken.value,
    })
    fide_reports.value = reply.data
  } catch (error) {
    console.log("download error", error)
    showSnackbar("Download error: " + error.detail)
  } finally {
    showLoading(false)
  }
}

async function get_penalties_report(bp) {
  let reply, report
  showLoading(true)
  try {
    reply = await $backend("interclub", "get_penalties_report", {
      token: idtoken.value,
      path: bp,
    })
    report = reply.data.report
  } catch (error) {
    console.log("download error", error)
    showSnackbar("Download error: " + error.detail)
  } finally {
    showLoading(false)
  }
  const link = document.createElement("a")
  link.download = bp
  link.href = "data:text/plain;base64," + report
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  showSnackbar("Downloading penalties report successful")
}

async function list_penalties_reports() {
  let reply, report
  showLoading(true)
  try {
    reply = await $backend("interclub", "list_penalties_reports", {
      token: idtoken.value,
    })
    penalties_reports.value = reply.data
  } catch (error) {
    console.log("download error", error)
    showSnackbar("Download error: " + error.detail)
  } finally {
    showLoading(false)
  }
}

async function setup(icclub_, round_, icdata_) {
  console.log("setup Downloads", icclub_, round_, icdata_)
  icclub = icclub_
  round = round_
  icdata = icdata_
  showSnackbar = refsnackbar.value.showSnackbar
  showLoading = refloading.value.showLoading
  await list_bel_reports()
  await list_fide_reports()
  await list_penalties_reports()
}
</script>

<template>
  <VContainer>
    <SnackbarMessage ref="refsnackbar" />
    <ProgressLoading ref="refloading" />
    <h3>Registrations</h3>
    <v-btn @click="download_registrations">Download registrations</v-btn>
    <h3>Venues</h3>
    <v-btn @click="download_venues">Download venues</v-btn>
    <h3>Playerlists</h3>
    <v-btn @click="download_playerlists">Download playerlists</v-btn>
    <h3>Belgian Elo reports</h3>
    <v-row>
      <v-col cols="12" sm="6" md="4" lg="3" v-for="br in bel_reports">
        <v-btn @click="get_bel_report(br)">{{ br }}</v-btn>
      </v-col>
    </v-row>
    <h3>FIDE Elo reports</h3>
    <v-row>
      <v-col cols="12" sm="6" md="4" lg="3" v-for="br in fide_reports">
        <v-btn @click="get_fide_report(br)">{{ br }}</v-btn>
      </v-col>
    </v-row>
    <h3>Penalties reports</h3>
    <v-row>
      <v-col cols="12" sm="6" md="4" lg="3" v-for="br in penalties_reports">
        <v-btn @click="get_penalties_report(br)">{{ br }}</v-btn>
      </v-col>
    </v-row>
  </VContainer>
</template>
