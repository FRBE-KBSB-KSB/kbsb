<script setup>
import { ref } from "vue"
import { useI18n } from "vue-i18n"

// communication
defineExpose({ setup })
const { t } = useI18n()
const { $backend } = useNuxtApp()

// snackbar and laoding weidgets
import ProgressLoading from "@/components/ProgressLoading.vue"
import SnackbarMessage from "@/components/SnackbarMessage.vue"
const refsnackbar = ref(null)
let showSnackbar
const refloading = ref(null)
let showLoading

// datamodel
const icstandings = ref([])
const icclubs = ref([])
const idclub = ref(null)
let icdata = {}

async function getClubs() {
  let reply
  showLoading(true)
  try {
    reply = await $backend("interclub", "anon_getICclubs", {})
  } catch (error) {
    showSnackbar(t(error.message))
    return
  } finally {
    showLoading(false)
  }
  icclubs.value = reply.data
  icclubs.value.forEach((p) => {
    p.merged = `${p.idclub}: ${p.name}`
  })
}

async function getStandings() {
  let reply
  showLoading(true)
  try {
    reply = await $backend("interclub", "anon_getICstandings", {
      idclub: idclub.value,
    })
  } catch (error) {
    showSnackbar(t(error.message))
    return
  } finally {
    showLoading(false)
  }
  icstandings.value = reply.data
}

function setup(icdata_) {
  console.log("setup standings", icdata_)
  icdata = icdata_
  showSnackbar = refsnackbar.value.showSnackbar
  showLoading = refloading.value.showLoading
  getClubs()
}
</script>

<template>
  <v-container>
    <SnackbarMessage ref="refsnackbar" />
    <ProgressLoading ref="refloading" />
    <h2>{{ $t("Standings") }}</h2>
    <v-row>
      <v-col cols="8">
        <VAutocomplete
          v-model="idclub"
          :items="icclubs"
          item-title="merged"
          item-value="idclub"
          color="green"
          label="Club"
          clearable
        >
        </VAutocomplete>
      </v-col>
      <v-col cols="4">
        <VBtn icon="mdi-play" @click="getStandings"></VBtn>
      </v-col>
    </v-row>
    <v-card v-for="s in icstandings" class="my-2">
      <v-card-title>
        {{ $t("Division") }} {{ s.division }}{{ s.index }}
        <VDivider />
      </v-card-title>
      <v-card-text>
        <v-row>
          <v-col>#</v-col>
          <v-col cols="6">{{ $t("Team") }}</v-col>
          <v-col># {{ $t("Played") }}</v-col>
          <v-col><b>MP</b></v-col>
          <v-col>BP</v-col>
        </v-row>
        <v-row v-for="(t, ix) in s.teams">
          <v-col>{{ ix + 1 }}</v-col>
          <v-col cols="6">{{ t.name }} ({{ t.idclub }})</v-col>
          <v-col>{{ t.games.length }}</v-col>
          <v-col
            ><b>{{ t.matchpoints }}</b></v-col
          >
          <v-col>{{ t.boardpoints }}</v-col>
        </v-row>
      </v-card-text>
    </v-card>
    <v-dialog width="10em" v-model="waitingdialog">
      <v-card>
        <v-card-title>{{ $t("Loading...") }}</v-card-title>
        <v-card-text>
          <v-progress-circular indeterminate color="green" />
        </v-card-text>
      </v-card>
    </v-dialog>
  </v-container>
</template>
