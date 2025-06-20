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
const season = ref(0)

async function getStandings() {
  let reply
  showLoading(true)
  try {
    reply = await $backend("interclub", "anon_getICStandingsArchive", {
      season: season.value,
    })
  } catch (error) {
    showSnackbar(t(error.message))
    return
  } finally {
    showLoading(false)
  }
  icstandings.value = reply.data
}

function setup(season_) {
  console.log("setup standings archive", season_)
  season.value = season_
  showSnackbar = refsnackbar.value.showSnackbar
  showLoading = refloading.value.showLoading
  getStandings()
}
</script>

<template>
  <v-container>
    <SnackbarMessage ref="refsnackbar" />
    <ProgressLoading ref="refloading" />
    <h2>{{ $t("Standings") }}</h2>
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
  </v-container>
</template>
