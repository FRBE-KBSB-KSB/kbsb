<script setup>
import { ref } from 'vue'

// stores
import { useMgmtTokenStore } from "@/store/mgmttoken"
import { useMgmtInterclubStore } from "@/store/mgmtinterclub"
import { storeToRefs } from 'pinia'
const mgmttokenstore = useMgmtTokenStore()
const { token: mgmttoken } = storeToRefs(mgmttokenstore)
const mgmtinterclubstore = useMgmtInterclubStore()
const { club, round } = storeToRefs(mgmtinterclubstore)

// communication 
defineExpose({ checkStore })
const { $backend } = useNuxtApp()

//  snackbar and loading widgets
import ProgressLoading from '@/components/ProgressLoading.vue'
import SnackbarMessage from '@/components/SnackbarMessage.vue'
const refsnackbar = ref(null)
let showSnackbar
const refloading = ref(null)
let showLoading


// datamodel
const runtimeConfig = useRuntimeConfig();

function checkStore() {
  // nothing happens here
}

function d() {
  console.log('token', mgmttoken.value)
  const url = `${runtimeConfig.public.apiurl}api/v1/interclubs/mgmt/command/xls/allplayerlist?token=${mgmttoken.value}`
  window.location.href = url
}

async function generateBelELO() {
  showLoading(true)
  try {
    const reply = await $backend("interclub", "mgmt_generate_bel_elo", {
      round: round.value,
      token: mgmttoken.value,
    })
    showSnackbar("BEL elo rapport created")
  }
  catch (error) {
    showSnackbar(error.message)
  }
  finally {
    showLoading(false)
  }
}

async function generateFideELO() {
  showLoading(true)
  try {
    const reply = await $backend("interclub", "mgmt_generate_fide_elo", {
      round: round.value,
      token: mgmttoken.value,
    })
    showSnackbar("FIDE elo rapport created")
  }
  catch (error) {
    console.error(error)
    showSnackbar(error.message)
  }
  finally {
    showLoading(false)
  }
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
    <h3>Playerlist</h3>
    <v-btn @click="d">Download full playerlist</v-btn>
    <h3 class="mt-3">ELO processing</h3>
    <VBtn class="ma-2" @click="generateFideELO" disabled>Generate FIDE rapport</VBtn>
    <VBtn class="ma-2" @click="generateBelELO" disabled>Generate BEL rapport</VBtn>
    <!-- <VBtn class="ma-2" @click="generateFideELO" >Generate FIDE rapport</VBtn>
    <VBtn class="ma-2" @click="generateBelELO" >Generate BEL rapport</VBtn> -->
    <h4 class="mt-2">Availabale ELo rapports</h4>
  </VContainer>
</template>
