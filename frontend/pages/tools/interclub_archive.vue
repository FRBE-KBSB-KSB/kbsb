<script setup>
import { ref, onMounted } from "vue"
import { useI18n } from "vue-i18n"
import ResultsArchive from "@/components/interclubs/ResultsArchive.vue"
import StandingsArchive from "@/components/interclubs/StandingsArchive.vue"

// locale
const { locale, t } = useI18n()

// communication
const route = useRoute()

// datamodel
const tab = ref(null)
const refresults = ref(null)
const refstandings = ref(null)
const season = ref("2425") // default season

// methods alphabetically

function changeTab() {
  switch (tab.value) {
    case "standings":
      refstandings.value.setup(season.value)
      break
    case "results":
      refresults.value.setup(season.value)
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
    <h1>Interclubs Archive</h1>
    <v-select
      v-model="season"
      label="Season"
      :items="['2425', '2324']"
      width="10em"
      v-on:update:modelValue="changeTab()"
    ></v-select>
    <v-tabs v-model="tab" color="green" @update:modelValue="changeTab">
      <v-tab value="standings">{{ t("Standings") }}</v-tab>
      <v-tab value="results">{{ t("Results") }}</v-tab>
    </v-tabs>
    <v-window v-model="tab" @update:modelValue="changeTab" :touch="false">
      <v-window-item :eager="true" value="standings">
        <StandingsArchive ref="refstandings" />
      </v-window-item>
      <v-window-item :eager="true" value="results">
        <ResultsArchive ref="refresults" />
      </v-window-item>
    </v-window>
  </v-container>
</template>
