<script setup>
import { ref, onMounted, ReactiveEffect } from "vue"
import { useI18n } from "vue-i18n"
import { parse } from "yaml"

import ResultsArchive from "@/components/interclubs/ResultsPublic.vue"
import StandingsArchive from "@/components/interclubs/StandingsArchive.vue"
// import Dates from "@/components/interclubs/Dates.vue"

// locale
const { locale, t } = useI18n()

// communication
const { $backend } = useNuxtApp()
const route = useRoute()

// datamodel
const tab = ref(null)
const refresults = ref(null)
const refstandings = ref(null)
const round = ref("1")

// methods alphabetically

function changeTab() {
  switch (tab.value) {
    case "standings":
      refstandings.value.setup("2324")
      break
    case "R1":
      refplayerlist.value.setup("2324", 1)
      break
    case "R2":
      refplayerlist.value.setup("2324", 2)
      break
    case "R3":
      refplayerlist.value.setup("2324", 3)
      break
    case "R4":
      refplayerlist.value.setup("2324", 4)
      break
    case "R5":
      refplayerlist.value.setup("2324", 5)
      break
    case "R6":
      refplayerlist.value.setup("2324", 6)
      break
    case "R7":
      refplayerlist.value.setup("2324", 7)
      break
    case "R8":
      refplayerlist.value.setup("2324", 8)
      break
    case "R9":
      refplayerlist.value.setup("2324", 9)
      break
    case "R10":
      refplayerlist.value.setup("2324", 10)
      break
    case "R11":
      refplayerlist.value.setup("2324", 11)
      break
  }
}

onMounted(async () => {
  let l = route.query.locale
  locale.value = l ? l : "nl"
  tab.value = "standings"
  changeTab()
})

definePageMeta({
  layout: "nomenu",
})
</script>

<template>
  <v-container>
    <h1>Interclubs 2023-24</h1>
    <v-tabs v-model="tab" color="green" @update:modelValue="changeTab">
      <v-tab value="standings">{{ t("Standings") }}</v-tab>
      <v-tab value="R1" max-width="50px">1</v-tab>
      <v-tab value="R2">2</v-tab>
      <v-tab value="R3">3</v-tab>
      <v-tab value="R4">4</v-tab>
      <v-tab value="R5">5</v-tab>
      <v-tab value="R6">6</v-tab>
      <v-tab value="R7">7</v-tab>
      <v-tab value="R8">8</v-tab>
      <v-tab value="R9">9</v-tab>
      <v-tab value="R10">10</v-tab>
      <v-tab value="R11">12</v-tab>
    </v-tabs>
    <v-window v-model="tab" @update:modelValue="changeTab" :touch="false">
      <v-window-item :eager="true" value="standings">
        <StandingsArchive ref="refstandings" />
      </v-window-item>
      <div v-for="r in 11" :key="r">
        <v-window-item :eager="true" :value="'R' + r">
          <ResultsArchive ref="refplayerlist" />
        </v-window-item>
      </div>
    </v-window>
  </v-container>
</template>
