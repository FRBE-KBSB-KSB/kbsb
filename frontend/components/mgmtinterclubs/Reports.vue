<script setup>
import { ref, computed } from "vue"
import { useMgmtTokenStore } from "@/store/mgmttoken"
import { storeToRefs } from "pinia"

// communication
defineExpose({ setup })
const mgmttokenstore = useMgmtTokenStore()
const { token } = storeToRefs(mgmttokenstore)
const { $backend } = useNuxtApp()

//  snackbar and loading widgets
import ProgressLoading from "@/components/ProgressLoading.vue"
import SnackbarMessage from "@/components/SnackbarMessage.vue"
const refsnackbar = ref(null)
let showSnackbar
const refloading = ref(null)
let showLoading

// datamodel
const eloprocs = ref([])
const sel_eloproc = ref()
let icdata, icclub, round

async function listEloprocessing() {
  showLoading(true)
  try {
    const reply = await $backend("interclub", "mgmt_list_eloprocessing", {
      token: token.value,
    })
    console.log(reply.data)
    eloprocs.value = []
    reply.data.forEach((ep) => {
      let short = ep.split("/")[1]
      if (short.length) eloprocs.value.push(short)
    })
  } catch (error) {
    console.error(error)
    showSnackbar(error.message)
  } finally {
    showLoading(false)
  }
}

async function write_eloprocessing() {
  showLoading(true)
  try {
    const reply = await $backend("interclub", "mgmt_write_eloprocessing", {
      token: token.value,
    })
    console.log(reply.data)
  } catch (error) {
    console.error(error)
    showSnackbar(error.message)
  } finally {
    showLoading(false)
  }
  await listEloprocessing()
}

async function write_bel_report() {
  showLoading(true)
  try {
    const reply = await $backend("interclub", "mgmt_write_bel_report", {
      token: token.value,
      round: round,
      path_elo: sel_eloproc.value,
    })
    showSnackbar("BEL elo rapport created")
  } catch (error) {
    showSnackbar(error.message)
  } finally {
    showLoading(false)
  }
}

async function write_fide_report() {
  showLoading(true)
  try {
    const reply = await $backend("interclub", "mgmt_write_fide_report", {
      token: token.value,
      round: round,
      path_elo: sel_eloproc.value,
    })
    showSnackbar("FIDE elo rapport created")
  } catch (error) {
    console.error(error)
    showSnackbar(error.message)
  } finally {
    showLoading(false)
  }
}

async function write_penalties_report() {
  showLoading(true)
  try {
    const reply = await $backend("interclub", "write_penalties_report", {
      token: token.value,
      round: round,
    })
    showSnackbar("BEL elo rapport created")
  } catch (error) {
    showSnackbar(error.message)
  } finally {
    showLoading(false)
  }
}

async function setup(icclub_, round_, icdata_) {
  console.log("setup reports", icclub_, round_, icdata_)
  icclub = icclub_
  round = round_
  icdata = icdata_
  showSnackbar = refsnackbar.value.showSnackbar
  showLoading = refloading.value.showLoading
  await listEloprocessing()
}
</script>

<template>
  <VContainer>
    <SnackbarMessage ref="refsnackbar" />
    <ProgressLoading ref="refloading" />
    <h3>Elo processing views</h3>
    <p>
      An Elo processing view is a snapshot of the of ratings (belgian and fide) in a
      certain point in time. The snapshot is needed because the fide ratings change every
      month while having no history in the Infomaniak SQL database.
    </p>
    <p>The view is used to calculate the elo reports.</p>
    <p>List of available elo processings views:</p>
    <ul>
      <li v-for="ep in eloprocs">
        {{ ep }}
      </li>
    </ul>
    <p>
      <v-btn @click="write_eloprocessing">Take new shapshot</v-btn>
    </p>
    <h3>Belgian Elo report</h3>
    <p>
      <v-select :items="eloprocs" v-model="sel_eloproc"</v-select>
      <v-btn @click="write_bel_report">Gererate BEL elo report round {{ round }}</v-btn>
    </p>
    <h3>Fide Elo report</h3>
    <p>
      <v-select :items="eloprocs" v-model="sel_eloproc"></v-select>
      <v-btn @click="write_fide_report">Gererate Fide elo report round {{ round }}</v-btn>
    </p>
    <h3>Penalties report</h3>
    <v-btn @click="write_penalties_report">Generate penalties report round {{ round }}</v-btn>    
  </VContainer>
</template>
