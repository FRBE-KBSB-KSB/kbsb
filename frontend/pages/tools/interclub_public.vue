<script setup>
import { ref, onMounted } from "vue"
import { useI18n } from "vue-i18n"

// import ResultsPublic from '@/components/interclubs/ResultsPublic.vue'
// import Standings from '@/components/interclubs/Standings.vue'
import VenuePublic from "@/components/interclubs/VenuePublic.vue"
// import PlayerlistPublic from '@/components/interclubs/PlayerlistPublic.vue'
import Dates from "@/components/interclubs/Dates.vue"

// locale
const { locale, t } = useI18n()

// communication
const { $backend } = useNuxtApp()
const route = useRoute()

// datamodel
const tab = ref(null)
// const refresults = ref(null)
// const refstandings = ref(null)
// const refplayerlist = ref(null)
const refvenues = ref(null)
const refdates = ref(null)

// methods alphabetically

function changeTab() {
  console.log("changeTab", tab.value)
  switch (tab.value) {
    //     case 'results':
    //       refresults.value.setup()
    //       break
    //     case 'standings':
    //       refstandings.value.setup()
    //       break
    //     case 'playerlist':
    //       refplayerlist.value.setup()
    //       break
    case "venues":
      refvenues.value.setup()
      break
    case "dates":
      refdates.value.setup()
      break
  }
}

onMounted(() => {
  let l = route.query.locale
  console.log("query locale", l)
  locale.value = l ? l : "nl"
  // tab.value = "results"
  // changeTab()
})

definePageMeta({
  layout: "nomenu",
})
</script>

<template>
  <v-container>
    <h1>Interclubs 2024-25</h1>
    <v-tabs v-model="tab" color="green" @update:modelValue="changeTab">
      <!-- <v-tab value="results">{{ t("Results") }}</v-tab> -->
      <!-- <v-tab value="standings">{{ t('Standings') }}</v-tab> -->
      <!-- <v-tab value="playerlist">{{ t('Player list') }}</v-tab> -->
      <v-tab value="venues">{{ t("icn.ven_2") }}</v-tab>
      <v-tab value="dates">{{ t("Dates") }}</v-tab>
    </v-tabs>
    <v-window v-model="tab" @update:modelValue="changeTab">
      <!-- <v-window-item :eager="true" value="results">
        <ResultsPublic ref="refresults" />
      </v-window-item> -->
      <!-- <v-window-item :eager="true" value="standings">
        <Standings ref="refstandings" />
      </v-window-item> -->
      <!-- <v-window-item :eager="true" value="playerlist">
        <PlayerlistPublic ref="refplayerlist"/>
      </v-window-item>       -->
      <v-window-item :eager="true" value="venues">
        <VenuePublic ref="refvenues" />
      </v-window-item>
      <v-window-item :eager="true" value="dates">
        <Dates ref="refdates" />
      </v-window-item>
    </v-window>
  </v-container>
</template>
