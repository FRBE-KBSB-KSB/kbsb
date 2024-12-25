<script setup>
import { ref, onMounted } from "vue"
import { useI18n } from "vue-i18n"
import { parse } from "yaml"

import ResultsPublic from "@/components/interclubs/ResultsPublic.vue"
import Standings from "@/components/interclubs/Standings.vue"
import VenuePublic from "@/components/interclubs/VenuePublic.vue"
import PlayerlistPublic from "@/components/interclubs/PlayerlistPublic.vue"
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
const refplayerlist = ref(null)
const refvenues = ref(null)
// const refdates = ref(null)
const icdata = ref({})
const ic_rounds = ref([])

// methods alphabetically

function changeTab() {
  console.log("changeTab", tab.value)
  switch (tab.value) {
    case "results":
      refresults.value.setup(icdata.value)
      break
    case "standings":
      refstandings.value.setup(icdata.value)
      break
    case "playerlist":
      refplayerlist.value.setup()
      break
    case "venues":
      refvenues.value.setup()
      break
    // case "dates":
    //   refdates.value.setup()
    //   break
  }
}

async function parseYaml(group, name) {
  try {
    const yamlcontent = await readBucket(group, name)
    if (!yamlcontent) {
      return null
    }
    return parse(yamlcontent)
  } catch (error) {
    console.error("cannot parse yaml", yamlcontent)
  }
}

async function processICdata() {
  icdata.value = await parseYaml("data", "ic2425.yml")
  ic_rounds.value = Object.keys(icdata.value.rounds).map((x) => {
    return { value: x, title: `R${x}: ${icdata.value.rounds[x]}` }
  })
}

async function readBucket(group, name) {
  try {
    const reply = await $backend("filestore", "anon_get_file", {
      group,
      name,
    })
    return reply.data
  } catch (error) {
    console.error("failed to fetch file from bucket")
    return null
  }
}

onMounted(async () => {
  let l = route.query.locale
  console.log("query locale", l)
  locale.value = l ? l : "nl"
  await processICdata()
  tab.value = "results"
  changeTab()
})

definePageMeta({
  layout: "nomenu",
})
</script>

<template>
  <v-container>
    <h1>Interclubs 2024-25</h1>
    <v-tabs v-model="tab" color="green" @update:modelValue="changeTab">
      <v-tab value="results">{{ t("Results") }}</v-tab>
      <v-tab value="standings">{{ t("Standings") }}</v-tab>
      <v-tab value="playerlist">{{ t("Player list") }}</v-tab>
      <v-tab value="venues">{{ t("icn.ven_2") }}</v-tab>
      <!-- <v-tab value="dates">{{ t("Dates") }}</v-tab> -->
    </v-tabs>
    <v-window v-model="tab" @update:modelValue="changeTab" :touch="false">
      <v-window-item :eager="true" value="results">
        <ResultsPublic ref="refresults" />
      </v-window-item>
      <v-window-item :eager="true" value="standings">
        <Standings ref="refstandings" />
      </v-window-item>
      <v-window-item :eager="true" value="playerlist">
        <PlayerlistPublic ref="refplayerlist" />
      </v-window-item>
      <v-window-item :eager="true" value="venues">
        <VenuePublic ref="refvenues" />
      </v-window-item>
      <!-- <v-window-item :eager="true" value="dates">
        <Dates ref="refdates" />
      </v-window-item> -->
    </v-window>
  </v-container>
</template>
